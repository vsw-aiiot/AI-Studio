from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, column
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from datetime import datetime, timezone 
import logging

timeStamp_now = datetime.now(timezone.utc)
logger = logging.getLogger(__name__)

def utc_now():
    """Return current UTC datetime with timezone awareness."""
    logger.info('Defined [utc_now] is initiated ')
    return datetime.now(timezone.utc)

class User(SQLModel, table=True):
    logger.info('Defined [User model] is initiated ')
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="user")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)

    config: "UserConfig" = Relationship(back_populates="user")

class UserConfig(SQLModel, table=True):
    logger.info('Defined [UserConfig model] is initiated ')
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    data: dict = Field(sa_column=Column(SQLITE_JSON), default={})

    user: User = Relationship(back_populates="config")
    
class Conversation(SQLModel, table=True):
    logger.info('Defined [Conversation model] is initiated ')
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str = Field(default="New Conversation")
    system_prompt: str = Field(default="You are a helpful AI assistant.")
    temperature: float = Field(default=0.7)
    # messages: List[Dict] = Field(default_factory=list, sa_column=Column(JSON))
    messages: list[dict] = Field(default_factory=list, sa_column=Column(SQLITE_JSON))
    # messages_list: List[Message] = Relationship(back_populates="conversation")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

class ConversationRead(SQLModel):
    logger.info('Defined [ConversationRead model] is initiated ')
    id: int
    name: str
    messages: list[dict]

