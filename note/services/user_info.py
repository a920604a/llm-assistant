from storage.crud.user import get


def get_info(user_id: str):
    return get(user_id=user_id)
