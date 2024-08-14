from django.contrib import admin
from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', view=views.home),
    path("complete-payment-form/", view=views.complete_payment_form, name="card-complete-payment-form"),
    path('shop/',views.shop, name="shop"),
    path("blog/",views.blog,name="blog"),
    path("single_product/",views.single_product,name="single_product"), 
    path('manifest.json', TemplateView.as_view(template_name='PWA/manifest.json', content_type='application/json')),
    path('service-worker.js', TemplateView.as_view(template_name='PWA/service-worker.js', content_type='application/javascript')),
]
