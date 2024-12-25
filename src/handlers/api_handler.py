from nhlpy import NHLClient
from nhlpy.api.query.filters.franchise import FranchiseQuery
from nhlpy.api.query.filters.season import SeasonQuery
from nhlpy.api.query.builder import QueryBuilder, QueryContext

import pandas as pd
import requests

import src.team_info as team_info
from datetime import datetime
import pytz
from typing import Optional

class NHLClientProvider:
    """Provides an instance of the NHL api client. 
       Used and inherited so only one api instance is ever made.
    """
    def __init__(self):
        self.client: NHLClient = NHLClient()
        
class NHLScheduleHandler():
    def __init__(self, client: NHLClient, date: Optional[str] = datetime.today().strftime('%Y-%m-%d')):
        self.client: NHLClient = client
        self.day: str = date
        self.schedule_metadata: dict = self.client.schedule.get_schedule(date=self.day).get('games') # dict of schedule information
        
        if not self.schedule_metadata:
            raise ValueError(f"No games on date {self.day}")
        
        self.num_games: int = len(self.schedule_metadata) # number of games for today's date
        self.schedule: list[dict] = []
        self.scheduled_teams: list[str] = []
        
    def get_schedule_metadata(self) -> dict:
        return(self.schedule_metadata)
    
    def get_num_games(self) -> int:
        return(self.num_games)
    
    def __get_schedule(self) -> dict:
        return(self.schedule)
    
    def __get_scheduled_teams(self) -> list[dict]:
        return(self.scheduled_teams)
    
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
            
        for game in self.schedule_metadata:
            game_i: dict = game
            
            game_data: dict = self.parse_single_game_data(game_i)
            
            schedule.append(game_data)
            
        return schedule
    
    def build_scheduled_teams(self) -> list[str]:
        """Add each team to the list of daily scheduled teams

        Returns:
            list[str]: List of daily scheduled teams to play
        """
        teams: list[str] = []  
             
        for game in self.schedule:
            teams.append(game.get("away_team")["name"])
            teams.append(game.get("home_team")["name"])
            
        return teams
        
    def set_scheduled_teams(self) -> None:
        """Sets scheduled teams.
        """
        self.scheduled_teams: list[str] = self.build_scheduled_teams()
    
    def set_schedule(self) -> None:
        """Sets schedule with finalized data for each game.
        """
        self.schedule: dict = self.build_schedule()
        
    def nhl_schedule(self) -> list[dict]:
        """User function that sets and gets the finalized schedule data to the proper game data for use.

        Returns:
            list[dict]: List of dicts with finalized data for each game.
        """
        # set schedule if schedule was not built manually
        if not self.schedule:
            self.set_schedule()
            print('setting schedule cus this func, nhl_schedule, was called when no schedule was made')
            
        return(self.__get_schedule())
    
    def nhl_scheduled_teams(self) -> list[str]:
        """User function that sets and gets the finalized daily scheduled teams data
        
        Returns:
            list[str]: List of daily scheduled teams. Uses team names as values."""
            
        # set schedule if schedule was not built manually
        if not self.schedule:
            self.set_schedule()
            print('setting schedule cus this func, nhl_scheduled_teams, was called when no schedule was made')
            
        # sets scheduled teams if not built manually
        if not self.scheduled_teams:
            print("setting scheduled_teams cus this func, nhl_scheduled_teams, was called with no scheduled_teams made")
            self.set_scheduled_teams()
            
        return(self.__get_scheduled_teams())
    
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
        try:
            super().__init__(client=client, date=date)
        except ValueError:
            print("No games today, NHLPlayerDataHandler still useable.")
            pass
        
    def calculate_player_fantasy_pts(self, game_log_l10):
        pass
    
    def get_player_game_log(self, player_id: int) -> pd.DataFrame:
        url = f'https://www.naturalstattrick.com/playerreport.php?fromseason=20242025&thruseason=20242025&stype=2&sit=5v5&stdoi=std&rate=n&v=g&playerid={player_id}#'
        res = requests.get(url)
        raw: list = pd.read_html(pd.io.common.StringIO(res.text))
        game_log_nst = pd.DataFrame(raw[0])
        
        raw: list[dict] = self.client.stats.player_game_log(player_id=player_id, season_id="20242025", game_type='2')
        game_log_nhl = pd.DataFrame(raw)
    
    def calculate_player_variance(self):
        pass
    
    def get_team_player_data(self, team_name: str) -> dict:
        """Get the required GUI player data for a team.

        Args:
            team_name (str): team name of a team

        Returns:
            dict: dictionary containing required data for each player
        """
        
        team_player_data: list[dict] = []
        
        franchise_id: str = team_info.teams.get(team_name).get('id')
        team_abbrev: str = team_info.teams.get(team_name).get('abbreviation')
        
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
            player_id: int = pd_summary["playerId"]
            
            # self.get_player_game_log(player_id)
            
            player_stats: dict = {
                "name": pd_summary["skaterFullName"],
                "team": team_abbrev,
                "position": pd_summary["positionCode"],
                "games_played": pd_summary["gamesPlayed"],
                "points": pd_summary["points"],
                "goals": pd_summary["goals"],
                "assists": pd_summary["assists"],
                "shots": pd_summary["shots"],
                "blocked_shots": pd_misc["blockedShots"],
                'toi': round(pd_summary["timeOnIcePerGame"]/60, 2),
                "salary": None, # init to 0
                "ppg": None
            }
            
            team_player_data.append(player_stats)

        return team_player_data
    
    def get_team_player_data_as_df(self, team_name: str) -> pd.DataFrame:
        """Get the team player data and convert it to a pandas dataframe

        Args:
            team_name (str): team name of a team

        Returns:
            pd.DataFrame: dataframe of a team's player data
        """
        team_player_data = self.get_team_player_data(team_name=team_name)
        return pd.DataFrame(team_player_data)
        
class NHLHandler(NHLClientProvider):
    def __init__(self, date: Optional[str] = datetime.today().strftime('%Y-%m-%d')):
        super().__init__()
        try:
            self.schedule_handler: NHLScheduleHandler = NHLScheduleHandler(client=self.client, date=date)
        except ValueError:
            pass
        
        self.player_data_handler: NHLPlayerDataHandler = NHLPlayerDataHandler(client=self.client, date=date)