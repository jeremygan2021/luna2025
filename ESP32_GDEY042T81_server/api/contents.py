from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Security, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import json
import os
import sys
import tempfile
import importlib.util

from database import get_db
from schemas import Content as ContentSchema, ContentCreate, ContentUpdate, ContentResponse
from models import Content as ContentModel, Device as DeviceModel
from mqtt_manager import mqtt_manager
from image_processor import image_processor
from config import settings
from auth import get_api_key

router = APIRouter(
    tags=["contents"]
)

@router.post("/devices/{device_id}/content", response_model=ContentSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_api_key)])
async def create_content(
    device_id: str, 
    content: ContentCreate, 
    db: Session = Depends(get_db)
):
    """
    为设备创建新内容版本
    """
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 获取当前最大版本号
    max_version = db.query(func.max(ContentModel.version)).filter(
        ContentModel.device_id == device_id
    ).scalar() or 0
    
    # 创建新内容
    db_content = ContentModel(
        device_id=device_id,
        version=max_version + 1,
        title=content.title,
        description=content.description,
        image_path=content.image_path,
        layout_config=content.layout_config,
        timezone=content.timezone,
        time_format=content.time_format
    )
    
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    
    # 发送MQTT更新通知
    mqtt_manager.send_update_command(device_id, db_content.version)
    
    return db_content

@router.get("/devices/{device_id}/content", response_model=List[ContentSchema], dependencies=[Depends(get_api_key)])
async def list_content(
    device_id: str,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    获取设备内容列表
    """
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    query = db.query(ContentModel).filter(ContentModel.device_id == device_id)
    
    if is_active is not None:
        query = query.filter(ContentModel.is_active == is_active)
    
    contents = query.order_by(ContentModel.version.desc()).offset(skip).limit(limit).all()
    return contents

@router.get("/devices/{device_id}/content/{version}", response_model=ContentResponse, dependencies=[Depends(get_api_key)])
async def get_content(
    device_id: str,
    version: int,
    db: Session = Depends(get_db)
):
    """
    获取特定版本的内容详情
    """
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    content = db.query(ContentModel).filter(
        ContentModel.device_id == device_id,
        ContentModel.version == version
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="内容不存在"
        )
    
    # 构建图片URL
    image_url = None
    if content.image_path:
        # 确保路径是相对路径
        rel_path = os.path.relpath(content.image_path)
        image_url = f"/static/{rel_path}"
    
    # 解析布局配置
    layout_config = None
    if content.layout_config:
        try:
            layout_config = json.loads(content.layout_config)
        except json.JSONDecodeError:
            layout_config = None
    
    return ContentResponse(
        version=content.version,
        title=content.title,
        description=content.description,
        image_url=image_url,
        layout_config=layout_config,
        timezone=content.timezone,
        time_format=content.time_format,
        created_at=content.created_at
    )

@router.put("/devices/{device_id}/content/{version}", response_model=ContentSchema, dependencies=[Depends(get_api_key)])
async def update_content(
    device_id: str,
    version: int,
    content_update: ContentUpdate,
    db: Session = Depends(get_db)
):
    """
    更新内容
    """
    content = db.query(ContentModel).filter(
        ContentModel.device_id == device_id,
        ContentModel.version == version
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="内容不存在"
        )
    
    # 更新内容信息
    update_data = content_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)
    
    db.commit()
    db.refresh(content)
    
    # 如果内容被激活，发送MQTT更新通知
    if content.is_active:
        mqtt_manager.send_update_command(device_id, content.version)
    
    return content

@router.delete("/devices/{device_id}/content/{version}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_api_key)])
async def delete_content(
    device_id: str,
    version: int,
    db: Session = Depends(get_db)
):
    """
    删除内容
    """
    content = db.query(ContentModel).filter(
        ContentModel.device_id == device_id,
        ContentModel.version == version
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="内容不存在"
        )
    
    db.delete(content)
    db.commit()

@router.get("/devices/{device_id}/content/latest", response_model=ContentResponse)
async def get_latest_content(device_id: str, db: Session = Depends(get_db)):
    """
    获取设备的最新活跃内容
    """
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 获取最新的活跃内容
    content = db.query(ContentModel).filter(
        ContentModel.device_id == device_id,
        ContentModel.is_active == True
    ).order_by(ContentModel.version.desc()).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备没有活跃内容"
        )
    
    # 构建图片URL
    image_url = None
    if content.image_path:
        # 确保路径是相对路径
        rel_path = os.path.relpath(content.image_path)
        image_url = f"/static/{rel_path}"
    
    # 解析布局配置
    layout_config = None
    if content.layout_config:
        try:
            layout_config = json.loads(content.layout_config)
        except json.JSONDecodeError:
            layout_config = None
    
    return ContentResponse(
        version=content.version,
        title=content.title,
        description=content.description,
        image_url=image_url,
        layout_config=layout_config,
        timezone=content.timezone,
        time_format=content.time_format,
        created_at=content.created_at
    )

@router.post("/upload", dependencies=[Depends(get_api_key)])
async def upload_image(
    device_id: str = Query(..., description="设备ID"),
    version: Optional[int] = Query(None, description="内容版本，如果提供则更新指定版本"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    上传图片并处理为墨水屏兼容格式
    """
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件必须是图片格式"
        )
    
    try:
        # 保存上传的文件
        file_data = await file.read()
        upload_path = image_processor.save_upload(file_data, file.filename)
        
        # 处理图片
        processed_path = image_processor.process_image(upload_path)
        
        # 如果提供了版本号，更新指定版本
        if version:
            content = db.query(ContentModel).filter(
                ContentModel.device_id == device_id,
                ContentModel.version == version
            ).first()
            
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="指定版本的内容不存在"
                )
            
            content.image_path = processed_path
            db.commit()
            
            # 发送MQTT更新通知
            mqtt_manager.send_update_command(device_id, version)
        else:
            # 创建新内容版本
            max_version = db.query(func.max(ContentModel.version)).filter(
                ContentModel.device_id == device_id
            ).scalar() or 0
            
            content = ContentModel(
                device_id=device_id,
                version=max_version + 1,
                image_path=processed_path,
                title=f"图片内容 - {file.filename}",
                is_active=True
            )
            
            db.add(content)
            db.commit()
            db.refresh(content)
            
            # 发送MQTT更新通知
            mqtt_manager.send_update_command(device_id, content.version)
        
        # 构建图片URL
        rel_path = os.path.relpath(processed_path)
        image_url = f"/static/{rel_path}"
        
        return {
            "message": "图片上传并处理成功",
            "image_url": image_url,
            "version": content.version if version is None else version
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片处理失败: {str(e)}"
        )

