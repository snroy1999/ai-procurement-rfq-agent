import json
import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:4b"


async def generate(prompt: str) -> str:
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
    return r.json()["response"]


async def generate_json(prompt: str, schema: dict) -> dict:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": schema,
        "think": False,
        "options": {"temperature": 0},
    }
    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
    return json.loads(r.json()["response"])