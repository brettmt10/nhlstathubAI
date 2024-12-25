from django.db import models

class ApiData(models.Model):
    name = models.CharField(max_length=100, null=True)
    team = models.CharField(max_length=3, null=True) 
    position = models.CharField(max_length=2, null=True)
    games_played = models.IntegerField(null=True)
    points = models.IntegerField(null=True)
    goals = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    shots = models.IntegerField(null=True)
    blocked_shots = models.IntegerField(null=True)
    toi = models.FloatField(null=True, help_text="Average time on ice per game in minutes")
    
    def __str__(self):
        return self.name

class PlayerData(models.Model):
    player_data = models.ForeignKey(ApiData, on_delete=models.CASCADE, null=True)
    salary = models.CharField(max_length=10, null=True, blank=True)
    ppg = models.FloatField(null=True, blank=True, help_text="Points per game")
    
    def __str__(self):
        return self.salary