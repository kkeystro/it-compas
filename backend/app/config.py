from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CareerCompass"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
