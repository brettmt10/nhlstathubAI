from api_handler import NHLHandler
from dk_handler import DraftKingsDataHandler

import pandas as pd
from typing import Optional

import team_info

class DataMerger():
    def __init__(self, date: Optional[str] = None):
        if date:
            self.nhl: NHLHandler = NHLHandler(date=date)
        else:
            self.nhl: NHLHandler = NHLHandler()
        
        self.dk: DraftKingsDataHandler = DraftKingsDataHandler()
        
        try:
            self.scheduled_teams: list[str] = self.nhl.schedule_handler.nhl_scheduled_teams()
        except:
            raise ValueError("No scheduled games today. Merger will not run.")
        
        self.scheduled_teams_player_database: dict[pd.DataFrame] = {}
        
        self.schedule: list[dict] = self.nhl.schedule_handler.nhl_schedule()

        self.available_player_salaries: pd.DataFrame = self.dk.get_available_player_salaries()
        
    def __get_scheduled_teams_player_database(self) -> dict[pd.DataFrame]:
        return self.scheduled_teams_player_database
        
    def build_scheduled_teams_player_database(self) -> dict[pd.DataFrame]:
        db: dict[pd.DataFrame] = {}
        
        for team in self.scheduled_teams:
            print(team)
            team_data = self.nhl.player_data_handler.get_team_player_data_as_df(team_name=team)
            db[team_info.teams.get(team).get('abbreviation')] = team_data # needs to be team abbreviation to relate to salary data
            
        return db
    
    def merge_salaries_set_database(self) -> pd.DataFrame:
        db = self.build_scheduled_teams_player_database()
                                
    def set_scheduled_teams_player_database(self) -> None:
        self.scheduled_teams_player_database: dict[pd.DataFrame] = self.merge_salaries_set_database()
                
    def daily_player_database(self) -> dict[pd.DataFrame]:
        self.set_scheduled_teams_player_database()
        
        return self.__get_scheduled_teams_player_database()