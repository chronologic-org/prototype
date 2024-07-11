from google.oauth2 import credentials as google_credentials
from googleapiclient.discovery import build
from .base import CalendarClient

class GoogleCalendarClient(CalendarClient):
    def __init__(self, credentials):
        self.credentials = google_credentials.Credentials(**credentials)
        self.service = build('calendar', 'v3', credentials=self.credentials)

    def create_event(self, calendar_id, event):
        event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
        return event

    def delete_event(self, calendar_id, event_id):
        self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

    def update_event(self, calendar_id, event_id, event):
        event = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        return event