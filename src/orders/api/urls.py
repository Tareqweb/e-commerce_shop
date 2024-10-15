from django.urls import path, include
from .views import (
	add_to_cart, 
	remove_form_cart, 
	cart_products_api,
	delivery_info_api,
	delivery_info_save_api,
	shipping_method_api,
	add_shipping_method,
	create_order_api,
	)

urlpatterns = [
    path('add_to_cart/', add_to_cart, name="api-add_to_cart"),
    path('remove_form_cart/<int:id>/<int:cart_id>/', remove_form_cart, name="api-remove_form_cart"),
    path('cart_products_api/<int:id>/', cart_products_api, name="api_cart_products_api"),
    path('delivery_info_api/<int:cart>/', delivery_info_api, name="delivery_info_api"),
    path('delivery_info_save_api/<int:cart>/', delivery_info_save_api, name="delivery_info_save_api"),
    path('shipping_method_api/<int:cart>/', shipping_method_api, name="shipping_method_api"),
    path('add_shipping_method/<int:cart>/', add_shipping_method, name="add_shipping_method"),
    path('create_order_api/<int:cart>/', create_order_api, name="create_order_api"),

]