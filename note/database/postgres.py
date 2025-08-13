from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserData(Base):
    __tablename__ = "user_data"

    user_id = Column(String, primary_key=True, index=True)
    uploaded_notes = Column(Integer)
    last_query_date = Column(Date)
    total_queries = Column(Integer)
    remaining_tokens = Column(Integer)
