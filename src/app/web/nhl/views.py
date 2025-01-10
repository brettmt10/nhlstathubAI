from django.shortcuts import render
from django.template import loader

# Create your views here.
from django.http import HttpResponse
from nhl.models import PlayerData

def hockey_teams_menu(request):
    template = loader.get_template("templates/nhl/hockey-teams/index.html")
    return HttpResponse(template.render(request=request))

def team_data(request, team_abbrev):
    print(team_abbrev)
    players = PlayerData.objects.filter(team=str(team_abbrev))
    context = {'players': players}
    template = loader.get_template("templates/nhl/hockey-teams/team_data.html")
    return HttpResponse(template.render(context, request))