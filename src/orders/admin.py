from django.contrib import admin
from .models import (
	Cart, 
	CartProduct, 
	DeliveryAddress, 
	Order, 
	OrderDeliveryInfo,
	VendorOrder,
	VendorOrderProduct,
	CancelOrder,
	BillingAddress
	)
# Register your models here.


admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(DeliveryAddress)

admin.site.register(Order)
admin.site.register(OrderDeliveryInfo)

admin.site.register(VendorOrder)
admin.site.register(VendorOrderProduct)
admin.site.register(CancelOrder)
admin.site.register(BillingAddress)


