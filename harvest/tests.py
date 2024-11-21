from django.test import TestCase
from .models import (
    User, Category, Product, Tag, Article, Order, OrderItem, Review, 
    Reply, Event, Inventory, Subscription, Notification, SearchQuery, Season
)
from datetime import date, timedelta
from django.utils.text import slugify


class ModelsTestCase(TestCase):

    def setUp(self):
        # Setting up data for the tests
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            phone_number="1234567890",
            role="Customer"
        )

        self.category = Category.objects.create(
            name="Fruits",
            description="Fresh and organic fruits",
            slug=slugify("Fruits")
        )

        self.season = Season.objects.create(
            name="Summer",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90)
        )

        self.product = Product.objects.create(
            name="Apple",
            description="A juicy red apple",
            category=self.category,
            price=1.50,
            quantity=10,
            slug=slugify("Apple"),
            season=self.season
        )

        self.tag = Tag.objects.create(
            name="Organic",
            slug=slugify("Organic")
        )

        self.article = Article.objects.create(
            title="The Benefits of Organic Foods",
            content="Organic foods are healthier and better for the environment.",
            author=self.user,
            slug=slugify("The Benefits of Organic Foods")
        )

        self.order = Order.objects.create(
            user=self.user,
            total_price=15.00,
            status="Pending",
            shipping_address="123 Main St, Springfield",
            payment_method="Credit Card"
        )

        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=5,
            price=7.50
        )

        self.review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment="Excellent product!"
        )

        self.reply = Reply.objects.create(
            review=self.review,
            user=self.user,
            comment="Thank you for the feedback!"
        )

        self.event = Event.objects.create(
            title="Farmers' Market",
            description="A great opportunity to buy fresh produce directly from farmers.",
            date=date.today() + timedelta(days=7),
            location="Downtown Park"
        )

        self.inventory = Inventory.objects.create(
            product=self.product,
            quantity_in_stock=50
        )

        self.subscription = Subscription.objects.create(
            user=self.user,
            subscription_type="Monthly",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )

        self.notification = Notification.objects.create(
            user=self.user,
            message="Your order has been shipped!"
        )

        self.search_query = SearchQuery.objects.create(
            query="Organic Apples"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.phone_number, "1234567890")
        self.assertEqual(self.user.role, "Customer")

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Fruits")
        self.assertEqual(self.category.slug, "fruits")

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Apple")
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.season, self.season)

    def test_tag_creation(self):
        self.assertEqual(self.tag.name, "Organic")

    def test_article_creation(self):
        self.assertEqual(self.article.title, "The Benefits of Organic Foods")
        self.assertEqual(self.article.author, self.user)

    def test_order_creation(self):
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.total_price, 15.00)
        self.assertEqual(self.order.status, "Pending")

    def test_order_item_creation(self):
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 5)

    def test_review_creation(self):
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.rating, 5)

    def test_reply_creation(self):
        self.assertEqual(self.reply.review, self.review)
        self.assertEqual(self.reply.user, self.user)
        self.assertEqual(self.reply.comment, "Thank you for the feedback!")

    def test_event_creation(self):
        self.assertEqual(self.event.title, "Farmers' Market")
        self.assertTrue(self.event.is_active)

    def test_inventory_creation(self):
        self.assertEqual(self.inventory.product, self.product)
        self.assertEqual(self.inventory.quantity_in_stock, 50)

    def test_subscription_creation(self):
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.subscription_type, "Monthly")
        self.assertTrue(self.subscription.is_active)

    def test_notification_creation(self):
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.message, "Your order has been shipped!")
        self.assertFalse(self.notification.is_read)

    def test_search_query_creation(self):
        self.assertEqual(self.search_query.query, "Organic Apples")
        self.assertEqual(self.search_query.search_count, 0)

    def test_season_creation(self):
        self.assertEqual(self.season.name, "Summer")
        self.assertEqual(self.season.start_date, date.today())
