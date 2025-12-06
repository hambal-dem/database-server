from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

# Model input untuk request body
class UserCreate(BaseModel):
    name: str
    email: str
    password: str


@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        name=data.name,
        email=data.email,
        password=data.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "user_id": new_user.id}


@router.get("/list")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
