from .google_client import GoogleCalendarClient
# TODO
# from .outlook_client import OutlookCalendarClient

class CalendarClientFactory:
    
    api_to_client_map = {
        'google': GoogleCalendarClient,
        # TODO
        # 'outlook': OutlookCalendarClient
    }
    
    @staticmethod
    def get_clients(credentials_dict):
        clients = {}
        for api_type, creds in credentials_dict.items():
            if api_type in CalendarClientFactory.api_to_client_map:
                clients[api_type] = CalendarClientFactory.api_to_client_map[api_type](creds)
            else:
                raise ValueError(f"Unsupported API type: {api_type}")
        return clients
