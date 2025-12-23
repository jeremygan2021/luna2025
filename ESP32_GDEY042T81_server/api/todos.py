from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from schemas import Todo as TodoSchema, TodoCreate, TodoUpdate
from models import Todo as TodoModel
from database import Device as DeviceModel
from auth import get_api_key

router = APIRouter(
    tags=["todos"]
)

@router.post("/", response_model=TodoSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_api_key)])
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """
    创建新的待办事项
    """
    # 检查设备是否存在
    device = db.query(DeviceModel).filter(DeviceModel.device_id == todo.device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )
    
    # 创建新的待办事项
    db_todo = TodoModel(
        title=todo.title,
        description=todo.description,
        device_id=todo.device_id,
        due_date=todo.due_date
    )
    
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    
    return db_todo

@router.get("/", response_model=List[TodoSchema], dependencies=[Depends(get_api_key)])
async def list_todos(
    skip: int = 0, 
    limit: int = 100, 
    device_id: Optional[str] = None,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    获取待办事项列表
    """
    query = db.query(TodoModel)
    
    if device_id:
        query = query.filter(TodoModel.device_id == device_id)
    
    if is_completed is not None:
        query = query.filter(TodoModel.is_completed == is_completed)
    
    todos = query.order_by(TodoModel.created_at.desc()).offset(skip).limit(limit).all()
    return todos

@router.get("/{todo_id}", response_model=TodoSchema, dependencies=[Depends(get_api_key)])
async def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    获取待办事项详情
    """
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在"
        )
    return todo

@router.put("/{todo_id}", response_model=TodoSchema, dependencies=[Depends(get_api_key)])
async def update_todo(
    todo_id: int, 
    todo_update: TodoUpdate, 
    db: Session = Depends(get_db)
):
    """
    更新待办事项
    """
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在"
        )
    
    # 更新待办事项信息
    update_data = todo_update.model_dump(exclude_unset=True)
    
    # 如果状态从未完成变为完成，设置完成时间
    if "is_completed" in update_data and update_data["is_completed"] and not todo.is_completed:
        update_data["completed_at"] = datetime.utcnow()
    # 如果状态从完成变为未完成，清除完成时间
    elif "is_completed" in update_data and not update_data["is_completed"] and todo.is_completed:
        update_data["completed_at"] = None
    
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    todo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(todo)
    
    return todo

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_api_key)])
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    删除待办事项
    """
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在"
        )
    
    db.delete(todo)
    db.commit()

@router.post("/{todo_id}/complete", response_model=TodoSchema, dependencies=[Depends(get_api_key)])
async def complete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    标记待办事项为完成
    """
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在"
        )
    
    todo.is_completed = True
    todo.completed_at = datetime.utcnow()
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)
    
    return todo

@router.post("/{todo_id}/incomplete", response_model=TodoSchema, dependencies=[Depends(get_api_key)])
async def incomplete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    标记待办事项为未完成
    """
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="待办事项不存在"
        )
    
    todo.is_completed = False
    todo.completed_at = None
    todo.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(todo)
    
    return todo