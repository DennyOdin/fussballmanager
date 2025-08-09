from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health_check():
    return {"status": "healthy", "message": "Fussball Manager API is running"}
