from restbucks import views

from django.conf import settings
from django.urls import path

from restbucks.views import Products, Orders


urlpatterns=[
    path('product', Products.as_view(), name='product_list'),
    path('order', Orders.as_view(), name='order_management')
]