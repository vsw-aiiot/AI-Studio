from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from studio.auth.sso.google import oauth, get_google_user

router = APIRouter()

@router.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback/google")
async def google_callback(request: Request):
    user_info = await get_google_user(request)
    # Process user_info: check if user exists or register new user
    return {"email": user_info["email"], "name": user_info.get("name")}
