from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
import logging

from studio.services.db import get_session
from studio.services.crud import get_user_by_id
from studio.services.security import decode_token
from studio.settings import ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
logger = logging.getLogger(__name__)

def _get_token_from_request(request: Request) -> str | None:
    # Prefer Authorization header; fallback to cookie "access_token"
    logger.info('\nDefined [_get_token_from_request] is initiated ')
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1]
    return request.cookies.get("access_token")

def get_current_user(
    request: Request,
    session: Session = Depends(get_session)
):
    logger.info('\nDefined [get_current_user] is initiated ')
    token = _get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_token(token)
        if payload.get("typ") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = get_user_by_id(session, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

def require_roles(*roles: str):
    def wrapper(user = Depends(get_current_user)):
        logger.info('\nDefined [require_roles - wrapper] is initiated ')
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return wrapper
