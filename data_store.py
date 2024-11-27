from api_handler import NHLHandler
from dk_handler import DraftKingsDataHandler

class DataStore():
    def __init__(self, date: str = None):
        if date:
            self.nhl: NHLHandler = NHLHandler(date=date)
        else:
            self.nhl: NHLHandler = NHLHandler()
            
        self.dk: DraftKingsDataHandler = DraftKingsDataHandler()