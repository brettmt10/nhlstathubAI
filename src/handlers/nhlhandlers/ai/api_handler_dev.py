import pandas as pd
from nhlpy import NHLClient
from nhlpy.api.query.filters.franchise import FranchiseQuery
from nhlpy.api.query.filters.season import SeasonQuery
from nhlpy.api.query.filters.game_type import GameTypeQuery
from nhlpy.api.query.builder import QueryBuilder, QueryContext
from typing import Optional, Dict
from team_info import teams
import json
from datetime import datetime

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
        roster_raw: Dict = self.client.teams.team_roster(team_abbr=team_abbrev, season="20252026")
        all_players = []
        for position_group in ['forwards', 'defensemen', 'goalies']:
            all_players.extend(roster_raw.get(position_group, []))
        
        players_data = []
        
        for player_raw in all_players:
            player_raw: Dict = player_raw
            player_full_name = f"{player_raw.get('firstName').get('default')} {player_raw.get('lastName').get('default')}"
            pos = player_raw.get('positionCode')
            player_id = player_raw.get('id')
            players_data.append({
                'player_id': player_id,
                'player_name': player_full_name,
                'team_abbrev': team_abbrev,
                'position': pos
            })
            
        roster_df = pd.DataFrame(players_data)
        return roster_df
    
    def get_team_player_data(self, team_abbrev: str) -> list:        
        
        # Get franchise_id from team_info
        franchise_id = None
        for team_name, team_data in teams.items():
            if team_data['abbreviation'] == team_abbrev:
                franchise_id = team_data['id']
                break
        
        if not franchise_id:
            raise ValueError(f"Team abbreviation {team_abbrev} not found")
        
        filters: list = [
            GameTypeQuery(game_type="2"),
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

        players_data = []
        for pd_summary, pd_misc in zip(team_player_data_summary, team_player_data_misc):
            player_stats: dict = {
                "id": pd_summary["playerId"],
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
                "salary": None,
                "ppg": None
            }
            players_data.append(player_stats)
        
        return players_data
        
    def get_player_game_log(self, player_id: int, player_name: str):
        game_log = self.client.stats.player_game_log(
            player_id=player_id, 
            season_id="20232024", 
            game_type=2  # Regular season
        )
        
        return [
            {
            'player_id': player_id,
            'player_name': player_name,
            'homeRoadFlag': game['homeRoadFlag'],
            'gameDate': game['gameDate'],
            'goals': game['goals'],
            'assists': game['assists'],
            'opponentCommonName': game['opponentCommonName']['default'],
            'points': game['points'],
            'shots': game['shots'],
            'toi': game['toi']
            }
            for game in game_log
        ]