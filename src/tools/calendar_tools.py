"""Tools for interacting with Google Calendar API."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pytz
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def get_calendar_events(
    credentials: Credentials,
    calendar_id: str,
    time_min: str,
    time_max: str = None
) -> List[Dict[str, Any]]:
    """
    Fetch calendar events for a specified time range.
    Implements User Story 5.1 (PRD).
    """
    service = build('calendar', 'v3', credentials=credentials)
    
    query_params = {
        'calendarId': calendar_id,
        'timeMin': time_min,
        'singleEvents': True,
        'orderBy': 'startTime',
        'maxResults': 250
    }
    
    if time_max:
        query_params['timeMax'] = time_max
    
    events_result = service.events().list(**query_params).execute()
    events = events_result.get('items', [])
    
    standardized_events = []
    for event in events:
        start = event.get('start', {})
        end = event.get('end', {})
        
        if 'dateTime' not in start:
            continue
        
        attendees = []
        for attendee in event.get('attendees', []):
            attendees.append({
                'email': attendee.get('email', ''),
                'responseStatus': attendee.get('responseStatus', 'needsAction'),
                'organizer': attendee.get('organizer', False)
            })
        
        standardized_events.append({
            'id': event['id'],
            'summary': event.get('summary', 'No Title'),
            'start': start['dateTime'],
            'end': end['dateTime'],
            'attendees': attendees,
            'calendar_id': calendar_id
        })
    
    return standardized_events


def get_free_busy(
    credentials: Credentials,
    calendars: List[str],
    time_min: str,
    time_max: str
) -> Dict[str, Any]:
    """Get free/busy information for multiple calendars."""
    service = build('calendar', 'v3', credentials=credentials)
    
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": cal} for cal in calendars]
    }
    
    result = service.freebusy().query(body=body).execute()
    return result.get('calendars', {})


def create_calendar_event(
    credentials: Credentials,
    calendar_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    attendees: List[str] = None,
    description: str = ""
) -> Dict[str, Any]:
    """Create a new calendar event."""
    service = build('calendar', 'v3', credentials=credentials)
    
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Los_Angeles',
        }
    }
    
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]
    
    created_event = service.events().insert(
        calendarId=calendar_id,
        body=event,
        sendUpdates='all'
    ).execute()
    
    return created_event


def update_calendar_event(
    credentials: Credentials,
    calendar_id: str,
    event_id: str,
    start_time: str,
    end_time: str,
    send_updates: bool = True
) -> Dict[str, Any]:
    """Update an existing calendar event's time."""
    service = build('calendar', 'v3', credentials=credentials)
    
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    
    event['start']['dateTime'] = start_time
    event['end']['dateTime'] = end_time
    
    updated_event = service.events().update(
        calendarId=calendar_id,
        eventId=event_id,
        body=event,
        sendUpdates='all' if send_updates else 'none'
    ).execute()
    
    return updated_event


def calculate_busyness(
    events: List[Dict[str, Any]],
    work_hours: Dict[str, Any],
    time_min: str,
    time_max: str
) -> Dict[str, Any]:
    """Calculate schedule density percentage."""
    work_start = datetime.strptime(work_hours['start'], '%H:%M').time()
    work_end = datetime.strptime(work_hours['end'], '%H:%M').time()
    
    start_date = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
    end_date = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
    
    total_work_hours = 0.0
    current_date = start_date.date()
    
    while current_date <= end_date.date():
        if current_date.weekday() < 5:
            work_duration = datetime.combine(current_date, work_end) - datetime.combine(current_date, work_start)
            total_work_hours += work_duration.total_seconds() / 3600
        current_date += timedelta(days=1)
    
    total_event_hours = 0.0
    for event in events:
        start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
        
        if work_start <= start.time() <= work_end:
            duration = (end - start).total_seconds() / 3600
            total_event_hours += duration
    
    if total_work_hours == 0:
        density = 0.0
    else:
        density = total_event_hours / total_work_hours
    
    return {
        'is_busy': density > 0.85,
        'density': round(density, 2),
        'total_event_hours': round(total_event_hours, 1),
        'total_work_hours': round(total_work_hours, 1)
    }