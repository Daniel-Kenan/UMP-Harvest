from django.shortcuts import render
from django.http import HttpResponse
from .models import Category,Product, SearchQuery
from django.core.paginator import Paginator
from django.db.models import F
from django.utils import timezone
from django import template
from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
from django.conf import settings
from .gateway import PayfastPayment
from . import wiki

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
    data = {
    # Merchant details
    'merchant_id': settings.GATEWAY_CONFIG['merchant_id'],
    'merchant_key':settings.GATEWAY_CONFIG['merchant_key'],
    'return_url': settings.GATEWAY_REDIRECT_SITE+"payment-successful/",
    'cancel_url': settings.GATEWAY_REDIRECT_SITE+"payment-failed/",
    'notify_url': 'https://www.nextgensell.com/err',
    # Buyer details
    'name_first': 'First Name',
    'name_last': 'Last Name',
    'email_address': 'test@test.com',
    # Transaction details
    'm_payment_id': '1234', #Unique payment ID to pass through to notify_url
    'amount': "200",
    'item_name': 'Order#123'}
    payfast_payment = PayfastPayment(data,settings.GATEWAY_CONFIG['passphrase'],sandbox_mode=settings.GATEWAY_CONFIG['mode'])
    html_form = payfast_payment.generate_html_form()
    return render(request , page("Card"),{"html_form":html_form}) 

from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product

def single_product(request,id):
    top_searches = get_top_searches()
    product = get_object_or_404(Product, id=id)
    product.discountedPrice = calculate_discounted_price(product.price, product.discounted_price_percentage)
    product.isOnDiscount = bool( not (product.price == product.discountedPrice) )
    product.summary, product.wiki_image = wiki.search_object_history(str(product.name))
    return render(request, page("SingleProduct"),{'product': product, "top_searches" : top_searches})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages

def SignIn(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
            print(f'User exists: {user.username}')

        except User.DoesNotExist:
            print('User does not exist')
            user = None

        if user and user.check_password(password):
            print('Password is correct')
            # Authenticate manually
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print(("passed"))
                return redirect('home')
            else:
                messages.error(request, 'Authentication failed.')
        else:
            messages.error(request, 'Invalid username or password.')
     
    return render(request, "Auth/SignIn.html")

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from .models import User

def SignUp(request):
    
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')

        if not username or not password:
            return HttpResponse("Username and password are required", status=400)

        # Create user
        try:
            user = User(
                username=username,
                password=make_password(password),  # Hash the password
                is_active=True
            )
            user.save()
            login(request, user,backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')  # Redirect to a success page
        except ValidationError as e:
            return HttpResponse(f"Error: {e}", status=400)
    
        
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


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product,User
import json

@csrf_exempt
def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data['product_id']
        product_name = data['product_name']
        product_price = data['product_price']
        quantity = data.get('quantity', 1)

        cart = request.session.get('cart', {})
        print(cart)
        if product_id in cart:
            cart[product_id]['quantity'] += quantity
        else:
            cart[product_id] = {
                'name': product_name,
                'price': product_price,
                'quantity': quantity
            }

        request.session['cart'] = cart

        return JsonResponse({'cart_item_count': len(cart)}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)



def view_cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('view_cart')


from django.http import JsonResponse
@csrf_exempt
def cart_data(request):
    if request.method == 'GET':
        cart = request.session.get('cart', {})
        
        # Ensure that 'cart' contains numerical values
        for item in cart.values():
            item['price'] = float(item.get('price', 0))
            item['quantity'] = int(item.get('quantity', 0))

        total_price = sum(item['price'] * item['quantity'] for item in cart.values())

        response_data = {
            'cart': [{'name': item['name'], 'price': item['price'], 'quantity': item['quantity']} for item in cart.values()],
            'total_price': total_price,
        }

        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request method'}, status=400)



# print(html_form)

def testpage(request):
    return render(request, 'testpage.html',{'form':html_form})


def bank_payment_transfer(request):
    return render(request, page("BankTransfer"))


from django.shortcuts import render, redirect
from django.http import Http404

def dashboard(request):
    if request.user.is_staff:  # Check if the user is an admin
        return render(request, 'admin/dashboard.html')
    else:
        raise Http404("Page not found")
    
from django.shortcuts import render
from django.conf import settings
import os

def list_logs(request):
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    log_files = [f for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))]
    return render(request, 'list_logs.html', {'log_files': log_files})

def view_log(request, filename):
    log_file_path = os.path.join(settings.BASE_DIR, 'logs', filename)
    try:
        with open(log_file_path, 'r') as file:
            log_content = file.read()
    except FileNotFoundError:
        log_content = "Log file not found."
    except Exception as e:
        log_content = f"An error occurred while reading the log file: {str(e)}"
    
    return render(request, 'view_log.html', {'log_content': log_content, 'filename': filename})


