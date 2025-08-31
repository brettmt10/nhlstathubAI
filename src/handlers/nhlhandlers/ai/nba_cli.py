import pandas as pd
from datetime import datetime
from nba_api.stats.endpoints import TeamPlayerDashboard, CommonTeamRoster
from nba_teams import NBA_TEAMS

class NBADataHandler:
    def get_team_roster(self, team_id):
        roster = CommonTeamRoster(team_id=team_id, season='2024-25')
        data = roster.common_team_roster.get_data_frame()
        team_abbrev = NBA_TEAMS[team_id]['team_abbrev']
        data['TEAM_ABBREV'] = team_abbrev
        return data[['PLAYER_ID', 'PLAYER', 'POSITION', 'TEAM_ABBREV']]

    def get_team_player_data(self, team_id: str) -> list:  
        roster = TeamPlayerDashboard(team_id=team_id, season='2024-25', per_mode_detailed='PerGame')
        data = roster.players_season_totals.get_data_frame()
        team_abbrev = NBA_TEAMS[team_id]['team_abbrev']
        data['TEAM_ABBREV'] = team_abbrev
        return data[['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREV', 'GP', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'MIN']]