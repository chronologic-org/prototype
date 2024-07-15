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
        return event['htmlLink']

    def delete_event(self, calendar_id, event_id):
        """
        Deletes an event from the specified calendar.

        Args:
            calendar_id (str): The ID of the calendar containing the event.
            event_id (str): The ID of the event to delete.
        """
        if self.service:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

    def update_event(self, calendar_id, event_id, event):
        """
        Updates an existing event in the specified calendar.

        Args:
            calendar_id (str): The ID of the calendar containing the event.
            event_id (str): The ID of the event to update.
            event (dict): A dictionary containing the updated details of the event.

        Returns:
            str: A message indicating that the event has been updated, along with the HTML link to the updated event.
        """
        if self.service:
            event = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
            return 'Done! See your updated event here: ' + event['htmlLink']
        return 'dummy_link'  # For testing without actual Google service

    def get_events(self, calendar_id, max_results=10):
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
