from fastapi import APIRouter, Request, Form, File, UploadFile, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List
import json
import os
import secrets
from datetime import datetime
from config import settings

from database import get_db
from models import Device as DeviceModel, Content as ContentModel, Todo as TodoModel
from database import Song as SongModel
from schemas import DeviceCreate, ContentCreate, TodoCreate, TodoUpdate, SongCreate
from image_processor import image_processor
from mqtt_manager import mqtt_manager

# 创建模板对象
templates = Jinja2Templates(directory="templates")

# 添加自定义过滤器
def from_json_filter(value):
    """将JSON字符串转换为Python对象"""
    try:
        return json.loads(value) if value else []
    except (json.JSONDecodeError, TypeError):
        return []

templates.env.filters['from_json'] = from_json_filter

# 创建管理后台路由
admin_router = APIRouter()

# 登录页面
@admin_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: Optional[str] = None):
    """
    管理员登录页面
    """
    # 如果已经登录，重定向到首页
    if request.session.get("authenticated"):
        return RedirectResponse(url=next or "/admin/", status_code=303)
    
    return templates.TemplateResponse("admin/login.html", {
        "request": request,
        "next": next
    })

# 登录处理
@admin_router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request, 
    username: str = Form(...), 
    password: str = Form(...),
    remember: Optional[bool] = Form(False),
    next: Optional[str] = None
):
    """
    处理管理员登录
    """
    # 验证用户名和密码
    # 这里使用配置文件中的设置，实际项目中应该使用数据库存储用户信息
    if username == settings.admin_username and password == settings.admin_password:
        # 设置会话
        request.session["authenticated"] = True
        request.session["username"] = username
        
        # 设置会话过期时间
        if remember:
            request.session["expire_at_browser_close"] = False
        else:
            request.session["expire_at_browser_close"] = True
        
        # 重定向到原始请求的页面或首页
        return RedirectResponse(url=next or "/admin/", status_code=303)
    else:
        # 登录失败，返回错误信息
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "next": next,
            "error": "用户名或密码错误"
        })

# 登出
@admin_router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """
    管理员登出
    """
    # 清除会话
    request.session.clear()
    
    # 重定向到登录页面
    return RedirectResponse(url="/admin/login", status_code=303)

