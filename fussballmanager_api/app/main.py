from fastapi import FastAPI
from app.routes import health, auth, members
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine

app = FastAPI(title="FussballManager API")

# Create all DB tables on startup (only during dev)
Base.metadata.create_all(bind=engine)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(members.router)
