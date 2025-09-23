from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GROQ_API: str
    TOGETHER_API: str
    TOGETHER_URL: str

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
