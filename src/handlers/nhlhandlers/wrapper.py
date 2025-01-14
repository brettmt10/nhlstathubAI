from nhlhandlers.data_merger import DataMerger
from typing import Optional

class NHLData(DataMerger):
    """User scoped wrapper class to fetch essential data.
    NHL Schedule automatically builds in proper class. No need to instantiate anything manually.

    Args:
        DataMerger: DataMerger class - merges and finalizes data.
        Inherited to create wrapper functions around finalized data.
    """
    def __init__(self, date: Optional[str] = None):
        super().__init__(date=date)
    
    def get_db_data(self) -> None:
        """Get player model instance
        """
        return self.player_data_model()
    
    