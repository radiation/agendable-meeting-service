from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    model_config = ConfigDict(from_attributes=True)
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "super_duper_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"  # Automatically load values from `.env`


settings = Settings()
