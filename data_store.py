from data_merger import DataMerger
from typing import Optional
import pandas as pd

class NHLData(DataMerger):
    """Public user scoped wrapper class to fetch essential data.

    Args:
        DataMerger: DataMerger class - merges and finalizes data.
        Inherited to create wrapper functions around finalized data.
    """
    def __init__(self, date: Optional[str] = None):
        super().__init__(date=date)
    
    def get_daily_player_data(self) -> dict[pd.DataFrame]:
        """Front facing wrapper to get  daily player data.

        Returns:
            dict[pd.DataFrame]: a dictionary, by team name, for each team, with dataframes containing
            player data: "name", "team", "position", "games_played", "points", "goals", "assists", "shots"
            "blocked_shots", 'toi', "salary".
        """
        data = self.daily_player_database()
        return data
    
    def get_schedule(self) -> list[dict]:
        """Front fracing wrapper to get daily schedule.

        Returns:
            list[dict]: daily schedule, of each team's full name, city name, 
            team name, logo information, and match time.
        """
        self.nhl.schedule_handler.nhl_schedule()
    
    def get_scheduled_teams(self) -> list[str]:
        """Front facing wrapper to get list of scheduled teams.

        Returns:
            list[str]: Returns a list of teams scheduled to play in given date. Values are team names.
        """
        self.nhl.schedule_handler.nhl_scheduled_teams()