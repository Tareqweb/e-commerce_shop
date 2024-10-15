from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail

from .models import (
	Cart, 
	CartProduct, 
	DeliveryAddress, 
	Order,
	OrderStatus,
	VendorOrder,
	VendorOrderProduct,
	OrderDeliveryInfo
	)
from products.models import Product, ProductReview
from products.forms import ProductReviewForm
import random
import string
from .forms import (
	DeliveryAddressForm, 
	PayPalPaymentsForm, 
	CancelOrderForm,
)
from vendors.models import Vendor

from dashboard.models import FreeShippingSettings, GroceryShippingArea, ShippingPriceSettings

from .usps_api_request import get_shipping_slots

from paypalcheckoutsdk.core import LiveEnvironment, SandboxEnvironment, PayPalHttpClient
from paypalcheckoutsdk.orders import OrdersGetRequest

from django.views.generic import FormView



# Create your views here.

def get_random_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(12))


def add_to_cart(request):
	data = dict()
	if request.method == "POST":
		product = Product.objects.get(id=int(request.POST.get("product")))
		buy_now = request.GET.get("buy_now")
		if buy_now:
			redirect_url = "/order/shipping-info/"
		else:
			redirect_url = "/product/{}/".format(product.slug)
		quantity = request.POST.get("quantity")
		size = request.POST.get("size") or ""
		color = request.POST.get("color") or ""
		try:
			get_cart_session_id = request.session['cart_id']
			cart_obj = Cart.objects.get(id=int(get_cart_session_id))
			if request.user.is_authenticated and not cart_obj.user:
				cart_obj.user = request.user
				cart_obj.save()
		except Exception as e:
			if request.user.is_authenticated:
				cart_obj = Cart.objects.create(user=request.user, id_no=get_random_string())
			else:
				cart_obj = Cart.objects.create(id_no=get_random_string())

			request.session['cart_id'] = cart_obj.id

		pro_existis = CartProduct.objects.filter(cart=cart_obj, product=product).exists()
		if not pro_existis:
			CartProduct.objects.create(
				cart=cart_obj,
				product=product,
				product_price=product.get_price(),
				quantity=int(quantity),
				color=color,
				size=size,
				tax_amount=product.tax_amount
			)

		data["cart_item"] = cart_obj.cartproduct_set.count()

		messages.success(request, 'Added To Cart')

	return redirect(redirect_url)


def remove_form_cart(request,id):
	product = Product.objects.get(id=int(id))
	redirect_url = "/product/{}/".format(product.slug)
	try:
		get_cart_session_id = request.session['cart_id']
		cart_obj = Cart.objects.get(id=int(get_cart_session_id))
		cart_obj.cartproduct_set.get(product=product).delete()
		redirect_url = "/product/{}/".format(product.slug)
		messages.success(request, 'Removed From Cart')
	except Exception as e:
		data["cart_found"] = False

	return redirect(redirect_url)

def remove_form_cart_by_id(request,id):
	product = Product.objects.get(id=int(id))
	try:
		get_cart_session_id = request.session['cart_id']
		cart_obj = Cart.objects.get(id=int(get_cart_session_id))
		cart_obj.cartproduct_set.get(product=product).delete()
	except Exception as e:
		pass
	return redirect('/order/cart/')



def cart(request):
	template_name = "orders/cart.html"
	try:
		get_cart_session_id = request.session['cart_id']
		cart_obj = Cart.objects.get(id=int(get_cart_session_id))
	except Exception as e:
		cart_obj = None

	context= {
		"cart_obj":cart_obj,
	}
	return render(request, template_name,context)



def update_cart_qty(request):
	data = dict()
	if request.method == "POST":
		qty = request.POST.get("qty")
		product = request.POST.get("product")
		try:
			get_cart_session_id = request.session['cart_id']
			cart_obj = Cart.objects.get(id=int(get_cart_session_id))
			cart_product = cart_obj.cartproduct_set.get(product__id=int(product))
			cart_product.quantity = int(qty)
			cart_product.save()
		except Exception as e:
			pass

		try:
			data['cart_product_total'] = cart_product.get_price()
			data['cart_total'] = float(cart_obj.cart_subtotal_amount())
		except Exception as e:
			data['cart_product_total'] = "0"
			data['cart_total'] = "0"
			print("error")

		return JsonResponse(data)


