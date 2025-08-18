import pandas as pd
from nhlpy import NHLClient
from nhlpy.api.query.filters.franchise import FranchiseQuery
from nhlpy.api.query.filters.season import SeasonQuery
from nhlpy.api.query.builder import QueryBuilder, QueryContext
from typing import Optional, Dict

class NHLClientHandler:
    """
    Base handler class that provides a shared NHL client instance.
    """
    _client = NHLClient()
   
    def __init__(self):
        """Initialize the handler with access to the shared NHL client."""
        self.client = NHLClientHandler._client

class NHLDataHandler(NHLClientHandler):
    """
    Handler for NHL player and team data.
    """
    def __init__(self):
        super().__init__()

    def get_team_roster(self, team_abbrev: str) -> pd.DataFrame:
        """
        Get the roster for a specific NHL team.
        
        Args:
            team_abbrev (str): The team abbreviation of NHL API (e.g., 'TOR', 'NYR')
            
        Returns:
            pd.DataFrame: DataFrame containing player name + team abbrev
        """
        # Get current season roster
        roster_raw: Dict = self.client.teams.team_roster(team_abbr=team_abbrev, season="20242025")
        all_players = []
        for position_group in ['forwards', 'defensemen', 'goalies']:
            all_players.extend(roster_raw.get(position_group, []))
        
        players_data = []
        
        for player_raw in all_players:
            player_raw: Dict = player_raw
            player_full_name = f"{player_raw.get('firstName').get('default')} {player_raw.get('lastName').get('default')}"
            pos = player_raw.get('positionCode')
            players_data.append({
                'player_name': player_full_name,
                'team_abbrev': team_abbrev,
                'position': pos
            })
            
        roster_df = pd.DataFrame(players_data)
        return roster_df