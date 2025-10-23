"""Configuration management for the ABP Agent."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google API
    google_api_key: str
    google_client_id: str
    google_client_secret: str
    
    # Application
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./abp_agent.db"
    
    # Email
    sendgrid_api_key: str = ""
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google Calendar API
    calendar_scopes: List[str] = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    # Redirect URI for OAuth
    redirect_uri: str = "http://localhost:8000/auth/callback"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
