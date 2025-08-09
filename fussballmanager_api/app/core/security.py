from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Settings(BaseSettings):
    # Same idea: read .env but ignore unrelated keys
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
    jwt_secret: str = Field(default="change_me_in_prod", alias="JWT_SECRET")
    jwt_alg: str = Field(default="HS256", alias="JWT_ALG")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

@lru_cache
def get_settings() -> Settings:
    return Settings()

def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(sub: str) -> str:
    s = get_settings()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode({"sub": sub, "exp": expire}, s.jwt_secret, algorithm=s.jwt_alg)
