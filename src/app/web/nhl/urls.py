from django.urls import path

from . import views

urlpatterns = [
    path("", views.hockey_teams_menu, name="hockey menu"),
    path("bruins", views.bruins, name="bruins page"),
]