from sqlmodel import SQLModel, create_engine, Session, select
import os
import logging
from .models import Conversation

DB_URL = os.getenv("DB_URL", "sqlite:///./studio.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

logger = logging.getLogger(__name__)

def get_session():
    logger.info('\nDefined [get_session] is initiated ')
    with Session(engine) as session:
        yield session

def init_db():
    logger.info('\nDefined [init_db] is initiated ')
    SQLModel.metadata.create_all(engine)

def get_user_sessions(user_id: int):
    logger.info(f"[get_user_sessions] fetching sessions for user {user_id}")
    with Session(engine) as session:
        statement = select(Conversation).where(Conversation.user_id == user_id)
        results = session.exec(statement).all()
        return results
    
    