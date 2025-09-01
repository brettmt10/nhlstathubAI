import pandas as pd
from datetime import datetime
from nba_api.stats.endpoints import TeamPlayerDashboard, CommonTeamRoster, PlayerGameLogs
from src_api.nba_teams import NBA_TEAMS

class NBADataHandler:
    def get_team_roster(self, team_id):
        team_abbrev = NBA_TEAMS[team_id]['team_abbrev']
        print(f"Fetching {team_abbrev} team roster from API...")
        roster = CommonTeamRoster(team_id=team_id, season='2024-25')
        data = roster.common_team_roster.get_data_frame()
        data['TEAM_ABBREV'] = team_abbrev
        return data[['PLAYER_ID', 'PLAYER', 'POSITION', 'TEAM_ABBREV']]

    def get_team_player_data(self, team_id: str) -> pd.DataFrame:
        team_abbrev = NBA_TEAMS[team_id]['team_abbrev']
        print(f"Fetching {team_abbrev} team player data from API...")
        roster = TeamPlayerDashboard(team_id=team_id, season='2024-25', per_mode_detailed='PerGame')
        data = roster.players_season_totals.get_data_frame()
        data['TEAM_ABBREV'] = team_abbrev
        return data[['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREV', 'GP', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'MIN']]
    
    def get_player_game_log(self, player_id):
        print(f"Fetching player_id: {player_id} from API...")
        data = PlayerGameLogs(player_id_nullable=player_id, last_n_games_nullable=10, season_nullable='2024-25')
        data = data.get_data_frames()[0]
        data = data[:10]
        data = data[['PLAYER_ID', 'PLAYER_NAME', 'MATCHUP', 'GAME_DATE', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'MIN']]
        data['MIN'] = round(data['MIN'], 2)
        return data