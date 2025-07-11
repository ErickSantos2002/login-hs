# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, UserOut, UserUpdate
from app.models.user import User
from app.models.role import Role
from app.utils.db import get_db
from app.core.security import hash_password, verify_password, create_access_token
from sqlalchemy import func

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Busca a role pelo nome, ou usa 'comum' como padrão
    role_name = user_in.role_name or "comum"
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=400, detail=f"Role '{role_name}' not found.")

    new_user = User(
        username=user_in.username.lower(),
        password_hash=hash_password(user_in.password),
        role_id=role.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.username:
        user.username = user_in.username.lower()
    if user_in.password:
        user.password_hash = hash_password(user_in.password)
    if user_in.role_name:
        role = db.query(Role).filter(Role.name == user_in.role_name).first()
        if not role:
            raise HTTPException(status_code=400, detail=f"Role '{user_in.role_name}' not found.")
        user.role_id = role.id

    db.commit()
    db.refresh(user)
    return user