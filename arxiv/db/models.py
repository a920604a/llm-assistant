from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    arxiv_id = Column(String(32), unique=True, nullable=False)
    title = Column(Text, nullable=True)
    authors = Column(ARRAY(Text), nullable=True)
    abstract = Column(Text, nullable=True)
    categories = Column(ARRAY(Text), nullable=True)
    published_date = Column(Date, nullable=True)
    updated_date = Column(Date, nullable=True)
    pdf_url = Column(Text, nullable=True)

    # Parsed PDF content (added for comprehensive storage)
    raw_text = Column(Text, nullable=True)
    sections = Column(JSON, nullable=True)
    references = Column(JSON, nullable=True)
    # PDF processing metadata
    parser_used = Column(String, nullable=True)
    parser_metadata = Column(JSON, nullable=True)
    pdf_processed = Column(Boolean, default=False, nullable=False)
    pdf_processing_date = Column(DateTime, nullable=True)
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
