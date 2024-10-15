from django.contrib import admin

from .models import (
	FreeShippingSettings, 
	GroceryShippingArea, 
	ProductSlider, 
	CouponCode,
	MobileApps,
	AboutUs,
	ContactUs,
	FAQ,
	PrivacyPolicy,
	TermsOfUse,
	RefundReturnPolicy,
	VendorPaymentRelease,
	ShippingPriceSettings
	)

# Register your models here.


admin.site.register(FreeShippingSettings)
admin.site.register(GroceryShippingArea)
admin.site.register(ProductSlider)

admin.site.register(MobileApps)
admin.site.register(AboutUs)
admin.site.register(ContactUs)
admin.site.register(FAQ)
admin.site.register(PrivacyPolicy)
admin.site.register(RefundReturnPolicy)
admin.site.register(VendorPaymentRelease)
admin.site.register(ShippingPriceSettings)

