import json

import httpx
import requests
from api.schemas.ask import AskResponse


def call_note_server(server_url: str, payload: dict) -> str:
    resp = requests.post(f"{server_url}/api/v1/ask", json=payload, timeout=180)
    resp.raise_for_status()
    response = resp.json()
    askResponse = AskResponse(
        query=response["query"],
        answer=response["answer"],
        sources=response["sources"],
        chunks_used=response["chunks_used"],
        search_mode=response["search_mode"],
    )
    reply = f"{askResponse.answer}\n\n\n"

    if askResponse.chunks_used:
        reply += f"引用的資料片段 {askResponse.chunks_used} 個:\n"

    if askResponse.sources:
        reply += "\n".join(f"- {s}" for s in askResponse.sources)
    # reply += f"檢索模式：{askResponse.search_mode}\n"

    return reply


async def call_note_stream_server(server_url: str, payload: dict):
    async with httpx.AsyncClient(timeout=180.0) as client:
        async with client.stream(
            "POST", f"{server_url}/api/v1/stream", json=payload
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    yield chunk
                except json.JSONDecodeError:
                    # 如果不是 json，可以忽略或 log
                    continue
