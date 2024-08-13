from django.shortcuts import render
from django.http import HttpResponse
from .models import Category,Product
def page(name): 
    return f"Pages/{name}.html"

def home(request):
    categories = Category.objects.all()
    best_selling_products = Product.objects.filter(is_best_selling=True) 
    return  render(request, page("Home"),{'categories': categories,'best_selling_products': best_selling_products})

def complete_payment_form(request):
    return render(request , page("Card")) 

def shop(request):
    return render(request, page("Shop"))

def single_product(request):
    return render(request, page("SingleProduct"))

def blog(request):
    return render(request, page("Blog"))
