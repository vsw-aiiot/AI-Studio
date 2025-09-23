from fastapi import APIRouter

from studio.auth.sso.google import router as google_router
# from auth.sso.google import router as google_router
# from studio.auth.sso.github import router as github_router (later)
# from sso.google import router as google_router

router = APIRouter()
router.include_router(google_router, prefix="/sso")

