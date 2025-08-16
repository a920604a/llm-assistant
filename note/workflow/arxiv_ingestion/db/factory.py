import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SessionType, declarative_base
from typing import Generator, Optional
import os
from contextlib import contextmanager

logger = logging.getLogger(__name__)

Base = declarative_base()

class Database:
    """
    DB 工廠與 Session 管理
    """

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@note-db:5432/note"  # 請替換成實際帳密與 DB 名稱
        )
        self.engine = create_engine(self.db_url, echo=False, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False, class_=SessionType)
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
