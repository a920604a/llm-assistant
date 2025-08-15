from datetime import date, datetime
from typing import List
from storage import db_session
from storage.postgres import User, Note
from datetime import date
from storage.crud.user import get_or_create_user


def update_notes(user_id: str, saved_files: List[str]):

    # save postgres: 寫入 notes table
    with db_session() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = get_or_create_user(db, user_id)

        for filename in saved_files:
            note = Note(
                filename=filename,
                s3_key=filename,
                upload_time=datetime.utcnow(),
                owner=user,
            )
            db.add(note)
        db.commit()


def get_notes(user_id: str):
    with db_session() as db:
        notes = db.query(Note).filter(Note.user_id == user_id).all()
        return notes