# 管理后台路由
@admin_router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    管理后台首页
    """
    # 获取设备数量
    device_count = db.query(DeviceModel).count()
    active_device_count = db.query(DeviceModel).filter(DeviceModel.is_active == True).count()
    
    # 获取内容数量
    content_count = db.query(ContentModel).count()
    
    # 获取待办事项数量
    todo_count = db.query(TodoModel).count()
    completed_todo_count = db.query(TodoModel).filter(TodoModel.is_completed == True).count()
    pending_todo_count = todo_count - completed_todo_count
    
    # 获取歌曲数量
    song_count = db.query(SongModel).count()
    
    # 获取最近上线的设备
    recent_devices = db.query(DeviceModel).order_by(DeviceModel.last_online.desc()).limit(5).all()
    
    # 获取最近创建的待办事项
    recent_todos_query = db.query(TodoModel, DeviceModel).join(
        DeviceModel, TodoModel.device_id == DeviceModel.device_id
    ).order_by(TodoModel.created_at.desc()).limit(5).all()
    
    # 转换为包含todo和device的对象列表
    recent_todos = [{"todo": todo, "device": device} for todo, device in recent_todos_query]
    
    # 获取最近创建的歌曲
    recent_songs_query = db.query(SongModel, DeviceModel).join(
        DeviceModel, SongModel.device_id == DeviceModel.device_id
    ).order_by(SongModel.created_at.desc()).limit(5).all()
    
    # 转换为包含song和device的对象列表
    recent_songs = [{"song": song, "device": device} for song, device in recent_songs_query]
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "device_count": device_count,
        "active_device_count": active_device_count,
        "content_count": content_count,
        "todo_count": todo_count,
        "completed_todo_count": completed_todo_count,
        "pending_todo_count": pending_todo_count,
        "song_count": song_count,
        "recent_devices": recent_devices,
        "recent_todos": recent_todos,
        "recent_songs": recent_songs
    })

@admin_router.get("/devices", response_class=HTMLResponse)
async def devices_list(request: Request, db: Session = Depends(get_db)):
    """
    设备列表页面
    """
    devices = db.query(DeviceModel).order_by(DeviceModel.created_at.desc()).all()
    return templates.TemplateResponse("admin/devices.html", {
        "request": request,
        "devices": devices
    })

@admin_router.get("/devices/{device_id}", response_class=HTMLResponse)
async def device_detail(request: Request, device_id: str, db: Session = Depends(get_db)):
    """
    设备详情页面
    """
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 获取设备的内容
    contents = db.query(ContentModel).filter(ContentModel.device_id == device_id).order_by(ContentModel.version.desc()).all()
    
    return templates.TemplateResponse("admin/device_detail.html", {
        "request": request,
        "device": device,
        "contents": contents
    })

@admin_router.get("/devices/add", response_class=HTMLResponse)
@admin_router.post("/devices/add", response_class=HTMLResponse)
async def add_device(request: Request, db: Session = Depends(get_db)):
    """
    添加设备页面和处理
    """
    if request.method == "GET":
        return templates.TemplateResponse("admin/add_device.html", {"request": request})
    
    # 处理POST请求
    form = await request.form()
    device_id = form.get("device_id")
    name = form.get("name")
    scene = form.get("scene")
    
    # 检查设备ID是否已存在
    existing_device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if existing_device:
        return templates.TemplateResponse("admin/add_device.html", {
            "request": request,
            "error": "设备ID已存在"
        })
    
    # 创建新设备
    secret = secrets.token_urlsafe(32)
    new_device = DeviceModel(
        device_id=device_id,
        secret=secret,
        name=name,
        scene=scene
    )
    
    db.add(new_device)
    db.commit()
    
    # 订阅设备状态
    mqtt_manager.subscribe_to_device_status(device_id)
    
    return RedirectResponse(url="/admin/devices", status_code=303)

@admin_router.get("/contents", response_class=HTMLResponse)
async def contents_list(request: Request, device_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    内容列表页面
    """
    if device_id:
        # 获取特定设备的内容
        device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="设备不存在")
        
        contents = db.query(ContentModel).filter(ContentModel.device_id == device_id).order_by(ContentModel.version.desc()).all()
        return templates.TemplateResponse("admin/contents.html", {
            "request": request,
            "contents": contents,
            "device": device,
            "filtered": True
        })
    else:
        # 获取所有内容
        contents = db.query(ContentModel).order_by(ContentModel.created_at.desc()).all()
        devices = db.query(DeviceModel).all()
        
        # 为每个内容添加设备信息
        content_list = []
        for content in contents:
            device = db.query(DeviceModel).filter(DeviceModel.device_id == content.device_id).first()
            content_list.append({
                "content": content,
                "device": device
            })
        
        return templates.TemplateResponse("admin/contents.html", {
            "request": request,
            "content_list": content_list,
            "devices": devices,
            "filtered": False
        })

