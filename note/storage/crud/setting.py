from datetime import date

from storage import db_session
from storage.postgres import User, UserSetting


def get(user_id: str):
    with db_session() as db:
        setting = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
        if setting:
            return setting
        else:
            return None


def update(user_id: str, settings: dict) -> bool:
    with db_session() as db:  # type: Session
        # 先檢查 user 是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            # 建立新的 user（避免 user_setting 孤兒）
            user = User(
                id=user_id,
                last_query_date=date.today(),
                total_queries=0,
                remaining_tokens=1000,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 再檢查 userSetting
        setting = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
        if not setting:
            setting = UserSetting(user_id=user_id, **settings)
            db.add(setting)
        else:
            for key, value in settings.items():
                if hasattr(setting, key):  # 確保是合法欄位
                    setattr(setting, key, value)

        db.commit()
        return True
