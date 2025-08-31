import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2
import os
from dotenv import load_dotenv
from nhl_cli import NHLDataHandler
from nba_cli import NBADataHandler
from nhl_teams import teams
from nba_teams import NBA_TEAMS

class NHLConnHandler:
    def __init__(self, engine):
        self.engine = engine
        self.nhl_handler = NHLDataHandler()
        
    def truncate_tables(self):
        with self.engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE nhlraw.player_info"))
            connection.execute(text("TRUNCATE TABLE nhlraw.player_data"))
            connection.execute(text("TRUNCATE TABLE nhlraw.player_game_log"))
            # staged data should be views
            
    def player_info_refresh(self):
        try:
            for team_name, team_data in teams.items():
                team_abbrev = team_data['abbreviation']
                try:
                    roster_df = self.nhl_handler.get_team_roster(team_abbrev)
                    
                    with self.engine.begin() as connection:
                        for _, player in roster_df.iterrows():
                            connection.execute(text(
                                "INSERT INTO nhlraw.player_info (player_id, player_name, team_abbrev, position) VALUES (:player_id, :player_name, :team_abbrev, :pos)"
                            ), {
                                'player_id': player['player_id'],
                                'player_name': player['player_name'],
                                'team_abbrev': player['team_abbrev'], 
                                'pos': player['position']
                            })
                except Exception as team_error:
                    print(f"Failed to process {team_abbrev}: {team_error}")
                    continue
                        
        except Exception as e:
            print(f"Data insertion failed: {e}")

    def team_player_data_refresh(self):
        try:
            with self.engine.begin() as connection:
                for team_name, team_data in teams.items():
                    players_data = None
                    team_abbrev = team_data['abbreviation']
                    players_data = self.nhl_handler.get_team_player_data(team_abbrev)
                    print(f"inserting {team_abbrev} into player_data")
                    for player_stats in players_data:
                        connection.execute(text(f"""
                            INSERT INTO nhlraw.player_data
                            (player_id, player_name, team_abbrev, position, games_played, points, goals, assists, shots, blocked_shots, toi, salary, ppg)
                            VALUES (:player_id, :player_name, :team_abbrev, :position, :games_played, :points, :goals, :assists, :shots, :blocked_shots, :toi, :salary, :ppg)
                        """), player_stats)        
        except Exception as e:
            print(f"Team player data insertion failed for {team_abbrev}: {e}")
            
    def player_game_log_refresh(self):
        
        try:
            query = "SELECT player_id, player_name FROM nhlraw.player_info"
            df = pd.read_sql_query(query, self.engine)
            
            for index, row in df.iterrows():
                player_id = row['player_id']
                player_name = row['player_name']
                
                l10 = self.nhl_handler.get_player_game_log(player_id, player_name)
                l10 = l10[:10]  # keep only the first 10 games

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
    def __init__(self, engine):
        self.engine = engine
        self.nba_handler = NBADataHandler()
        
    def truncate_tables(self):
        with self.engine.begin() as connection:
            # connection.execute(text("TRUNCATE TABLE nbaraw.player_info"))
            connection.execute(text("TRUNCATE TABLE nbaraw.player_data"))
            # staged data should be views
            
    def player_info_refresh(self):
        try:
            with self.engine.begin() as connection:
                connection.execute(text("TRUNCATE TABLE nbaraw.player_info"))
            
            for team_id in NBA_TEAMS.keys():
                try:
                    roster_df = self.nba_handler.get_team_roster(team_id)
                    
                    with self.engine.begin() as connection:
                        for _, player in roster_df.iterrows():
                            connection.execute(text("""
                                INSERT INTO nbaraw.player_info 
                                (player_id, player_name, position, team_abbrev)
                                VALUES (:player_id, :player_name, :position, :team_abbreviation)
                            """), {
                                'player_id': player['PLAYER_ID'],
                                'player_name': player['PLAYER'],
                                'position': player['POSITION'],
                                'team_abbreviation': player['TEAM_ABBREV']
                            })
                except Exception as e:
                    print(f"Error processing team {team_id}: {e}")
                    
        except Exception as e:
            print(f"Player info insertion failed: {e}")
    
    def team_player_data_refresh(self):
        try:
            with self.engine.begin() as connection:
                connection.execute(text("TRUNCATE TABLE nbaraw.player_data"))
            
            for team_id in NBA_TEAMS.keys():
                try:
                    player_data = self.nba_handler.get_team_player_data(team_id)
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
                    print(f"Error processing team {team_id}: {e}")
                    
        except Exception as e:
            print(f"Team player data insertion failed: {e}")
            