class SocialAccount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider: str
    provider_user_id: str
    user_id: int = Field(foreign_key="user.id")
