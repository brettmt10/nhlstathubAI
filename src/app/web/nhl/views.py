from django.shortcuts import render
from django.template import loader

# Create your views here.
from django.http import HttpResponse
from nhl.models import PlayerData
from nhl.static import teams_abbrev
ta = teams_abbrev.teams_abbrev

def hockey_teams_menu(request):
    template = loader.get_template("templates/nhl/index.html")
    return HttpResponse(template.render(request=request))

def team_data(request, team_abbrev):
    players = PlayerData.objects.filter(team=str(team_abbrev))
    context = {'players': players, 'team_abbrev': str(team_abbrev), 'team_name': str(ta.get(str(team_abbrev)))}
    template = loader.get_template("templates/nhl/team_data.html")
    return HttpResponse(template.render(context, request))