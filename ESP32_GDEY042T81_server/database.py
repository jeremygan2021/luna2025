from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

Base = declarative_base()

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, index=True, nullable=False)
    secret = Column(String(100), nullable=False)
    name = Column(String(100), nullable=True)
    scene = Column(String(100), nullable=True)
    last_online = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联内容版本
    contents = relationship("Content", back_populates="device")

class Content(Base):
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False)
    version = Column(Integer, nullable=False)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)
    layout_config = Column(Text, nullable=True)  # JSON格式的布局配置
    timezone = Column(String(50), default="Asia/Shanghai")
    time_format = Column(String(20), default="%Y-%m-%d %H:%M")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联设备
    device = relationship("Device", back_populates="contents")

class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联设备
    device = relationship("Device")

class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False)
    song_id = Column(Integer, nullable=False)  # 歌曲ID (1, 2, 3...)
    name = Column(String(200), nullable=False)  # 歌曲名称
    tempo = Column(String(10), nullable=False)  # 节拍 (存储为字符串，如 "1.2")
    notes = Column(Text, nullable=False)  # 音符数据 (JSON格式存储)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联设备
    device = relationship("Device")

# 创建数据库连接
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建所有表
def init_db():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()