def convert_to_binary_data(image_path: str, width: int = 400, height: int = 300, invert: bool = False, rotate: bool = False, dither: bool = True) -> bytes:
    """
    使用image_converter.py工具将图片转换为二进制数据
    
    Args:
        image_path: 图片路径
        width: 目标宽度
        height: 目标高度
        invert: 是否反转颜色
        rotate: 是否旋转90度
        dither: 是否使用抖动算法
        
    Returns:
        二进制数据
    """
    try:
        # 动态导入image_converter模块 - 使用相对路径
        import os
        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建到tool目录的路径
        tool_dir = os.path.join(current_dir, "..", "tool")
        image_converter_path = os.path.join(tool_dir, "image_converter.py")
        # 导入模块
        spec = importlib.util.spec_from_file_location("image_converter", image_converter_path)
        image_converter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(image_converter)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # 使用image_converter转换图片
            image_converter.convert_image_to_epaper(
                image_path, 
                temp_path, 
                width=width, 
                height=height, 
                invert=invert, 
                rotate=rotate, 
                dither=dither
            )
            
            # 读取生成的Python文件并提取二进制数据
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 解析二进制数据
            start_idx = content.find("bytearray(b'") + len("bytearray(b'")
            end_idx = content.find("')", start_idx)
            
            # 提取并解析十六进制字符串
            hex_str = content[start_idx:end_idx]
            # 替换换行符和空格
            hex_str = hex_str.replace("'\n    b'", "")
            
            # 转换为字节数组
            binary_data = bytearray()
            i = 0
            while i < len(hex_str):
                if hex_str[i] == '\\' and i + 1 < len(hex_str) and hex_str[i+1] == 'x':
                    # 提取十六进制值
                    hex_val = hex_str[i+2:i+4]
                    binary_data.append(int(hex_val, 16))
                    i += 4
                else:
                    i += 1
            
            return bytes(binary_data)
            
        finally:
            # 删除临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        raise Exception(f"图片转换为二进制数据失败: {str(e)}")