@login_required
def delivery_info(request):
	template_name = "orders/delivery_info.html"
	try:
		get_cart_session_id = request.session['cart_id']
		cart_obj = Cart.objects.get(id=int(get_cart_session_id))
	except Exception as e:
		return redirect("/")

	try:
		delivery_info = DeliveryAddress.objects.get(user=request.user)
		form = DeliveryAddressForm(instance=delivery_info)
	except Exception as e:
		delivery_info = None
		form = DeliveryAddressForm()

	context= {
		"delivery_info":delivery_info,
		"form":form,
		"cart_obj":cart_obj,
	}
	return render(request, template_name,context)



def apply_promo_code(request):
	from dashboard.models import CouponCode
	if request.method == "POST":
		code = request.POST.get("promo")
		try:
			get_code_obj = CouponCode.objects.get(coupon_code=code, deactivate=False)
		except Exception as e:
			get_code_obj = None

		if get_code_obj:
			try:
				get_cart_session_id = request.session['cart_id']
				cart_obj = Cart.objects.get(id=int(get_cart_session_id))
				cart_obj.promo_code = get_code_obj.coupon_code
				cart_obj.save()
			except Exception as e:
				return redirect("/")

	return redirect(request.META.get('HTTP_REFERER'))

def remove_promo_code(request):
	try:
		get_cart_session_id = request.session['cart_id']
		cart_obj = Cart.objects.get(id=int(get_cart_session_id))
		cart_obj.promo_code = None
		cart_obj.save()
	except Exception as e:
		return redirect("/")

	return redirect(request.META.get('HTTP_REFERER'))


ORDER_ADDRESS_FORMAT = '''
{} {}
{}, {}
{}
{}, {}, {}
{}
'''.strip()

ORDER_BILLING_ADDRESS_FORMAT = '''
{} {}
{}, {}
{}
{}, {}, {}
{}
'''.strip()

def express_shipping_cost(amount):
	shipping_price = ShippingPriceSettings.objects.last()
	if amount <= 10:
		return shipping_price.amount_lte_10
	if amount >= 11 and amount <=20:
		return shipping_price.amount_lte_20
	elif amount >= 21 and amount <=30:
		return shipping_price.amount_lte_30
	elif amount >= 31 and amount <=40:
		return shipping_price.amount_lte_40
	elif amount >= 41 and amount <=50:
		return shipping_price.amount_lte_50


@login_required
def create_shipping_details(request):
	try:
		get_cart_session_id = request.session['cart_id']
		cart_obj = Cart.objects.get(id=int(get_cart_session_id))
	except Exception as e:
		return redirect("/")

	if request.method == "POST":
		try:
			delivery_info = DeliveryAddress.objects.get(user=request.user)
			form = DeliveryAddressForm(request.POST, instance=delivery_info)
		except Exception as e:
			form = DeliveryAddressForm(request.POST)

		if form.is_valid():
			delivery_info = form.save()
			delivery_info.user = request.user
			delivery_info.save()

		else:
			print(form.errors)

	return redirect("/order/shipping-method/")

@login_required
def shipping_method(request):
	template_name = "orders/shipping_method.html"
	free_shipping = False
	express_shipping = False
	express_shipping_amount = 0.0
	free_shipping_in_zip = False
	usps_shipping = False
	try:
		get_cart_session_id = request.session['cart_id']
		cart_obj = Cart.objects.get(id=int(get_cart_session_id))
	except Exception as e:
		return redirect("/")

	ship_to = DeliveryAddress.objects.get(user=request.user)
	user_zipcode = ship_to.zipcode.strip()
	zipcodes = []

	if cart_obj.is_express_shipping_product_in_cart():
		express_shipping = True
		express_shipping_amount = express_shipping_cost(int(cart_obj.cart_subtotal_amount()))

	free_shipping_settings = FreeShippingSettings.objects.last()

	if free_shipping_settings.apply_for_all:
		free_shipping_in_zip = False
	else:
		if free_shipping_settings.zipcodes:
			free_shipping_in_zip = True
			zipcode = free_shipping_settings.zipcodes.split(",")
			for code in zipcode:
				zipcodes.append(code.strip())

	if free_shipping_in_zip:
		if cart_obj.cart_subtotal_amount() >= free_shipping_settings.amount and user_zipcode in zipcodes:
			free_shipping = True
	else:
		if cart_obj.cart_subtotal_amount() >= free_shipping_settings.amount:
			free_shipping = True

	if not free_shipping and not express_shipping:
		try:
			shipping_data = get_shipping_slots(ship_to, cart_obj)
			if shipping_data['meta']['code'] == 200:
				usps_shipping = shipping_data['data']['rates']
			else:
				express_shipping = True
		except Exception as e:
			express_shipping = True
			usps_shipping = False

	elif free_shipping and express_shipping:
		express_shipping = False

	# print(free_shipping)
	# print(usps_shipping)
	# print(express_shipping)

	context= {
		"cart_obj":cart_obj,
		"free_shipping":free_shipping,
		"free_shipping_settings":free_shipping_settings,
		"usps_shipping":usps_shipping,
		"express_shipping":express_shipping,
		"express_shipping_amount":express_shipping_amount,
	}
	return render(request, template_name,context)

