from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 数据库配置
    #database_url: str = "postgresql://luna:123luna@121.43.104.161:6432/luna"
    database_url: str = "postgresql://luna:123luna@6.6.6.86:5432/luna"
    
    
    # MQTT配置
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    
    # 应用配置
    app_name: str = "墨水屏桌面屏幕系统"
    debug: bool = False
    
    # 文件存储配置
    static_dir: str = "static"
    upload_dir: str = "static/uploads"
    processed_dir: str = "static/processed"
    
    # 墨水屏配置
    ink_width: int = 400
    ink_height: int = 300
    
    # 安全配置
    secret_key: str = "123tangledup-ai"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 管理员配置
    admin_username: str = "admin"
    admin_password: str = "123456"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()