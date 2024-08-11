from django.shortcuts import render
from django.http import HttpResponse

def page(name):return f"Pages/{name}.html"

def home(request):
    return  render(request, page("Home"))
