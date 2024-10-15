from django.shortcuts import render
from django.contrib import messages
from orders.models import Order, DeliveryAddress
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
# Create your views here.
from django.contrib.auth.decorators import login_required
from products.models import ProductWishList
from django.contrib.auth.forms import PasswordChangeForm
from orders.forms import DeliveryAddressForm


@login_required
def order_history(request):
	template_name = "myaccount/order_history.html"
	orders = Order.objects.filter(user=request.user)
	context = {
		'orders':orders,
		'history':True
	}
	return render(request, template_name, context)


@login_required
def order_details_modal(request, id):
	data = dict()
	template_name = "myaccount/order_details.html"
	order = Order.objects.get(id=id)
	context = {
		"order":order,
	}
	data['order_html'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)




@login_required
def product_wish_list(request):
	template_name = "myaccount/product_wishlist_view.html"
	products = ProductWishList.objects.filter(user=request.user)
	context= {
		"products":products,
		"wish":True,
	}
	return render(request, template_name,context)



@login_required
def shipping_address(request):
	template_name = "myaccount/shipping_address.html"
	try:
		delivery_info = DeliveryAddress.objects.get(user=request.user)
	except Exception as e:
		delivery_info = None

	if request.method == "POST":
		if delivery_info:
			form = DeliveryAddressForm(request.POST, instance=delivery_info)
		else:
			form = DeliveryAddressForm(request.POST)

		if form.is_valid():
			print("valid form")
			delivery_info = form.save()
			delivery_info.user = request.user
			delivery_info.save()
		else:
			print(form.errors)
	else:
		if delivery_info:
			form = DeliveryAddressForm(instance=delivery_info)
		else:
			form = DeliveryAddressForm()

	context = {
		"form":form,
		"address":True,
	}

	return render(request, template_name,context)

@login_required
def change_password_view(request):
	template_name = "myaccount/change_password_view.html"
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			messages.success(request, "Your password was successfully updated!")
			# return redirect('/')
		else:
			messages.error(request, "Please correct the error below.")
	else:
		form = PasswordChangeForm(request.user)

	context = {
		"password":True, 
		"form": form
	}
	return render(request, template_name, context)



