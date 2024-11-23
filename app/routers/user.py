from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.user import User
from app.models.task import Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify




router = APIRouter(prefix='/user', tags=['user'])


@router.get("/")
async def all_user(db: Annotated[Session, Depends(get_db)]):
    users_query = db.scalars(select(User))
    return users_query.all()


@router.get("/user_id")
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user_query = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    if user_query is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    return user_query


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    db.execute(insert(User).values(username=create_user.username,
                                   firstname=create_user.firstname,
                                   lastname=create_user.lastname,
                                   age=create_user.age,
                                   slug=slugify(create_user.username)
                                   ))
    db.commit()

    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}


@router.put("/update")
async def update_user(
        user_id: int,
        updated_user: UpdateUser,
        db: Annotated[Session, Depends(get_db)],
):
    user_to_update = (
        db.query(User).filter(User.id == user_id).first()
    )

    if user_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    for key, value in updated_user.dict().items():
        setattr(user_to_update, key, value)

    db.commit()
    db.refresh(user_to_update)

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "User update is successful!",
    }


@router.delete("/delete")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    tasks_to_delete = db.query(Task).filter(Task.user_id == user_id).all()
    for task in tasks_to_delete:
        db.delete(task)

    user_to_delete = db.query(User).filter(User.id == user_id).first()

    if user_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    db.delete(user_to_delete)
    db.commit()

    return {
        "status_code": status.HTTP_204_NO_CONTENT,
        "transaction": "User and associated tasks deleted successfully",
    }


@router.get("/{user_id}/tasks/")
async def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    tasks_query = db.execute(select(Task).where(Task.user_id == user_id))
    return tasks_query.scalars().all()