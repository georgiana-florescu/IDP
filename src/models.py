from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    email = Column(String, unique=True, index=True)
    
    projects = relationship("Project", back_populates="admin")

class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.user_id"))
    title = Column(String)
    description = Column(String)
    
    admin = relationship("User", back_populates="projects")
    data_entries = relationship("DataEntry", back_populates="project")

class DataEntry(Base):
    __tablename__ = "data_entries"
    
    entry_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    data_type = Column(String)
    data_content = Column(String)
    timestamp = Column(String)
    
    project = relationship("Project", back_populates="data_entries")
    validator_approvals = relationship("ApprovalStatus", back_populates="entry")

class ApprovalStatus(Base):
    __tablename__ = "approval_status"
    
    approval_id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("data_entries.entry_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    approved = Column(Boolean)
    comments = Column(String, nullable=True)
    
    entry = relationship("DataEntry", back_populates="validator_approvals")

class Validators(Base):
    __tablename__ = "validators"
    
    project_id = Column(Integer, ForeignKey("projects.project_id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

    project = relationship("Project", back_populates="validators")
    user = relationship("User", back_populates="projects")