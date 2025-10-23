"""Tests for calendar tools."""
import pytest
from datetime import datetime, timedelta
from src.tools.calendar_tools import calculate_busyness


def test_calculate_busyness_empty_schedule():
    """Test busyness calculation with no events."""
    events = []
    work_hours = {'start': '09:00', 'end': '17:00'}
    time_min = '2025-10-27T00:00:00Z'  # Monday
    time_max = '2025-10-31T23:59:59Z'  # Friday
    
    result = calculate_busyness(events, work_hours, time_min, time_max)
    
    assert result['density'] == 0.0
    assert result['is_busy'] == False
    assert result['total_event_hours'] == 0.0
    assert result['total_work_hours'] == 40.0  # 5 days * 8 hours


def test_calculate_busyness_full_schedule():
    """Test busyness calculation with very full schedule."""
    # Create events that fill 90% of work hours
    events = []
    base_date = datetime(2025, 10, 27, 9, 0)  # Monday 9 AM
    
    for day in range(5):  # Mon-Fri
        for hour in range(7):  # 7 hours per day = 87.5% of 8-hour day
            start = base_date + timedelta(days=day, hours=hour)
            end = start + timedelta(hours=1)
            events.append({
                'start': start.isoformat() + 'Z',
                'end': end.isoformat() + 'Z'
            })
    
    work_hours = {'start': '09:00', 'end': '17:00'}
    time_min = '2025-10-27T00:00:00Z'
    time_max = '2025-10-31T23:59:59Z'
    
    result = calculate_busyness(events, work_hours, time_min, time_max)
    
    assert result['density'] >= 0.85
    assert result['is_busy'] == True
    assert result['total_event_hours'] == 35.0