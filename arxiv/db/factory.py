from contextlib import contextmanager
from typing import Generator, Optional

from config import DATABASE_URL
from logger import get_logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)


class Database:
    """
    DB 工廠與 Session 管理
    """

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or DATABASE_URL
        self.engine = create_engine(self.db_url, echo=False, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False, class_=SessionType
        )
        logger.info(f"Database initialized with {self.db_url}")

    @contextmanager
    def get_session(self) -> Generator[SessionType, None, None]:
        """
        使用 context manager 取得 session
        """
        session: SessionType = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()


def make_database(db_url: Optional[str] = None) -> Database:
    """
    建立 Database 實例
    """
    return Database(db_url=db_url)
