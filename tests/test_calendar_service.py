import pytest
from services.calendar_service import CalendarService

@pytest.fixture
def calendar_service():
    return CalendarService()

def test_create_event(calendar_service):
    api_types = ['google']
    event = {
        'title': 'Test Event',
        'start_time': '2022-01-01 10:00:00',
        'end_time': '2022-01-01 12:00:00',
        'location': 'Test Location'
    }
    result = calendar_service.create_event(api_types, event)
    assert result == 'Done! See your event here: '

def test_create_event_invalid_api_type(calendar_service):
    api_types = ['invalid']
    event = {
        'title': 'Test Event',
        'start_time': '2022-01-01 10:00:00',
        'end_time': '2022-01-01 12:00:00',
        'location': 'Test Location'
    }
    with pytest.raises(ValueError):
        calendar_service.create_event(api_types, event)

def test_create_event_missing_required_fields(calendar_service):
    api_types = ['google']
    event = {
        'title': 'Test Event',
        'start_time': '2022-01-01 10:00:00'
    }
    with pytest.raises(ValueError):
        calendar_service.create_event(api_types, event)