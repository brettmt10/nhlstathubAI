import pandas as pd
from sqlalchemy import text, Engine
from nhl_cli import NHLDataHandler
from nba_cli import NBADataHandler
from nhl_teams import teams
from nba_teams import NBA_TEAMS
import time
from typing import Any

class NHLConnHandler:
    """DB connection handler for NHL tables.
    
    Attributes:
        engine (Engine): SQLAlchemy Engine object connected to DB.
        nhl_handler (NHLHandler): NHLHandler - object which fetches and curates NHL data from NHL API
    """
    def __init__(self, engine: Engine):
        """Initialize new connection manager.
        
        Args:
            engine (Engine): SQLAlchemy Engine object connected to DB.
            nhl_handler (NHLHandler): NHLHandler - object which fetches and curates NHL data from NHL API
        """
        self.engine: Engine = engine
        self.nhl_handler: NHLDataHandler = NHLDataHandler()
        
    def truncate_tables(self):
        """Truncates tables. Used before inserting fetched data into DB.
        """
        with self.engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE nhlraw.player_info"))
            connection.execute(text("TRUNCATE TABLE nhlraw.player_data"))
            connection.execute(text("TRUNCATE TABLE nhlraw.player_game_log"))
            
    def player_info_refresh(self):
        """Refreshes the nhlraw.player_info table.
        The table includes player_id, player_name, team_abbrev and position.
        Iterates through each team and calls NHLDataHandler's team roster method.  
        """
        try:
            for team_name, team_data in teams.items():
                team_abbrev: str = team_data['abbreviation']
                try:
                    roster_df: pd.DataFrame = self.nhl_handler.get_team_roster(team_abbrev)
                    
                    with self.engine.begin() as connection:
                        for _, player in roster_df.iterrows(): # iterates through each player in the roster. df.to_sql causing weird bugs.
                            connection.execute(text(
                                "INSERT INTO nhlraw.player_info (player_id, player_name, team_abbrev, position) VALUES (:player_id, :player_name, :team_abbrev, :position)"
                            ), {
                                'player_id': player['player_id'],
                                'player_name': player['player_name'],
                                'team_abbrev': player['team_abbrev'], 
                                'position': player['position']
                            })
                except Exception as team_error:
                    print(f"Failed to process {team_abbrev}: {team_error}")
                    continue
                        
        except Exception as e:
            print(f"Data insertion failed: {e}")

    def team_player_data_refresh(self):
        """Refreshes the nhlraw.player_data table.
        The table includes player_id, player_name, team_abbrev, position, games_played, points, goals, assists, shots, blocked_shots, toi, salary, ppg.
        Iterates through each team and calls NHLDataHandler's team data method.  
        """
        try:
            with self.engine.begin() as connection:
                for _, team_data in teams.items():
                    players_data = None
                    team_abbrev: str = team_data['abbreviation']
                    players_data: list = self.nhl_handler.get_team_player_data(team_abbrev)
                    for player_stats in players_data:
                        connection.execute(text(f"""
                            INSERT INTO nhlraw.player_data
                            (player_id, player_name, team_abbrev, position, games_played, points, goals, assists, shots, blocked_shots, toi, salary, ppg)
                            VALUES (:player_id, :player_name, :team_abbrev, :position, :games_played, :points, :goals, :assists, :shots, :blocked_shots, :toi, :salary, :ppg)
                        """), player_stats)        
        except Exception as e:
            print(f"Team player data insertion failed for {team_abbrev}: {e}")
            
    def player_game_log_refresh(self):
        """Refreshes the nhlraw.player_game_log table.
        The table includes player_id, player_name, home_road_flag, game_date, goals, assists, opponent_common_name, points, shots, toi
        Iterates through each team and calls NHLDataHandler's player game log method.
        """
        try:
            query = "SELECT player_id, player_name FROM nhlraw.player_info"
            df = pd.read_sql_query(query, self.engine)
            
            for _, row in df.iterrows():
                player_id: int = row['player_id']
                player_name: str = row['player_name']
                
                l10: list[dict[str, Any]] = self.nhl_handler.get_player_game_log(player_id, player_name)
                l10 = l10[:10]  # keep only the first 10 games

                # convert toi into float form
                for game in l10:
                    minutes, seconds = map(int, game['toi'].split(':'))
                    seconds_percent = round(seconds / 60, 2)
                    game['toi'] = minutes + seconds_percent
                
                with self.engine.begin() as connection:
                    for game in l10:
                        connection.execute(text("""
                            INSERT INTO nhlraw.player_game_log
                            (player_id, player_name, home_road_flag, game_date, goals, assists, opponent_common_name, points, shots, toi)
                            VALUES (:player_id, :player_name, :home_road_flag, :game_date, :goals, :assists, :opponent_common_name, :points, :shots, :toi)
                        """), {
                            'player_id': player_id,
                            'player_name': player_name,
                            'home_road_flag': game.get('homeRoadFlag'),
                            'game_date': game.get('gameDate'),
                            'goals': game.get('goals'),
                            'assists': game.get('assists'),
                            'opponent_common_name': game.get('opponentCommonName'),
                            'points': game.get('points'),
                            'shots': game.get('shots'),
                            'toi': game.get('toi')
                        })   
        except Exception as e:
            print(f"Error processing player data: {e}")
        finally:
            self.engine.dispose()
            
