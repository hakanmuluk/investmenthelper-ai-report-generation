from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx, asyncio, json, logging, os
from datetime import date
from report_ai.report import run_generation_async
from report_ai.components.prompts import (
    generateQuestions, generateMoreQuestions, generateReportName
)

logger = logging.getLogger(__name__)
app = FastAPI()
UPLOAD_ENDPOINT = (
    "https://investmenthelper-ai-backend.up.railway.app/api/report/upload"
)

# ---------------------------------------------------------------------------

class ReportRequest(BaseModel):
    reportGenerationQuery: str
    username: str

# ---------------------------------------------------------------------------

@app.post("/generate-report")
async def generate_report(req: ReportRequest):
    """
    Streams a single whitespace byte immediately (< 1 s) to keep Cloudflare
    happy, then does all the heavy work and finally streams the JSON body.
    """
    async def streamer():
        # 0) Immediately flush headers + first chunk  ------------------------
        yield b' '                                 # <= keeps connection alive

        # 1) Build the Q-A pairs  ------------------------------------------------
        user_query  = req.reportGenerationQuery
        user_name   = req.username

        answered, unanswerable = [], []

        async def ask(q: str, client: httpx.AsyncClient):
            r = await client.post(
                "https://investmenthelper-ai-backend.up.railway.app/api/ask/",
                json={"user_query": q, "past_messages": []},
                timeout=3000.0,
            )
            r.raise_for_status()
            return q, r.json().get("answer", "")

        ask_loop = 0
        while len(answered) < 6 and ask_loop < 5:
            ask_loop += 1
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

        # 2) Build chat conversation  -------------------------------------------
        conversations = [
            element
            for pair in answered[:5]
            for element in ({"role": "user", "content": pair[0]},
                            {"role": "assistant", "content": pair[1]})
        ]

        rep_name   = generateReportName(user_query)
        title_dict = {"title": rep_name, "sub_title": "AI Generated Report"}

        # 3) Generate the PDF  ---------------------------------------------------
        pdf_path = await run_generation_async(
            user_query,
            conversation=conversations,
            title_dict=title_dict,
            user_name=user_name,
            request_id=None,
            llm=os.getenv("LLM", "gpt"),
            apply_section_dedup=True,
        )

        # 4) Upload to GridFS-via-backend  --------------------------------------
        try:
            async with httpx.AsyncClient() as client, open(pdf_path, "rb") as f:
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
            raise HTTPException(502, "Failed to upload PDF to storage") from e
        finally:
            # 5) Clean up local file
            try:
                os.remove(pdf_path)
            except Exception:
                pass

        # 6) Final chunk: the real JSON  ----------------------------------------
        yield json.dumps({"file_id": file_id}).encode()

    # Return the streaming response
    return StreamingResponse(streamer(), media_type="application/json")
