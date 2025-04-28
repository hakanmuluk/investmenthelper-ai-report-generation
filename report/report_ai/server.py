from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx, asyncio, json, logging, os, uuid
from report_ai.report import run_generation_async
from report_ai.components.prompts import (
    generateQuestions, generateMoreQuestions, generateReportName
)

logger = logging.getLogger(__name__)
app = FastAPI()
UPLOAD_ENDPOINT = (
    "https://investmenthelper-ai-backend.up.railway.app/api/report/upload"
)

# In-memory job store; replace with Redis/Mongo for production
jobs: dict[str, dict] = {}

class ReportRequest(BaseModel):
    reportGenerationQuery: str
    username: str

@app.post("/generate-report")
async def start_report(req: ReportRequest, background_tasks: BackgroundTasks):
    """
    Starts a background job for report generation and returns a job_id immediately.
    """
    job_id = uuid.uuid4().hex
    jobs[job_id] = {"state": "running"}
    background_tasks.add_task(run_job, job_id, req)
    return JSONResponse({"job_id": job_id})

@app.get("/report-status/{job_id}")
def report_status(job_id: str):
    """
    Returns the state of a report job: "running", "ready", or "error".
    """
    return jobs.get(job_id, {"state": "unknown"})

@app.get("/report-result/{job_id}")
def report_result(job_id: str):
    """
    Returns the file_id if the job is ready; 404 otherwise.
    """
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("state") == "ready":
        return {"file_id": job["file_id"]}
    if job.get("state") == "error":
        raise HTTPException(status_code=500, detail=job.get("error"))
    raise HTTPException(status_code=202, detail="Report is still running")

async def run_job(job_id: str, req: ReportRequest):
    """
    Worker function for generating the report and uploading it.
    Updates the jobs dict upon completion or error.
    """
    try:
        # Q/A generation
        answered, unanswerable = [], []
        for _ in range(10):
            needed = 13 - len(answered)
            questions = (
                generateQuestions(req.reportGenerationQuery, needed)
                if not answered and not unanswerable
                else generateMoreQuestions(
                    req.reportGenerationQuery,
                    needed,
                    [q for q, _ in answered],
                    unanswerable,
                )
            )
            async with httpx.AsyncClient() as client:
                qa_pairs = await asyncio.gather(*[ask_question(q, client) for q in questions])
            for q, a in qa_pairs:
                (unanswerable if "Bilmiyorum" in a else answered).append((q, a))
            if len(answered) >= 10:
                break

        # Build conversation
        conversations = []
        for q, a in answered[:5]:
            conversations.append({"role": "user", "content": q})
            conversations.append({"role": "assistant", "content": a})

        # Generate PDF
        rep_name = generateReportName(req.reportGenerationQuery)
        title_dict = {"title": rep_name, "sub_title": "AI Generated Report"}
        pdf_path = await run_generation_async(
            req.reportGenerationQuery,
            conversation=conversations,
            title_dict=title_dict,
            user_name=req.username,
            request_id=None,
            llm=os.getenv("LLM", "gpt"),
            apply_section_dedup=True,
        )

        # Upload PDF
        with open(pdf_path, "rb") as f:
            async with httpx.AsyncClient() as client:
                upload_resp = await client.post(
                    UPLOAD_ENDPOINT,
                    files={"file": (rep_name, f, "application/pdf")},
                    headers={"x-user-id": req.username},
                    timeout=60.0,
                )
                upload_resp.raise_for_status()
                file_id = upload_resp.json().get("id")

        # Clean up
        try:
            os.remove(pdf_path)
        except Exception:
            pass

        # Mark job ready
        jobs[job_id] = {"state": "ready", "file_id": file_id}
    except Exception as e:
        logger.error(f"Job {job_id} failed: %s", e, exc_info=True)
        jobs[job_id] = {"state": "error", "error": str(e)}

# Helper for asking questions in run_job
async def ask_question(q: str, client: httpx.AsyncClient):
    resp = await client.post(
        "https://investmenthelper-ai-backend.up.railway.app/api/ask/",
        json={"user_query": q, "past_messages": []},
        timeout=3000.0,
    )
    resp.raise_for_status()
    return q, resp.json().get("answer", "")
