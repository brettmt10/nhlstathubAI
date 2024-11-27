from api_handler import NHLHandler
from dk_handler import DraftKingsDataHandler

class NHLDataStore():
    def __init__(self, date: str = None):
        if date:
            self.nhl: NHLHandler = NHLHandler(date=date)
        else:
            self.nhl: NHLHandler = NHLHandler()
            
        self.dk: DraftKingsDataHandler = DraftKingsDataHandler()
        
        self.scheduled_teams = self.nhl.schedule_handler.scheduled_teams()
        self.schedule = self.nhl.schedule_handler.nhl_schedule()

        
    