from db.crud.user import get_or_create_user
from db.postgres import UserSetting
from db.storage_metrics import monitored_db

from db import db_session


@monitored_db
def get(user_id: str):
    with db_session() as db:
        setting = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
        if setting:
            return setting
        else:
            return None


@monitored_db
def update(user_id: str, settings: dict) -> bool:
    with db_session() as db:  # type: Session
        # 先檢查 user 是否存在
        user = get_or_create_user(db, user_id)

        # 再檢查 userSetting
        setting = db.query(UserSetting).filter(UserSetting.user_id == user.id).first()
        if not setting:
            setting = UserSetting(user_id=user_id, **settings)
            db.add(setting)
        else:
            for key, value in settings.items():
                if hasattr(setting, key):  # 確保是合法欄位
                    setattr(setting, key, value)

        db.commit()
        return True
