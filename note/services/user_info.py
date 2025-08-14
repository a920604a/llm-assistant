from storage.crud.user import get_info


def get_user_info(user_id: str):
    return get_info(user_id=user_id)
