from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgresql://user:password@host:port/dbname"

    secret_key: str = ""
    algorithm: str = "HS256"

    cloudinary_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 587
    mail_server: str = ""

    redis_host: str = "redis"
    redis_port: int = 6379

    model_config = SettingsConfigDict(env_file=env_path, extra="ignore")


settings = Settings()
