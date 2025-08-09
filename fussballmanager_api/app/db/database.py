from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # Read .env, case-insensitive, and IGNORE any keys we don't define here
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
    database_url: str = Field(default="sqlite:///./dev.db", alias="DATABASE_URL")

@lru_cache
def get_settings() -> Settings:
    return Settings()

class Base(DeclarativeBase):
    pass

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, future=True, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
