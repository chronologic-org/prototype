from abc import ABC, abstractmethod

class CalendarClient(ABC):
    @abstractmethod
    def create_event(self, calendar_id, event):
        pass

    @abstractmethod
    def delete_event(self, calendar_id, event_id):
        pass

    @abstractmethod
    def update_event(self, calendar_id, event_id, event):
        pass
    
    @abstractmethod
    def get_events(self, calendar_id, max_results=10):
        pass
