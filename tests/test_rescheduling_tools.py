"""Tests for rescheduling logic - implements PRD test cases."""
import pytest
from datetime import datetime, timedelta
from src.tools.rescheduling_tools import (
    find_reschedule_candidate,
    is_solo_attendee_event,
    count_internal_attendees
)


@pytest.fixture
def user_context():
    """Standard user context for tests."""
    return {
        "user_email": "user@octifai.com",
        "internal_domain": "octifai.com"
    }


def test_solo_attendee_detection(user_context):
    """
    Test solo attendee detection.
    Implements AC 5.1.2 with IQ-02 clarification.
    """
    # Event where user is solo accepted attendee
    event1 = {
        'id': '1',
        'summary': 'Solo Meeting',
        'start': '2025-10-28T10:00:00Z',
        'end': '2025-10-28T11:00:00Z',
        'attendees': [
            {'email': 'user@octifai.com', 'responseStatus': 'accepted'},
            {'email': 'external@other.com', 'responseStatus': 'declined'}
        ]
    }
    
    assert is_solo_attendee_event(event1, user_context['user_email']) == True
    
    # Event with multiple accepted attendees
    event2 = {
        'id': '2',
        'summary': 'Team Meeting',
        'start': '2025-10-28T14:00:00Z',
        'end': '2025-10-28T15:00:00Z',
        'attendees': [
            {'email': 'user@octifai.com', 'responseStatus': 'accepted'},
            {'email': 'colleague@octifai.com', 'responseStatus': 'accepted'}
        ]
    }
    
    assert is_solo_attendee_event(event2, user_context['user_email']) == False


def test_tier1_selects_solo_meeting_first(user_context):
    """
    Tier 1: Agent should prioritize solo-attendee meetings.
    Tests AC 5.1.2 & 5.1.3.
    """
    events = [
        {
            'id': '1',
            'summary': 'Solo Focus Time',
            'start': '2025-10-29T10:00:00Z',
            'end': '2025-10-29T11:00:00Z',
            'attendees': [
                {'email': 'user@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'external@company.com', 'responseStatus': 'declined'}
            ]
        },
        {
            'id': '2',
            'summary': 'Team Sync',
            'start': '2025-10-28T14:00:00Z',
            'end': '2025-10-28T15:00:00Z',
            'attendees': [
                {'email': 'user@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague1@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague2@octifai.com', 'responseStatus': 'accepted'}
            ]
        }
    ]
    
    result = find_reschedule_candidate(
        events,
        user_context['user_email'],
        user_context['internal_domain']
    )
    
    assert result is not None
    assert result['candidate_event']['id'] == '1'
    assert result['reason'] == 'solo_attendee'


def test_tier2_selects_fewest_internal_attendees(user_context):
    """
    Tier 2: When no solo meetings, select meeting with fewest internal attendees.
    Tests AC 5.1.4.
    """
    events = [
        {
            'id': '1',
            'summary': 'Large Team Meeting',
            'start': '2025-10-28T10:00:00Z',
            'end': '2025-10-28T11:00:00Z',
            'attendees': [
                {'email': 'user@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague1@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague2@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague3@octifai.com', 'responseStatus': 'accepted'}
            ]
        },
        {
            'id': '2',
            'summary': 'Small Sync',
            'start': '2025-10-28T14:00:00Z',
            'end': '2025-10-28T15:00:00Z',
            'attendees': [
                {'email': 'user@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague4@octifai.com', 'responseStatus': 'accepted'}
            ]
        }
    ]
    
    result = find_reschedule_candidate(
        events,
        user_context['user_email'],
        user_context['internal_domain']
    )
    
    assert result is not None
    assert result['candidate_event']['id'] == '2'
    assert result['reason'] == 'fewest_internal'
    assert result['internal_count'] == 1


def test_tie_breaking_by_duration_then_time(user_context):
    """
    Test tie-breaking logic: shortest duration → soonest start time.
    Tests PRD Addendum AC 5.1.4 clarification.
    """
    base_time = datetime(2025, 10, 28, 10, 0)
    
    events = [
        {
            'id': '1',
            'summary': 'Meeting A - 2 people, 60 min, day 3',
            'start': (base_time + timedelta(days=3)).isoformat() + 'Z',
            'end': (base_time + timedelta(days=3, hours=1)).isoformat() + 'Z',
            'attendees': [
                {'email': 'user@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague1@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague2@octifai.com', 'responseStatus': 'accepted'}
            ]
        },
        {
            'id': '2',
            'summary': 'Meeting B - 2 people, 30 min, day 2',
            'start': (base_time + timedelta(days=2)).isoformat() + 'Z',
            'end': (base_time + timedelta(days=2, minutes=30)).isoformat() + 'Z',
            'attendees': [
                {'email': 'user@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague3@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague4@octifai.com', 'responseStatus': 'accepted'}
            ]
        },
        {
            'id': '3',
            'summary': 'Meeting C - 2 people, 30 min, day 1 (WINNER)',
            'start': (base_time + timedelta(days=1)).isoformat() + 'Z',
            'end': (base_time + timedelta(days=1, minutes=30)).isoformat() + 'Z',
            'attendees': [
                {'email': 'user@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague5@octifai.com', 'responseStatus': 'accepted'},
                {'email': 'colleague6@octifai.com', 'responseStatus': 'accepted'}
            ]
        }
    ]
    
    result = find_reschedule_candidate(
        events,
        user_context['user_email'],
        user_context['internal_domain']
    )
    
    assert result is not None
    # Should select meeting C: same attendee count, but shortest duration and soonest
    assert result['candidate_event']['id'] == '3'


def test_internal_vs_external_attendee_distinction(user_context):
    """Test that external attendees are not counted as internal."""
    event = {
        'id': '1',
        'summary': 'Mixed Meeting',
        'start': '2025-10-28T10:00:00Z',
        'end': '2025-10-28T11:00:00Z',
        'attendees': [
            {'email': 'user@octifai.com', 'responseStatus': 'accepted'},
            {'email': 'internal1@octifai.com', 'responseStatus': 'accepted'},
            {'email': 'internal2@octifai.com', 'responseStatus': 'accepted'},
            {'email': 'external@otherdomain.com', 'responseStatus': 'accepted'},
            {'email': 'vendor@vendorco.com', 'responseStatus': 'accepted'}
        ]
    }
    
    internal_count = count_internal_attendees(
        event,
        user_context['user_email'],
        user_context['internal_domain']
    )
    
    # Should count only 2 internal attendees (not the user, not external)
    assert internal_count == 2


def test_no_candidate_found_returns_none(user_context):
    """Test that None is returned when no suitable candidates exist."""
    events = []
    
    result = find_reschedule_candidate(
        events,
        user_context['user_email'],
        user_context['internal_domain']
    )
    
    assert result is None