from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    last_query_date = Column(Date)
    total_queries = Column(Integer, default=0, nullable=False)
    remaining_tokens = Column(Integer, default=1000, nullable=False)

    setting = relationship("UserSetting", back_populates="user", uselist=False)
    chat_histories = relationship(
        "ChatHistory", back_populates="user", passive_deletes=True
    )


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    input_token = Column(Integer)
    output_token = Column(Integer)
    latency_ms = Column(Integer)
    model = Column(String(64))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 與 User 建立 ORM 關聯
    user = relationship("User", back_populates="chat_histories", passive_deletes=True)


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
