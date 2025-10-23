"""Calendar service - high-level calendar operations."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CalendarService:
    """High-level calendar operations service."""
    
    def __init__(self, credentials_manager):
        self.creds_manager = credentials_manager
    
    async def get_events_for_user(
        self,
        user_id: str,
        calendar_ids: List[str],
        days_ahead: int = 14
    ) -> List[Dict[str, Any]]:
        """Get events from all user calendars."""
        from src.tools import calendar_tools
        
        credentials = await self.creds_manager.get_credentials(user_id)
        time_min = datetime.now().isoformat() + 'Z'
        time_max = (datetime.now() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        all_events = []
        for calendar_id in calendar_ids:
            try:
                events = calendar_tools.get_calendar_events(
                    credentials, calendar_id, time_min, time_max
                )
                all_events.extend(events)
            except Exception as e:
                logger.error(f"Failed to fetch calendar {calendar_id}: {e}")
        
        return all_events
    
    async def calculate_schedule_density(
        self,
        user_id: str,
        calendar_ids: List[str],
        work_hours: Dict[str, str],
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """Calculate schedule density for a user."""
        from src.tools import calendar_tools
        
        events = await self.get_events_for_user(user_id, calendar_ids, days_ahead)
        
        time_min = datetime.now().isoformat() + 'Z'
        time_max = (datetime.now() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        busyness_data = calendar_tools.calculate_busyness(
            events, work_hours, time_min, time_max
        )
        
        density_pct = busyness_data['density'] * 100
        if busyness_data['is_busy']:
            busyness_data['message'] = (
                f"Your schedule is {density_pct:.0f}% booked, which exceeds "
                f"your 85% threshold."
            )
        else:
            busyness_data['message'] = f"Your schedule is {density_pct:.0f}% booked."
        
        return busyness_data
