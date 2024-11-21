from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
# Custom User model to handle different roles and additional fields
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import json
import requests

class Season(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name
    
class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=50, choices=[('Customer', 'Customer'), ('Admin', 'Admin'), ('Farmer', 'Farmer')], default='Customer')
    is_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name='harvest_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='harvest_user_permissions_set', blank=True)
    
    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price_percentage = models.IntegerField(default=0)
    quantity = models.IntegerField()
    image = models.URLField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    slug = models.SlugField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(default=0)
    is_best_selling = models.BooleanField(default=False)
    review_count = models.IntegerField(default=0)
    season = models.ForeignKey(Season, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)

    def upload_image_to_server(self, file, folder='public'):
        """Upload image to the external server and update the `image` field."""
        url = 'https://media.nextgensell.com/files/upload'
        files = {'file': file}
        data = {'folder': folder}

        try:
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            result = response.json()
            if 'access_url' in result:
                self.image = result['access_url']
                self.save()
            return result
        except Exception as e:
            raise Exception(f"Error uploading file: {e}")

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, related_name='articles', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.URLField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, unique=True)
    tags = models.ManyToManyField(Tag, related_name='articles')
    
    def __str__(self):
        return self.title

class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')], default='Pending')
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=50, choices=[('Credit Card', 'Credit Card'), ('PayPal', 'PayPal'), ('Cash on Delivery', 'Cash on Delivery')], default='Credit Card')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
    def get_orders_summary(self):
        today = timezone.now().date()
        start_of_week = today - timezone.timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)

        # Filtering orders
        today_orders = self.__class__.objects.filter(created_at__date=today)
        week_orders = self.__class__.objects.filter(created_at__date__gte=start_of_week)
        month_orders = self.__class__.objects.filter(created_at__date__gte=start_of_month)

        # Helper function to extract product details
        def get_order_products(orders):
            return [
                {
                'order_id': order.id,
                'products': list(order.items.values('product__name', 'quantity', 'price'))
                }
            for order in orders]

            # Creating the JSON structure
        summary = {
                'today': get_order_products(today_orders),
                'week': get_order_products(week_orders),
                'this_month': get_order_products(month_orders)
                }

        return json.dumps(summary)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Review(models.Model):
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"


class Reply(models.Model):
    review = models.ForeignKey(Review, related_name='replies', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - Reply to {self.review.user.username}'
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=200)
    image = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Inventory(models.Model):
    product = models.OneToOneField(Product, related_name='inventory', on_delete=models.CASCADE)
    quantity_in_stock = models.IntegerField()
    restock_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Inventory for {self.product.name}"

class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='subscriptions', on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=50, choices=[('Monthly', 'Monthly'), ('Yearly', 'Yearly')], default='Monthly')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.subscription_type} Subscription for {self.user.username}"

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}"


class SearchQuery(models.Model):
    query = models.CharField(max_length=255)
    search_count = models.PositiveIntegerField(default=0)
    last_searched = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.query