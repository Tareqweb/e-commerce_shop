from django.urls import path, include
from .views import (
	cart, 
	update_cart_qty, 
	add_to_cart, 
	remove_form_cart, 
	delivery_info,
	# order_summery_and_payment,
	create_shipping_details,
	add_shipping_method,
	shipping_method,
	# create_order,
	remove_form_cart_by_id,
	apply_promo_code,
	remove_promo_code,
	PayPalCheckOutView,
	order_success,
	order_failed,
	order_tracking,
	order_confirm_recived,
	product_review,
	cancel_order_form
	)


urlpatterns = [
    path('order/remove_form_cart/<int:id>/', remove_form_cart, name='remove_form_cart'),
    path('order/add_to_cart/', add_to_cart, name='add_to_cart'),
    path('order/cart/', cart, name='cart'),
    # path('order/payment-and-order-confirmation/', order_summery_and_payment, name='order_summery_and_payment'),
    path('order/shipping-info/', delivery_info, name='delivery_info'),
    path('order/update_cart_qty/', update_cart_qty, name='update_cart_qty'),
    path('order/create_shipping_details/', create_shipping_details, name='create_shipping_details'),
    path('order/shipping-method/', shipping_method, name='shipping_method'),
    path('order/add_shipping_method/', add_shipping_method, name='add_shipping_method'),
    # path('order/create_order/cart/<int:cart_id>/', create_order, name='create_order'),
    path('order/remove_form_cart_by_id/<int:id>/', remove_form_cart_by_id, name='remove_form_cart_by_id'),
    path('order/apply_promo_code/', apply_promo_code, name='apply_promo_code'),
    path('order/remove_promo_code/', remove_promo_code, name='remove_promo_code'),
    path('order/payment-and-order-confirmation/', PayPalCheckOutView.as_view(), name='order_summery_and_payment'),
    path('order/order-success/<int:id>/', order_success, name='order_success'),
    path('order/order-failed/', order_failed, name='order_failed'),
    path('order/order-tracking/', order_tracking, name='order_tracking'),
    path('order/order-confirm-recived/<int:id>/', order_confirm_recived, name='order_confirm_recived'),
    path('order/product_review/<int:id>/', product_review, name='product_review'),
    path('order/cancel_order_form/<int:id>/', cancel_order_form, name='cancel_order_form'),
]

