from django.core.management.base import BaseCommand
from nhlhandlers.wrapper import NHLData
from nhl.models import PlayerData

class Command(BaseCommand):
    help = 'Updates database with new player data from previous game slate.'
    
    def handle(self, *args, **options):
        try:
            PlayerData.objects.all().delete()
            d = NHLData()
            all_players = d.get_db_data()
            
            for player in all_players:
                
                p = PlayerData(name = player["name"],
                            team=player["team"],
                            position=player["position"],
                            games_played=player["games_played"],
                            points=player["points"],
                            goals=player["goals"],
                            assists=player["assists"],
                            shots=player["shots"],
                            blocked_shots=player["blocked_shots"], 
                            toi=player["toi"],
                            salary=player["salary"],
                            ppg=player["ppg"])
        
                p.save()
                
            print("got all the players for today!")
        except Exception as e:
            print(e)



