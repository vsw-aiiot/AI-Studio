from sqlmodel import select, Session
from passlib.hash import bcrypt
from studio.services.models import User, UserConfig
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Optional
from datetime import datetime, timezone
import logging

from studio.services.models import User, UserConfig
from studio.services.security import hash_password, verify_password
from studio.services.models import Conversation

logger = logging.getLogger(__name__)

def create_user(session: Session, email: str, password: str, role: str = "user") -> User:
    logger.info('\nDefined [create_user] is initiated ')
    hashed = hash_password(password)
    user = User(email=email, password_hash=hashed, role=role)
    session.add(user)
    session.commit()
    session.refresh(user)
    cfg = UserConfig(user_id=user.id, data={})
    session.add(cfg)
    session.commit()
    return user

def authenticate_user(session: Session, email: str, password: str) -> User | None:
    logger.info('\nDefined [authenticate_user] is initiated ')
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def get_user_by_id(session: Session, user_id: int) -> User | None:
    logger.info('\nDefined [get_user_by_id] is initiated ')
    return session.get(User, user_id)

def get_user_config(session: Session, user_id: int) -> dict:
    logger.info('\nDefined [get_user_config] is initiated ')
    cfg = session.exec(select(UserConfig).where(UserConfig.user_id == user_id)).first()
    return cfg.data if cfg else {}

def set_user_config(session: Session, user_id: int, data: dict):
    logger.info('\nDefined [set_user_config] is initiated ')
    cfg = session.exec(select(UserConfig).where(UserConfig.user_id == user_id)).first()
    if not cfg:
        cfg = UserConfig(user_id=user_id, data=data)
        session.add(cfg)
    else:
        cfg.data = data
    session.commit()
    session.refresh(cfg)
    return cfg.data

def create_conversation(db: Session, user_id: int, name: str):
    logger.info('\nDefined [create_conversation] is initiated ')
    if not name:
        name = "New Conversation"
    convo = Conversation(user_id=user_id, name=name)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo

def get_conversations_by_user(db: Session, user_id: int) -> List[Conversation]:
    logger.info('\nDefined [get_conversations_by_user] is initiated ')
    return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).all()

def get_conversation(db: Session, convo_id: int, user_id: int) -> Optional[Conversation]:
    logger.info('\nDefined [get_conversation] is initiated ')
    return db.query(Conversation).filter(
        Conversation.id == convo_id, Conversation.user_id == user_id
    ).first()

 

def update_conversation_settings(db: Session, convo_id: int, user_id: int, system_prompt: str, temperature: float):
    logger.info('\nDefined [update_conversation_settings] is initiated ')
    convo = get_conversation(db, convo_id, user_id)
    if convo:
        convo.system_prompt = system_prompt
        convo.temperature = temperature
        convo.updated_at = datetime.now(timezone.utc)
        db.commit()
        return convo
    return None

def append_message(db: Session, convo_id: int, user_id: int, role: str, content: str):
    logger.info('\nDefined [append_message] is initiated ')
    convo = get_conversation(db, convo_id, user_id)
    if convo:
        convo.messages.append({"role": role, "content": content})
        flag_modified(convo, "messages")
        convo.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(convo)
        print(f"[DEBUG] Messages after append: {convo.messages}")  # debugging
        return convo
    return None

def update_conversation(db: Session, convo: Conversation):
    logger.info('\nDefined [update_conversation] is initiated ')
    convo.updated_at = datetime.now(timezone.utc)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return convo

def delete_conversation(db: Session, convo_id: int, user_id: int):
    logger.info('\nDefined [delete_conversation] is initiated ')
    convo = get_conversation(db, convo_id, user_id)
    if not convo:
        return None
    db.delete(convo)
    db.commit()
    return True

