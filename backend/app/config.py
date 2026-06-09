from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_host : str
    database_port : int
    database_user : str
    database_password : str
    database_name : str
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 30 # 30 minutes by default
    OPENAI_API_KEY : Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()