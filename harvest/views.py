from django.shortcuts import render
from django.http import HttpResponse
from .models import Category,Product
from django.core.paginator import Paginator

def page(name): 
    return f"Pages/{name}.html"

def home(request):
    categories = Category.objects.all()
    best_selling_products = Product.objects.filter(is_best_selling=True) 
    return  render(request, page("Home"),{'categories': categories,'best_selling_products': best_selling_products})

def complete_payment_form(request):
    return render(request , page("Card")) 

def shop(request):
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, page("Shop"),{'page_obj': page_obj})

def single_product(request):
    return render(request, page("SingleProduct"))

def blog(request):
    return render(request, page("Blog"))
