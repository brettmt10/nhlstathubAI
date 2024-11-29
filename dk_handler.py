import requests
import pandas as pd

class DraftKingsDataHandler:
    def get_contests(self) -> dict:
        """Gets the data attributes of the daily contests. Fetching this to get the daily
            draft group of available players.

        Returns:
            dict: a dictionary, with each contest and its attributes
        """
        response: requests.Response = requests.get('https://www.draftkings.com/lobby/getcontests?sport=NHL')
        return response.json()

    def get_daily_draft_group(self) -> int:
        """Grabs the draft group for daily available players

        Returns:
            int: draft group number
        """
        data: dict = self.get_contests()
        dg: int = data.get("Contests")[0].get('dg')
        return dg
    
    def get_available_player_salaries(self) -> pd.DataFrame:
        """With the draft group, downloads a csv of player data.

        Returns:
            pd.DataFrame: Name and salary (cost) of each available player
        """
        dg: int = self.get_daily_draft_group()
        url: str = f'https://www.draftkings.com/lineup/getavailableplayerscsv?contestTypeId=125&draftGroupId={dg}'
        response: requests.Response = requests.get(url)
        df: pd.DataFrame = pd.read_csv(pd.io.common.StringIO(response.text), usecols=['Name', 'Salary', 'TeamAbbrev'])
        return df
    
    def available_player_salaries(self) -> pd.DataFrame:
        """User function to get the finalized draftkings salary data

        Returns:
            pd.DataFrame: dataframe containing each available draftable player and their draftkings salary
        """
        
        data = self.get_available_player_salaries()
        return data