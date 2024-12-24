from django.urls import path

from . import views

urlpatterns = [
    path("", views.front_page, name="poop"),
    path("bruins", views.bruins, name="index"),
]