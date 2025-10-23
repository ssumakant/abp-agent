"""Tools for intelligent meeting rescheduling."""
from typing import List, Dict, Any, Optional
from datetime import datetime


def is_solo_attendee_event(event: Dict[str, Any], user_email: str) -> bool:
    """
    Check if user is the only accepted attendee.
    Implements IQ-02 clarification (PRD Addendum).
    """
    accepted_attendees = [
        a for a in event.get('attendees', []) 
        if a['responseStatus'] == 'accepted'
    ]
    
    return (
        len(accepted_attendees) == 1 and 
        accepted_attendees[0]['email'].lower() == user_email.lower()
    )


def count_internal_attendees(event: Dict[str, Any], user_email: str, internal_domain: str) -> int:
    """
    Count number of internal attendees (excluding the user).
    """
    count = 0
    for attendee in event.get('attendees', []):
        email = attendee['email'].lower()
        if email != user_email.lower() and email.endswith(f"@{internal_domain}"):
            if attendee['responseStatus'] == 'accepted':
                count += 1
    
    return count


def find_reschedule_candidate(
    events: List[Dict[str, Any]],
    user_email: str,
    internal_domain: str
) -> Optional[Dict[str, Any]]:
    """
    Find the best meeting to reschedule using tiered search logic.
    Implements User Story 5.1 (PRD) with Addendums.
    
    Tier 1: Solo-attendee meetings (AC 5.1.2-5.1.3)
    Tier 2: Meetings with fewest internal attendees (AC 5.1.4)
    Tie-breaking: Shortest duration → Soonest start time
    """
    if not events:
        return None
    
    # Tier 1: Find solo-attendee meetings
    solo_meetings = [e for e in events if is_solo_attendee_event(e, user_email)]
    
    if solo_meetings:
        solo_meetings.sort(key=lambda e: e['start'])
        return {
            'candidate_event': solo_meetings[0],
            'reason': 'solo_attendee',
            'explanation': 'Found a meeting where you are the only accepted attendee.'
        }
    
    # Tier 2: Find meeting with fewest internal attendees
    valid_events = [
        e for e in events 
        if any(
            a['email'].lower() == user_email.lower() and a['responseStatus'] == 'accepted'
            for a in e.get('attendees', [])
        )
    ]
    
    if not valid_events:
        return None
    
    # Score each event by (num_internal_attendees, duration_minutes, start_time)
    scored_events = []
    for event in valid_events:
        internal_count = count_internal_attendees(event, user_email, internal_domain)
        
        start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
        duration_minutes = (end - start).total_seconds() / 60
        
        score = (internal_count, duration_minutes, start)
        scored_events.append((event, score))
    
    # Sort by score tuple (applies tie-breaking automatically)
    scored_events.sort(key=lambda x: x[1])
    
    best_event, (internal_count, _, _) = scored_events[0]
    
    return {
        'candidate_event': best_event,
        'reason': 'fewest_internal',
        'explanation': f'Found a meeting with {internal_count} internal colleague(s).',
        'internal_count': internal_count
    }


def find_available_slots(
    free_busy_data: Dict[str, Any],
    duration_minutes: int,
    time_min: str,
    time_max: str,
    work_hours: Dict[str, str]
) -> List[Dict[str, str]]:
    """Find available time slots across all calendars."""
    from datetime import datetime, timedelta
    
    work_start_time = datetime.strptime(work_hours['start'], '%H:%M').time()
    work_end_time = datetime.strptime(work_hours['end'], '%H:%M').time()
    
    # Collect all busy periods
    all_busy_periods = []
    for calendar_id, calendar_data in free_busy_data.items():
        for busy_period in calendar_data.get('busy', []):
            start = datetime.fromisoformat(busy_period['start'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(busy_period['end'].replace('Z', '+00:00'))
            all_busy_periods.append((start, end))
    
    all_busy_periods.sort(key=lambda x: x[0])
    
    # Find gaps
    available_slots = []
    search_start = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
    search_end = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
    
    current_time = search_start
    
    for busy_start, busy_end in all_busy_periods:
        if current_time < busy_start:
            gap_start = max(current_time, search_start)
            gap_end = min(busy_start, search_end)
            
            if (work_start_time <= gap_start.time() <= work_end_time and
                (gap_end - gap_start).total_seconds() / 60 >= duration_minutes):
                
                available_slots.append({
                    'start': gap_start.isoformat(),
                    'end': (gap_start + timedelta(minutes=duration_minutes)).isoformat()
                })
        
        current_time = max(current_time, busy_end)
    
    # Check after last busy period
    if current_time < search_end:
        gap_start = current_time
        gap_end = search_end
        
        if (work_start_time <= gap_start.time() <= work_end_time and
            (gap_end - gap_start).total_seconds() / 60 >= duration_minutes):
            
            available_slots.append({
                'start': gap_start.isoformat(),
                'end': (gap_start + timedelta(minutes=duration_minutes)).isoformat()
            })
    
    return available_slots[:5]