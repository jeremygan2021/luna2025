from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# 设备相关模型
class DeviceBase(BaseModel):
    device_id: str = Field(..., description="设备唯一标识")
    name: Optional[str] = Field(None, description="设备名称")
    scene: Optional[str] = Field(None, description="设备使用场景")

class DeviceCreate(DeviceBase):
    secret: str = Field(..., description="设备密钥")

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    scene: Optional[str] = None
    is_active: Optional[bool] = None

class Device(DeviceBase):
    id: int
    last_online: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 内容相关模型
class ContentBase(BaseModel):
    title: Optional[str] = Field(None, description="内容标题")
    description: Optional[str] = Field(None, description="内容描述")
    image_path: Optional[str] = Field(None, description="图片路径")
    layout_config: Optional[str] = Field(None, description="布局配置JSON")
    timezone: str = Field("Asia/Shanghai", description="时区")
    time_format: str = Field("%Y-%m-%d %H:%M", description="时间显示格式")

class ContentCreate(ContentBase):
    device_id: str = Field(..., description="设备ID")

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_path: Optional[str] = None
    layout_config: Optional[str] = None
    timezone: Optional[str] = None
    time_format: Optional[str] = None
    is_active: Optional[bool] = None

class Content(ContentBase):
    id: int
    device_id: str
    version: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# 响应模型
class BootstrapResponse(BaseModel):
    device_id: str
    content_version: Optional[int] = None
    timezone: str
    time_format: str
    last_updated: Optional[datetime] = None

class ContentResponse(BaseModel):
    version: int
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    layout_config: Optional[Dict[str, Any]] = None
    timezone: str
    time_format: str
    created_at: datetime

# MQTT消息模型
class MQTTCommand(BaseModel):
    type: str = Field(..., description="命令类型")
    content_version: Optional[int] = None
    timestamp: Optional[int] = None

class MQTTStatus(BaseModel):
    event: str = Field(..., description="事件类型")
    content_version: Optional[int] = None
    timestamp: int = Field(..., description="时间戳")
    device_id: str = Field(..., description="设备ID")
    message: Optional[str] = None

# 待办事项相关模型
class TodoBase(BaseModel):
    title: str = Field(..., description="待办事项标题")
    description: Optional[str] = Field(None, description="待办事项描述")
    due_date: Optional[datetime] = Field(None, description="截止日期")

class TodoCreate(TodoBase):
    device_id: str = Field(..., description="设备ID")

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None

class Todo(TodoBase):
    id: int
    device_id: str
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 歌曲相关模型
class SongBase(BaseModel):
    song_id: int = Field(..., description="歌曲ID")
    name: str = Field(..., description="歌曲名称")
    tempo: float = Field(..., description="节拍")
    notes: list = Field(..., description="音符数据")

class SongCreate(SongBase):
    pass

class SongUpdate(BaseModel):
    name: Optional[str] = None
    tempo: Optional[float] = None
    notes: Optional[list] = None

class Song(SongBase):
    id: int
    device_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True