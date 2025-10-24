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

    async def find_available_slots(
        self,
        user_id: str,
        calendar_ids: List[str],
        duration_minutes: int,
        work_hours: Dict[str, str],
        days_ahead: int = 7
    ) -> List[Dict[str, str]]:
        """Find available time slots for scheduling."""
        from src.tools import calendar_tools, rescheduling_tools

        credentials = await self.creds_manager.get_credentials(user_id)
        time_min = datetime.now().isoformat() + 'Z'
        time_max = (datetime.now() + timedelta(days=days_ahead)).isoformat() + 'Z'

        # Get free/busy data
        free_busy_data = calendar_tools.get_free_busy(
            credentials, calendar_ids, time_min, time_max
        )

        # Find available slots
        slots = rescheduling_tools.find_available_slots(
            free_busy_data, duration_minutes, time_min, time_max, work_hours
        )

        return slots

    async def create_event(
        self,
        user_id: str,
        calendar_id: str,
        summary: str,
        start_time: str,
        end_time: str,
        attendees: List[str] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a new calendar event."""
        from src.tools import calendar_tools

        credentials = await self.creds_manager.get_credentials(user_id)

        return calendar_tools.create_calendar_event(
            credentials, calendar_id, summary, start_time, end_time, attendees, description
        )
