from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import Task, User
from app.schemas import UpdateTask, CreateTask, CreateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix='/task', tags=['task'])


@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    task_query = db.scalars(select(Task))
    return task_query.all()


@router.get("/task_id")
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task_query = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()

    if task_query is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")

    return task_query


@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)], create_task: CreateTask, user_id:int):
    user = db.query(User).filter(User.id == user_id).one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    db.execute(insert(Task).values(title=create_task.title,
                                   content=create_task.content,
                                   priority=create_task.priority,
                                   user_id=user_id,
                                   slug=slugify(create_task.title)
                                   ))
    db.commit()

    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put("/update")
async def update_task(
        task_id: int,
        updated_task: UpdateTask,
        db: Annotated[Session, Depends(get_db)],
):
    task_to_update = (
        db.query(Task).filter(Task.id == task_id).first()
    )

    if task_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")

    for key, value in updated_task.dict().items():
        setattr(task_to_update, key, value)

    db.commit()
    db.refresh(task_to_update)

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Task update is successful!",
    }


@router.delete("/delete")
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task_to_delete = db.query(Task).filter(Task.id == task_id).first()

    if task_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task was not found")

    db.delete(task_to_delete)
    db.commit()

    return {
        "status_code": status.HTTP_204_NO_CONTENT,
        "transaction": "Task deleted successfully",
    }