class NBAConnHandler:
    """DB connection handler for NBA tables.
    
    Attributes:
        engine (Engine): SQLAlchemy Engine object connected to DB.
        nhl_handler (NBAHandler): NBAHandler - object which fetches and curates NBA data from NBA API
    """
    def __init__(self, engine):
        """Initialize new connection manager.
        
        Args:
        engine (Engine): SQLAlchemy Engine object connected to DB.
        nhl_handler (NBAHandler): NBAHandler - object which fetches and curates NBA data from NBA API
        """
        self.engine: Engine = engine
        self.nba_handler: NBADataHandler = NBADataHandler()
        
    def truncate_tables(self):
        """Truncates tables. Used before inserting fetched data into DB.
        """
        with self.engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE nbaraw.player_info"))
            connection.execute(text("TRUNCATE TABLE nbaraw.player_data"))
            connection.execute(text("TRUNCATE TABLE nbaraw.player_game_log"))
            
    def player_info_refresh(self):
        """Refreshes the nbaraw.player_info table.
        The table includes player_id, player_name, team_abbrev and position.
        Iterates through each team and calls NBADataHandler's team roster method.  
        """
        for team_id in NBA_TEAMS.keys():
            try:
                roster_df: pd.DataFrame = self.nba_handler.get_team_roster(team_id)
                with self.engine.begin() as connection:
                    for _, player in roster_df.iterrows():
                        connection.execute(text("""
                            INSERT INTO nbaraw.player_info 
                            (player_id, player_name, team_abbrev, position)
                            VALUES (:player_id, :player_name, :team_abbrev, :position)
                        """), {
                            'player_id': player['PLAYER_ID'],
                            'player_name': player['PLAYER'],
                            'team_abbrev': player['TEAM_ABBREV'],
                            'position': player['POSITION']
                        })
            except Exception as e:
                print(f"Error fetching team info for {team_id}: {e}. \n Continuing to next team...")
                continue
    
    def team_player_data_refresh(self):
        """Refreshes the nbaraw.player_game_log table.
        The table includes player_id, player_name, team_abbrev, games_played, points, rebounds, assists, turnovers, steals, blocks, minutes
        Iterates through each team and calls NBADataHandler's player game log method.
        """
        for team_id in NBA_TEAMS.keys():
            try:
                player_data: pd.DataFrame = self.nba_handler.get_team_player_data(team_id)
                with self.engine.begin() as connection:
                    for _, player in player_data.iterrows():
                        connection.execute(text("""
                            INSERT INTO nbaraw.player_data 
                            (player_id, player_name, team_abbrev, games_played, points, rebounds, assists, turnovers, steals, blocks, minutes)
                            VALUES (:player_id, :player_name, :team_abbrev, :games_played, :points, :rebounds, :assists, :turnovers, :steals, :blocks, :minutes)
                        """), {
                            'player_id': player['PLAYER_ID'],
                            'player_name': player['PLAYER_NAME'],
                            'team_abbrev': player['TEAM_ABBREV'],
                            'games_played': player['GP'],
                            'points': player['PTS'],
                            'rebounds': player['REB'],
                            'assists': player['AST'],
                            'turnovers': player['TOV'],
                            'steals': player['STL'],
                            'blocks': player['BLK'],
                            'minutes': player['MIN']
                        })
            except Exception as e:
                print(f"Error fetching player data for team {team_id}: {e}. Continuing to next team...")
                continue
            
            
    def player_game_log_refresh(self):
        """Refreshes the nbaraw.player_game_log table.
        The table includes player_id, player_name, homevaway, date, points, rebounds, assists, turnovers, steals, blocks, minutes
        Iterates through each team and calls NHLDataHandler's player game log method.
        """

        query = "SELECT player_id, player_name FROM nbaraw.player_info"
        df = pd.read_sql_query(query, self.engine)
  
        for _, row in df.iterrows():
            try:
                player_id = row['player_id']
                time.sleep(5) # timeout avoidance
                l10 = self.nba_handler.get_player_game_log(player_id)
                
                with self.engine.begin() as connection:
                    for _, game in l10.iterrows():
                        connection.execute(text("""
                            INSERT INTO nbaraw.player_game_log
                            (player_id, player_name, homevaway, date, points, rebounds, assists, turnovers, steals, blocks, minutes)
                            VALUES (:player_id, :player_name, :homevaway, :date, :points, :rebounds, :assists, :turnovers, :steals, :blocks, :minutes)
                        """), {
                            'player_id': player_id,
                            'player_name': game['PLAYER_NAME'],
                            'homevaway': game['MATCHUP'],
                            'date': game['GAME_DATE'],
                            'points': game['PTS'],
                            'rebounds': game['REB'],
                            'assists': game['AST'],
                            'turnovers': game['TOV'],
                            'steals': game['STL'],
                            'blocks': game['BLK'],
                            'minutes': game['MIN']
                        })                
            except Exception as e:
                print(f"Error fetching NBA player game log data: {e}. Continuing to next player...")
                continue
                    
            self.engine.dispose()