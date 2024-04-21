from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, engine
from models import User, Project, DataEntry, ApprovalStatus
import database
import models

# FastAPI app
app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

models.Base.metadata.create_all(bind=database.engine)

# API endpoints
@app.post("/users/")
def create_user(username: str, password_hash: str, email: str, role: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(username=username, password_hash=password_hash, email=email, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.user_id == user_id).first()

@app.post("/projects/")
def create_project(title: str, description: str, admin_id: int, db: Session = Depends(get_db)):
    db_project = Project(title=title, description=description, admin_id=admin_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.post("/data_entries/")
def create_data_entry(project_id: int, user_id: int, data_type: str, data_content: str, timestamp: str, db: Session = Depends(get_db)):
    db_entry = DataEntry(project_id=project_id, user_id=user_id, data_type=data_type, data_content=data_content, timestamp=timestamp)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.post("/approval_status/")
def approve_entry(entry_id: int, user_id: int, approved: bool, comments: str, db: Session = Depends(get_db)):
    db_approval = ApprovalStatus(entry_id=entry_id, user_id=user_id, approved=approved, comments=comments)
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    return db_approval
