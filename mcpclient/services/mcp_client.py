import requests


def call_note_server(server_url: str, payload: dict):
    resp = requests.post(f"{server_url}/api/query", json=payload)
    resp.raise_for_status()
    return resp.json()
