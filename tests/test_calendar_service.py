import pytest
from unittest.mock import patch, MagicMock
from services.calendar_service import CalendarService

@pytest.fixture
def calendar_service():
    credentials_dict = {
        'google': {
            'token': 'dummy_token',
            'refresh_token': 'dummy_refresh_token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'dummy_client_id',
            'client_secret': 'dummy_client_secret'
        }
    }
    return CalendarService(credentials_dict)


def test_create_event(calendar_service):
    api_types = ['google']
    event = {
        'summary': 'Test Event',
        'location': 'Test Location',
        'description': 'A test event',
        'start': {
            'dateTime': '2022-01-01T10:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2022-01-01T12:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
    }
    
    with patch('calendar_clients.google_client.GoogleCalendarClient.create_event', return_value='http://example.com/event'):
        result = calendar_service.create_event(api_types, event)
        assert result == 'Done! See your event here: http://example.com/event'

def test_create_event_invalid_api_type(calendar_service):
    api_types = ['invalid']
    event = {
        'summary': 'Test Event',
        'location': 'Test Location',
        'description': 'A test event',
        'start': {
            'dateTime': '2022-01-01T10:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2022-01-01T12:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
    }
    with pytest.raises(KeyError):
        calendar_service.create_event(api_types, event)

def test_create_event_missing_required_fields(calendar_service):
    api_types = ['google']
    event = {
        'summary': 'Test Event',
        'start': {
            'dateTime': '2022-01-01T10:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        }
        # Missing 'end' field
    }
    
    with patch('calendar_clients.google_client.GoogleCalendarClient.create_event', side_effect=ValueError("Missing required fields")):
        with pytest.raises(ValueError):
            calendar_service.create_event(api_types, event)
