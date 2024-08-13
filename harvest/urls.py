from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', view=views.home),
    path("complete-payment-form/", view=views.complete_payment_form, name="card-complete-payment-form"),
    path('shop/',views.shop, name="shop"),
    path("blog/",views.blog,name="blog"),
    path("single_product/",views.single_product,name="single_product")
]
