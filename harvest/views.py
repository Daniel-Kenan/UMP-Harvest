from django.shortcuts import render
from django.http import HttpResponse
from .models import Category,Product, SearchQuery
from django.core.paginator import Paginator
from django.db.models import F
from django.utils import timezone
from django import template
from django.shortcuts import render, get_object_or_404
from decimal import Decimal

def calculate_discounted_price(price, discount):
    if not isinstance(price, Decimal):
        price = Decimal(price)
    if not isinstance(discount, Decimal):
        discount = Decimal(discount)
    
    if discount < 0 or discount > 100:
        raise ValueError("Discount must be between 0 and 100")

    discounted_price = price * (Decimal('1') - discount / Decimal('100'))
    return discounted_price.quantize(Decimal('0.01'))

def generate_stars(rating):
    # Number of stars to display
    total_stars = 5
    full_star_svg = '<svg width="18" height="18" class="text-warning"><use xlink:href="#star-full"></use></svg>'
    empty_star_svg = '<svg width="18" height="18" class="text-muted"><use xlink:href="#star-empty"></use></svg>'
    
    # Generate stars based on the rating
    stars = ''
    for i in range(total_stars):
        if i < rating:
            stars += full_star_svg
        else:
            stars += empty_star_svg
            
    return stars

def page(name): 
    return f"Pages/{name}.html"


# Utility function to get top 18 most searched items
def get_top_searches():
    return SearchQuery.objects.order_by('-search_count', '-last_searched')[:18]

def home(request):
    top_searches = get_top_searches()
    categories = Category.objects.all()
    best_selling_products = Product.objects.filter(is_best_selling=True) 
    return  render(request, page("Home"),{'categories': categories,'best_selling_products': best_selling_products, 'top_searches': top_searches,})

def complete_payment_form(request):
    return render(request , page("Card")) 

from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product

def single_product(request,id):
    top_searches = get_top_searches()
    product = get_object_or_404(Product, id=id)
    product.discountedPrice = calculate_discounted_price(product.price, product.discounted_price_percentage)
    product.isOnDiscount = bool( not (product.price == product.discountedPrice) )
    return render(request, page("SingleProduct"),{'product': product, "top_searches" : top_searches})

def SignIn(request):
    return render(request, "Auth/SignIn.html")
def SignUp(request):
    return render(request, "Auth/SignUp.html")

def blog(request):
    return render(request, page("Blog"))

def shop(request):
    # Get the search query, price range, and category
    search_query = request.GET.get('search', '')
    price_range = request.GET.get('price_range', '')
    category = request.GET.get('category', '')
    top_searches = get_top_searches()
    if search_query:
        # Check if the search query already exists
        search_entry, created = SearchQuery.objects.get_or_create(query=search_query)
        if not created:
            search_entry.search_count += 1
            search_entry.last_searched = timezone.now()
        search_entry.save()
    
    # Build the base query with search filter
    product_list = Product.objects.filter(name__icontains=search_query)

    # Apply price range filter if specified
    if price_range:
        price_bounds = price_range.split('-')
        if len(price_bounds) == 2:
            min_price = float(price_bounds[0].replace('$', ''))
            max_price = float(price_bounds[1].replace('$', ''))
            product_list = product_list.filter(discounted_price__gte=min_price, discounted_price__lte=max_price)

    # Apply category filter if specified
    if category:
        product_list = product_list.filter(category__name=category)

    
    # Order the product list randomly
    product_list = product_list.order_by('?')

    # Paginate the product list
    paginator = Paginator(product_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   
    # Fetch all categories for the sidebar
    categories = Category.objects.all()

    # Add star ratings to each product in the page_obj
    for product in page_obj.object_list:
        product.stars = generate_stars(product.rating)
        product.discountedPrice = calculate_discounted_price(product.price, product.discounted_price_percentage)
        product.isOnDiscount = bool( not (product.price == product.discountedPrice) )

    return render(request, page("Shop"), {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category,
        'top_searches': top_searches,
    })


from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

@never_cache
def clear_cache(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    cache.clear()
    return HttpResponse('Cache has been cleared')

