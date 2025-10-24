from pydantic import BaseModel
from typing import Optional

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