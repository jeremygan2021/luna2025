from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import logging
import os

from config import settings
from database import init_db
from mqtt_manager import mqtt_manager
from api import api_router
from admin_routes import admin_router
from auth import APIKeyMiddleware, AdminAuthMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info("正在启动墨水屏桌面屏幕系统服务端...")
    
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
    
    # 连接MQTT代理
    try:
        mqtt_manager.connect()
        logger.info("MQTT连接已启动")
    except Exception as e:
        logger.error(f"MQTT连接失败: {str(e)}")
    
    # 确保静态文件目录存在
    os.makedirs(settings.static_dir, exist_ok=True)
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭墨水屏桌面屏幕系统服务端...")
    
    # 断开MQTT连接
    mqtt_manager.disconnect()
    logger.info("MQTT连接已断开")

# 创建FastAPI应用
app = FastAPI(
    title="墨水屏桌面屏幕系统 API",
    description="用于管理墨水屏设备、内容和待办事项的API",
    version="1.0.0",
    lifespan=lifespan,
    openapi_components={
        "securitySchemes": {
            "APIKeyHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API Key鉴权，请在下方输入正确的API Key"
            }
        }
    },
    security=[{"APIKeyHeader": []}]
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的允许来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加API Key鉴权中间件
app.add_middleware(APIKeyMiddleware)

# 添加Admin认证中间件
app.add_middleware(AdminAuthMiddleware)

# 添加Session中间件
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

# 注册API路由
app.include_router(api_router, prefix="/api")

# 包含管理后台路由
app.include_router(admin_router, prefix="/admin", tags=["管理后台"])

# 根路径
@app.get("/")
async def root():
    return {
        "message": "墨水屏桌面屏幕系统服务端",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mqtt_connected": mqtt_manager.connected
    }

# 中间件：记录请求日志
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"请求: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"响应状态码: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9999,
        reload=settings.debug
    )