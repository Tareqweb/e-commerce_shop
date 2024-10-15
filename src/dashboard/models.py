from django.db import models
from products.models import Category
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
# Create your models here.


class SiteLogoAndTitle(models.Model):
	logo = models.ImageField(upload_to="logo", null=True, blank=True)
	title = models.CharField(max_length=200)
	slider_image_height = models.PositiveIntegerField(default=580)

	def __str__(self):
		return str(self.title)


class FreeShippingSettings(models.Model):
	amount = models.DecimalField(max_digits=19, decimal_places=2, default=49.00)
	shipping_name = models.CharField(max_length=200, default="Express shipping")
	delivery_time = models.CharField(max_length=200, default="8 - 10 days")
	zipcodes = models.TextField(null=True, blank=True)
	apply_for_all = models.BooleanField(default=False)

	def __str__(self):
		return str(self.amount)


class ShippingPriceSettings(models.Model):
	amount_lte_10 = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	amount_lte_20 = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	amount_lte_30 = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	amount_lte_40 = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	amount_lte_50 = models.DecimalField(max_digits=19, decimal_places=2, default=0)

	def __str__(self):
		return str(self.id)


class GroceryShippingArea(models.Model):
	zipcodes = models.TextField()

	def __str__(self):
		return self.zipcodes

class ProductSlider(models.Model):
	image = models.ImageField(upload_to="slider_image", null=True, blank=True)
	link = models.URLField(max_length=250, null=True, blank=True)

	def __str__(self):
		return str(self.id)



AMOUNT_CHOICES = (
	("Percentage", "Percentage"),
	("Money", "Money")
)

class CouponCode(models.Model):
	coupon_code = models.CharField(max_length=250, unique=True)
	coupon_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	coupon_amount_in = models.CharField(max_length=250, choices=AMOUNT_CHOICES, default="Percentage")
	# cupon_for = models.ManyToManyField(Category, blank=True)
	# all_applicable = models.BooleanField(default=True)
	deactivate = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.coupon_code

	def get_status(self):
		return "Deactivate" if self.deactivate else "Active"

	def get_total_used(self):
		return "0"


class MobileApps(models.Model):
	android_app_url = models.CharField(max_length=250)
	ios_app_url = models.CharField(max_length=250)

	def __str__(self):
		return str(self.id)

class AboutUs(models.Model):
	description = RichTextUploadingField()

	def __str__(self):
		return str(self.id)

class ContactUs(models.Model):
	office_location = models.TextField()
	office_address = models.TextField()
	office_phone = models.TextField()
	office_email = models.TextField()
	working_hour = models.TextField()
	facebook_url = models.CharField(max_length=250, null=True, blank=True)
	twitter_url = models.CharField(max_length=250, null=True, blank=True)
	youtube_url = models.CharField(max_length=250, null=True, blank=True)

	def __str__(self):
		return str(self.id)


class FAQ(models.Model):
	question = models.CharField(max_length=250)
	answer = RichTextUploadingField()

	def __str__(self):
		return str(self.question)


class PrivacyPolicy(models.Model):
	description = RichTextUploadingField()

	def __str__(self):
		return str(self.id)


class TermsOfUse(models.Model):
	description = RichTextUploadingField()

	def __str__(self):
		return str(self.id)


class RefundReturnPolicy(models.Model):
	description = RichTextUploadingField()

	def __str__(self):
		return str(self.id)


# VendorOrder

class VendorPaymentRelease(models.Model):
	days = models.PositiveIntegerField(default=15)

	def __str__(self):
		return str(self.days)


class VendorPaymentRequest(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	pay_by = models.CharField(max_length=250)
	pay_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	description = RichTextUploadingField(null=True, blank=True)
	orders_id = models.TextField(null=True, blank=True)
	is_paid = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.id)












