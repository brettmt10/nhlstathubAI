from nhlpy import NHLClient
from datetime import datetime

class NHLScheduleHandler():
    def __init__(self, date: str = datetime.today().strftime('%Y-%m-%d')):
        self.client = NHLClient()
        self.day: str = date
        self.schedule_metadata: dict = self.client.schedule.get_schedule(date=date).get('games') # dict of schedule information
        self.num_games: int = len(self.schedule_metadata) # number of games for today's date
        self.schedule: list[dict] = []
        
    def get_schedule_metadata(self) -> dict:
        return(self.schedule_metadata)
    
    def get_num_games(self) -> int:
        return(self.num_games)
    
    def __get_schedule(self) -> dict:
        return(self.schedule)
    
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
            print("rahhhhh")
            name_away_team = "Hockey Club"
        
        logo_away_team: str = game_metadata.get('awayTeam').get('logo')
        logo_home_team: str = game_metadata.get('homeTeam').get('logo')
        
        full_name_away_team: str = city_away_team + " " + name_away_team
        full_name_home_team: str = city_home_team + " " + name_home_team
            
        game_data: dict = {
                            "away_team": {"full_name": full_name_away_team, "city": city_away_team, "name": name_away_team,"logo": logo_away_team},
                            "home_team": {"full_name": full_name_home_team, "city": city_home_team, "name": name_home_team, "logo": logo_home_team},
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
                
                game_data = self.parse_single_game_data(game_i)
                
                schedule.append(game_data)
        except IndexError:
            raise IndexError(f'No games today: {self.day}')
            
        return schedule
    
    def set_schedule(self) -> None:
        """Sets schedule with finalized data for each game.
        """
        self.schedule = self.build_schedule()
        
    def nhl_schedule(self) -> list[dict]:
        """Sets the schedule to the proper game data for use.

        Returns:
            list[dict]: List of dicts with finalized data for each game.
        """
        self.set_schedule()
        return(self.__get_schedule())
    
    def beautify_schedule(self, schedule: list[dict]) -> None:
        """Prints a readable version of the schedule passed through.

        Args:
            schedule (list[dict]): daily nhl schedule. set with conventions of this class' schedule dictionary.
        """
        
        print('---')
        for idx, game in enumerate(schedule):
            print(f"Game {idx + 1}: {game.get("away_team")["full_name"]} vs {game.get("home_team")["full_name"]}. Starts at time EST.")
            print('---')