from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def bruins(request):
    return HttpResponse("Hello, world. You are at the Bruins page.")

def hockey_teams_menu(request):
    return HttpResponse("Pick a hockey team.")