@login_required
def add_shipping_method(request):
	try:
		get_cart_session_id = request.session['cart_id']
		cart_obj = Cart.objects.get(id=int(get_cart_session_id))
	except Exception as e:
		return redirect("/")

	if request.method == "POST":
		shipping_method  = request.POST.get('shipping-method')
		delivery_method, delivery_time, delivery_amount= shipping_method.split(",")
		cart_obj.delivery_method = delivery_method
		cart_obj.delivery_time = delivery_time
		cart_obj.delivery_amount = delivery_amount
		cart_obj.save()

		return redirect("/order/payment-and-order-confirmation/") 


class PayPalCheckOutView(FormView):    
	"""Handle a PayPal payments"""
	form_class = PayPalPaymentsForm
	template_name = "orders/order_summery_and_payment.html"
	# success_url = '/payment-success-page/'
	PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
	PAYPAL_CLIENT_SECRET = settings.PAYPAL_SECRET_ID
	# Production or Sandbox PayPal environment
	PAYPAL_SERVER = settings.PAYPAL_TEST

	def check_payment_status(self, order_id):
		""" Checks payment status and return True if it paid or False if it not """

		# handle PayPal environment - production or sandbox
		if self.PAYPAL_SERVER:
			environment_case = SandboxEnvironment
		else: 
			environment_case = LiveEnvironment

		# connect to PayPal REST API and get the status of this order_id
		environment = environment_case(client_id=self.PAYPAL_CLIENT_ID, client_secret=self.PAYPAL_CLIENT_SECRET)
		client = PayPalHttpClient(environment)
		request = OrdersGetRequest(order_id)
		# form the response. You could put this in try block and handle IOError or other exceptions
		response = client.execute(request)
		#get the status of this payment
		result = response.result['status'].lower()
		#return True if it is completed
		return result == 'completed'

	def get_context_data(self, **kwargs):       
		context = super().get_context_data(**kwargs)
		try:
			get_cart_session_id = self.request.session['cart_id']
			self.cart_obj = Cart.objects.get(id=int(get_cart_session_id))
		except Exception as e:
			return redirect("/")

		if self.cart_obj.is_valid_promo():
			amount = self.cart_obj.get_cart_total_with_promo()
		else:
			amount = self.cart_obj.get_cart_total()

		context['delivery_info'] = DeliveryAddress.objects.get(user=self.request.user)
		context['cart_obj'] = self.cart_obj
		context['client_id'] = self.PAYPAL_CLIENT_ID
		context['amount'] = float(amount) 
		context['currency'] = 'USD'
		context['description'] = 'Some payment description to the user'

		return context


	def form_valid(self, form):
		order_id = form.cleaned_data['order_id']
		result_status = self.check_payment_status(order_id)
		if result_status:
			try:
				get_cart_session_id = self.request.session['cart_id']
				cart_obj = Cart.objects.get(id=int(get_cart_session_id))
			except Exception as e:
				return redirect("/")

			order = Order.objects.create(
				id_no = cart_obj.id_no,
				user = self.request.user,
				promo_code = cart_obj.promo_code,
				delivery_method = cart_obj.delivery_method,
				delivery_time = cart_obj.delivery_time,
				delivery_amount = cart_obj.delivery_amount,
				payment_id = order_id
			)
			self.order_obj = order

			OrderStatus.objects.create(order=order)

			dinfo = OrderDeliveryInfo.objects.create(
				order = order,
				address=ORDER_ADDRESS_FORMAT.format(
					self.request.user.deliveryaddress.first_name,
					self.request.user.deliveryaddress.last_name,
					self.request.user.deliveryaddress.phone,
					self.request.user.deliveryaddress.email,
					self.request.user.deliveryaddress.address,
					self.request.user.deliveryaddress.city,
					self.request.user.deliveryaddress.state,
					self.request.user.deliveryaddress.zipcode,
					self.request.user.deliveryaddress.country
					)
				)

			vendor_emails = []
			for vendor in cart_obj.cartproduct_set.values('product__vendor').distinct():
				vendor = Vendor.objects.get(id=vendor['product__vendor'])
				vendor_emails.append(vendor.email)
				vendor_order = VendorOrder.objects.create(
					main_order=order,
					vendor= vendor
					)

				for product in cart_obj.cartproduct_set.filter(product__vendor=vendor):
					VendorOrderProduct.objects.create(
						vendor_order = vendor_order,
						product = product.product,
						product_price = product.product_price,
						quantity = product.quantity,
						color = product.color,
						size = product.size
					)

					try:
						product.product.stock = product.product.stock - int(product.quantity)
						product.product.save()
					except Exception as e:
						pass

			order.is_paid = True
			order.save()

			try:
				subject = "FnfBuy: Order confirmation"
				from_email = "noreply@bizoytech.com"
				to_email = []
				to_email.append(self.request.user.email)
				message_body = "Hello {},\nThank you for ordering, We received your order and we will begin processing it soon.".format(self.request.user.username)
				send_mail(subject, message_body, from_email, to_email)
			except Exception as e:
				print(e)

			try:
				subject = "FnfBuy: New order"
				from_email = "noreply@bizoytech.com"
				to_email = vendor_emails
				message_body = "You have new order"
				send_mail(subject, message_body, from_email, to_email)
			except Exception as e:
				print(e)

			try:
				cart_obj.delete()
				del self.request.session['cart_id']
				print("deleted")
			except Exception as e:
				print("pai nai mama")
		else:
			print("order is not created")

		return super().form_valid(form)

	def get_success_url(self):
		if self.order_obj:
			return "/order/order-success/{}/".format(self.order_obj.id)
		else:
			return "/order/order-failed/"
			
