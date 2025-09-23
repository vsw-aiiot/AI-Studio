# studio/settings.py
from datetime import timedelta
import secrets

SECRET_KEY = secrets.token_urlsafe(32)  # put a fixed value in env/secret manager in prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
COOKIE_DOMAIN = None            # e.g. ".yourdomain.com" in prod
SECURE_COOKIES = False          # True in prod (https)
