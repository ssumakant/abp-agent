"""Email service."""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """High-level email operations."""
    
    def __init__(self, llm_service, credentials_manager):
        self.llm_service = llm_service
        self.creds_manager = credentials_manager
    
    def draft_reschedule_email(
        self,
        meeting: Dict[str, Any],
        new_time_slot: Dict[str, str],
        user_name: str
    ) -> Dict[str, Any]:
        """Draft a rescheduling email."""
        from src.tools.email_tools import draft_reschedule_email
        
        drafted = draft_reschedule_email(meeting, new_time_slot, user_name)
        return drafted
