from .google_client import GoogleCalendarClient
# TODO
# from .outlook_client import OutlookCalendarClient

class CalendarClientFactory:
    @staticmethod
    def get_clients(credentials_dict):
        clients = {}
        for api_type, creds in credentials_dict.items():
            if api_type == 'google':
                clients['google'] = GoogleCalendarClient(creds)
            # TODO
            # elif api_type == 'outlook':
            #     clients['outlook'] = OutlookCalendarClient(creds)
            else:
                raise ValueError(f"Unsupported API type: {api_type}")
        return clients
