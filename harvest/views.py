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

from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product

def shop(request):
    # Get the search query
    search_query = request.GET.get('search', '')

    # Get the price range
    price_range = request.GET.get('price_range', '')
    
    # Build the base query
    product_list = Product.objects.filter(name__icontains=search_query)
    
    # Apply price range filter if specified
    if price_range:
        price_bounds = price_range.split('-')
        if len(price_bounds) == 2:
            min_price = float(price_bounds[0].replace('R', ''))
            max_price = float(price_bounds[1].replace('R', ''))
            product_list = product_list.filter(discounted_price__gte=min_price, discounted_price__lte=max_price)
    
    # Paginate the product list
    paginator = Paginator(product_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, page("Shop"), {'page_obj': page_obj})


def single_product(request):
    return render(request, page("SingleProduct"))

def blog(request):
    return render(request, page("Blog"))
