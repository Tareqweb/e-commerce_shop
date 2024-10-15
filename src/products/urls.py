from django.urls import path, include
from .views import (
	product_details, 
	category_details, 
	sub_category_details, 
	product_category_details,
	add_to_wishlist,
	remove_from_wishlist,
	search_product,
	product_global_filter,
	daily_deals,
	check_zip_code
	)



urlpatterns = [
    path('product/<slug:slug>/', product_details, name='product_details'),
    path('product/category/<slug:slug>/', category_details, name='category_details'),
    path('product/subcategory/<slug:slug>/', sub_category_details, name='sub_category_details'),
    path('product/product-category/<slug:slug>/', product_category_details, name='product_category_details'),
    path('product/add_to_wishlist/<int:id>/', add_to_wishlist, name='add_to_wishlist'),
    path('product/remove_from_wishlist/<int:id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('search/products/', search_product, name='search_product'),
    path('filter/product/', product_global_filter, name='product_global_filter'),
    path('daily-deals/', daily_deals, name='daily_deals'),
    path('check_zip_code/<zipcode>/', check_zip_code, name='check_zip_code'),
]
