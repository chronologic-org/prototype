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
    
    def update_event(self, api_types, event_name, updated_event):
        """
        Updates an event in multiple calendar APIs.

        Args:
            api_types (list): A list of calendar API types to update the event in.
            event_name (str): The name of the event to update.
            updated_event (dict): The updated event details.

        Returns:
            str: A message indicating the success of the operation and the URLs of the updated events.
        """
        urls = []
        for api_type in api_types:
            if api_type not in self.clients:
                raise KeyError(f'Client for API type {api_type} not found')
            client = self.clients[api_type]
            urls.append(client.update_event(event_name, updated_event))
            
        return 'Done! See your updated event here: ' + ', '.join(urls)
    
    def delete_event(self, api_types, event_name):
        """
        Deletes an event from multiple calendar APIs.

        Args:
            api_types (list): A list of calendar API types to delete the event from.
            event_name (str): The name of the event to delete.

        Returns:
            str: A message indicating the success of the operation.
        """
        for api_type in api_types:
            if api_type not in self.clients:
                raise KeyError(f'Client for API type {api_type} not found')
            client = self.clients[api_type]
            url = client.delete_event(event_name)
            
        return 'Done! The event has been deleted. See your calendar: ' + url
            