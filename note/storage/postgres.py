from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, date


Base = declarative_base()


# class UserData(Base):
#     __tablename__ = "user_data"

#     user_id = Column(String, primary_key=True, index=True)
#     uploaded_papers = Column(Integer)
#     last_query_date = Column(Date)
#     total_queries = Column(Integer)
#     remaining_tokens = Column(Integer)


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
