from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging

router = APIRouter()
templates = Jinja2Templates(directory="studio/templates")
logger = logging.getLogger(__name__)

@router.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
    logger.info('Defined [projects] is initiated ')
    models = {}
    return templates.TemplateResponse("projects.html", {"request": request, "models": models})

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    logger.info('Defined [settings] is initiated ')
    models = {}
    return templates.TemplateResponse("settings.html", {"request": request, "models": models})

