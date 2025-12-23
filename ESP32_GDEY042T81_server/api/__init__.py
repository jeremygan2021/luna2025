from fastapi import APIRouter
from api import devices, contents, todos

api_router = APIRouter()

# 注册所有路由，并添加全局安全要求
api_router.include_router(devices.router, prefix="/devices")
api_router.include_router(contents.router, prefix="/contents")
api_router.include_router(todos.router, prefix="/todos")