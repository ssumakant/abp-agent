from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class Token(BaseModel):
    """Pydantic model for the access token."""
    access_token: str
    token_type: str

class UserCreateRequest(BaseModel):
    """Schema for creating a new user."""
    email: str
    password: str
    internal_domain: str
    timezone: str = "America/Los_Angeles"

class AgentInvokeRequest(BaseModel):
    """Schema for invoking the agent."""
    query: str
    user_id: Optional[str] = None

class TokenData(BaseModel):
    """Schema for the data encoded in the JWT token."""
    email: str | None = None


# ==================== Settings/Constitution Schemas ====================

class WorkHours(BaseModel):
    """Work hours configuration."""
    start: str  # e.g., "09:00"
    end: str    # e.g., "17:00"
    timezone: str = "America/Los_Angeles"

class ProtectedTimeBlock(BaseModel):
    """Protected time block in the constitution."""
    id: Optional[str] = None
    name: str
    day_of_week: str  # e.g., "weekdays", "monday", etc.
    start_time: str   # e.g., "15:00"
    end_time: str     # e.g., "16:00"
    recurring: bool = True

class SchedulingRules(BaseModel):
    """General scheduling rules."""
    no_weekend_meetings: bool = True
    busyness_threshold: float = 0.85
    lookahead_days: int = 14

class Settings(BaseModel):
    """User settings/constitution."""
    user_id: Optional[str] = None
    work_hours: WorkHours
    protected_time_blocks: List[ProtectedTimeBlock] = []
    scheduling_rules: SchedulingRules

class SettingsUpdateRequest(BaseModel):
    """Request to update settings (partial updates allowed)."""
    work_hours: Optional[WorkHours] = None
    protected_time_blocks: Optional[List[ProtectedTimeBlock]] = None
    scheduling_rules: Optional[SchedulingRules] = None

class SettingsUpdateResponse(BaseModel):
    """Response for settings update."""
    message: str
    updated_at: datetime


# ==================== Google Account Management Schemas ====================

class GoogleAuthUrlResponse(BaseModel):
    """Response containing Google OAuth URL."""
    auth_url: str

class ConnectedAccount(BaseModel):
    """A connected Google Calendar account."""
    account_id: str
    email: str
    is_primary: bool = False
    connected_at: datetime
    status: str  # "active", "expired", "revoked", "error"

class ConnectedAccountsResponse(BaseModel):
    """List of connected accounts."""
    accounts: List[ConnectedAccount]

class AccountDeleteResponse(BaseModel):
    """Response for account deletion."""
    message: str
    account_id: str


# ==================== Thread Management Schemas (Optional) ====================

class Thread(BaseModel):
    """Conversation thread."""
    thread_id: str
    title: str
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

class CreateThreadRequest(BaseModel):
    """Request to create a new thread."""
    title: str

class ThreadsResponse(BaseModel):
    """List of threads."""
    threads: List[Thread]

class ThreadDeleteResponse(BaseModel):
    """Response for thread deletion."""
    message: str
    thread_id: str