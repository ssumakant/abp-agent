"""Rescheduling service."""
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class ReschedulingService:
    """High-level rescheduling operations."""
    
    def __init__(self, calendar_service):
        self.calendar_service = calendar_service
    
    async def find_best_meeting_to_move(
        self,
        user_id: str,
        user_email: str,
        internal_domain: str,
        calendar_ids: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Find the best candidate meeting to reschedule."""
        from src.tools.rescheduling_tools import find_reschedule_candidate
        
        events = await self.calendar_service.get_events_for_user(
            user_id, calendar_ids, days_ahead=14
        )
        
        if not events:
            return None
        
        result = find_reschedule_candidate(events, user_email, internal_domain)
        return result
    
    def format_reschedule_proposal(self, result: Dict[str, Any]) -> str:
        """Format a rescheduling proposal message."""
        candidate = result['candidate_event']
        meeting_title = candidate.get('summary', 'Untitled Meeting')
        
        if result['reason'] == 'solo_attendee':
            return (
                f"To free up time, I suggest rescheduling '{meeting_title}' "
                f"where you are the only accepted attendee. Shall I proceed?"
            )
        else:
            return (
                f"No solo-attendee meetings found. {result['explanation']} "
                f"I suggest rescheduling '{meeting_title}'. Shall I proceed?"
            )
