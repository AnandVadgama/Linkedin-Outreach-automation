"""
Database models for LinkedIn Outreach Automation.
Defines SQLAlchemy models for prospects, campaigns, and interactions.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, 
    String, Text, create_engine, inspect
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

from ..core.config import settings


Base = declarative_base()


class ProspectStatus(Enum):
    """Prospect status enumeration."""
    NEW = "new"
    CONTACTED = "contacted"
    CONNECTED = "connected"
    REPLIED = "replied"
    NOT_INTERESTED = "not_interested"
    CONVERTED = "converted"


class ConnectionStatus(Enum):
    """Connection request status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"


class Prospect(Base):
    """LinkedIn prospect model."""
    
    __tablename__ = "prospects"
    
    id = Column(Integer, primary_key=True)
    linkedin_url = Column(String(500), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    headline = Column(String(500))
    location = Column(String(200))
    industry = Column(String(200))
    company = Column(String(200))
    company_size = Column(String(50))
    experience_level = Column(String(50))
    profile_picture_url = Column(String(500))
    
    # Contact Information
    email = Column(String(200))
    phone = Column(String(50))
    
    # Prospect Management
    status = Column(SQLEnum(ProspectStatus), default=ProspectStatus.NEW, nullable=False)
    source = Column(String(100))  # How we found this prospect
    tags = Column(String(500))  # Comma-separated tags
    notes = Column(Text)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_contacted_at = Column(DateTime(timezone=True))
    
    # Relationships
    connection_requests = relationship("ConnectionRequest", back_populates="prospect")
    messages = relationship("Message", back_populates="prospect")
    
    def __repr__(self) -> str:
        return f"<Prospect(name='{self.full_name}', status='{self.status.value}')>"


class ConnectionRequest(Base):
    """LinkedIn connection request tracking."""
    
    __tablename__ = "connection_requests"
    
    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=False)
    
    # Request Details
    message = Column(Text)  # Personal note sent with request
    status = Column(SQLEnum(ConnectionStatus), default=ConnectionStatus.PENDING, nullable=False)
    
    # Tracking
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    response_at = Column(DateTime(timezone=True))
    
    # Relationships
    prospect = relationship("Prospect", back_populates="connection_requests")
    
    def __repr__(self) -> str:
        return f"<ConnectionRequest(prospect='{self.prospect.full_name}', status='{self.status.value}')>"


class Message(Base):
    """LinkedIn message tracking."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"), nullable=False)
    
    # Message Details
    content = Column(Text, nullable=False)
    is_sent_by_us = Column(Boolean, default=True)  # True if we sent it, False if received
    message_type = Column(String(50))  # 'connection', 'follow_up', 'reply', etc.
    
    # Tracking
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    
    # Relationships
    prospect = relationship("Prospect", back_populates="messages")
    
    def __repr__(self) -> str:
        direction = "sent" if self.is_sent_by_us else "received"
        return f"<Message({direction} to/from '{self.prospect.full_name}')>"


class Campaign(Base):
    """Outreach campaign model."""
    
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Campaign Configuration
    target_keywords = Column(String(500))  # Comma-separated keywords
    target_locations = Column(String(500))  # Comma-separated locations
    target_industries = Column(String(500))  # Comma-separated industries
    
    # Templates
    connection_message_template = Column(Text)
    follow_up_message_template = Column(Text)
    
    # Settings
    daily_connection_limit = Column(Integer, default=20)
    daily_message_limit = Column(Integer, default=15)
    is_active = Column(Boolean, default=True)
    
    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<Campaign(name='{self.name}', active={self.is_active})>"


# Database setup and utilities
engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize the database with tables."""
    create_tables()
    print("✅ Database initialized successfully!")


def check_database_exists() -> bool:
    """Check if database tables exist."""
    inspector = inspect(engine)
    return bool(inspector.get_table_names())