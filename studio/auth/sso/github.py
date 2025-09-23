from fastapi import Request


async def login(request: Request):
    redirect_uri = request.url_for("github_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

async def callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    profile = await oauth.google.parse_id_token(request, token)
    return get_or_create_user_from_sso("github", profile)
