from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "RakshaNet Web Backend"
    API_V1_STR: str = "/api/v1"
    PORT: int = Field(default=8000)
    HOST: str = Field(default="0.0.0.0")
    DEBUG: bool = Field(default=True)
    
    FIREBASE_CREDENTIALS_PATH: str = Field(default="firebase-key.json")
    GEMINI_API_KEY: str = Field(...)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings(
    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY", "dummy_key")
)
