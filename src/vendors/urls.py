from django.urls import path, include
from .views import (
	vendor_details,
	product_vendor_filter
	)



urlpatterns = [
    path('vendor/<int:id>/', vendor_details, name='vendor_details'),
    path('vendor/<int:id>/filter/product/', product_vendor_filter, name='product_vendor_filter'),
]