def order_success(request, id):
	try:
		order = Order.objects.get(id=id)
	except Exception as e:
		order = None
	template_name = "orders/order_success.html"
	context= {
		"order":order,
	}
	return render(request, template_name,context)


def order_failed(request):
	template_name = "orders/order_failed.html"
	context= {}
	return render(request, template_name, context)


def order_tracking(request):
	template_name = "orders/order_tracking.html"
	context= {}
	return render(request, template_name, context)


def order_confirm_recived(request, id):
	template_name = "orders/order_confirm_recived.html"
	v_product = VendorOrderProduct.objects.get(id=id)
	already_reviewd = ProductReview.objects.filter(
		user=request.user, 
		product=v_product.product,
		vendor_order_id=v_product.vendor_order.id
		).exists()
	form = ProductReviewForm()
	cform = CancelOrderForm()
	context= {
		"v_product":v_product,
		"already_reviewd":already_reviewd,
		"form":form,
		"cform":cform
	}
	return render(request, template_name, context)

def product_review(request, id):
	v_product = VendorOrderProduct.objects.get(id=id)
	if request.method == "POST":
		form = ProductReviewForm(request.POST, request.FILES or None)
		if form.is_valid():
			print(request.POST)
			form = form.save(commit=False)
			form.user = request.user
			form.product = v_product.product
			form.vendor_order_id = v_product.vendor_order.id
			form.save()

		v_product.is_reviewd = True
		v_product.save()

	return redirect(request.META.get('HTTP_REFERER'))


def cancel_order_form(request, id):
	v_product = VendorOrderProduct.objects.get(id=id)
	if request.method == "POST":
		form = CancelOrderForm(request.POST, request.FILES or None)
		if form.is_valid():
			form = form.save(commit=False)
			form.user = request.user
			form.product = v_product.product
			form.vendor_order_product = v_product
			form.save()
		else:
			print(form.errors)

		v_product.is_cancellation_request = True
		v_product.save()

	return redirect(request.META.get('HTTP_REFERER'))
# CancelOrderForm

