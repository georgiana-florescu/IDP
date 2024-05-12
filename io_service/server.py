from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect 
from typing import List
from database import SessionLocal, engine
from models import User, Project, DataEntry, ApprovalStatus
from datetime import datetime
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

# API endpoints
@app.get("/keepalive/")
def keepalive():
    return {"status": "ok"}

# USERS
@app.get("/users/")
def get_user(username: str, password_hash: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username and User.password_hash == password_hash).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    return {"user_id": user.user_id}

@app.post("/users/")
def create_user(username: str, password_hash: str, email: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(username=username, password_hash=password_hash, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.user_id == user_id).first()

# PROJECTS

@app.post("/projects/")
def create_project(title: str, description: str, admin_id: int, status: str, access_level: str, db: Session = Depends(get_db)):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_project = Project(title=title, description=description, admin_id=admin_id, status=status, access_level=access_level, timestamp=timestamp)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/{user_id}")
def get_projects(db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Get all public projects and private projects where user is admin
    return db.query(Project).filter((Project.access_level == "public") | (Project.admin_id == user_id)).all()

@app.get("/projects/{user_id}/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Check if project exists 
    project = db.query(Project).filter(Project.project_id == project_id).first()

    # Check if user is admin or project is public
    if project.admin_id == user_id or project.access_level == "public":
        raise HTTPException(status_code=400, detail="User not authorized to access project")

    return project

@app.get("/projects/{user_id}/{project_id}/entries")
def get_entries(project_id: int, user_id = str, db: Session = Depends(get_db)):
    # Check if project exists
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=400, detail="Project not found")

    # Check if user is admin or project is public
    if project.admin_id != user_id and project.access_level != "public":
        raise HTTPException(status_code=400, detail="User not authorized to access project")

    return db.query(DataEntry).filter(DataEntry.project_id == project_id).all()

# DATA ENTRIES

@app.post("/add_entry/")
def create_data_entry(project_id: int, user_id: int, data_type: str, data_content: str, db: Session = Depends(get_db)):
    # Check if project exists
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=400, detail="Project not found")
    
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Check if user is admin or project is public
    if project.admin_id != user_id and project.access_level != "public":
        raise HTTPException(status_code=400, detail="User not authorized to add entry to project")

    # Check if data type is valid
    valid_data_types = ["text", "image", "video", "audio"]
    if data_type not in valid_data_types:
        raise HTTPException(status_code=400, detail="Invalid data type")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    db_entry = DataEntry(project_id=project_id, user_id=user_id, data_type=data_type, data_content=data_content, timestamp=timestamp)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.post("/approve_entry/")
def approve_entry(entry_id: int, user_id: int, approved: bool, comments: str, db: Session = Depends(get_db)):
    # Check if entry exists
    entry = db.query(DataEntry).filter(DataEntry.entry_id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=400, detail="Entry not found")

    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Check if user is validator for project
    project = db.query(Project).filter(Project.project_id == entry.project_id).first()
    validator = db.query(Validators).filter(Validators.project_id == entry.project_id, Validators.user_id == user_id).first()
    if not validator:
        raise HTTPException(status_code=400, detail="User not authorized to validate entries for project")

    # Check if entry is already approved
    existing_approval = db.query(ApprovalStatus).filter(ApprovalStatus.entry_id == entry_id, ApprovalStatus.user_id == user_id).first()
    if existing_approval:
        raise HTTPException(status_code=400, detail="Entry already approved by user")

    db_approval = ApprovalStatus(entry_id=entry_id, user_id=user_id, approved=approved, comments=comments)
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    return db_approval

@app.post("/add_validator/{project_id}/{user_id}")
def add_validator(project_id: int, user_id: int, db: Session = Depends(get_db)):
    # Check if project exists
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=400, detail="Project not found")
    
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    db_validator = Validators(project_id=project_id, user_id=user_id)
    db.add(db_validator)
    db.commit()
    db.refresh(db_validator)
    return db_validator
