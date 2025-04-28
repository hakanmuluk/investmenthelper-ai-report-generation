from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx, asyncio, json, logging, os
from report_ai.report import run_generation_async
from report_ai.components.prompts import (
    generateQuestions, generateMoreQuestions, generateReportName
)

logger = logging.getLogger(__name__)
app = FastAPI()
UPLOAD_ENDPOINT = (
    "https://investmenthelper-ai-backend.up.railway.app/api/report/upload"
)

class ReportRequest(BaseModel):
    reportGenerationQuery: str
    username: str

@app.post("/generate-report")
async def generate_report(req: ReportRequest):
    """
    Streams a single whitespace byte immediately to reset Cloudflare's 100s timer,
    then performs Q/A generation, PDF creation, upload, and finally streams JSON.
    """
    async def streamer():
        # 0) Prevent Cloudflare timeout
        yield b' '  

        # 1) Build Q-A pairs
        user_query = req.reportGenerationQuery
        user_name = req.username
        answered, unanswerable = [], []

        async def ask(q: str, client: httpx.AsyncClient):
            r = await client.post(
                "https://investmenthelper-ai-backend.up.railway.app/api/ask/",
                json={"user_query": q, "past_messages": []},
                timeout=3000.0,
            )
            r.raise_for_status()
            return q, r.json().get("answer", "")

        loop_count = 0
        while len(answered) < 6 and loop_count < 5:
            loop_count += 1
            needed = 6 - len(answered)
            questions = (
                generateQuestions(user_query, needed)
                if not answered and not unanswerable
                else generateMoreQuestions(
                    user_query,
                    needed,
                    [q for q, _ in answered],
                    unanswerable,
                )
            )
            async with httpx.AsyncClient() as client:
                qa_pairs = await asyncio.gather(*(ask(q, client) for q in questions))
            for q, a in qa_pairs:
                (unanswerable if "Bilmiyorum" in a else answered).append((q, a))

        # 2) Prepare conversation for PDF generation
        conversations = []
        for q, a in answered[:5]:
            conversations.append({"role": "user", "content": q})
            conversations.append({"role": "assistant", "content": a})

        rep_name = generateReportName(user_query)
        title_dict = {"title": rep_name, "sub_title": "AI Generated Report"}

        # 3) Generate PDF asynchronously
        pdf_path = await run_generation_async(
            user_query,
            conversation=conversations,
            title_dict=title_dict,
            user_name=user_name,
            request_id=None,
            llm=os.getenv("LLM", "gpt"),
            apply_section_dedup=True,
        )

        # 4) Upload PDF
        file_id = None
        try:
            with open(pdf_path, "rb") as f:
                async with httpx.AsyncClient() as client:
                    upload_resp = await client.post(
                        UPLOAD_ENDPOINT,
                        files={"file": (rep_name, f, "application/pdf")},
                        headers={"x-user-id": user_name},
                        timeout=60.0,
                    )
                    upload_resp.raise_for_status()
                    file_id = upload_resp.json().get("id")
        except Exception as e:
            logger.error("Upload failed: %s", e, exc_info=True)
            # Stream an error JSON and end
            yield json.dumps({"error": "upload_failed", "detail": str(e)}).encode()
            return
        finally:
            # Clean up local file
            try:
                os.remove(pdf_path)
            except Exception:
                pass

        # 5) Stream final result
        yield json.dumps({"file_id": file_id}).encode()

    return StreamingResponse(streamer(), media_type="application/json")
