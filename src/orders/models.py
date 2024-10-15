from django.db import models
from products.models import Product
from django.contrib.auth.models import User
from vendors.models import STATE_LIST_CHOICES, COUNTRY_CHOICES, Vendor
from dashboard.models import CouponCode, VendorPaymentRelease
from decimal import Decimal
from datetime import datetime, timedelta
# Create your models here.

CART_STATUS = (
	("pending","pending"),
	("ordered","ordered"),
)


class Cart(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	status = models.CharField(max_length=200, choices=CART_STATUS, default='pending')
	cart_date_time = models.DateTimeField(auto_now_add=True)
	cart_total = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	promo_code = models.CharField(max_length=200, null=True, blank=True)
	delivery_method = models.CharField(max_length=200, null=True, blank=True)
	delivery_time = models.CharField(max_length=200, null=True, blank=True)
	delivery_amount = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
	id_no = models.CharField(max_length=200, unique=True, null=True, blank=True)

	def __str__(self):
		return str(self.id)

	def cart_subtotal_amount(self):
		return self.cartproduct_set.aggregate(
			total=models.Sum(models.F('product_price') * models.F('quantity'), output_field=models.FloatField()))['total']

	def cart_total_qty(self):
		return self.cartproduct_set.aggregate(
			qty=models.Sum(models.F('quantity'), output_field=models.IntegerField()))['qty']

	def get_total_weight(self):
		return self.cartproduct_set.aggregate(
			weight=models.Sum(models.F('product__weight'), output_field=models.FloatField()))['weight']

	def is_express_shipping_product_in_cart(self):
		return self.cartproduct_set.filter(product__category__sub_category__category__express_shipping=True).exists()

	def get_tax_total(self):
		return self.cartproduct_set.aggregate(
			total=models.Sum(models.F('tax_amount'), output_field=models.FloatField()))['total']

	def get_delivery_total(self):
		if self.delivery_amount:
			return self.delivery_amount
		else:
			return 0

	def is_valid_promo(self):
		if self.promo_code:
			return CouponCode.objects.filter(coupon_code=self.promo_code, deactivate=False).exists()
		else:
			return False

	def get_promo_amount(self):
		if self.is_valid_promo():
			code_obj = CouponCode.objects.get(coupon_code=self.promo_code, deactivate=False)
			if code_obj.coupon_amount_in == "Percentage":
				discount_amount = Decimal(self.cart_subtotal_amount()) * code_obj.coupon_amount / 100
			else:
				discount_amount = code_obj.coupon_amount
			return discount_amount

		return 0

	def cart_subtotal_with_promo(self):
		try:
			return Decimal(self.cart_subtotal_amount()) - self.get_promo_amount()
		except Exception as e:
			return 0 

	def get_cart_total(self):
		try:
			return Decimal(self.cart_subtotal_amount()) + Decimal(self.get_tax_total()) + self.get_delivery_total()
		except Exception as e:
			return 0

	def get_cart_total_with_promo(self):
		try:
			return Decimal(self.cart_subtotal_amount()) + Decimal(self.get_tax_total()) + self.get_delivery_total() - self.get_promo_amount()
		except Exception as e:
			return 0



class CartProduct(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	product_price = models.DecimalField(max_digits=19, decimal_places=2)
	tax_amount = models.DecimalField(max_digits=19, decimal_places=2)
	quantity = models.PositiveIntegerField()
	color = models.CharField(max_length=200, null=True, blank=True)
	size = models.CharField(max_length=200, null=True, blank=True)

	def __str__(self):
		return str(self.id)

	def get_price(self):
		return self.quantity * self.product_price



class Order(models.Model):
	id_no = models.CharField(max_length=200, unique=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	promo_code = models.CharField(max_length=200, null=True, blank=True)
	delivery_method = models.CharField(max_length=200, null=True, blank=True)
	delivery_time = models.CharField(max_length=200, null=True, blank=True)
	delivery_amount = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
	is_paid = models.BooleanField(default=False)
	is_complete = models.BooleanField(default=False)
	payment_id = models.CharField(max_length=200, null=True, blank=True)


	def __str__(self):
		return str(self.id)


	def order_subtotal_amount(self):
		total = 0.0
		for order in self.vendororder_set.all():
			total = total + order.vendororderproduct_set.aggregate(
				total=models.Sum(models.F('product_price') * models.F('quantity'), output_field=models.FloatField()))['total']
		return total


	def get_vendor_list(self):
		vendors = []
		for vorder in self.vendororder_set.all():
			vendors.append(vorder.vendor.company_name)

		return ", ".join(vendors)


	def get_total_cancellation_amount(self):
		total = 0
		for order in self.vendororder_set.all():
			for product in order.vendororderproduct_set.all():
				if product.cancelorder:
					if product.cancelorder.is_accepted:
						total = product.cancelorder.cancel_amount
						return total
		return total


	def is_cancellation(self):
		total = False
		for order in self.vendororder_set.all():
			for product in order.vendororderproduct_set.all():
				if product.cancelorder:
					if product.cancelorder.is_accepted:
						total = True
						return total
		return total



	def get_order_subtotal_with_promo(self):
		try:
			return Decimal(self.order_subtotal_amount()) - self.get_promo_amount()
		except Exception as e:
			return 0 

	def order_total_qty(self):
		total = 0
		for order in self.vendororder_set.all():
			total = total + order.vendororderproduct_set.aggregate(
			qty=models.Sum(models.F('quantity'), output_field=models.IntegerField()))['qty']

		return total


	def get_total_weight(self):
		total = 0
		for order in self.vendororder_set.all():
			total = total + order.vendororderproduct_set.aggregate(
				weight=models.Sum(models.F('product__weight'), output_field=models.FloatField()))['weight']

		return total

	def get_tax_total(self):
		return  Decimal(self.order_subtotal_amount()) * Decimal(8.87) / 100


	def get_tax_total_with_promo(self):
		return Decimal(self.get_order_subtotal_with_promo()) * Decimal(8.87) / 100


	def get_delivery_total(self):
		if self.delivery_amount:
			return self.delivery_amount
		else:
			return 0

	def is_valid_promo(self):
		if self.promo_code:
			return CouponCode.objects.filter(coupon_code=self.promo_code, deactivate=False).exists()
		else:
			return False

	def get_promo_percentage(self):
		if self.is_valid_promo():
			code_obj = CouponCode.objects.get(coupon_code=self.promo_code, deactivate=False)
			if code_obj.coupon_amount_in == "Percentage":
				discount_amount = "({}){}%".format(code_obj.coupon_code, code_obj.coupon_amount)
			else:
				discount_amount = "({}){} USD".format(code_obj.coupon_code, code_obj.coupon_amount)
			return discount_amount

		return 0


	def get_promo_amount(self):
		if self.is_valid_promo():
			code_obj = CouponCode.objects.get(coupon_code=self.promo_code, deactivate=False)
			if code_obj.coupon_amount_in == "Percentage":
				discount_amount = Decimal(self.order_subtotal_amount()) * code_obj.coupon_amount / 100
			else:
				discount_amount = code_obj.coupon_amount
			return discount_amount

		return 0

	def get_order_total(self):
		return Decimal(self.order_subtotal_amount()) + Decimal(self.get_tax_total()) + self.get_delivery_total()


	def get_order_total_with_promo(self):
		return Decimal(self.get_order_subtotal_with_promo()) + Decimal(self.get_tax_total_with_promo()) + Decimal(self.get_delivery_total()) - Decimal(self.get_promo_amount())


	def get_total_cancellation_total(self):
		print("hiiiii")
		if self.is_valid_promo():
			total = self.get_order_total_with_promo()
		else:
			total = self.get_order_total()
		return total - self.get_total_cancellation_amount()



ORDER_STATUS = (
	("Confirm","Confirm"),
	("Shipment","Shipment"),
	("Delivered","Delivered"),
	("Cancel","Cancel")
)

class OrderStatus(models.Model):
	order = models.OneToOneField(Order, on_delete=models.CASCADE)
	status = models.CharField(max_length=200, choices=ORDER_STATUS, default='Confirm')
	tracking_url = models.TextField(null=True, blank=True)
	expected_delivery_form = models.DateField(null=True, blank=True)
	expected_delivery_to = models.DateField(null=True, blank=True)

	def __str__(self):
		return str(self.id)
		

class VendorOrder(models.Model):
	main_order = models.ForeignKey(Order, on_delete=models.CASCADE)
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
	is_complete = models.BooleanField(default=False)
	is_payment_released = models.BooleanField(default=False)
	is_payment_request_sent = models.BooleanField(default=False)
	is_paid = models.BooleanField(default=False)

	def __str__(self):
		return str(self.id)

	def get_cancellation_amount(self):
		amount = 0.0
		for product in self.vendororderproduct_set.all():
			if product.cancelorder:
				if product.cancelorder.is_accepted:
					amount = Decimal(amount) + product.cancelorder.cancel_amount
		return amount

	def get_payment_released_date(self):
		days = VendorPaymentRelease.objects.last().days
		day = self.main_order.created_at + timedelta(days=days)
		return day.date()

	def order_subtotal_amount(self):
		try:
			return self.vendororderproduct_set.aggregate(
			total=models.Sum(models.F('product_price') * models.F('quantity'), output_field=models.FloatField()))['total']
		except Exception as e:
			return 0

	def order_total_qty(self):
		return self.vendororderproduct_set.aggregate(
			qty=models.Sum(models.F('quantity'), output_field=models.IntegerField()))['qty']

	def get_tax_total(self):
		try:
			return self.order_subtotal_amount() * 8.87 / 100
		except Exception as e:
			return 0

	def get_delivery_total(self):
		return 50.0

	def get_order_total(self):
		try:
			return self.order_subtotal_amount() + self.get_tax_total()
		except Exception as e:
			return 0


class VendorOrderProduct(models.Model):
	vendor_order = models.ForeignKey(VendorOrder, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	product_price = models.DecimalField(max_digits=19, decimal_places=2)
	quantity = models.PositiveIntegerField()
	color = models.CharField(max_length=200, null=True, blank=True)
	size = models.CharField(max_length=200, null=True, blank=True)
	is_cancellation_request = models.BooleanField(default=False)
	is_reviewd = models.BooleanField(default=False)

	def __str__(self):
		return str(self.id)

	def get_price(self):
		return self.quantity * self.product_price



# class OrderDeliveryMethod(models.Model):
# 	order = models.OneToOneField(Order, on_delete=models.CASCADE)
# 	shipping_method = models.CharField(max_length=200)
# 	delivery_time = models.CharField(max_length=200)
# 	handling_fee = models.DecimalField(max_digits=19, decimal_places=2)

# 	def __str__(self):
# 		return str(self.order.id_no)

class OrderDeliveryInfo(models.Model):
	order = models.OneToOneField(Order, on_delete=models.CASCADE)
	address = models.TextField()
	billing_address = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.order.id_no)


class DeliveryAddress(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)
	email = models.EmailField()
	phone = models.CharField(max_length=200)
	country = models.CharField(max_length=200, choices=COUNTRY_CHOICES, default="United States")
	state = models.CharField(max_length=200, choices=STATE_LIST_CHOICES)
	city = models.CharField(max_length=200)
	address = models.TextField()
	zipcode = models.CharField(max_length=200)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return "{} {}".format(self.first_name, self.last_name)

	def get_name(self):
		return "{} {}".format(self.first_name, self.first_name)


class BillingAddress(models.Model):
	billing_user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
	billing_first_name = models.CharField(max_length=200, null=True, blank=True)
	billing_last_name = models.CharField(max_length=200, null=True, blank=True)
	billing_email = models.EmailField(null=True, blank=True)
	billing_phone = models.CharField(max_length=200, null=True, blank=True)
	billing_country = models.CharField(max_length=200, choices=COUNTRY_CHOICES, default="United States")
	billing_state = models.CharField(max_length=200, choices=STATE_LIST_CHOICES, null=True, blank=True)
	billing_city = models.CharField(max_length=200, null=True, blank=True)
	billing_address = models.TextField(null=True, blank=True)
	billing_zipcode = models.CharField(max_length=200, null=True, blank=True)
	billing_created_at = models.DateTimeField(auto_now_add=True)
	billing_updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return "{} {}".format(self.billing_first_name, self.billing_last_name)

	def get_name(self):
		return "{} {}".format(self.first_name, self.first_name)


class CancelOrder(models.Model):
	vendor_order_product = models.OneToOneField(VendorOrderProduct, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	details = models.TextField(null=True, blank=True)
	image = models.ImageField(upload_to="review_product_image", null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	is_accepted = models.BooleanField(default=False)
	is_rejected = models.BooleanField(default=False)
	cancel_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.product.name
