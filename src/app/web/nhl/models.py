from django.db import models

class ApiData(models.Model):
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=3) 
    position = models.CharField(max_length=2)
    games_played = models.IntegerField()
    points = models.IntegerField()
    goals = models.IntegerField()
    assists = models.IntegerField()
    shots = models.IntegerField()
    blocked_shots = models.IntegerField()
    toi = models.FloatField(help_text="Average time on ice per game in minutes")

class DkData(models.Model):
    salary = models.CharField(max_length=10, null=True, blank=True)
    ppg = models.FloatField(null=True, blank=True, help_text="Points per game")