@admin_router.get("/contents/{device_id}/{version}", response_class=HTMLResponse)
async def content_detail(request: Request, device_id: str, version: int, db: Session = Depends(get_db)):
    """
    内容详情页面
    """
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    content = db.query(ContentModel).filter(
        ContentModel.device_id == device_id,
        ContentModel.version == version
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    
    # 解析布局配置
    layout_config = None
    if content.layout_config:
        try:
            layout_config = json.loads(content.layout_config)
        except json.JSONDecodeError:
            layout_config = None
    
    return templates.TemplateResponse("admin/content_detail.html", {
        "request": request,
        "device": device,
        "content": content,
        "layout_config": layout_config
    })

@admin_router.get("/contents/add", response_class=HTMLResponse)
@admin_router.post("/contents/add", response_class=HTMLResponse)
async def add_content(request: Request, device_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    添加内容页面和处理
    """
    if request.method == "GET":
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/add_content.html", {
            "request": request,
            "devices": devices,
            "selected_device": device_id
        })
    
    # 处理POST请求
    form = await request.form()
    device_id = form.get("device_id")
    title = form.get("title")
    description = form.get("description")
    timezone = form.get("timezone", "Asia/Shanghai")
    time_format = form.get("time_format", "%Y-%m-%d %H:%M")
    
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/add_content.html", {
            "request": request,
            "devices": devices,
            "error": "设备不存在"
        })
    
    # 获取当前最大版本号
    from sqlalchemy import func
    max_version = db.query(func.max(ContentModel.version)).filter(
        ContentModel.device_id == device_id
    ).scalar() or 0
    
    # 创建新内容
    new_content = ContentModel(
        device_id=device_id,
        version=max_version + 1,
        title=title,
        description=description,
        timezone=timezone,
        time_format=time_format,
        is_active=True
    )
    
    db.add(new_content)
    db.commit()
    
    # 发送MQTT更新通知
    mqtt_manager.send_update_command(device_id, new_content.version)
    
    return RedirectResponse(url=f"/admin/devices/{device_id}", status_code=303)

@admin_router.get("/upload", response_class=HTMLResponse)
@admin_router.post("/upload", response_class=HTMLResponse)
async def upload_image(request: Request, db: Session = Depends(get_db)):
    """
    图片上传页面和处理
    """
    if request.method == "GET":
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/upload_image.html", {
            "request": request,
            "devices": devices
        })
    
    # 处理POST请求
    form = await request.form()
    device_id = form.get("device_id")
    version = form.get("version")
    file: UploadFile = form.get("image")
    
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/upload_image.html", {
            "request": request,
            "devices": devices,
            "error": "设备不存在"
        })
    
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/upload_image.html", {
            "request": request,
            "devices": devices,
            "error": "文件必须是图片格式"
        })
    
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
                ContentModel.version == int(version)
            ).first()
            
            if not content:
                devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
                return templates.TemplateResponse("admin/upload_image.html", {
                    "request": request,
                    "devices": devices,
                    "error": "指定版本的内容不存在"
                })
            
            content.image_path = processed_path
            db.commit()
            
            # 发送MQTT更新通知
            mqtt_manager.send_update_command(device_id, int(version))
        else:
            # 创建新内容版本
            from sqlalchemy import func
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
            
            # 发送MQTT更新通知
            mqtt_manager.send_update_command(device_id, content.version)
        
        return RedirectResponse(url=f"/admin/devices/{device_id}", status_code=303)
        
    except Exception as e:
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/upload_image.html", {
            "request": request,
            "devices": devices,
            "error": f"图片处理失败: {str(e)}"
        })

# 待办事项管理路由
@admin_router.get("/todos", response_class=HTMLResponse)
async def todos_list(request: Request, device_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    待办事项列表页面
    """
    if device_id:
        # 获取特定设备的待办事项
        device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="设备不存在")
        
        todos = db.query(TodoModel).filter(TodoModel.device_id == device_id).order_by(TodoModel.created_at.desc()).all()
        return templates.TemplateResponse("admin/todos.html", {
            "request": request,
            "todos": todos,
            "device": device,
            "filtered": True
        })
    else:
        # 获取所有待办事项
        todos = db.query(TodoModel).order_by(TodoModel.created_at.desc()).all()
        devices = db.query(DeviceModel).all()
        
        # 为每个待办事项添加设备信息
        todo_list = []
        for todo in todos:
            device = db.query(DeviceModel).filter(DeviceModel.device_id == todo.device_id).first()
            todo_list.append({
                "todo": todo,
                "device": device
            })
        
        return templates.TemplateResponse("admin/todos.html", {
            "request": request,
            "todo_list": todo_list,
            "devices": devices,
            "filtered": False
        })

@admin_router.get("/todos/add", response_class=HTMLResponse)
@admin_router.post("/todos/add", response_class=HTMLResponse)
async def add_todo(request: Request, device_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    添加待办事项页面和处理
    """
    if request.method == "GET":
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/todo_add.html", {
            "request": request,
            "devices": devices,
            "selected_device": device_id
        })
    
    # 处理POST请求
    form = await request.form()
    device_id = form.get("device_id")
    title = form.get("title")
    description = form.get("description")
    due_date_str = form.get("due_date")
    
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/todo_add.html", {
            "request": request,
            "devices": devices,
            "error": "设备不存在"
        })
    
    # 处理截止日期
    due_date = None
    if due_date_str:
        try:
            from datetime import datetime
            due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
            return templates.TemplateResponse("admin/todo_add.html", {
                "request": request,
                "devices": devices,
                "error": "截止日期格式不正确"
            })
    
    # 创建新的待办事项
    new_todo = TodoModel(
        title=title,
        description=description,
        device_id=device_id,
        due_date=due_date
    )
    
    db.add(new_todo)
    db.commit()
    
    # 发送MQTT通知给设备
    mqtt_manager.send_todo_command(device_id, "create", {
        "id": new_todo.id,
        "title": title,
        "description": description,
        "due_date": due_date.isoformat() if due_date else None
    })
    
    return RedirectResponse(url="/admin/todos", status_code=303)

@admin_router.get("/todos/{todo_id}", response_class=HTMLResponse)
async def todo_detail(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """
    待办事项详情页面
    """
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    
    # 获取设备信息
    device = db.query(DeviceModel).filter(DeviceModel.device_id == todo.device_id).first()
    
    return templates.TemplateResponse("admin/todo_detail.html", {
        "request": request,
        "todo": todo,
        "device": device
    })

@admin_router.post("/todos/{todo_id}/toggle", response_class=HTMLResponse)
async def toggle_todo_status(todo_id: int, db: Session = Depends(get_db)):
    """
    切换待办事项完成状态
    """
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    
    # 切换状态
    todo.is_completed = not todo.is_completed
    if todo.is_completed:
        todo.completed_at = datetime.utcnow()
    else:
        todo.completed_at = None
    
    todo.updated_at = datetime.utcnow()
    db.commit()
    
    # 发送MQTT通知给设备
    mqtt_manager.send_todo_command(todo.device_id, "update", {
        "id": todo.id,
        "is_completed": todo.is_completed,
        "completed_at": todo.completed_at.isoformat() if todo.completed_at else None
    })
    
    return RedirectResponse(url=f"/admin/todos/{todo_id}", status_code=303)

@admin_router.get("/todos/{todo_id}/edit", response_class=HTMLResponse)
async def edit_todo_page(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    
    devices = db.query(DeviceModel).all()
    
    return templates.TemplateResponse("admin/todo_edit.html", {
        "request": request,
        "todo": todo,
        "devices": devices
    })

@admin_router.post("/todos/{todo_id}/edit")
async def edit_todo(
    request: Request,
    todo_id: int,
    title: str = Form(...),
    description: str = Form(""),
    device_id: str = Form(...),
    due_date: Optional[str] = Form(None),
    is_completed: bool = Form(False),
    db: Session = Depends(get_db)
):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 更新待办事项
    todo.title = title
    todo.description = description if description else None
    todo.device_id = device_id
    todo.due_date = datetime.fromisoformat(due_date) if due_date else None
    
    # 检查完成状态变化
    was_completed = todo.is_completed
    todo.is_completed = is_completed
    
    # 如果从未完成变为已完成，设置完成时间
    if not was_completed and is_completed:
        todo.completed_at = datetime.utcnow()
    # 如果从已完成变为未完成，清除完成时间
    elif was_completed and not is_completed:
        todo.completed_at = None
    
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    
    # 发送MQTT通知到设备
    if hasattr(request.app.state, 'mqtt_manager') and request.app.state.mqtt_manager:
        try:
            await request.app.state.mqtt_manager.send_todo_command(
                device_id=device_id,
                action="update",
                todo_data={
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "due_date": todo.due_date.isoformat() if todo.due_date else None,
                    "is_completed": todo.is_completed
                }
            )
        except Exception as e:
            print(f"发送待办事项更新MQTT消息失败: {e}")
    
    return RedirectResponse(url=f"/admin/todos/{todo_id}", status_code=303)

@admin_router.post("/todos/{todo_id}/delete")
async def delete_todo(
    request: Request,
    todo_id: int,
    db: Session = Depends(get_db)
):
    """
    删除待办事项
    """
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    
    device_id = todo.device_id
    
    # 发送MQTT通知到设备
    if hasattr(request.app.state, 'mqtt_manager') and request.app.state.mqtt_manager:
        try:
            await request.app.state.mqtt_manager.send_todo_command(
                device_id=device_id,
                action="delete",
                todo_data={
                    "id": todo.id
                }
            )
        except Exception as e:
            print(f"发送待办事项删除MQTT消息失败: {e}")
    
    db.delete(todo)
    db.commit()
    
    return RedirectResponse(url=f"/admin/todos?device_id={device_id}", status_code=303)

# 歌曲管理路由
@admin_router.get("/songs", response_class=HTMLResponse)
async def songs_list(request: Request, device_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    歌曲列表页面
    """
    if device_id:
        # 获取特定设备的歌曲
        device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="设备不存在")
        
        songs = db.query(SongModel).filter(SongModel.device_id == device_id).order_by(SongModel.created_at.desc()).all()
        return templates.TemplateResponse("admin/songs.html", {
            "request": request,
            "songs": songs,
            "device": device,
            "filtered": True
        })
    else:
        # 获取所有歌曲
        songs = db.query(SongModel).order_by(SongModel.created_at.desc()).all()
        devices = db.query(DeviceModel).all()
        
        # 为每个歌曲添加设备信息
        song_list = []
        for song in songs:
            device = db.query(DeviceModel).filter(DeviceModel.device_id == song.device_id).first()
            song_list.append({
                "song": song,
                "device": device
            })
        
        return templates.TemplateResponse("admin/songs.html", {
            "request": request,
            "song_list": song_list,
            "devices": devices,
            "filtered": False
        })

@admin_router.get("/songs/add", response_class=HTMLResponse)
@admin_router.post("/songs/add", response_class=HTMLResponse)
async def add_song(request: Request, device_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    添加歌曲页面和处理
    """
    if request.method == "GET":
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/song_add.html", {
            "request": request,
            "devices": devices,
            "selected_device": device_id
        })
    
    # 处理POST请求
    form = await request.form()
    device_id = form.get("device_id")
    song_id = form.get("song_id")
    name = form.get("name")
    tempo = form.get("tempo")
    notes_json = form.get("notes")
    
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/song_add.html", {
            "request": request,
            "devices": devices,
            "error": "设备不存在"
        })
    
    # 检查歌曲ID是否已存在
    existing_song = db.query(SongModel).filter(
        SongModel.device_id == device_id,
        SongModel.song_id == int(song_id)
    ).first()
    if existing_song:
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/song_add.html", {
            "request": request,
            "devices": devices,
            "error": "歌曲ID已存在"
        })
    
    try:
        # 解析音符数据
        notes = json.loads(notes_json)
        
        # 创建新歌曲
        new_song = SongModel(
            device_id=device_id,
            song_id=int(song_id),
            name=name,
            tempo=str(tempo),
            notes=notes_json
        )
        
        db.add(new_song)
        db.commit()
        
        return RedirectResponse(url="/admin/songs", status_code=303)
        
    except json.JSONDecodeError:
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/song_add.html", {
            "request": request,
            "devices": devices,
            "error": "音符数据格式不正确，请输入有效的JSON格式"
        })
    except ValueError:
        devices = db.query(DeviceModel).filter(DeviceModel.is_active == True).all()
        return templates.TemplateResponse("admin/song_add.html", {
            "request": request,
            "devices": devices,
            "error": "歌曲ID或节拍必须是数字"
        })

@admin_router.get("/songs/{song_id}", response_class=HTMLResponse)
async def song_detail(request: Request, song_id: int, db: Session = Depends(get_db)):
    """
    歌曲详情页面
    """
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    
    # 获取设备信息
    device = db.query(DeviceModel).filter(DeviceModel.device_id == song.device_id).first()
    
    # 解析音符数据
    notes = []
    try:
        notes = json.loads(song.notes)
    except json.JSONDecodeError:
        notes = []
    
    return templates.TemplateResponse("admin/song_detail.html", {
        "request": request,
        "song": song,
        "device": device,
        "notes": notes
    })

@admin_router.get("/songs/{song_id}/edit", response_class=HTMLResponse)
async def edit_song_page(request: Request, song_id: int, db: Session = Depends(get_db)):
    """
    编辑歌曲页面
    """
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    
    devices = db.query(DeviceModel).all()
    
    return templates.TemplateResponse("admin/song_edit.html", {
        "request": request,
        "song": song,
        "devices": devices
    })

@admin_router.post("/songs/{song_id}/edit")
async def edit_song(
    request: Request,
    song_id: int,
    device_id: str = Form(...),
    song_number: int = Form(...),
    name: str = Form(...),
    tempo: float = Form(...),
    notes: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    处理歌曲编辑
    """
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    try:
        # 验证JSON格式
        json.loads(notes)
        
        # 检查歌曲ID冲突（如果改变了歌曲ID）
        if song.song_id != song_number:
            existing_song = db.query(SongModel).filter(
                SongModel.device_id == device_id,
                SongModel.song_id == song_number,
                SongModel.id != song_id
            ).first()
            if existing_song:
                devices = db.query(DeviceModel).all()
                return templates.TemplateResponse("admin/song_edit.html", {
                    "request": request,
                    "song": song,
                    "devices": devices,
                    "error": "歌曲ID已存在"
                })
        
        # 更新歌曲
        song.device_id = device_id
        song.song_id = song_number
        song.name = name
        song.tempo = str(tempo)
        song.notes = notes
        song.updated_at = datetime.utcnow()
        
        db.commit()
        
        return RedirectResponse(url=f"/admin/songs/{song_id}", status_code=303)
        
    except json.JSONDecodeError:
        devices = db.query(DeviceModel).all()
        return templates.TemplateResponse("admin/song_edit.html", {
            "request": request,
            "song": song,
            "devices": devices,
            "error": "音符数据格式不正确，请输入有效的JSON格式"
        })

@admin_router.post("/songs/{song_id}/delete")
async def delete_song(
    request: Request,
    song_id: int,
    db: Session = Depends(get_db)
):
    """
    删除歌曲
    """
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    
    device_id = song.device_id
    
    db.delete(song)
    db.commit()
    
    return RedirectResponse(url=f"/admin/songs?device_id={device_id}", status_code=303)

@admin_router.post("/songs/batch", response_class=HTMLResponse)
async def create_batch_songs(request: Request, db: Session = Depends(get_db)):
    """
    批量创建预定义歌曲
    """
    form = await request.form()
    device_id = form.get("device_id")
    
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 预定义歌曲数据
    SONGS_EXT = {
        1: {
            "name": "Super Mario Theme",
            "tempo": 1.2,
            "notes": [['E5', 100], ['E5', 100], ['REST', 100], ['E5', 100],
                     ['REST', 100], ['C5', 100], ['E5', 100], ['REST', 100],
                     ['G5', 100], ['REST', 300], ['G4', 100], ['REST', 300],
                     ['C5', 150], ['REST', 50], ['G4', 150], ['REST', 150],
                     ['E4', 150], ['REST', 100], ['A4', 100], ['B4', 100],
                     ['AS4', 50], ['A4', 100], ['G4', 100], ['E5', 100], ['G5', 100],
                     ['A5', 100], ['F5', 100], ['G5', 100], ['REST', 50],
                     ['E5', 100], ['C5', 100], ['D5', 100], ['B4', 100]]
        },
        2: {
            "name": "Star Wars - Imperial March",
            "tempo": 1.0,
            "notes": [['A3', 500], ['A3', 500], ['A3', 500], ['F3', 350], ['C4', 150],
                     ['A3', 500], ['F3', 350], ['C4', 150], ['A3', 1000],
                     ['E4', 500], ['E4', 500], ['E4', 500], ['F4', 350], ['C4', 150],
                     ['GS3', 500], ['F3', 350], ['C4', 150], ['A3', 1000]]
        }
    }
    
    created_count = 0
    for song_id, song_data in SONGS_EXT.items():
        # 检查歌曲是否已存在
        existing_song = db.query(SongModel).filter(
            SongModel.device_id == device_id,
            SongModel.song_id == song_id
        ).first()
        
        if not existing_song:
            # 创建新歌曲
            new_song = SongModel(
                device_id=device_id,
                song_id=song_id,
                name=song_data["name"],
                tempo=str(song_data["tempo"]),
                notes=json.dumps(song_data["notes"])
            )
            db.add(new_song)
            created_count += 1
    
    db.commit()
    
    return RedirectResponse(url=f"/admin/songs?device_id={device_id}", status_code=303)