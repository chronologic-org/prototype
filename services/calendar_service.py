from calendar_clients import CalendarClientFactory
from calendar_clients.google_client import GoogleCalendarClient

class CalendarService():
    """
    A service for creating events in multiple calendar APIs.

    Attributes:
        api_to_client_map (dict): A mapping of calendar API types to their respective client classes.
    """

    def __init__(self, credentials_dict):
        self.clients = CalendarClientFactory.get_clients(credentials_dict)
        
    def create_event(self, api_types, event):
        """
        Creates an event in multiple calendar APIs.

        Args:
            api_types (list): A list of calendar API types to create the event in.
            event (dict): The event details.

        Returns:
            str: A message indicating the success of the operation and the URLs of the created events.
        """
        urls = []
        for api_type in api_types:
            if api_type not in self.clients:
                raise KeyError(f'Client for API type {api_type} not found')
            client = self.clients[api_type]
            urls.append(client.create_event(event))
            
        return 'Done! See your event here: ' + ', '.join(urls)
            