from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from contextlib import contextmanager
from conf import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


# 在 FastAPI 中取得 Session
# 這個 get_db 就是給 FastAPI 用的依賴注入
def get_db():
    with db_session() as session:
        yield session
