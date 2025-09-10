from db.models import Paper
from sqlalchemy.dialects.postgresql import insert


class PaperRepository:
    def __init__(self, session):
        self.session = session

    def upsert_paper(self, paper_data: dict) -> None:
        """
        Upsert a paper record into the database using arxiv_id as unique key.
        If arxiv_id already exists, update fields.
        """
        stmt = insert(Paper).values(**paper_data)
        update_dict = {
            c.name: stmt.excluded[c.name]
            for c in Paper.__table__.columns
            if c.name not in ("id", "created_at")
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=["arxiv_id"],
            set_=update_dict,  # unique constraint
        )
        self.session.execute(stmt)
