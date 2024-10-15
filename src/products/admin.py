from django.contrib import admin

from .models import (
	Category, 
	SubCategory, 
	ProductCategory, 
	ProductSize,
	ProductColor,
	Product,
	ProductImage,
	ProductReview,
	ProductWishList,
	ProductCommissionPercentage,
	RecentlyViewedProducts
)
# Register your models here.

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(ProductCategory)
admin.site.register(ProductSize)
admin.site.register(ProductColor)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductReview)
admin.site.register(ProductWishList)
admin.site.register(ProductCommissionPercentage)
admin.site.register(RecentlyViewedProducts)