from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError 
from database import get_db
import models
import schemas

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    username = user_data.username.strip()
    
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

    new_user = models.User(username=username)
    db.add(new_user)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback() 
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
        
    db.refresh(new_user)
    return new_user
