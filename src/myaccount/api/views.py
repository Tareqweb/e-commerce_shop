from orders.models import (
	Cart, 
	Order,
	VendorOrderProduct,
	DeliveryAddress

)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from products.models import ProductWishList, Product
from orders.forms import DeliveryAddressForm


@api_view(['GET'])
def get_order_history(request):
	order_history = []
	orders = Order.objects.filter(user=request.user)
	for order in orders:
		order_history.append({
			"order_did": order.id,
			"order_id_no": order.id_no,
			"created_at": order.created_at,
			"promo_code": order.promo_code,
			"delivery_method": order.delivery_method,
			"delivery_time": order.delivery_time + " days",
			"delivery_amount": order.delivery_amount,
			"is_paid": order.is_paid,
			"is_complete": order.is_complete,
			"payment_id": order.payment_id,
			"order_subtotal_amount": order.order_subtotal_amount(),
			"get_order_subtotal_with_promo": order.get_order_subtotal_with_promo(),
			"get_order_total": order.get_order_total(),
			"get_order_total_with_promo": order.get_order_total_with_promo(),
			"get_promo_amount": order.get_promo_amount(),
			"get_promo_percentage": order.get_promo_percentage(),
			"is_valid_promo": order.is_valid_promo(),
			"get_tax_total": order.get_tax_total(),


		})
	return Response(order_history)


@api_view(['GET'])
def get_order_details(request,id):
	order_history = {}
	try:
		# user=request.user, 
		order = Order.objects.get(user=request.user, id=id)
		order_history = {
			"order_did": order.id,
			"order_id_no": order.id_no,
			"created_at": order.created_at,
			"promo_code": order.promo_code,
			"delivery_method": order.delivery_method,
			"delivery_time": order.delivery_time,
			"delivery_amount": order.delivery_amount,
			"payment_id": order.payment_id,
			"address": order.orderdeliveryinfo.address,
			"sub_total": float("{0:.2f}".format(order.get_order_subtotal_with_promo())),
			"tax_total": float("{0:.2f}".format(order.get_tax_total_with_promo())),
			"order_total": float("{0:.2f}".format(order.get_order_total_with_promo())),
			"total_product": VendorOrderProduct.objects.filter(vendor_order__main_order=order).count(),
			"products": []
		}

		for product in VendorOrderProduct.objects.filter(vendor_order__main_order=order):
			order_history['products'].append({
				"id": product.product.id,
				"name": product.product.name,
				"product_price": float("{0:.2f}".format(product.product_price)),
				"total_price" : float("{0:.2f}".format(product.get_price())),
				"quantity": product.quantity,
				"color": product.color,
				"size": product.size,
				"vendor": product.vendor_order.vendor.company_name,
				"image": "{}{}".format(request.build_absolute_uri('/')[:-1],product.product.image_sm.url)
				})
	except Exception as e:
		print(e)

	return Response(order_history)




@api_view(['GET'])
def get_product_wishlist(request):
	product_wishList = []
	wishLists = ProductWishList.objects.filter(user=request.user)
	for wishlist in wishLists:
		product_wishList.append({
			"id": wishlist.product.id,
			"name": wishlist.product.name,
			"price": wishlist.product.price,
			"sell_price": wishlist.product.sell_price,
			"is_discounted": True if wishlist.product.discount_percentage > 0 else False,
			"discount_percentage": wishlist.product.discount_percentage,
			"vendor": wishlist.product.vendor.company_name,
			"image": "{}{}".format(request.build_absolute_uri('/')[:-1],wishlist.product.image_sm.url)
		})

	return Response(product_wishList)


@api_view(['GET'])
def add_to_wishlist_api(request, id):
	product = Product.objects.get(id=id)
	try:
		ProductWishList.objects.create(
			user=request.user,
			product=product
			)
	except Exception as e:
		return Response({"status": "Bad Request"})
		
	return Response({"status": "success"})


@api_view(['GET'])
def remove_from_wishlist_api(request, id):
	product = Product.objects.get(id=id)
	try:
		ProductWishList.objects.filter(
			user=request.user,
			product=product
			).last().delete()
	except Exception as e:
		pritn(e)
		return Response({"status": "Bad Request"})

	return Response({"status": "success"})







@api_view(['POST'])
def change_password_api_view(request):
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.data)
		if form.is_valid():
			user = form.save()
			return Response({"status": "success"})
		else:
			return Response({"status": "wrong info"})
	return Response({"status": "Bad Request"})



@api_view(['GET'])
def delivery_address_api(request):
	content = {}
	try:
		delivery_info = DeliveryAddress.objects.get(user=request.user)
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
def delivery_address_save_api(request):
	if request.method == "POST":
		print(request.data)
		try:
			delivery_info = DeliveryAddress.objects.get(user=request.user)
			form = DeliveryAddressForm(request.data, instance=delivery_info)
		except Exception as e:
			form = DeliveryAddressForm(request.data)

		if form.is_valid():
			delivery_info = form.save()
			delivery_info.save()
			return Response({"status": "updated"})
		else:
			print(form.errors)
			return Response({"status": "error"})


	return Response({"status": "Bad Request"})




