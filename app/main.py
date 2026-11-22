import json
import time

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

from app.schemas import ExtractRequest, RFQExtraction
from app.services.ollama_client import MODEL, generate, generate_json
from app.utils.audit import log_event

app = FastAPI(title="Procurement & RFQ Intelligence Agent")


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    answer: str
    latency_sec: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    start = time.time()
    try:
        answer = await generate(req.prompt)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}")

    latency = round(time.time() - start, 2)
    log_event(endpoint="chat", model=MODEL, prompt=req.prompt,
              answer=answer, latency_sec=latency)
    return ChatResponse(answer=answer, latency_sec=latency)


@app.post("/extract", response_model=RFQExtraction)
async def extract(req: ExtractRequest):
    start = time.time()
    prompt = (
        "Extract the RFQ details from the document below. "
        "Use null for anything not stated. Do not invent values.\n\n"
        f"DOCUMENT:\n{req.text}"
    )
    try:
        raw = await generate_json(prompt, RFQExtraction.model_json_schema())
        result = RFQExtraction.model_validate(raw)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}")
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(status_code=422, detail=f"Model output invalid: {e}")

    latency = round(time.time() - start, 2)
    log_event(endpoint="extract", model=MODEL, input_chars=len(req.text),
              output=result.model_dump(), latency_sec=latency)
    return result