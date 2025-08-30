import pandas as pd
from datetime import datetime
from nba_api.stats.endpoints import LeagueLeaders

class NBADataHandler:
    # this is all we really need, can use sql to put them into separate DBs
    def get_all_player_data():
        data = LeagueLeaders(
            league_id = '00',
            season = '2024-25',
            per_mode48 = 'PerGame',
        )

        return data.get_data_frames()[0]