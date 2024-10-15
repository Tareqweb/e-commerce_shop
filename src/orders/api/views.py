from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import (
	Cart, 
	CartProduct, 
	DeliveryAddress, 
	Order,
	OrderStatus,
	VendorOrder,
	VendorOrderProduct,
	OrderDeliveryInfo,
	BillingAddress
	)
from products.models import Product, ProductReview
from products.forms import ProductReviewForm
import random
import string
from ..forms import (
	DeliveryAddressForm, 
	PayPalPaymentsForm, 
	CancelOrderForm,
	BillingAddressForm
)

from ..usps_api_request import get_shipping_slots
from dashboard.models import FreeShippingSettings, GroceryShippingArea, ShippingPriceSettings
from vendors.models import Vendor

@api_view(['GET'])
def cart_products_api(request,id):
	cart_details = {
		'products':[]
	}

	try:
		cart_obj = Cart.objects.get(id=id)
		try:
			cart_details['subtotal_amount'] = float("{:.2f}".format(cart_obj.cart_subtotal_amount()))
		except Exception as e:
			cart_details['subtotal_amount'] = 0.0
		try:
			cart_details['total_amount'] = float("{:.2f}".format(cart_obj.get_cart_total()))
		except Exception as e:
			cart_details['total_amount'] = 0.0

		try:
			cart_details['tax_amount'] = float("{:.2f}".format(cart_obj.get_tax_total()))
		except Exception as e:
			cart_details['tax_amount'] = 0

		for product in cart_obj.cartproduct_set.all():
			cart_details['products'].append({
					"id": product.product.id,
					"name": product.product.name,
					"price": product.product.price,
					"sell_price": product.product_price,
					"color": product.color,
					"quantity":product.quantity,
					"size": product.size,
					"is_discounted": True if product.product.discount_percentage > 0 else False,
					"discount_percentage": product.product.discount_percentage,
					"image": "{}{}".format(request.build_absolute_uri('/')[:-1],product.product.image.url)
			})
	except Exception as e:
		print("========")
		print(e)
		print("========")


	return Response(cart_details)






def get_random_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(12))


@api_view(['POST'])
def add_to_cart(request):
	data = dict()
	if request.method == "POST":
		product = Product.objects.get(id=request.data.get("product"))
		quantity = request.data.get("quantity")
		size = request.data.get("size") or ""
		color = request.data.get("color") or ""
		cart = request.data.get("cart") or None
		try:
			cart_obj = Cart.objects.get(id=int(cart))
			if request.user.is_authenticated and not cart_obj.user:
				cart_obj.user = request.user
				cart_obj.save()
		except Exception as e:
			if request.user.is_authenticated:
				cart_obj = Cart.objects.create(user=request.user, id_no=get_random_string())
			else:
				cart_obj = Cart.objects.create(id_no=get_random_string())

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

		
		return Response({"status": "Added to Cart", "cart":cart_obj.id})

	return Response({"status": "Bad Request"})


@api_view(['GET'])
def remove_form_cart(request,id,cart_id):
	try:
		product = Product.objects.get(id=id)
		cart_obj = Cart.objects.get(id=cart_id)
		cart_obj.cartproduct_set.get(product=product).delete()
	except Exception as e:
		print(e)
		return Response({"status": "Bad Request"})

	return Response({"status": "Remove from Cart"})




@api_view(['POST'])
def apply_promo_code(request):
	from dashboard.models import CouponCode
	if request.method == "POST":
		code = request.data.get("promo")
		cart = request.data.get("cart")
		try:
			get_code_obj = CouponCode.objects.get(coupon_code=code, deactivate=False)
		except Exception as e:
			get_code_obj = None

		if get_code_obj:
			try:
				cart_obj = Cart.objects.get(id=int(cart))
				cart_obj.promo_code = get_code_obj.coupon_code
				cart_obj.save()
			except Exception as e:
				return Response({"status": "Bad Request"})
				
		return Response({"status": "Promo Code Applied"})

	return Response({"status": "Bad Request"})





@api_view(['GET'])
def remove_promo_code(request):
	try:
		get_cart_session_id = request.session['cart_id']
		cart_obj = Cart.objects.get(id=int(get_cart_session_id))
		cart_obj.promo_code = None
		cart_obj.save()
	except Exception as e:
		return Response({"status": "Bad Request"})

	return Response({"status": "Remove Promo Code"})



