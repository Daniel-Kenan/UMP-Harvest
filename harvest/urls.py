from django.contrib import admin
from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', view=views.home,name="home"),
    path("complete-payment-form/", view=views.complete_payment_form, name="card-complete-payment-form"),
    path('shop/',views.shop, name="shop"),
    path('signin/',views.SignIn, name="signin"),
    path('signup/',views.SignUp, name="signup"),
    path("blog/",views.blog,name="blog"),
    path('product/<int:id>/', views.single_product, name='single_product'),
    path('manifest.json', TemplateView.as_view(template_name='PWA/manifest.json', content_type='application/json')),
    path('service-worker.js', TemplateView.as_view(template_name='PWA/service-worker.js', content_type='application/javascript')),
    path('clear_cache/', views.clear_cache),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/', views.cart_data, name='cart_data'),
    path("payment-tranfer/", views.bank_payment_transfer, name='bank_payment_transfer'),
    path("dashboard/", views.dashboard, name='dashboard'),
    path('logs/', views.list_logs, name='list_logs'),
    path('logs/<str:filename>/', views.view_log, name='view_log'),
]
