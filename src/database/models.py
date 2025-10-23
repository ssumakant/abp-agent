"""Database models for user data and configuration."""
from sqlalchemy import Column, String, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """User model storing basic profile and settings."""
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    timezone = Column(String, default="America/Los_Angeles")
    internal_domain = Column(String, nullable=False)  # e.g., "octifai.com"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    calendar_accounts = relationship("CalendarAccount", back_populates="user", cascade="all, delete-orphan")
    scheduling_rules = relationship("SchedulingRule", back_populates="user", cascade="all, delete-orphan")
    oauth_tokens = relationship("OAuthToken", back_populates="user", cascade="all, delete-orphan")


class CalendarAccount(Base):
    """Connected calendar accounts for a user."""
    __tablename__ = "calendar_accounts"
    
    account_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    account_email = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="calendar_accounts")


class SchedulingRule(Base):
    """User's scheduling rules (The Constitution)."""
    __tablename__ = "scheduling_rules"
    
    rule_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    rule_type = Column(String, nullable=False)  # PROTECTED_TIME, DENSITY_THRESHOLD, WORK_HOURS
    rule_definition = Column(JSON, nullable=False)
    
    user = relationship("User", back_populates="scheduling_rules")


class OAuthToken(Base):
    """Encrypted OAuth tokens for calendar access."""
    __tablename__ = "oauth_tokens"
    
    token_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    provider = Column(String, default="google")
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    token_uri = Column(String)
    client_id = Column(String)
    client_secret = Column(String)
    scopes = Column(JSON)
    expiry = Column(DateTime)
    
    user = relationship("User", back_populates="oauth_tokens")