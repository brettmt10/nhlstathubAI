from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def bruins(request):
    return HttpResponse("Hello, world. You are at the Bruins page.")

def front_page(request):
    return HttpResponse("Welcome! Pick a hockey team.")