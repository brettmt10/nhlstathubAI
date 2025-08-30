import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2
import os
from dotenv import load_dotenv
from nba_cli import NBADataHandler

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

def nba_player_data_refresh(engine):
    try:
        nba_handler = NBADataHandler()

        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE raw.nba_player_data"))

        player_data_df = nba_handler.get_all_player_data()
        
        with engine.begin() as connection:
            for _, player in player_data_df.iterrows():
                connection.execute(text("""
                    INSERT INTO raw.nba_player_data 
                    (player_id, player_name, team_abbreviation, games_played, minutes, rebounds, assists, steals, blocks, turnovers, points)
                    VALUES (:player_id, :player_name, :team_abbreviation, :games_played, :minutes, :rebounds, :assists, :steals, :blocks, :turnovers, :points)
                """), {
                    'player_id': player['PLAYER_ID'],
                    'player_name': player['PLAYER'],
                    'team_abbreviation': player['TEAM'],
                    'games_played': player['GP'],
                    'minutes': player['MIN'],
                    'rebounds': player['REB'],
                    'assists': player['AST'],
                    'steals': player['STL'],
                    'blocks': player['BLK'],
                    'turnovers': player['TOV'],
                    'points': player['PTS']
                })
                    
    except Exception as e:
        print(f"NBA data insertion failed: {e}")

if __name__ == "__main__":
    try:
        engine = db_conn()
        nba_player_data_refresh(engine)
    except Exception as e:
        print(f"Connection or data insertion failed: {e}")