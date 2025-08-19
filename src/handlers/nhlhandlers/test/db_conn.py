import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2
import os
from dotenv import load_dotenv
from api_handler_dev import NHLDataHandler
from team_info import teams

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

try:
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
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
                        "INSERT INTO raw.player_info (player_name, team_abbrev, position) VALUES (:name, :team, :pos)"
                    ), {
                        'name': player['player_name'],
                        'team': player['team_abbrev'], 
                        'pos': player['position']
                    })
        except Exception as team_error:
            print(f"Failed to process {team_abbrev}: {team_error}")
            continue
                
except Exception as e:
    print(f"Connection or data insertion failed: {e}")