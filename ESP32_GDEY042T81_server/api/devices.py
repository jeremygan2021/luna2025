from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import secrets
import json

from database import get_db
from schemas import Device as DeviceSchema, DeviceCreate, DeviceUpdate, BootstrapResponse, Song, SongCreate, SongUpdate
from models import Device as DeviceModel
from database import Content as ContentModel, Song as SongModel
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

@router.post("/{device_id}/songs", response_model=Song, dependencies=[Depends(get_api_key)])
async def create_song(
    device_id: str, 
    song: SongCreate, 
    db: Session = Depends(get_db)
):
    """
    创建歌曲
    """
    # 验证设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 检查歌曲ID是否已存在
    existing_song = db.query(SongModel).filter(
        SongModel.device_id == device_id,
        SongModel.song_id == song.song_id
    ).first()
    if existing_song:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="歌曲ID已存在"
        )
    
    # 创建歌曲
    db_song = SongModel(
        device_id=device_id,
        song_id=song.song_id,
        name=song.name,
        tempo=str(song.tempo),
        notes=json.dumps(song.notes)
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    
    # 返回格式化的响应
    return Song(
        id=db_song.id,
        device_id=db_song.device_id,
        song_id=db_song.song_id,
        name=db_song.name,
        tempo=float(db_song.tempo),
        notes=json.loads(db_song.notes),
        created_at=db_song.created_at,
        updated_at=db_song.updated_at
    )

@router.get("/{device_id}/songs", response_model=List[Song], dependencies=[Depends(get_api_key)])
async def list_songs(
    device_id: str, 
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取设备的歌曲列表
    """
    # 验证设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    songs = db.query(SongModel).filter(
        SongModel.device_id == device_id
    ).offset(skip).limit(limit).all()
    
    # 转换数据格式
    result = []
    for song in songs:
        song_data = {
            "id": song.id,
            "device_id": song.device_id,
            "song_id": song.song_id,
            "name": song.name,
            "tempo": float(song.tempo),
            "notes": json.loads(song.notes),
            "created_at": song.created_at,
            "updated_at": song.updated_at
        }
        result.append(song_data)
    
    return result

@router.get("/{device_id}/songs/latest", response_model=Song, dependencies=[Depends(get_api_key)])
async def get_latest_song(device_id: str, db: Session = Depends(get_db)):
    """
    获取设备最新的歌曲
    """
    # 验证设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 获取最新歌曲（按创建时间排序）
    song = db.query(SongModel).filter(
        SongModel.device_id == device_id
    ).order_by(SongModel.created_at.desc()).first()
    
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该设备没有歌曲"
        )
    
    # 转换数据格式
    return {
        "id": song.id,
        "device_id": song.device_id,
        "song_id": song.song_id,
        "name": song.name,
        "tempo": float(song.tempo),
        "notes": json.loads(song.notes),
        "created_at": song.created_at,
        "updated_at": song.updated_at
    }

@router.get("/{device_id}/songs/{song_id}", response_model=Song, dependencies=[Depends(get_api_key)])
async def get_song(device_id: str, song_id: int, db: Session = Depends(get_db)):
    """
    获取指定歌曲详情
    """
    song = db.query(SongModel).filter(
        SongModel.device_id == device_id,
        SongModel.song_id == song_id
    ).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="歌曲不存在"
        )
    
    # 转换数据格式
    return {
        "id": song.id,
        "device_id": song.device_id,
        "song_id": song.song_id,
        "name": song.name,
        "tempo": float(song.tempo),
        "notes": json.loads(song.notes),
        "created_at": song.created_at,
        "updated_at": song.updated_at
    }

@router.put("/{device_id}/songs/{song_id}", response_model=Song, dependencies=[Depends(get_api_key)])
async def update_song(
    device_id: str,
    song_id: int,
    song_update: SongUpdate,
    db: Session = Depends(get_db)
):
    """
    更新歌曲信息
    """
    song = db.query(SongModel).filter(
        SongModel.device_id == device_id,
        SongModel.song_id == song_id
    ).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="歌曲不存在"
        )
    
    # 更新歌曲信息
    update_data = song_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "tempo":
            setattr(song, field, str(value))
        elif field == "notes":
            setattr(song, field, json.dumps(value))
        else:
            setattr(song, field, value)
    
    song.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(song)
    
    # 转换数据格式返回
    return {
        "id": song.id,
        "device_id": song.device_id,
        "song_id": song.song_id,
        "name": song.name,
        "tempo": float(song.tempo),
        "notes": json.loads(song.notes),
        "created_at": song.created_at,
        "updated_at": song.updated_at
    }

@router.delete("/{device_id}/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_api_key)])
async def delete_song(device_id: str, song_id: int, db: Session = Depends(get_db)):
    """
    删除歌曲
    """
    song = db.query(SongModel).filter(
        SongModel.device_id == device_id,
        SongModel.song_id == song_id
    ).first()
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="歌曲不存在"
        )
    
    db.delete(song)
    db.commit()

@router.post("/{device_id}/songs/batch", response_model=List[Song], dependencies=[Depends(get_api_key)])
async def create_songs_batch(
    device_id: str,
    db: Session = Depends(get_db)
):
    """
    批量创建预定义歌曲
    """
    # 验证设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 预定义歌曲数据
    SONGS_EXT = {
        1: {
            "name": "Super Mario Theme",
            "tempo": 1.2,
            "notes": [('E5', 100), ('E5', 100), ('REST', 100), ('E5', 100),
                     ('REST', 100), ('C5', 100), ('E5', 100), ('REST', 100),
                     ('G5', 100), ('REST', 300), ('G4', 100), ('REST', 300),
                     ('C5', 150), ('REST', 50), ('G4', 150), ('REST', 150),
                     ('E4', 150), ('REST', 100), ('A4', 100), ('B4', 100),
                     ('AS4', 50), ('A4', 100), ('G4', 100), ('E5', 100), ('G5', 100),
                     ('A5', 100), ('F5', 100), ('G5', 100), ('REST', 50),
                     ('E5', 100), ('C5', 100), ('D5', 100), ('B4', 100)]
        },
        2: {
            "name": "Star Wars - Imperial March",
            "tempo": 1.0,
            "notes": [('A3', 500), ('A3', 500), ('A3', 500), ('F3', 350), ('C4', 150),
                     ('A3', 500), ('F3', 350), ('C4', 150), ('A3', 1000),
                     ('E4', 500), ('E4', 500), ('E4', 500), ('F4', 350), ('C4', 150),
                     ('GS3', 500), ('F3', 350), ('C4', 150), ('A3', 1000)]
        }
    }
    
    created_songs = []
    for song_id, song_data in SONGS_EXT.items():
        # 检查歌曲是否已存在
        existing_song = db.query(SongModel).filter(
            SongModel.device_id == device_id,
            SongModel.song_id == song_id
        ).first()
        
        if not existing_song:
            # 创建新歌曲
            db_song = SongModel(
                device_id=device_id,
                song_id=song_id,
                name=song_data["name"],
                tempo=str(song_data["tempo"]),
                notes=json.dumps(song_data["notes"])
            )
            db.add(db_song)
            db.commit()
            db.refresh(db_song)
            
            # 转换数据格式
            song_result = {
                "id": db_song.id,
                "device_id": db_song.device_id,
                "song_id": db_song.song_id,
                "name": db_song.name,
                "tempo": float(db_song.tempo),
                "notes": json.loads(db_song.notes),
                "created_at": db_song.created_at,
                "updated_at": db_song.updated_at
            }
            created_songs.append(song_result)
    
    return created_songs