@router.get("/devices/{device_id}/content/latest/binary", dependencies=[Depends(get_api_key)])
async def get_latest_content_binary(
    device_id: str,
    invert: bool = Query(False, description="是否反转颜色"),
    rotate: bool = Query(False, description="是否旋转90度"),
    dither: bool = Query(True, description="是否使用抖动算法"),
    db: Session = Depends(get_db)
):
    """
    获取设备最新活跃内容的二进制数据，适用于墨水屏显示
    """
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 获取最新的活跃内容
    content = db.query(ContentModel).filter(
        ContentModel.device_id == device_id,
        ContentModel.is_active == True
    ).order_by(ContentModel.version.desc()).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备没有活跃内容"
        )
    
    if not content.image_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="内容没有关联的图片"
        )
    
    try:
        # 获取完整的图片路径
        # 检查image_path是否已经包含static目录
        if content.image_path.startswith('static/'):
            # 已经包含static目录，直接使用
            image_path = content.image_path
        elif content.image_path.startswith('/'):
            # 以/开头的完整路径，去掉开头的斜杠
            image_path = content.image_path[1:]
        else:
            # 相对路径，添加static_dir前缀
            image_path = os.path.join(settings.static_dir, content.image_path)
        
        # 确保图片文件存在
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图片文件不存在"
            )
        
        # 转换为二进制数据
        binary_data = convert_to_binary_data(
            image_path,
            width=settings.ink_width,
            height=settings.ink_height,
            invert=invert,
            rotate=rotate,
            dither=dither
        )
        
        # 返回二进制数据
        return Response(
            content=binary_data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={device_id}_latest.bin",
                "Content-Length": str(len(binary_data))
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成二进制数据失败: {str(e)}"
        )

@router.get("/public/devices/{device_id}/content/latest/binary")
async def get_latest_content_binary_public(
    device_id: str,
    invert: bool = Query(False, description="是否反转颜色"),
    rotate: bool = Query(False, description="是否旋转90度"),
    dither: bool = Query(True, description="是否使用抖动算法"),
    db: Session = Depends(get_db)
):
    """
    获取设备最新活跃内容的二进制数据，适用于墨水屏显示（无需鉴权）
    """
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 获取最新的活跃内容
    content = db.query(ContentModel).filter(
        ContentModel.device_id == device_id,
        ContentModel.is_active == True
    ).order_by(ContentModel.version.desc()).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备没有活跃内容"
        )
    
    if not content.image_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="内容没有关联的图片"
        )
    
    try:
        # 获取完整的图片路径
        # 检查image_path是否已经包含static目录
        if content.image_path.startswith('static/'):
            # 已经包含static目录，直接使用
            image_path = content.image_path
        elif content.image_path.startswith('/'):
            # 以/开头的完整路径，去掉开头的斜杠
            image_path = content.image_path[1:]
        else:
            # 相对路径，添加static_dir前缀
            image_path = os.path.join(settings.static_dir, content.image_path)
        
        # 确保图片文件存在
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图片文件不存在"
            )
        
        # 转换为二进制数据
        binary_data = convert_to_binary_data(
            image_path,
            width=settings.ink_width,
            height=settings.ink_height,
            invert=invert,
            rotate=rotate,
            dither=dither
        )
        
        # 返回二进制数据
        return Response(
            content=binary_data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={device_id}_latest.bin",
                "Content-Length": str(len(binary_data))
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成二进制数据失败: {str(e)}"
        )

@router.get("/devices/{device_id}/content/{version}/binary", dependencies=[Depends(get_api_key)])
async def get_content_binary(
    device_id: str,
    version: int,
    invert: bool = Query(False, description="是否反转颜色"),
    rotate: bool = Query(False, description="是否旋转90度"),
    dither: bool = Query(True, description="是否使用抖动算法"),
    db: Session = Depends(get_db)
):
    """
    获取内容的二进制数据，适用于墨水屏显示
    """
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 获取内容
    content = db.query(ContentModel).filter(
        ContentModel.device_id == device_id,
        ContentModel.version == version
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="内容不存在"
        )
    
    if not content.image_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="内容没有关联的图片"
        )
    
    try:
        # 获取完整的图片路径
        # 检查image_path是否已经包含static目录
        if content.image_path.startswith('static/'):
            # 已经包含static目录，直接使用
            image_path = content.image_path
        elif content.image_path.startswith('/'):
            # 以/开头的完整路径，去掉开头的斜杠
            image_path = content.image_path[1:]
        else:
            # 相对路径，添加static_dir前缀
            image_path = os.path.join(settings.static_dir, content.image_path)
        
        # 确保图片文件存在
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图片文件不存在"
            )
        
        # 转换为二进制数据
        binary_data = convert_to_binary_data(
            image_path,
            width=settings.ink_width,
            height=settings.ink_height,
            invert=invert,
            rotate=rotate,
            dither=dither
        )
        
        # 返回二进制数据
        return Response(
            content=binary_data,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={device_id}_v{version}.bin",
                "Content-Length": str(len(binary_data))
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成二进制数据失败: {str(e)}"
        )