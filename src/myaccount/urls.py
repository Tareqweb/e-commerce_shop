from django.urls import path, include
from .views import (
	order_history, 
	order_details_modal, 
	product_wish_list, 
	shipping_address,
	change_password_view
	)



urlpatterns = [
    path('myaccount/address/', shipping_address, name='shipping_address'),
    path('myaccount/wishlist/', product_wish_list, name='product_wish_list'),
    path('myaccount/order-history/', order_history, name='order_history'),
    path('myaccount/change-password-view/', change_password_view, name='change_password_view'),
    path('myaccount/<int:id>/order_details_modal/', order_details_modal, name='order_details'),
]
