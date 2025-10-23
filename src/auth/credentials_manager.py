"""OAuth 2.0 credentials management for Google Calendar API."""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import json

from src.database.models import OAuthToken, User
from src.config import settings


class CredentialsManager:
    """Manages OAuth 2.0 credentials for users."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_credentials(self, user_id: str) -> Credentials:
        """
        Get valid credentials for a user.
        Refreshes token if expired.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Valid Google OAuth credentials
            
        Raises:
            ValueError: If no credentials found for user
        """
        # Fetch token from database
        result = await self.session.execute(
            select(OAuthToken).where(OAuthToken.user_id == user_id)
        )
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            raise ValueError(f"No credentials found for user {user_id}")
        
        # Construct credentials object
        creds = Credentials(
            token=token_record.access_token,
            refresh_token=token_record.refresh_token,
            token_uri=token_record.token_uri,
            client_id=token_record.client_id,
            client_secret=token_record.client_secret,
            scopes=token_record.scopes
        )
        
        # Check if expired and refresh if needed
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
            # Update database with new token
            token_record.access_token = creds.token
            token_record.expiry = creds.expiry
            await self.session.commit()
        
        return creds
    
    async def save_credentials(self, user_id: str, creds: Credentials):
        """
        Save or update credentials for a user.
        
        Args:
            user_id: The user's ID
            creds: Google OAuth credentials to save
        """
        # Check if token exists
        result = await self.session.execute(
            select(OAuthToken).where(OAuthToken.user_id == user_id)
        )
        token_record = result.scalar_one_or_none()
        
        if token_record:
            # Update existing
            token_record.access_token = creds.token
            token_record.refresh_token = creds.refresh_token
            token_record.expiry = creds.expiry
        else:
            # Create new
            token_record = OAuthToken(
                user_id=user_id,
                provider="google",
                access_token=creds.token,
                refresh_token=creds.refresh_token,
                token_uri=creds.token_uri,
                client_id=creds.client_id,
                client_secret=creds.client_secret,
                scopes=creds.scopes,
                expiry=creds.expiry
            )
            self.session.add(token_record)
        
        await self.session.commit()
    
    def get_authorization_url(self, state: str = None) -> tuple[str, str]:
        """
        Generate OAuth authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Tuple of (authorization_url, state)
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.redirect_uri]
                }
            },
            scopes=settings.calendar_scopes,
            redirect_uri=settings.redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )
        
        return authorization_url, state
    
    async def exchange_code_for_token(self, code: str, user_id: str) -> Credentials:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            user_id: User ID to associate credentials with
            
        Returns:
            Google OAuth credentials
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.redirect_uri]
                }
            },
            scopes=settings.calendar_scopes,
            redirect_uri=settings.redirect_uri
        )
        
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Save to database
        await self.save_credentials(user_id, creds)
        
        return creds


def get_calendar_service(credentials: Credentials):
    """
    Build Google Calendar API service.
    
    Args:
        credentials: Valid OAuth credentials
        
    Returns:
        Google Calendar API service object
    """
    return build('calendar', 'v3', credentials=credentials)