import requests
from conf import NOTE_API_URL


def get_user_data(user_id: str):
    # uploaded_papers: int
    # last_query_date: date
    # total_queries: int
    # remaining_tokens: int
    resp = requests.get(f"{NOTE_API_URL}/api/user/{user_id}")

    resp.raise_for_status()
    return resp.json()


def update_user_settings(user_id: str):
    pass
