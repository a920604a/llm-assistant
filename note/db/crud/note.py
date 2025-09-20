from datetime import datetime
from typing import List

from db.crud.user import get_or_create_user
from db.postgres import Note, User
from db.storage_metrics import monitored_db

from db import db_session


@monitored_db
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


@monitored_db
def get_note(user_id: str):
    with db_session() as db:
        notes = db.query(Note).filter(Note.user_id == user_id).all()
        return notes
