from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging

router = APIRouter()
templates = Jinja2Templates(directory="studio/templates")
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info('Defined [home] is initiated ')
    return templates.TemplateResponse("base.html", {
        "request": request,
        "models": {"gpt-4": "GPT-4", "gemini": "Gemini"},
        "conversations": {"Demo Chat": {}, "Meeting Notes": {}},
        "agent": "gpt-4"
    })

# ---------- Chat Page ----------
@router.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    logger.info('Defined [chat_page] is initiated ')
    user_id = request.session.get("user_id")
    role = request.session.get("role", "guest")

    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user_id": user_id,
        "role": role
    })

# ---------- Optional: Profile Page ----------
@router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    logger.info('Defined [profile_page] is initiated ')
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user_id": user_id,
        "role": request.session.get("role")
    })


