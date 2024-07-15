from google.oauth2 import credentials as google_credentials
from googleapiclient.discovery import build
from .base import CalendarClient

class GoogleCalendarClient(CalendarClient):
    """
    A client for interacting with Google Calendar API.

    Args:
        credentials (dict): A dictionary containing the credentials required to authenticate with Google Calendar API.

    Attributes:
        credentials (google.auth.credentials.Credentials): The credentials used for authentication.
        service (googleapiclient.discovery.Resource): The Google Calendar service object.
    """

    def __init__(self, credentials=None):
        if credentials:
            self.credentials = google_credentials.Credentials(**credentials)
            self.service = build('calendar', 'v3', credentials=self.credentials)
        else:
            # Handle case when no credentials are provided, e.g., for testing purposes
            self.credentials = None
            self.service = None

    def create_event(self, event, calendar_id='primary'):
        """
        Creates a new event in the specified calendar.

        Args:
            event (dict): A dictionary containing the details of the event.
            calendar_id (str, optional): The ID of the calendar to create the event in. Defaults to 'primary'.

        Returns:
            str: The HTML link to the created event.
        """
        if not self.service:
            return 'dummy_link'  # For testing without actual Google service
        event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
        calendar_email = event['organizer']['email']

        return event['htmlLink'] + f'&authuser={calendar_email}'

    def delete_event(self, event_name, calendar_id='primary'):
        """
        Deletes an event from the specified calendar.

        Args:
            calendar_id (str): The ID of the calendar containing the event.
            event_id (str): The ID of the event to delete.
        """
        if not self.service:
            return 'dummy_link'  # For testing without actual Google service
        
        events_result = self.service.events().list(calendarId=calendar_id, q=event_name).execute()
        events = events_result.get('items', [])
        
        if not events:
            raise ValueError(f"No event found with the name '{event_name}'")
        
        event_id = events[0]['id']  # Assuming the first match is the correct one
        calendar_email = events[0]['organizer']['email']
        self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return f"https://calendar.google.com/calendar?authuser={calendar_email}"

    def update_event(self, event_name, updated_event, calendar_id='primary'):
        """
        Updates an existing event in the specified calendar.

        Args:
            calendar_id (str): The ID of the calendar containing the event.
            event_id (str): The ID of the event to update.
            event (dict): A dictionary containing the updated details of the event.

        Returns:
            str: A message indicating that the event has been updated, along with the HTML link to the updated event.
        """
        if not self.service:
            return 'dummy_link'  # For testing without actual Google service
        
        events_result = self.service.events().list(calendarId=calendar_id, q=event_name).execute()
        events = events_result.get('items', [])
        
        if not events:
            raise ValueError(f"No event found with the name '{event_name}'")
        
        event_id = events[0]['id']  # Assuming the first match is the correct one
        calendar_email = events[0]['organizer']['email']
        event = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=updated_event).execute()
        return event['htmlLink'] + f'&authuser={calendar_email}'

    def get_events(self, max_results=10, calendar_id='primary'):
        """
        Retrieves a list of events from the specified calendar.

        Args:
            calendar_id (str): The ID of the calendar to retrieve events from.
            max_results (int, optional): The maximum number of events to retrieve. Defaults to 10.

        Returns:
            list: A list of dictionaries representing the retrieved events.
        """
        if not self.service:
            return []  # For testing without actual Google service
        events_result = self.service.events().list(calendarId=calendar_id, maxResults=max_results).execute()
        events = events_result.get('items', [])
        return events
