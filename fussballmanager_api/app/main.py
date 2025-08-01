from fastapi import FastAPI
from app.routes import health, auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FussballManager API")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(auth.router)