@api_view(['GET'])
def delivery_info_api(request, cart):
	content = {}
	cart_obj = Cart.objects.get(id=int(cart))
	try:
		delivery_info = DeliveryAddress.objects.get(user=cart_obj.user)
	except Exception as e:
		delivery_info = None

	if delivery_info:
		content["first_name"] = delivery_info.first_name
		content["last_name"] = delivery_info.last_name
		content["email"] = delivery_info.email
		content["phone"] = delivery_info.phone
		content["country"] = delivery_info.country
		content["state"] = delivery_info.state
		content["city"] = delivery_info.city
		content["address"] = delivery_info.address
		content["zipcode"] = delivery_info.zipcode
	else:
		content["first_name"] = ""
		content["last_name"] = ""
		content["email"] = ""
		content["phone"] = ""
		content["country"] = ""
		content["state"] = ""
		content["city"] = ""
		content["address"] = ""
		content["zipcode"] = ""

	return Response(content)


@api_view(['POST'])
def delivery_info_save_api(request, cart):
	cart_obj = Cart.objects.get(id=int(cart))
	if request.method == "POST":
		try:
			delivery_info = DeliveryAddress.objects.get(user=cart_obj.user)
			form = DeliveryAddressForm(request.data, instance=delivery_info)
		except Exception as e:
			form = DeliveryAddressForm(request.data)

		if form.is_valid():
			delivery_info = form.save()
			delivery_info.user = cart_obj.user
			delivery_info.save()
			return Response({"status": "updated"})
		else:
			return Response({"status": "error"})

	return Response({"status": "Bad Request"})


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


@api_view(['GET'])
def shipping_method_api(request, cart):
	cart_obj = Cart.objects.get(id=int(cart))

	free_shipping = False
	express_shipping = False
	express_shipping_amount = 0.0
	free_shipping_in_zip = False
	usps_shipping = False


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


	content = []

	if usps_shipping:
		for method in usps_shipping:
			content.append({
				"service_name": method['service_name'],
				"transit_time": method['transit_time'],
				"total_charge": method['total_charge']['amount'],
				"currency": method['total_charge']['currency'],
				"custom_data": "{},{},{}".format(
					method['service_name'],
					method['transit_time'],
					method['total_charge']['amount']
					)
				})


	if express_shipping:
		content.append({
			"service_name": "Express shipping",
			"transit_time": '10 days',
			"total_charge": express_shipping_amount,
			"currency": "USD",
			"custom_data": "{},{},{}".format(
				'Express shipping',
				'10 days',
				express_shipping_amount
				)
			})

	if free_shipping:
		content.append({
			"service_name": free_shipping_settings.shipping_name,
			"transit_time": free_shipping_settings.delivery_time,
			"total_charge": 0.0,
			"currency": "USD",
			"custom_data": "{},{},{}".format(
				free_shipping_settings.shipping_name,
				free_shipping_settings.delivery_time,
				0.0
				)
			})

	return Response(content)



@api_view(['POST'])
def add_shipping_method(request, cart):
	cart_obj = Cart.objects.get(id=int(cart))
	if request.method == "POST":
		shipping_method  = request.data.get('shipping-method')
		delivery_method, delivery_time, delivery_amount = shipping_method.split(",")
		cart_obj.delivery_method = delivery_method
		cart_obj.delivery_time = delivery_time
		cart_obj.delivery_amount = delivery_amount
		cart_obj.save()

		return Response({"status": "success"})
	
	return Response({"status": "Bad Request"})

ORDER_ADDRESS_FORMAT = '''
{} {}
{}, {}
{}
{}, {}, {}
{}
'''.strip()

@api_view(['POST'])
def create_order_api(request, cart):
	if request.method == "POST":
		order_id = request.data.get('order_id')
		cart_obj = Cart.objects.get(id=int(cart))

		order = Order.objects.create(
			id_no = cart_obj.id_no,
			user = request.user,
			promo_code = cart_obj.promo_code,
			delivery_method = cart_obj.delivery_method,
			delivery_time = cart_obj.delivery_time,
			delivery_amount = cart_obj.delivery_amount,
			payment_id = order_id
		)

		OrderStatus.objects.create(order=order)

		dinfo = OrderDeliveryInfo.objects.create(
			order = order,
			address=ORDER_ADDRESS_FORMAT.format(
				request.user.deliveryaddress.first_name,
				request.user.deliveryaddress.last_name,
				request.user.deliveryaddress.phone,
				request.user.deliveryaddress.email,
				request.user.deliveryaddress.address,
				request.user.deliveryaddress.city,
				request.user.deliveryaddress.state,
				request.user.deliveryaddress.zipcode,
				request.user.deliveryaddress.country
				)
			)

		for vendor in cart_obj.cartproduct_set.values('product__vendor').distinct():
			vendor = Vendor.objects.get(id=vendor['product__vendor'])
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
			cart_obj.delete()
		except Exception as e:
			print("cart_obj not found")


		return Response({"status": "success"})
	
	return Response({"status": "Bad Request"})





