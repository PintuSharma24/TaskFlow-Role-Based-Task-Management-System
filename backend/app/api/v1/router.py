
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    manager,
    admin,
    employee,
    chatbot
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(manager.router)
api_router.include_router(admin.router)
api_router.include_router(employee.router)
api_router.include_router(chatbot.router)
