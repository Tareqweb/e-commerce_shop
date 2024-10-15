from django import forms
from django.forms import ModelForm, inlineformset_factory, TextInput, RadioSelect
from .models import (
	ProductSlider, 
	FreeShippingSettings, 
	GroceryShippingArea, 
	SiteLogoAndTitle,
	CouponCode,
	MobileApps,
	AboutUs,
	ContactUs,
	FAQ,
	PrivacyPolicy,
	TermsOfUse,
	RefundReturnPolicy,
	VendorPaymentRequest,
	ShippingPriceSettings
	)

from vendors.models import VendorDocument

class VendorDocumentForm(forms.ModelForm):
	class Meta:
		model = VendorDocument
		exclude = ['vendor']

class ShippingPriceSettingsForm(forms.ModelForm):
	class Meta:
		model = ShippingPriceSettings
		exclude = ()


class MobileAppsForm(forms.ModelForm):
	class Meta:
		model = MobileApps
		exclude = ()


class AboutUsForm(forms.ModelForm):
	class Meta:
		model = AboutUs
		exclude = ()


class ContactUsForm(forms.ModelForm):
	class Meta:
		model = ContactUs
		exclude = ()

class FAQForm(forms.ModelForm):
	class Meta:
		model = FAQ
		exclude = ()


class PrivacyPolicyForm(forms.ModelForm):
	class Meta:
		model = PrivacyPolicy
		exclude = ()


class TermsOfUseForm(forms.ModelForm):
	class Meta:
		model = TermsOfUse
		exclude = ()


class RefundReturnPolicyForm(forms.ModelForm):
	class Meta:
		model = RefundReturnPolicy
		exclude = ()


class SliderForm(forms.ModelForm):
	class Meta:
		model = ProductSlider
		exclude = ()
		widgets = {
			'image': forms.FileInput()
		}

class CouponCodeForm(forms.ModelForm):
	class Meta:
		model = CouponCode
		exclude = ()


class FreeShippingSettingsForm(forms.ModelForm):
	class Meta:
		model = FreeShippingSettings
		exclude = ()

class GroceryShippingAreaForm(forms.ModelForm):
	class Meta:
		model = GroceryShippingArea
		exclude = ()


class SiteLogoAndTitleForm(forms.ModelForm):
	class Meta:
		model = SiteLogoAndTitle
		exclude = ()
		widgets = {
			'logo': forms.FileInput()
		}


class VendorPaymentRequestForm(forms.ModelForm):
	class Meta:
		model = VendorPaymentRequest
		exclude = ['user','pay_amount','orders_id','is_paid']



