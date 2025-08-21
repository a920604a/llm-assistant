from storage.crud.note import get_note


def get_notes(user_id: str):
    notes = get_note(user_id=user_id)
    return [
        {
            "filename": note.filename,
            "s3_key": note.s3_key,
            "upload_time": note.upload_time,
        }
        for note in notes
    ]
