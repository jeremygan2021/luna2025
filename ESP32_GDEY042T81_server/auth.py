from fastapi import HTTPException, status, Request, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from config import settings
import logging

logger = logging.getLogger(__name__)

# 创建API Key安全方案
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    API Key依赖项，用于路由级别的鉴权
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key

class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    API Key鉴权中间件
    验证请求中的Secret Key
    """
    
    async def dispatch(self, request: Request, call_next):
        # 跳过不需要鉴权的路径
        if self._should_skip_auth(request.url.path):
            return await call_next(request)
        
        # 检查API Key
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            logger.warning(f"缺少API Key: {request.method} {request.url.path}")
            return Response(
                content='{"detail": "缺少API Key"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json"
            )
        
        # 验证API Key
        if api_key != settings.secret_key:
            logger.warning(f"无效的API Key: {request.method} {request.url.path}")
            return Response(
                content='{"detail": "无效的API Key"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json"
            )
        
        return await call_next(request)
    
    def _should_skip_auth(self, path: str) -> bool:
        """
        判断是否跳过鉴权的路径
        """
        # 公共API路径不需要鉴权
        public_api_paths = [
            "/api/contents/public/",
        ]
        
        # 检查是否是公共API路径
        for public_path in public_api_paths:
            if path.startswith(public_path):
                return True
        
        # 所有其他API路径都需要鉴权，不跳过
        # 如果路径以/api开头，则不跳过（需要鉴权）
        if path.startswith("/api"):
            return False
            
        skip_paths = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/admin",
            "/admin/login",
            "/static",
        ]
        
        # 检查是否以跳过路径开头
        for skip_path in skip_paths:
            if path.startswith(skip_path):
                return True
            
        return False


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """
    Admin页面认证中间件
    验证用户是否已登录
    """
    
    async def dispatch(self, request: Request, call_next):
        # 只对admin路径进行认证
        if not request.url.path.startswith("/admin") or request.url.path == "/admin/login":
            return await call_next(request)
        
        # 检查会话
        if not self._is_authenticated(request):
            # 重定向到登录页面
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/admin/login?next=" + request.url.path, status_code=303)
        
        return await call_next(request)
    
    def _is_authenticated(self, request: Request) -> bool:
        """
        检查用户是否已认证
        """
        # 从session中获取认证信息
        session = request.session
        return session.get("authenticated", False)