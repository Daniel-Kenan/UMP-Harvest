from django.shortcuts import render
from django.http import HttpResponse

def page(name):return f"Pages/{name}.html"

def home(request):
    return  render(request, page("Home"))

def complete_payment_form(request):
    return render(request , page("Card")) 

def shop(request):
    return render(request, page("Shop"))

def single_product(request):
    return render(request, page("SingleProduct"))

def blog(request):
    return render(request, page("Blog"))
