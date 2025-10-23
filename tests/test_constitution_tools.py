"""Tests for constitution enforcement - implements PRD test cases."""
import pytest
from src.tools.constitution_tools import check_constitution, get_default_constitution


@pytest.fixture
def standard_constitution():
    """Standard constitution for testing."""
    return get_default_constitution()


def test_allows_meeting_within_working_hours(standard_constitution):
    """
    Test that constitution allows meetings within defined working hours.
    Tests User Story 2.1.
    """
    meeting_time = '2025-10-27T10:00:00Z'  # Monday at 10 AM
    
    is_allowed, reason, approval_type = check_constitution(
        meeting_time,
        standard_constitution
    )
    
    assert is_allowed == True
    assert "complies with all scheduling rules" in reason.lower()
    assert approval_type is None


def test_blocks_weekend_business_meeting(standard_constitution):
    """
    Test that constitution blocks business meetings on weekends.
    Tests AC 2.2 & MVP Rule 1.
    """
    meeting_time = '2025-10-25T10:00:00Z'  # Saturday
    
    is_allowed, reason, approval_type = check_constitution(
        meeting_time,
        standard_constitution,
        meeting_type="business"
    )
    
    assert is_allowed == False
    assert "protected for personal time" in reason.lower()
    assert approval_type == "weekend_override"


def test_allows_weekend_personal_meeting(standard_constitution):
    """
    Test that personal events are allowed on weekends.
    Tests MVP Rule 1 exception.
    """
    meeting_time = '2025-10-25T10:00:00Z'  # Saturday
    
    is_allowed, reason, approval_type = check_constitution(
        meeting_time,
        standard_constitution,
        meeting_type="personal"
    )
    
    assert is_allowed == True
    assert "personal event" in reason.lower()


def test_blocks_meeting_outside_working_hours(standard_constitution):
    """
    Test that constitution blocks meetings outside working hours.
    Tests AC 2.2.
    """
    meeting_time = '2025-10-27T18:00:00Z'  # Monday at 6 PM (after 5 PM end)
    
    is_allowed, reason, approval_type = check_constitution(
        meeting_time,
        standard_constitution
    )
    
    assert is_allowed == False
    assert "outside working hours" in reason.lower()
    assert approval_type == "work_hours_override"


def test_blocks_protected_time_block(standard_constitution):
    """
    Test that protected time blocks (Kids School Run) are enforced.
    Tests MVP Rule 2.
    """
    meeting_time = '2025-10-27T07:45:00Z'  # Monday at 7:45 AM (during 7:30-8:30 block)
    
    is_allowed, reason, approval_type = check_constitution(
        meeting_time,
        standard_constitution
    )
    
    assert is_allowed == False
    assert "kids school run" in reason.lower()
    assert approval_type == "protected_time_override"


def test_allows_meeting_after_protected_block(standard_constitution):
    """Test that meetings after protected blocks are allowed."""
    meeting_time = '2025-10-27T09:00:00Z'  # Monday at 9 AM (after school run)
    
    is_allowed, reason, approval_type = check_constitution(
        meeting_time,
        standard_constitution
    )
    
    assert is_allowed == True


def test_protected_block_only_applies_to_specified_days():
    """Test that protected blocks respect day-of-week constraints."""
    constitution = {
        'working_hours': {'start': '09:00', 'end': '17:00'},
        'personal_time_rules': [],
        'protected_time_blocks': [
            {
                'name': 'Morning Block',
                'start': '08:00',
                'end': '09:00',
                'days': ['monday', 'wednesday', 'friday']
            }
        ]
    }
    
    # Tuesday at 8:30 AM - should be allowed (not a protected day)
    tuesday_meeting = '2025-10-28T08:30:00Z'
    is_allowed, _, _ = check_constitution(tuesday_meeting, constitution)
    assert is_allowed == True
    
    # Monday at 8:30 AM - should be blocked
    monday_meeting = '2025-10-27T08:30:00Z'
    is_allowed, _, _ = check_constitution(monday_meeting, constitution)
    assert is_allowed == False
"