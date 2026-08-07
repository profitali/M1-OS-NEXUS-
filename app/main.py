from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
from datetime import timedelta

from fastapi.staticfiles import StaticFiles
from app.db.database import SessionLocal, engine
from app.db import models
from app import crud, schemas
from app.utils.security import authenticate_user, create_access_token
from app.tasks import process_build

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="M1 OS Nexus - Master API (skeleton)")

# Serve artifacts folder as static
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'artifacts')
if not os.path.exists(ARTIFACTS_DIR):
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
app.mount('/artifacts', StaticFiles(directory=ARTIFACTS_DIR), name='artifacts')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user_in)


@app.post("/auth/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")))
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/apps", response_model=list[schemas.AppOut])
def list_apps(db: Session = Depends(get_db)):
    return crud.get_apps(db)


@app.post("/apps", response_model=schemas.AppOut)
def create_app(app_in: schemas.AppCreate, db: Session = Depends(get_db)):
    return crud.create_app(db, app_in)


@app.post("/builds/apk", response_model=schemas.BuildOut)
def request_apk_build(build_in: schemas.BuildCreate, db: Session = Depends(get_db)):
    # In production: check user tier, enqueue background build job, return job id
    build = crud.create_build(db, build_in)
    # Enqueue background build task
    try:
        process_build.delay(build.id)
    except Exception:
        # If Celery not available, we leave the build pending but still return
        pass
    return build


@app.get("/builds/{build_id}", response_model=schemas.BuildOut)
def get_build(build_id: int, db: Session = Depends(get_db)):
    build = crud.get_build(db, build_id)
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    return build
