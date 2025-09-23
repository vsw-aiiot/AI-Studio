from fastapi import APIRouter, Depends, Form, Response, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
import logging

from studio.services.db import get_session
from studio.services.crud import create_user, authenticate_user
from studio.services.security import (
    create_access_token, create_refresh_token, decode_token
)
from studio.settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS,
    COOKIE_DOMAIN, SECURE_COOKIES
)

templates = Jinja2Templates(directory="studio/templates")

router = APIRouter(prefix="/auth", tags=["auth"])

cookie_params = dict(
    httponly=True,
    secure=SECURE_COOKIES,
    samesite="lax",
    domain=COOKIE_DOMAIN or None,   # allow localhost
)
logger = logging.getLogger(__name__)

# ---------- Pages ----------
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    logger.info('Defined [login_page] is initiated ')
    return templates.TemplateResponse("login.html", {"request": request, "models": {}})

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    logger.info('Defined [register_page] is initiated ')
    return templates.TemplateResponse("register.html", {"request": request, "models": {}})

# ---------- Registration ----------
@router.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("user"),
    session: Session = Depends(get_session)
):
    logger.info('Defined [register] is initiated ')
    create_user(session, email, password, role)
    return RedirectResponse(url="/auth/login", status_code=303)  # <<< redirect

# ---------- Login ----------
@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session_db: Session = Depends(get_session)
):
    logger.info('Defined [login] is initiated ')
    user = authenticate_user(session_db, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access  = create_access_token(user.id, user.role, ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh = create_refresh_token(user.id, user.role, REFRESH_TOKEN_EXPIRE_DAYS)

    # persist in server-side session so your Jinja checks work
    request.session["user_id"] = user.id
    request.session["role"]    = user.role

    resp = RedirectResponse(url="/chat", status_code=303)  # <<< redirect to chat
    resp.set_cookie("access_token", access,  **cookie_params)
    resp.set_cookie("refresh_token", refresh, **cookie_params)
    return resp

# ---------- Refresh ----------
@router.post("/refresh")
def refresh_token(response: Response, refresh_token: str = Form(...)):
    logger.info('Defined [refresh_token] is initiated ')
    try:
        payload = decode_token(refresh_token)
        if payload.get("typ") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload["sub"])
        role = payload["role"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    access = create_access_token(user_id, role, ACCESS_TOKEN_EXPIRE_MINUTES)
    response.set_cookie("access_token", access, **cookie_params)
    return {"access_token": access, "token_type": "bearer"}

# ---------- Logout ----------
@router.post("/logout")
def logout(request: Request):
    logger.info('Defined [logout] is initiated ')
    request.session.clear()  # clear server-side session
    resp = RedirectResponse(url="/chat", status_code=303)  # <<< back to guest chat
    resp.delete_cookie("access_token", domain=COOKIE_DOMAIN or None)
    resp.delete_cookie("refresh_token", domain=COOKIE_DOMAIN or None)
    return resp
