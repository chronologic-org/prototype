from calendar_clients.google_client import GoogleCalendarClient

class CalendarService():
    """
    A service for creating events in multiple calendar APIs.

    Attributes:
        api_to_client_map (dict): A mapping of calendar API types to their respective client classes.
    """

    def __init__(self):
        self.api_to_client_map = {
            'google': GoogleCalendarClient,
            # TODO
            # 'outlook': OutlookCalendarClient
        }
        
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
            client = self.api_to_client_map[api_type]
            urls.append(client.create_event(event))
            
        return 'Done! See your event here: ' + ', '.join(urls)
            