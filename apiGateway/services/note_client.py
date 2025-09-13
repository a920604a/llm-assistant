import json

import httpx
import requests


def call_note_server(server_url: str, payload: dict):
    resp = requests.post(f"{server_url}/api/v1/ask", json=payload, timeout=180)
    resp.raise_for_status()
    return resp.json()


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
