from src.handlers.api_handler import NHLHandler
from src.handlers.dk_handler import DraftKingsDataHandler

import pandas as pd
from typing import Optional
import os
import django

import src.team_info as team_info

print("setting up django..")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.app.web.web.settings')
django.setup()

from src.app.web.nhl.models import PlayerData

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
            self.scheduled_teams_player_database: dict[pd.DataFrame] = {}
            self.schedule: list[dict] = self.nhl.schedule_handler.nhl_schedule()
            self.available_player_salaries: pd.DataFrame = self.dk.available_player_salaries()
        except:
            print("No scheduled games today. Merger will not run.")
            pass
        
        self.all_teams: list[str] = self.nhl.teams_handler.nhl_all_teams()

        
    def __get_scheduled_teams_player_database(self) -> dict[pd.DataFrame]:
        return self.scheduled_teams_player_database
        
    def build_scheduled_teams_player_database(self) -> dict[pd.DataFrame]:
        """Gets and builds a pandas dataframe for each teams player data, and puts it in a dictionary.
            Key is team name.

        Returns:
            dict[pd.DataFrame]: dictionary of pandas dataframes for each teams player data
        """
        try:
            db: dict[pd.DataFrame] = {}
            
            for team in self.scheduled_teams:
                team_data: pd.DataFrame = self.nhl.player_data_handler.get_team_player_data_as_df(team_name=team)
                db[team_info.teams.get(team).get('abbreviation')] = team_data # needs to be team abbreviation to relate to salary data
            
            return db
        except AttributeError:
            raise AttributeError("No games today, please run 'build_all_teams_player_database' for all teams without salaries.")
    
    def build_all_teams_player_database(self) -> dict[pd.DataFrame]:
        """Gets and builds a pandas dataframe for each teams player data, and puts it in a dictionary.
            Key is team name.

        Returns:
            dict[pd.DataFrame]: dictionary of pandas dataframes for each teams player data
        """
        db: dict[pd.DataFrame] = {}
        
        for team in self.all_teams:
            team_data: pd.DataFrame = self.nhl.player_data_handler.get_team_player_data_as_df(team_name=team)
            db[team_info.teams.get(team).get('abbreviation')] = team_data # needs to be team abbreviation to relate to salary data
            
        return db
    
    def create_player_merge_database_model(self) -> None:
        """Merges salary data with player data into PostgreSQL database"""
        db: dict[pd.DataFrame] = self.build_all_teams_player_database()
        for team in db:
            for player in db[team].iterrows():
                p_api: pd.Series = player[1]
                player_name = p_api.get("name")

                if player_name in self.available_player_salaries["Name"].values:
                    p_dk: pd.Series = self.available_player_salaries[self.available_player_salaries["Name"] == player_name].iloc[0]
                    salary = p_dk.get("Salary")
                    ppg: float = p_dk.get('AvgPointsPerGame')
                else:
                    salary = 0
                    ppg = 0
                
                position: str = p_api.get('position')
                games_played: int = p_api.get('games_played')
                points: int = p_api.get('points')
                goals: int = p_api.get('goals')
                assists: int = p_api.get('assists')
                shots: int = p_api.get('shots')
                blocked_shots: int = p_api.get('blocked_shots')
                toi: float = p_api.get('toi')
                salary: int = salary
                ppg: float = ppg
            
                p = PlayerData(name = player_name,
                            team=team,
                            position=position,
                            games_played=games_played,
                            points=points,
                            goals=goals,
                            assists=assists,
                            shots=shots,
                            blocked_shots=blocked_shots,
                            toi=toi,
                            salary=salary,
                            ppg=ppg)
                
                p.save()
            
            
    
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