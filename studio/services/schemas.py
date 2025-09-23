from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import logging


logger = logging.getLogger(__name__)

class Token(BaseModel):
    logger.info('\nDefined [Token Model] is initiated ')
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    logger.info('\nDefined [TokenPayload Model] is initiated ')
    sub: str
    role: str
    typ: str

class UserCreate(BaseModel):
    logger.info('\nDefined [UserCreate Model] is initiated ')
    email: EmailStr
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    logger.info('\nDefined [UserLogin Model] is initiated ')
    email: EmailStr
    password: str

class ConfigOut(BaseModel):
    logger.info('\nDefined [ConfigOut Model] is initiated ')
    data: Dict[str, Any]

class ConfigUpdate(BaseModel):
    logger.info('\nDefined [ConfigUpdate Model] is initiated ')
    data: Dict[str, Any]

    