import os
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Request, APIRouter
from fastapi.responses import RedirectResponse
from fastapi import Depends
from sqlmodel import Session

from studio.core.config import settings
from studio.services.db import get_session as get_db

print(">>> LOADED: google.py <<<")
load_dotenv()

router = APIRouter()
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("/google/login")
async def login_via_google(request: Request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8030/auth/sso/google/callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = await oauth.google.parse_id_token(request, token)

        email = user_info.get("email")

        # Check if user exists
        user = db.query(User).filter_by(email=email).first()
        if not user:
            # Register new user
            user = User(email=email, name=user_info.get("name"))
            db.add(user)
            db.commit()

        # Set cookie, create session, etc.
        return RedirectResponse(url="/dashboard")

    except OAuthError as e:
        return {"error": str(e)}


