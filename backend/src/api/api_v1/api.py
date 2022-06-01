from fastapi import APIRouter

from src.api.api_v1.endpoints import login, user, file, image, user_favorite


api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(file.router, prefix="/file", tags=["file"])
api_router.include_router(image.router, prefix="/image", tags=["image"])
api_router.include_router(user_favorite.router, prefix="/user_favorite", tags=["user_favorite"])
