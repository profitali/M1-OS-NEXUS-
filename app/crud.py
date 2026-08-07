from sqlalchemy.orm import Session
from app.db import models
from app import schemas
from app.utils.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user_in: schemas.UserCreate):
    hashed = get_password_hash(user_in.password)
    db_user = models.User(email=user_in.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_apps(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.App).offset(skip).limit(limit).all()

def create_app(db: Session, app_in: schemas.AppCreate):
    db_app = models.App(name=app_in.name, description=app_in.description, owner_id=app_in.owner_id)
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

def create_build(db: Session, build_in: schemas.BuildCreate):
    db_build = models.Build(app_id=build_in.app_id, platform=build_in.platform, status="pending")
    db.add(db_build)
    db.commit()
    db.refresh(db_build)
    return db_build

def get_build(db: Session, build_id: int):
    return db.query(models.Build).filter(models.Build.id == build_id).first()
