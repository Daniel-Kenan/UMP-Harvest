from django.shortcuts import render
from django.http import HttpResponse
from .models import Category,Product, SearchQuery,Season
from django.core.paginator import Paginator
from django.db.models import F
from django.utils import timezone
from django import template
from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
from django.conf import settings
from .gateway import PayfastPayment
from . import wiki

from allauth.socialaccount.models import SocialApp
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def anonymous_required(function=None, redirect_url=None):
    if not redirect_url:
        redirect_url = '/'

    actual_decorator = user_passes_test(
        lambda u: not u.is_authenticated,
        login_url=redirect_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


# # List all Google OAuth apps
# apps = SocialApp.objects.filter(provider='google')
# for app in apps:
#     print(app)  # Review the entries

# # Delete duplicates if necessary
# SocialApp.objects.filter(provider='google').exclude(pk=1).delete()


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
    return SearchQuery.objects.order_by('-search_count', '-last_searched')[:24]

from datetime import date

def get_current_season():
    today = date.today()
    try:
        season = Season.objects.get(start_date__lte=today, end_date__gte=today)
    except Season.DoesNotExist:
        season = None
    return season

def home(request):
    top_searches = get_top_searches()
    categories = Category.objects.all()

    # Fetch best selling products
    best_selling_products = Product.objects.filter(is_best_selling=True).order_by('?')[:4]
    for product in best_selling_products:
        product.stars = generate_stars(product.rating)
        product.discountedPrice = calculate_discounted_price(product.price, product.discounted_price_percentage)
        product.isOnDiscount = bool(product.price != product.discountedPrice)

    # Fetch just arrived products using 'created_at'
    just_arrived_products = Product.objects.filter(is_available=True).order_by('-created_at')[:4]
    for product in just_arrived_products:
        product.stars = generate_stars(product.rating)
        product.discountedPrice = calculate_discounted_price(product.price, product.discounted_price_percentage)
        product.isOnDiscount = bool(product.price != product.discountedPrice)

    # Fetch seasonal products
    current_season = get_current_season()
    if current_season:
        seasonal_products = Product.objects.filter(season=current_season).order_by('?')[:4]
    else:
        seasonal_products = Product.objects.none()  # Empty queryset if no season

    # If no seasonal products, fetch featured products
    if not seasonal_products.exists():
        seasonal_products = Product.objects.filter(is_featured=True).order_by('?')[:4]

    for product in seasonal_products:
        product.stars = generate_stars(product.rating)
        product.discountedPrice = calculate_discounted_price(product.price, product.discounted_price_percentage)
        product.isOnDiscount = bool(product.price != product.discountedPrice)

    isAuthenticated = request.user.is_authenticated
    return render(request, page("Home"), {
        'categories': categories,
        'best_selling_products': best_selling_products,
        'just_arrived_products': just_arrived_products,
        'seasonal_products': seasonal_products,
        'top_searches': top_searches,
        "isAuthenticated": isAuthenticated
    })



def complete_payment_form(request):
    data = {
    # Merchant details
    'merchant_id': settings.GATEWAY_CONFIG['merchant_id'],
    'merchant_key':settings.GATEWAY_CONFIG['merchant_key'],
    'return_url': settings.GATEWAY_REDIRECT_SITE+"payment-successful/",
    'cancel_url': settings.GATEWAY_REDIRECT_SITE+"payment-failed/",
    'notify_url': 'https://www.nextgensell.com/err',
    # Buyer details
    'name_first': 'Firstname',
    'name_last': 'Lastname',
    'email_address': 'sdanielkenan@gmail.com',
    # Transaction details
    'm_payment_id': '3454', #Unique payment ID to pass through to notify_url
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
    reviews = product.reviews.all()
    product.discountedPrice = calculate_discounted_price(product.price, product.discounted_price_percentage)
    product.isOnDiscount = bool( not (product.price == product.discountedPrice) )
    product.summary, product.wiki_image = wiki.search_object_history(str(product.name))
    return render(request, page("SingleProduct"),{'product': product, "top_searches" : top_searches,'reviews': reviews})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages

@anonymous_required(redirect_url='/')
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


        # Create user
@anonymous_required(redirect_url='/')
def SignUp(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeat_password')

        if not username or not password:
            messages.error(request, "Username and password are required")
            return redirect("signup")  # Redirect to SignUp page

        if password != repeat_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Email is already in use")
            return redirect("signup")

        try:
            user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=make_password(password),
                email=username,
                phone_number=phone_number,
                is_active=True,
            )
            user.full_clean()
            user.save()
            messages.success(request, "Account created successfully! Please sign in.")
            return redirect("signin")
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect("signup")
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


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Review

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment
        )
        return redirect('single_product', product.id)
    

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Review, Reply

from django.shortcuts import get_object_or_404, redirect
from .models import Review, Reply
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

@login_required
def add_reply(request, review_id):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        comment = request.POST.get('comment')
        new_reply = Reply(
            review=review,
            user=request.user,
            comment=comment
        )
        new_reply.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous page or home
    return HttpResponseRedirect('/')



# from django.shortcuts import render
# from django.http import JsonResponse
# from django.utils import timezone
# from django.db import models  # Import models to use aggregation functions
# from .models import Order, Review

# def admin_cards(request):
#     # Get the current date and time
#     now = timezone.now()
    
#     # Calculate start times
#     start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
#     start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#     start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

#     # Filter orders and calculate revenue for today
#     orders_today = Order.objects.filter(created_at__gte=start_of_today)
#     revenue_today = orders_today.aggregate(total_revenue=models.Sum('total_price'))['total_revenue'] or 0

#     # Filter orders and calculate revenue for this month
#     orders_this_month = Order.objects.filter(created_at__gte=start_of_month)
#     revenue_this_month = orders_this_month.aggregate(total_revenue=models.Sum('total_price'))['total_revenue'] or 0

#     # Filter orders and calculate revenue for this year
#     orders_this_year = Order.objects.filter(created_at__gte=start_of_year)
#     revenue_this_year = orders_this_year.aggregate(total_revenue=models.Sum('total_price'))['total_revenue'] or 0

#     # Filter reviews for today, this month, and this year
#     reviews_today = Review.objects.filter(created_at__gte=start_of_today).count()
#     reviews_this_month = Review.objects.filter(created_at__gte=start_of_month).count()
#     reviews_this_year = Review.objects.filter(created_at__gte=start_of_year).count()

#     # Prepare the response data with nested structure
#     data = {
#         "orders": {
#             "today": orders_today.count(),
#             "this_month": orders_this_month.count(),
#             "this_year": orders_this_year.count(),
#         },
#         "revenue": {
#             "today": revenue_today,
#             "this_month": revenue_this_month,
#             "this_year": revenue_this_year,
#         },
#         "reviews": {
#             "today": reviews_today,
#             "this_month": reviews_this_month,
#             "this_year": reviews_this_year,
#         }
#     }

#     # Return a JSON response
#     return JsonResponse(data)


from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db import models  # Import models to use aggregation functions
from .models import Order, Review
from datetime import timedelta

def calculate_percentage_change(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100

def admin_cards(request):
    # Get the current date and time
    now = timezone.now()
    
    # Calculate start times
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_yesterday = start_of_today - timedelta(days=1)
    
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_last_month = (start_of_month - timedelta(days=1)).replace(day=1)
    
    start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_last_year = start_of_year.replace(year=start_of_year.year - 1)

    # Orders and Revenue for today and yesterday
    orders_today = Order.objects.filter(created_at__gte=start_of_today)
    revenue_today = orders_today.aggregate(total_revenue=models.Sum('total_price'))['total_revenue'] or 0
    
    orders_yesterday = Order.objects.filter(created_at__gte=start_of_yesterday, created_at__lt=start_of_today)
    revenue_yesterday = orders_yesterday.aggregate(total_revenue=models.Sum('total_price'))['total_revenue'] or 0

    # Orders and Revenue for this month and last month
    orders_this_month = Order.objects.filter(created_at__gte=start_of_month)
    revenue_this_month = orders_this_month.aggregate(total_revenue=models.Sum('total_price'))['total_revenue'] or 0
    
    orders_last_month = Order.objects.filter(created_at__gte=start_of_last_month, created_at__lt=start_of_month)
    revenue_last_month = orders_last_month.aggregate(total_revenue=models.Sum('total_price'))['total_revenue'] or 0

    # Orders and Revenue for this year and last year
    orders_this_year = Order.objects.filter(created_at__gte=start_of_year)
    revenue_this_year = orders_this_year.aggregate(total_revenue=models.Sum('total_price'))['total_revenue'] or 0
    
    orders_last_year = Order.objects.filter(created_at__gte=start_of_last_year, created_at__lt=start_of_year)
    revenue_last_year = orders_last_year.aggregate(total_revenue=models.Sum('total_price'))['total_revenue'] or 0

    # Reviews for today, this month, and this year
    reviews_today = Review.objects.filter(created_at__gte=start_of_today).count()
    reviews_yesterday = Review.objects.filter(created_at__gte=start_of_yesterday, created_at__lt=start_of_today).count()
    
    reviews_this_month = Review.objects.filter(created_at__gte=start_of_month).count()
    reviews_last_month = Review.objects.filter(created_at__gte=start_of_last_month, created_at__lt=start_of_month).count()
    
    reviews_this_year = Review.objects.filter(created_at__gte=start_of_year).count()
    reviews_last_year = Review.objects.filter(created_at__gte=start_of_last_year, created_at__lt=start_of_year).count()

    # Calculate percentage changes
    orders_percentage_change_today = calculate_percentage_change(orders_today.count(), orders_yesterday.count())
    orders_percentage_change_month = calculate_percentage_change(orders_this_month.count(), orders_last_month.count())
    orders_percentage_change_year = calculate_percentage_change(orders_this_year.count(), orders_last_year.count())

    revenue_percentage_change_today = calculate_percentage_change(revenue_today, revenue_yesterday)
    revenue_percentage_change_month = calculate_percentage_change(revenue_this_month, revenue_last_month)
    revenue_percentage_change_year = calculate_percentage_change(revenue_this_year, revenue_last_year)

    reviews_percentage_change_today = calculate_percentage_change(reviews_today, reviews_yesterday)
    reviews_percentage_change_month = calculate_percentage_change(reviews_this_month, reviews_last_month)
    reviews_percentage_change_year = calculate_percentage_change(reviews_this_year, reviews_last_year)

    # Prepare the response data with nested structure
    data = {
        "orders": {
            "today": orders_today.count(),
            "this_month": orders_this_month.count(),
            "this_year": orders_this_year.count(),
            "percentage_change": {
                "today": orders_percentage_change_today,
                "this_month": orders_percentage_change_month,
                "this_year": orders_percentage_change_year,
            }
        },
        "revenue": {
            "today": revenue_today,
            "this_month": revenue_this_month,
            "this_year": revenue_this_year,
            "percentage_change": {
                "today": revenue_percentage_change_today,
                "this_month": revenue_percentage_change_month,
                "this_year": revenue_percentage_change_year,
            }
        },
        "reviews": {
            "today": reviews_today,
            "this_month": reviews_this_month,
            "this_year": reviews_this_year,
            "percentage_change": {
                "today": reviews_percentage_change_today,
                "this_month": reviews_percentage_change_month,
                "this_year": reviews_percentage_change_year,
            }
        }
    }

    # Return a JSON response
    return JsonResponse(data)



def intelli(request):
    return render(request, page("Intelli"))

def profile(request):
    return render(request, page("Profile"))


from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'  # Optional: Customize the password reset form
    email_template_name = 'registration/password_reset_email.html'  # Your custom email template
    success_url = reverse_lazy('password_reset_done')  # Redirect after successful email send
