def get_or_create_user_from_sso(provider: str, profile_data: dict):
    # Check if linked social account exists
    # If not, create user & social link
    # Return user
    