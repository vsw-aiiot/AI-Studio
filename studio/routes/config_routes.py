# routes/config.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
import logging

from studio.services.db import get_session
from studio.services.config_manager import load_user_config_db, save_user_config_db
from studio.dependency import get_current_user
from studio.services.schemas import ConfigOut, ConfigUpdate

DEFAULT_CONFIG = {
    "features": {
        "context_export": True,
        "context_import": True
    }
}

router = APIRouter(prefix="/me", tags=["config"])
logger = logging.getLogger(__name__)

@router.get("/config", response_model=ConfigOut)
def get_my_config(
    session: Session = Depends(get_session),
    user = Depends(get_current_user),
):
    logger.info('Defined [get_my_config] is initiated ')
    data = load_user_config_db(session, user.id, DEFAULT_CONFIG)
    return {"data": data}

@router.put("/config", response_model=ConfigOut)
def update_my_config(
    payload: ConfigUpdate,
    session: Session = Depends(get_session),
    user = Depends(get_current_user),
):
    logger.info('Defined [update_my_config] is initiated ')
    data = save_user_config_db(session, user.id, payload.data)
    return {"data": data}
