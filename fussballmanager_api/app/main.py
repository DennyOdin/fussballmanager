from fastapi import FastAPI
from app.routes import health, auth
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine  # ✅ added to trigger table creation

app = FastAPI(title="FussballManager API")

# ✅ Create all DB tables on startup (only during dev)
Base.metadata.create_all(bind=engine)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(auth.router)
