from django.urls import path
from . import views

urlpatterns = [
    path("", views.hockey_teams_menu, name="hockey-menu"),
    path("<str:team_abbrev>/", views.team_data, name="team-data"),
]