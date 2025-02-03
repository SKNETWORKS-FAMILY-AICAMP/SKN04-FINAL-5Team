from fastapi import APIRouter, Depends
from app.auth import get_current_user_from_cookie
from app.models import User

router = APIRouter(prefix="/protected", tags=["Protected"])
# router = APIRouter()

@router.get("/")
def protected_page(user: User = Depends(get_current_user_from_cookie)):
    return {"message": f"Hello, {user.username}. You are authenticated!"}
