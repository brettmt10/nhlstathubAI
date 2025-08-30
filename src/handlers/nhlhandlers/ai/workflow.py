import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from db_conn import NHLConnHandler

def engine_connect():
    load_dotenv()

    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')  
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    return engine

def nhl_refresh(handler: NHLConnHandler):
    handler.truncate_tables()
    handler.player_info_refresh()
    handler.team_player_data_refresh()
    
engine = engine_connect()
nhl = NHLConnHandler(engine = engine)
nhl_refresh(nhl)


# nba = NBAConnHandler(engine = engine)

