"""Tools for drafting and sending rescheduling emails."""
from typing import Dict, List
from datetime import datetime


def draft_reschedule_email(
    meeting: Dict,
    new_time_slot: Dict[str, str],
    user_name: str = "the organizer"
) -> Dict[str, any]:
    """
    Draft a polite rescheduling email.
    Implements User Story 5.2 (PRD).
    """
    meeting_title = meeting.get('summary', 'Our meeting')
    old_start = datetime.fromisoformat(meeting['start'].replace('Z', '+00:00'))
    new_start = datetime.fromisoformat(new_time_slot['start'].replace('Z', '+00:00'))
    new_end = datetime.fromisoformat(new_time_slot['end'].replace('Z', '+00:00'))
    
    # Extract recipients
    recipients = [
        a['email'] for a in meeting.get('attendees', [])
        if not a.get('organizer', False)
    ]
    
    # Format times
    old_time_str = old_start.strftime('%A, %B %d at %I:%M %p')
    new_time_str = new_start.strftime('%A, %B %d at %I:%M %p')
    new_end_str = new_end.strftime('%I:%M %p')
    
    subject = f"Request to Reschedule: {meeting_title}"
    
    body = f"""Hello,

I hope this message finds you well. I need to reschedule our meeting "{meeting_title}" that was originally planned for {old_time_str}.

Would you be available to meet on {new_time_str} - {new_end_str} instead?

I apologize for any inconvenience this may cause and appreciate your flexibility.

Please let me know if this new time works for you, or if you'd prefer to suggest an alternative.

Best regards,
{user_name}"""
    
    return {
        'subject': subject,
        'body': body,
        'recipients': recipients,
        'meeting_id': meeting['id'],
        'calendar_id': meeting.get('calendar_id'),
        'new_start': new_time_slot['start'],
        'new_end': new_time_slot['end']
    }


def send_email_via_gmail(
    credentials,
    to_addresses: List[str],
    subject: str,
    body: str,
    from_address: str
) -> bool:
    """Send email via Gmail API."""
    from googleapiclient.discovery import build
    from email.mime.text import MIMEText
    import base64
    
    try:
        service = build('gmail', 'v1', credentials=credentials)
        
        message = MIMEText(body)
        message['to'] = ', '.join(to_addresses)
        message['from'] = from_address
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False