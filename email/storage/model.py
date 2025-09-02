from datetime import datetime

from config import DATABASE_URL
from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    last_query_date = Column(Date)
    total_queries = Column(Integer, default=0, nullable=False)
    remaining_tokens = Column(Integer, default=1000, nullable=False)

    notes = relationship("Note", back_populates="owner")
    setting = relationship("UserSetting", back_populates="user", uselist=False)


class UserSetting(Base):
    __tablename__ = "user_setting"

    user_id = Column(
        String(255), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    user_language = Column(String(255), nullable=False, default="English")
    translate = Column(Boolean, nullable=False, default=False)
    system_prompt = Column(String, nullable=False, default="")
    top_k = Column(Integer, nullable=False, default=5)
    use_rag = Column(Boolean, nullable=False, default=True)
    subscribe_email = Column(Boolean, nullable=False, default=False)
    reranker_enabled = Column(Boolean, nullable=False, default=True)
    temperature = Column(Float, nullable=False, default=0.6)  # LLM temperature

    user = relationship("User", back_populates="setting")


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
