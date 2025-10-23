"""Tools for enforcing user's scheduling constitution."""
from datetime import datetime
from typing import Dict, Tuple
import pytz


def check_constitution(
    meeting_time_str: str,
    constitution: Dict[str, any],
    meeting_type: str = "business"
) -> Tuple[bool, str, str]:
    """
    Check if a proposed meeting adheres to user's scheduling rules.
    Implements User Story 2.1 & 2.2 (PRD).
    
    Returns:
        Tuple of (is_allowed, reason, approval_type)
    """
    meeting_time = datetime.fromisoformat(meeting_time_str.replace('Z', '+00:00'))
    day_of_week = meeting_time.strftime('%A').lower()
    
    # Rule 1: Weekend Protection (AC 2.2)
    personal_time_rules = constitution.get('personal_time_rules', [])
    if day_of_week in personal_time_rules:
        if meeting_type == "personal":
            return True, "Personal event scheduled on weekend.", None
        else:
            return False, f"This is a {day_of_week}, which is protected for personal time.", "weekend_override"
    
    # Rule 2: Protected Time Blocks (e.g., Kids School Run)
    protected_blocks = constitution.get('protected_time_blocks', [])
    for block in protected_blocks:
        block_start = datetime.strptime(block['start'], '%H:%M').time()
        block_end = datetime.strptime(block['end'], '%H:%M').time()
        block_days = block.get('days', ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
        
        if day_of_week in block_days:
            meeting_time_only = meeting_time.time()
            if block_start <= meeting_time_only <= block_end:
                block_name = block.get('name', 'protected time')
                return False, f"This time conflicts with {block_name}.", "protected_time_override"
    
    # Rule 3: Working Hours
    working_hours = constitution.get('working_hours', {'start': '09:00', 'end': '17:00'})
    work_start = datetime.strptime(working_hours['start'], '%H:%M').time()
    work_end = datetime.strptime(working_hours['end'], '%H:%M').time()
    
    meeting_time_only = meeting_time.time()
    if not (work_start <= meeting_time_only <= work_end):
        return False, f"Meeting at {meeting_time.strftime('%H:%M')} is outside working hours ({working_hours['start']}-{working_hours['end']}).", "work_hours_override"
    
    return True, "Meeting complies with all scheduling rules.", None


def get_default_constitution() -> Dict:
    """
    Get default constitution for new users.
    Based on MVP Scope Section 3.
    """
    return {
        'working_hours': {
            'start': '09:00',
            'end': '17:00'
        },
        'personal_time_rules': ['saturday', 'sunday'],
        'protected_time_blocks': [
            {
                'name': 'Kids School Run',
                'start': '07:30',
                'end': '08:30',
                'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            }
        ],
        'density_threshold': 0.85
    }


def check_density_threshold(
    density: float,
    constitution: Dict
) -> Tuple[bool, str]:
    """
    Check if schedule density exceeds user's threshold.
    Implements User Story 4.2 (PRD).
    """
    threshold = constitution.get('density_threshold', 0.85)
    
    if density > threshold:
        return True, f"Your schedule is {density*100:.0f}% booked, which exceeds your {threshold*100:.0f}% threshold. I recommend against adding new meetings."
    else:
        return False, f"Your schedule is {density*100:.0f}% booked. You have capacity for new meetings."