from src.handlers.api_handler import NHLHandler
from src.handlers.dk_handler import DraftKingsDataHandler

import pandas as pd
from typing import Optional

import src.team_info as team_info

from src.app.web.nhl.models import ApiData, PlayerData

class DataMerger:
    """Merges draft kings data into nhl api player data and finalizes data sets for web app.
        Used by NHLData to create wrapper functions.
    """
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

        self.available_player_salaries: pd.DataFrame = self.dk.available_player_salaries()
        
    def __get_scheduled_teams_player_database(self) -> dict[pd.DataFrame]:
        return self.scheduled_teams_player_database
        
    def build_scheduled_teams_player_database(self) -> dict[pd.DataFrame]:
        """Gets and builds a pandas dataframe for each teams player data, and puts it in a dictionary.
            Key is team name.

        Returns:
            dict[pd.DataFrame]: dictionary of pandas dataframes for each teams player data
        """
        db: dict[pd.DataFrame] = {}
        
        for team in self.scheduled_teams:
            team_data: pd.DataFrame = self.nhl.player_data_handler.get_team_player_data_as_df(team_name=team)
            db[team_info.teams.get(team).get('abbreviation')] = team_data # needs to be team abbreviation to relate to salary data
            
        return db
    
    def merge_salaries_into_database(self) -> None:
        """Merges salary data with player data into PostgreSQL database"""
        db: dict[pd.DataFrame] = self.build_scheduled_teams_player_database()

        for player in self.available_player_salaries.iterrows():
            p_dk: pd.Series = player[1]
            df = db[team]
            p_api: pd.Series = df[df['name'] == name].iloc[0]
            team: str = p_dk.get('TeamAbbrev')
    
            name: str = p_dk.get('Name')
            salary: int = p_dk.get('Salary')
            ppg: float = p_dk.get('AvgPointsPerGame')
            position: str = p_api.get('position')
            games_played: int = p_api.get('games_played')
            
            p = PlayerData(name = name,
                        team=team,
                        position=position,
                        games_played=games_played)
            
    
    def merge_salaries_set_database(self) -> dict[pd.DataFrame]:
        """Merge the draftkings player/salary database from date, and merges the salary values into
            each teams player dataframe

        Returns:
            pd.DataFrame: dictionary of pandas dataframes for each teams player data, with the merging of their draftkings salary
        """
        db: dict[pd.DataFrame] = self.build_scheduled_teams_player_database()

        for player_dk in self.available_player_salaries.iterrows():
            
            player: pd.Series = player_dk[1]
           
            team_abbrev: str = player.get('TeamAbbrev')

            player_salary: int = player.get('Salary')
            
            avg_ppg: float = player.get('AvgPointsPerGame')
            
            team_df: pd.DataFrame = db[team_abbrev]
            player_name: str = player.get('Name')
            
            # update the salary where the player name matches
            try:
                db[team_abbrev].loc[team_df['name'] == player_name, 'salary'] = player_salary
                db[team_abbrev].loc[team_df['name'] == player_name, 'ppg'] = avg_ppg
            except:
                print(f'{player_name} not draftable. skipping...')

        return db
                 
    def set_scheduled_teams_player_database(self) -> None:
        self.scheduled_teams_player_database: dict[pd.DataFrame] = self.merge_salaries_set_database()
                
    def daily_player_database(self) -> dict[pd.DataFrame]:
        """User function that sets and gets the finalized daily scheduled teams player data

        Returns:
            dict[pd.DataFrame]: dioctionary with each teams dataframe of player data
        """
        self.set_scheduled_teams_player_database()
        
        return self.__get_scheduled_teams_player_database()