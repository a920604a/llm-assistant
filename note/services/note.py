from storage.minio import s3_client, create_bucket_if_not_exists, MINIO_BUCKET
from storage.crud.user import get_user_notes_number
from storage.crud.note import update_note
from tasks.upload import import_md_notes_task
from storage.crud.note import get_notes


def get_notes(user_id: str):
    notes = get_notes(user_id=user_id)
    return [
        {
            "filename": note.filename,
            "s3_key": note.s3_key,
            "upload_time": note.upload_time,
        }
        for note in notes
    ]
