import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2
import os
from dotenv import load_dotenv
from api_handler_dev import NHLDataHandler
from team_info import teams

load_dotenv()

def db_conn():
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')  
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    return engine

def player_info_refresh(engine):
    try:
        nhl_handler = NHLDataHandler()

        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE raw.player_info"))

        for team_name, team_data in teams.items():
            team_abbrev = team_data['abbreviation']
            try:
                roster_df = nhl_handler.get_team_roster(team_abbrev)
                
                with engine.begin() as connection:
                    for _, player in roster_df.iterrows():
                        connection.execute(text(
                            "INSERT INTO raw.player_info (player_id, name, team_abbrev, position) VALUES (:id, :name, :team, :pos)"
                        ), {
                            'id': player['player_id'],
                            'name': player['player_name'],
                            'team': player['team_abbrev'], 
                            'pos': player['position']
                        })
            except Exception as team_error:
                print(f"Failed to process {team_abbrev}: {team_error}")
                continue
                    
    except Exception as e:
        print(f"Data insertion failed: {e}")

def team_player_data_refresh(engine):
    try:
        nhl_handler = NHLDataHandler()        
        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE raw.player_data"))
            for team_name, team_data in teams.items():
                players_data = None
                team_abbrev = team_data['abbreviation']
                players_data = nhl_handler.get_team_player_data(team_abbrev)
                print(f"inserting {team_abbrev} into player_data")
                for player_stats in players_data:
                    connection.execute(text(f"""
                        INSERT INTO raw.player_data
                        (player_id, name, team_abbrev, position, games_played, points, goals, assists, shots, blocked_shots, toi, salary, ppg)
                        VALUES (:id, :name, :team, :position, :games_played, :points, :goals, :assists, :shots, :blocked_shots, :toi, :salary, :ppg)
                    """), player_stats)        
    except Exception as e:
        print(f"Team player data insertion failed for {team_abbrev}: {e}")
        
def player_game_log_refresh(engine):
    engine = db_conn()
    
    try:
        nhl_handler = NHLDataHandler()
        query = "SELECT player_id, name FROM raw.player_info"
        
        
        df = pd.read_sql_query(query, engine)
        
        print(df)
        
        for index, row in df.iterrows():
            print(f"getting game log for {row['name']}")
            player_id = row['player_id']
            player_name = row['name']
            
            l10 = nhl_handler.get_player_game_log(player_id, player_name)
            for game in l10:
                print(game)
            return
            
            
    except Exception as e:
        print(f"Error processing player data: {e}")
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    try:
        engine = db_conn()
        player_game_log_refresh(engine)
    except Exception as e:
        print(f"Connection or data insertion failed: {e}")