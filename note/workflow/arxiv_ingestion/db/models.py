from sqlalchemy import Column, Integer, String, Text, Boolean, Date, TIMESTAMP, func
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
    pdf_cached_path = Column(Text, nullable=True)
    pdf_downloaded = Column(Boolean, default=False)
    pdf_parsed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
