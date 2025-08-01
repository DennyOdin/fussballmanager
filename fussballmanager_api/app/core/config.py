import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = "FussballManager API"
    DEBUG = True
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

settings = Settings()
