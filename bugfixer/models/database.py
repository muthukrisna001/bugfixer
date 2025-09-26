"""
Database models and configuration
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from decouple import config

# Database configuration
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./bugfixer.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class BugReportDB(Base):
    """Database model for bug reports"""
    __tablename__ = "bug_reports"
    
    id = Column(String, primary_key=True, index=True)
    error_type = Column(String, nullable=False)
    error_message = Column(Text, nullable=False)
    traceback = Column(Text, nullable=False)
    endpoint = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    line_number = Column(Integer, nullable=False)
    function_name = Column(String)
    class_name = Column(String)
    analysis = Column(Text)
    severity = Column(String, default="medium")
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FixResultDB(Base):
    """Database model for fix results"""
    __tablename__ = "fix_results"
    
    id = Column(String, primary_key=True, index=True)
    bug_id = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    original_code = Column(Text, nullable=False)
    fixed_code = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    status = Column(String, default="pending")
    branch_name = Column(String)
    pr_url = Column(String)
    commit_hash = Column(String)
    test_results = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProjectStatusDB(Base):
    """Database model for project status"""
    __tablename__ = "project_status"
    
    id = Column(String, primary_key=True, index=True)
    project_url = Column(String, nullable=False)
    target_app_url = Column(String, nullable=False)
    total_bugs_found = Column(Integer, default=0)
    bugs_fixed = Column(Integer, default=0)
    bugs_pending = Column(Integer, default=0)
    last_check = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
