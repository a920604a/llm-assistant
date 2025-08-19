from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    TIMESTAMP,
    func,
    ForeignKey,
    ARRAY,
)

from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, date


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    last_query_date = Column(Date)
    total_queries = Column(Integer)
    remaining_tokens = Column(Integer)

    notes = relationship("Note", back_populates="owner")


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)  # MinIO 上的 Key
    upload_time = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("users.id"))

    owner = relationship("User", back_populates="notes")


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
    pdf_cached_path = Column(Text, nullable=True)
    pdf_downloaded = Column(Boolean, default=False)
    pdf_parsed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
