from django.urls import path
from .views import (
	HomeView, 
	ProductDetailsView, 
	ProductCategoryDetailsView,
	ProductSubCategoryDetailsView,
	ProductInnerCategoryDetailsView,
	category_list_api_view,
	sub_category_list_api_view,
	daily_deals_api_view,
	verify_zip_code_api_view,
	sliders_api_view,
	ProductSearchView
	)

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('product/details/<int:pk>/', ProductDetailsView.as_view(), name='product_details'),
    path('product/cat/details/<int:pk>/', ProductCategoryDetailsView.as_view(), name='cat_details'),
    path('product/sub_cat/details/<int:pk>/', ProductSubCategoryDetailsView.as_view(), name='subcat_details'),
    path('product/inner_cat/details/<int:pk>/', ProductInnerCategoryDetailsView.as_view(), name='innercat_details'),
    path('product/category_list_api_view/', category_list_api_view, name='category_list_api_view'),
    path('product/sub_category_list_api_view/<int:id>/', sub_category_list_api_view, name='sub_category_list_api_view'),
    path('product/daily_deals_api_view/<int:min>/<int:max>/', daily_deals_api_view, name='daily_deals_api_view'),
    path('product/verify_zip_code_api_view/', verify_zip_code_api_view, name='verify_zip_code_api_view'),
    path('product/sliders_api_view/', sliders_api_view, name='sliders_api_view'),
    path('product/product_search_view/', ProductSearchView.as_view(), name='product_search_view'),
]

