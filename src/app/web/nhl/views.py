from django.shortcuts import render
from django.template import loader

# Create your views here.
from django.http import HttpResponse
from nhl.models import PlayerData

def bruins(request):
    boston_players = PlayerData.objects.filter(team='BOS')
    template = loader.get_template("templates/nhl/hockey-teams/boston.html")
    context = {'players': boston_players}
    return HttpResponse(template.render(context, request))

def hockey_teams_menu(request):
    return HttpResponse("Pick a hockey team.")