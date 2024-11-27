from nhlpy import NHLClient
from nhlpy.api.query.filters.franchise import FranchiseQuery
from nhlpy.api.query.filters.season import SeasonQuery
from nhlpy.api.query.builder import QueryBuilder, QueryContext

import pandas as pd

import team_info
from datetime import datetime
import pytz
from typing import Optional

class NHLClientProvider():
    def __init__(self):
        self.client: NHLClient = NHLClient()
        
class NHLScheduleHandler():
    def __init__(self, client: NHLClient, date: Optional[str] = datetime.today().strftime('%Y-%m-%d')):
        self.client: NHLClient = client
        self.day: str = date
        self.schedule_metadata: dict = self.client.schedule.get_schedule(date=self.day).get('games') # dict of schedule information
        self.num_games: int = len(self.schedule_metadata) # number of games for today's date
        self.schedule: list[dict] = []
        
    def get_schedule_metadata(self) -> dict:
        return(self.schedule_metadata)
    
    def get_num_games(self) -> int:
        return(self.num_games)
    
    def __get_schedule(self) -> dict:
        return(self.schedule)
    
    def localize_game_start(self, utc_time: str) -> tuple[str, str, str]:
        """Localizes utc time for game start time.
        Returns:
            tuple[str, str, str]: (time in H:MM format, timezone abbreviation, full time string)
        """
        utc_time: datetime = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%SZ')
        utc_time: datetime = pytz.utc.localize(utc_time)

        local_time = utc_time.astimezone()

        time_start: str = local_time.strftime('%#I:%M')
       
        local_timezone: str = local_time.strftime('%Z')
        
        full_time_str: str = time_start + " " + local_timezone

        return (time_start, local_timezone, full_time_str)
                
    def parse_single_game_data(self, game_metadata: dict) -> dict:
        """Parses the dictionary of a single game and grabs required data for GUI.

        Args:
            game_data (dict): metadata of a single game

        Returns:
            dict: required data dictionary for a single game
        """
        
        city_away_team: str = game_metadata.get('awayTeam').get('placeName')['default']
        city_home_team: str = game_metadata.get('homeTeam').get('placeName')['default']
        
        name_away_team: str = game_metadata.get('awayTeam').get('commonName')['default']
        name_home_team: str = game_metadata.get('homeTeam').get('commonName')['default']
        
        # bug in utah's name
        if name_home_team == "Utah Hockey Club":
            name_home_team = "Hockey Club"
        elif name_away_team == "Utah Hockey Club":
            name_away_team = "Hockey Club"
        
        logo_away_team: str = game_metadata.get('awayTeam').get('logo')
        logo_home_team: str = game_metadata.get('homeTeam').get('logo')
        
        full_name_away_team: str = city_away_team + " " + name_away_team
        full_name_home_team: str = city_home_team + " " + name_home_team
        
        game_start_utc: str = game_metadata.get('startTimeUTC')
        game_start_time_data: tuple = self.localize_game_start(game_start_utc)
            
        game_data: dict = {
                            "away_team": {"full_name": full_name_away_team, "city": city_away_team, "name": name_away_team, "logo": logo_away_team},
                            "home_team": {"full_name": full_name_home_team, "city": city_home_team, "name": name_home_team, "logo": logo_home_team},
                            "start_time": game_start_time_data[2]
                          }
        
        return game_data
    
    def build_schedule(self) -> list[dict]:
        """Adds each game's parsed data as a dict and builds proper schedule data.

        Returns:
            list[dict]: List of dicts with finalized schedule of required game data.
        """
        
        schedule: list = []
        
        try:      
            for game in self.schedule_metadata:
                game_i: dict = game
                
                game_data: dict = self.parse_single_game_data(game_i)
                
                schedule.append(game_data)
        except IndexError:
            raise IndexError(f'No games today: {self.day}')
            
        return schedule
    
    def set_schedule(self) -> None:
        """Sets schedule with finalized data for each game.
        """
        self.schedule: dict = self.build_schedule()
        
    def nhl_schedule(self) -> list[dict]:
        """Sets the schedule to the proper game data for use.

        Returns:
            list[dict]: List of dicts with finalized data for each game.
        """
        self.set_schedule()
        return(self.__get_schedule())
    
    def print_beautify_schedule(self, schedule: list[dict]) -> None:
        """Prints a readable version of the schedule passed through.

        Args:
            schedule (list[dict]): daily nhl schedule. set with conventions of this class' schedule dictionary.
        """
        
        print('---')
        for idx, game in enumerate(schedule):
            away_team: dict = game.get("away_team")
            home_team: dict = game.get("home_team")
            
            print(f"Game {idx + 1}: {away_team["full_name"]} vs {home_team["full_name"]}. Starts at {game["start_time"]}.")
            print('---')

class NHLPlayerDataHandler(NHLScheduleHandler):
    def __init__(self, client: NHLClient, date: Optional[str] = datetime.today().strftime('%Y-%m-%d')):
        super().__init__(client=client, date=date)
        self.schedule = self.nhl_schedule()
        
    def get_team_player_data(self, team_city: str) -> dict:
        """Get the required GUI player data for a team.

        Args:
            team_city (str): city name of a team

        Returns:
            dict: dictionary containing required data for each player
        """
        
        team_player_data: list[dict] = []
        
        franchise_id: str = team_info.teams.get(team_city).get('id')
        
        filters: list = [
            SeasonQuery(season_start="20242025", season_end="20242025"),
            FranchiseQuery(franchise_id=franchise_id)
        ]

        query_builder: QueryBuilder = QueryBuilder()
        query_context: QueryContext = query_builder.build(filters=filters)

        team_player_data_summary: dict = self.client.stats.skater_stats_with_query_context(
            report_type='summary',
            query_context=query_context,
            aggregate=True            
        ).get('data')
        
        team_player_data_misc: dict = self.client.stats.skater_stats_with_query_context(
            report_type='realtime',
            query_context=query_context,
            aggregate=True
        ).get('data')
        
        for pd_summary, pd_misc in zip(team_player_data_summary, team_player_data_misc):
            player_stats: dict = {
                "name": pd_summary["skaterFullName"],
                "games_played": pd_summary["gamesPlayed"],
                "points": pd_summary["points"],
                "goals": pd_summary["goals"],
                "assists": pd_summary["assists"],
                "shots": pd_summary["shots"],
                "blocked_shots": pd_misc["blockedShots"],
                'toi': round(pd_summary["timeOnIcePerGame"]/60, 2)
            }
            
            team_player_data.append(player_stats)
            
        return team_player_data
    
    def get_team_player_data_as_df(self, team_city: str) -> pd.DataFrame:
        """Get the team player data and convert it to a pandas dataframe

        Args:
            team_city (str): city name of a team

        Returns:
            pd.DataFrame: dataframe of a team's player data
        """
        team_player_data = self.get_team_player_data(team_city=team_city)
        return pd.DataFrame(team_player_data)
        
class NHLHandler(NHLClientProvider):
    def __init__(self, date: Optional[str] = datetime.today().strftime('%Y-%m-%d')):
        super().__init__()
        self.schedule_handler: NHLScheduleHandler = NHLScheduleHandler(client=self.client, date=date)
        self.player_data_handler: NHLPlayerDataHandler = NHLPlayerDataHandler(client=self.client, date=date)
        
    def set_date(self, date: str) -> None:
        self.day = date
        self.schedule_handler: NHLScheduleHandler = NHLScheduleHandler(client=self.client, date=date)
        self.player_data_handler: NHLPlayerDataHandler = NHLPlayerDataHandler(client=self.client, date=date)