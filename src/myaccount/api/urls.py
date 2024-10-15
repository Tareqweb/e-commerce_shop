from django.urls import path, include
from .views import (
	get_order_history,
	get_order_details,
	get_product_wishlist,
	change_password_api_view,
	delivery_address_api,
	delivery_address_save_api,
	add_to_wishlist_api,
	remove_from_wishlist_api,

	)

urlpatterns = [
    path('get_order_history/', get_order_history, name="get_order_history"),
    path('get_order_details/<int:id>/', get_order_details, name="get_order_details"),
    path('get_product_wishlist/', get_product_wishlist, name="get_product_wishlist"),
    path('change_password_api_view/', change_password_api_view, name="change_password_api_view"),
    path('delivery_address_api/', delivery_address_api, name="delivery_address_api"),
    path('delivery_address_save_api/', delivery_address_save_api, name="delivery_address_save_api"),
    path('add_to_wishlist_api/<id>/', add_to_wishlist_api, name="add_to_wishlist_api"),
    path('remove_from_wishlist_api/<id>/', remove_from_wishlist_api, name="remove_from_wishlist_api"),
    
]