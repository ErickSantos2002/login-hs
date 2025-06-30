# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, UserOut
from app.models.user import User
from app.models.role import Role
from app.utils.db import get_db
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # Busca a role padrão (ajuste 'comum' para o nome desejado)
    default_role = db.query(Role).filter(Role.name == 'comum').first()
    if not default_role:
        raise HTTPException(status_code=500, detail="Default role not found in the database.")

    new_user = User(
        username=user_in.username,
        password_hash=hash_password(user_in.password),
        role_id=default_role.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.name}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.name,
        "username": user.username
    }
