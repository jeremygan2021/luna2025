from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import secrets

from database import get_db
from schemas import Device as DeviceSchema, DeviceCreate, DeviceUpdate, BootstrapResponse
from models import Device as DeviceModel
from database import Content as ContentModel
from mqtt_manager import mqtt_manager
from auth import get_api_key

router = APIRouter(
    tags=["devices"]
)

@router.post("/", response_model=DeviceSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_api_key)])
async def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """
    注册新设备
    """
    # 检查设备ID是否已存在
    db_device = db.query(DeviceModel).filter(DeviceModel.device_id == device.device_id).first()
    if db_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="设备ID已存在"
        )
    
    # 创建新设备
    secret = device.secret if device.secret else secrets.token_urlsafe(32)
    db_device = DeviceModel(
        device_id=device.device_id,
        secret=secret,
        name=device.name,
        scene=device.scene
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    # 订阅设备状态
    mqtt_manager.subscribe_to_device_status(device.device_id)
    
    return db_device

@router.get("/", response_model=List[DeviceSchema], dependencies=[Depends(get_api_key)])
async def list_devices(
    skip: int = 0, 
    limit: int = 100, 
    scene: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    获取设备列表
    """
    query = db.query(DeviceModel)
    
    if scene:
        query = query.filter(DeviceModel.scene == scene)
    
    if is_active is not None:
        query = query.filter(DeviceModel.is_active == is_active)
    
    devices = query.offset(skip).limit(limit).all()
    return devices

@router.get("/{device_id}", response_model=DeviceSchema, dependencies=[Depends(get_api_key)])
async def get_device(device_id: str, db: Session = Depends(get_db)):
    """
    获取设备详情
    """
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    return device

@router.put("/{device_id}", response_model=DeviceSchema, dependencies=[Depends(get_api_key)])
async def update_device(
    device_id: str, 
    device_update: DeviceUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新设备信息
    """
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 更新设备信息
    update_data = device_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
    
    device.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(device)
    
    return device

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_api_key)])
async def delete_device(device_id: str, db: Session = Depends(get_db)):
    """
    删除设备
    """
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 取消订阅设备状态
    mqtt_manager.unsubscribe_from_device_status(device_id)
    
    db.delete(device)
    db.commit()

@router.post("/{device_id}/bootstrap", response_model=BootstrapResponse, dependencies=[Depends(get_api_key)])
async def bootstrap_device(device_id: str, db: Session = Depends(get_db)):
    """
    设备引导 - 获取设备配置和内容
    """
    # 验证设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 获取设备场景的内容
    contents = db.query(ContentModel).filter(ContentModel.scene == device.scene).all()
    
    # 构建响应
    response = BootstrapResponse(
        device_id=device_id,
        scene=device.scene,
        contents=contents
    )
    
    return response

@router.get("/{device_id}/status", dependencies=[Depends(get_api_key)])
async def get_device_status(device_id: str, db: Session = Depends(get_db)):
    """
    获取设备状态
    """
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    return {
        "device_id": device_id,
        "name": device.name,
        "scene": device.scene,
        "is_active": device.is_active,
        "last_online": device.last_online,
        "created_at": device.created_at,
        "updated_at": device.updated_at
    }