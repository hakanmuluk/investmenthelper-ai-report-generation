""" from fastapi import FastAPI, Body
from pydantic import BaseModel
import httpx
import asyncio
from report_ai.components.prompts import generateQuestions, generateMoreQuestions
#uvicorn report_ai.server:app --reload --host 0.0.0.0 --port 8000
app = FastAPI()

class ReportRequest(BaseModel):
    reportGenerationQuery: str

@app.post("/generate-report")
async def generate_report(req: ReportRequest):
    userQuery = req.reportGenerationQuery
    # 1) generate the 10 questions
    questions = generateQuestions(userQuery, 3)

    # 2) define an async helper to ask one question
    async def ask(q: str, client: httpx.AsyncClient):
        resp = await client.post(
            "http://localhost:5001/api/ask/",
            json={"user_query": q, "past_messages": []},
            timeout=3000.0
        )
        resp.raise_for_status()
        return q, resp.json()["answer"]

    # 3) send them all in parallel
    async with httpx.AsyncClient() as client:
        tasks = [ask(q, client) for q in questions]
        qa_pairs = await asyncio.gather(*tasks)

    # 4) build your report string (or return the raw pairs)
    report_lines = [f"Q: {q}\nA: {a}" for q, a in qa_pairs]
    report_text = "\n\n".join(report_lines)

    return {"report": report_text} """

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import httpx
import asyncio
import json
import logging
from datetime import date
from fastapi.responses import JSONResponse
import os
from report_ai.report import run_generation_async

from report_ai.components.prompts import generateQuestions, generateMoreQuestions, generateReportName
logger = logging.getLogger(__name__)
app = FastAPI()
UPLOAD_ENDPOINT = "https://investmenthelper-ai-backend.up.railway.app/api/report/upload"


class ReportRequest(BaseModel):
    reportGenerationQuery: str
    username: str                  # ← new field


@app.post("/generate-report")
async def generate_report(req: ReportRequest,
    background_tasks: BackgroundTasks):
    user_query = req.reportGenerationQuery
    user_name = req.username      # ← pull in the username

    answered = []        # List[Tuple[str, str]]
    unanswerable = []    # List[str]

    async def ask(q: str, client: httpx.AsyncClient):
        resp = await client.post(
            "https://investmenthelper-ai-backend.up.railway.app/api/ask/",
            json={"user_query": q, "past_messages": []},
            timeout=3000.0
        )
        resp.raise_for_status()
        return q, resp.json().get("answer", "")

    # keep collecting until we have 5 real answers
    askLoopCount = 0
    while len(answered) < 6:
        askLoopCount +=1
        if askLoopCount > 5:
            break
        needed = 6 - len(answered)
        if not answered and not unanswerable:
            questions = generateQuestions(user_query, needed)
            print(questions)
        else:
            prev_qs = [q for q, _ in answered]
            questions = generateMoreQuestions(
                user_query,
                needed,
                prev_qs,
                unanswerable
            )
            print(questions)

        async with httpx.AsyncClient() as client:
            tasks = [ask(q, client) for q in questions]
            qa_pairs = await asyncio.gather(*tasks)

        for q, a in qa_pairs:
            if "Bilmiyorum" in a:
                unanswerable.append(q)
            else:
                answered.append((q, a))

    final_pairs = answered[:5]

    # build the chat‐style conversation
    conversations = []
    for q, a in final_pairs:
        conversations.append({"role": "user",      "content": q})
        conversations.append({"role": "assistant", "content": a})

    # example title dict—you can adapt as needed
    repName = generateReportName(user_query)
    title_dict = {
        "title": repName,
        "sub_title": "AI Generated Report"
    }

    # now pass the real username
    pdf_path = await run_generation_async(user_query,
        conversation=conversations,
        title_dict=title_dict,
        user_name=user_name,                 # ← use the incoming username
        request_id=None,
        llm=os.getenv('LLM', 'gpt'),
        apply_section_dedup=True
    )

    try:
        async with httpx.AsyncClient() as client:
            with open(pdf_path, "rb") as f:
                files = {
                    "file": (
                        repName,
                        f,
                        "application/pdf"
                    )
                }
                headers = {"x-user-id": user_name}
                upload_resp = await client.post(
                    UPLOAD_ENDPOINT,
                    files=files,
                    headers=headers,
                    timeout=60.0
                )
                upload_resp.raise_for_status()
                file_id = upload_resp.json().get("id")
    except Exception as e:
        logger.error(f"Upload to storage failed: {e}")
        raise HTTPException(status_code=502, detail="Failed to upload PDF to storage service.")

    # 3) Clean up the local PDF after response
    background_tasks.add_task(os.remove, pdf_path)

    # 4) Return the GridFS file ID only
    print("RETURN")
    return JSONResponse(content={"file_id": file_id})