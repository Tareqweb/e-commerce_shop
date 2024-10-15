from django.shortcuts import render, redirect
from products.models import (
	Product, Category, 
	SubCategory, 
	ProductCategory,
	ProductSize,
	ProductColor,
	ProductCommissionPercentage
)
from products.forms import (
	ProductForm, 
	get_product_image_formset,
	CategoryForm,
	SubCategoryForm,
	ProductCategoryForm,
	ProductSizeForm,
	ProductColorForm,
	ProductCommissionPercentageForm,
	get_product_size_guid_formset,
	ProductSizeMeasurementForm
)

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from vendors.models import Vendor, VendorDocument
from orders.models import Order, VendorOrder
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Q
from django_datatables_view.base_datatable_view import BaseDatatableView
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
from .forms import (
	SliderForm, 
	FreeShippingSettingsForm, 
	GroceryShippingAreaForm, 
	SiteLogoAndTitle,
	SiteLogoAndTitleForm,
	CouponCodeForm,
	MobileAppsForm,
	AboutUsForm,
	ContactUsForm,
	FAQForm,
	PrivacyPolicyForm,
	TermsOfUseForm,
	RefundReturnPolicyForm,
	VendorPaymentRequestForm,
	ShippingPriceSettingsForm,
	VendorDocumentForm
	)

from orders.forms import OrderStatusForm
from orders.models import CancelOrder
from auth.vendor_permission import (
	vendor_permission_requird, 
	super_user_permission_requird,
	super_user_and_vendor_permission_requird
	)
from decimal import Decimal

from auth.forms import CreateVendor

# Create your views here.

@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def vendor_dashboard_home(request):
	template_name = "dashboard/dashboard_home.html"
	orders = VendorOrder.objects.filter(vendor__user=request.user)
	orders_total = orders.filter(is_complete=True)
	orders_today = orders_total.filter(main_order__created_at=timezone.now())
	today = datetime.now().date()

	for un_released_order in orders.filter(is_complete=True, is_payment_released=False, is_paid=False):
		if un_released_order.get_payment_released_date() <= today:
			un_released_order.is_payment_released = True
			un_released_order.save()

	try:
		orders_sell = sum([item.order_subtotal_amount() for item in orders_total])
		orders_today_sell = sum([item.order_subtotal_amount() for item in orders_today])
	except Exception as e:
		orders_sell = 0
		orders_today_sell = 0
	pending_orders = orders.filter(is_complete=False, main_order__is_paid=True)
	context = {
		"orders_total":orders_total.count(),
		"orders_sell":orders_sell,
		"orders_today":orders_today.count(),
		"orders_today_sell":orders_today_sell,
		"pending_orders":pending_orders,
		"vendor_menu":True,
		"admin_menu":False,
	}
	return render(request, template_name, context)



# FOR VENDOR/SELLER
@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def my_pending_orders(request):
	template_name = "dashboard/seller/my_pending_order.html"
	orders = VendorOrder.objects.filter(
		vendor__user=request.user, 
		is_complete=False,
		main_order__is_paid=True
		)
	context = {
		"orders":orders,
		"vendor_menu":True,
		"admin_menu":False,
	}
	return render(request, template_name, context)


class OrdersListJson(BaseDatatableView):
	order_columns = [
		"main_order__id_no",
		"main_order__user",
		"main_order",
		"main_order__created_at",
		"main_order",
		"main_order"
	]

	def get_initial_queryset(self):
		condition = self.request.GET.get("condition")
		if condition == "pending":
			return VendorOrder.objects.filter(vendor__user=self.request.user, 
				is_complete=False,main_order__is_paid=True).order_by("-id")
		else:
			return VendorOrder.objects.filter(vendor__user=self.request.user, 
				is_complete=True,main_order__is_paid=True).order_by("-id")

	def filter_queryset(self, qs):
		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			button = '<button class="btn btn-info btn-sm" onclick="loadOption(this)" target_url="/dashboard/vendor/my-order/{}/details/">View</button>'.format(item.id)
			json_data.append([
				item.main_order.id_no,
				item.main_order.user.username,
				"${}".format(item.main_order.order_subtotal_amount()),
				item.main_order.created_at.strftime("%m-%d-%Y"),
				item.main_order.orderstatus.status,
				button
			])
		return json_data


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def my_orders_details(request, id):
	data = dict()
	template_name = "dashboard/seller/my_orders_drtails.html"
	order = VendorOrder.objects.get(id=id)
	context = {
		"order":order,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)

@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def my_orders_is_complete(request, id):
	order = VendorOrder.objects.get(id=id)
	order.is_complete = True
	order.save()
	return redirect(request.META.get('HTTP_REFERER'))


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def my_cancel_orders(request):
	template_name = "dashboard/seller/my_cancel_orders.html"
	orders_list = CancelOrder.objects.filter(
		vendor_order_product__vendor_order__vendor=request.user.vendor,
		is_accepted = True
		).order_by("-id")
	context = {
		"orders_list":orders_list,
		"vendor_menu":True,
		"admin_menu":False,
	}
	return render(request, template_name, context)


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def my_cancel_orders_details(request, id):
	data = dict()
	template_name = "dashboard/seller/my_cancel_orders_details.html"
	order_product = CancelOrder.objects.get(id=id)
	# form = OrderStatusForm(instance=order.orderstatus)
	context = {
		"order_product":order_product,
		# "form":form,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def my_orders(request):
	template_name = "dashboard/seller/my_orders.html"
	context = {
		"vendor_menu":True,
		"admin_menu":False,
	}
	return render(request, template_name, context)


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def my_active_products(request):
	template_name = "dashboard/seller/my_active_products.html"
	context = {
		"vendor_menu":True,
		"admin_menu":False,
	}
	return render(request, template_name, context)


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def my_unapproved_products(request):
	template_name = "dashboard/seller/my_unapproved_products.html"
	context = {
		"vendor_menu":True,
		"admin_menu":False,
	}
	return render(request, template_name, context)


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def my_inactive_products(request):
	template_name = "dashboard/seller/my_inactive_products.html"
	context = {
		"vendor_menu":True,
		"admin_menu":False,
	}
	return render(request, template_name, context)

class ProductListJson(BaseDatatableView):
	order_columns = [
		"id",
		"image",
		"name",
		"category",
		"price",
		"discount_percentage",
		"discount_percentage",
		"tax_percentage",
		"size__size",
		"color__color",
		"productcommissionpercentage",
		"stock",
		"id",
		"id",
	]

	def get_initial_queryset(self):
		condition = self.request.GET.get("condition")
		if condition == "Active":
			return Product.objects.filter(vendor=self.request.user.vendor, approved=True, deactivate=False).order_by("-id")
		elif condition == "Inactive":
			return Product.objects.filter(vendor=self.request.user.vendor, approved=True, deactivate=True).order_by("-id")
		elif condition == "Unapproved":
			return Product.objects.filter(vendor=self.request.user.vendor,approved=False).order_by("-id")

	def filter_queryset(self, qs):
		search = self.request.POST.get('search[value]', None)
		if search:
		    qs = qs.filter(
				Q(name__icontains=search)|
				Q(price__icontains=search)|
				Q(discount_percentage__icontains=search)|
				Q(category__name__icontains=search)|
				Q(category__sub_category__name__icontains=search)|
				Q(category__sub_category__category__name__icontains=search)|
				Q(size__size__icontains=search)|
				Q(tax_percentage__icontains=search)|
				Q(color__color__icontains=search)|
				Q(stock__icontains=search)|
				Q(width__icontains=search)|
				Q(height__icontains=search)|
				Q(depth__icontains=search)|
				Q(weight__icontains=search)
		    ).distinct()

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			try:
				product_image_html = '<img src="{}" style="width: 30px;">'.format(item.image_sm.url)
			except Exception as e:
				product_image_html = '<img src="{}" style="width: 30px;">'.format(item.image.url)

			try:
				product_commission = item.productcommissionpercentage.commission
			except Exception as e:
				product_commission = "-"

			action_button = '''
				<a href="/dashboard/vendor/my-product/update/{}/">
					<button type="button" class="btn btn-info btn-sm">Edit</button>
				</a>
				
				<a href="/product/{}/" target="_blank">
					<button type="button" class="btn btn-info btn-sm">View</button>
				</a>
			'''.format(item.id, item.slug)

			json_data.append([
				item.id,
				product_image_html,
				"{}".format(item.name),
				"{}".format(item.category),
				"${}".format(item.price),
				"{}%".format(item.discount_percentage),
				"${}".format(item.get_sell_price()),
				"{}%".format(item.tax_percentage),
				", ".join(item.get_size_list()) if item.size else "-",
				", ".join(item.get_color_list()) if item.color else "-",
				product_commission,
				item.total_order(),
				item.stock,
				action_button
			])

		return json_data


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def create_my_product(request):
	template_name = "dashboard/seller/create_my_product.html"
	if request.method == "POST":
		form = ProductForm(request.POST, request.FILES or None)
		ProductImageForm = get_product_image_formset(0)
		ProductSizeGuidForm = get_product_size_guid_formset(0)
		image_form = ProductImageForm(request.POST, request.FILES or None, prefix='productimage_set')
		size_measurement = ProductSizeMeasurementForm(request.POST)
		size_guid_form = ProductSizeGuidForm(request.POST, prefix='productsizeguide_set')
		
		if form.is_valid() and image_form.is_valid() and size_guid_form.is_valid() and size_measurement.is_valid():
			form.instance.vendor = request.user.vendor
			form = form.save()

			size_measurement = size_measurement.save(commit=False)
			size_measurement.product = form
			size_measurement.save()

			with transaction.atomic():
				image_form.instance = form
				image_form = image_form.save()

				size_guid_form.instance = form
				size_guid_form = size_guid_form.save()

			return redirect("/dashboard/vendor/my-unapproved-product/")
		else:
			print(form.errors)
			print(image_form.errors)
			print(size_guid_form.errors)
			print(size_measurement.errors)
	else:
		form = ProductForm()
		size_measurement = ProductSizeMeasurementForm()
		ProductImageForm = get_product_image_formset(1)
		ProductSizeGuidForm = get_product_size_guid_formset(1)
		image_form = ProductImageForm()
		size_guid_form = ProductSizeGuidForm()

	context = {
		"form":form,
		'image_form': image_form,
		'size_measurement':size_measurement,
		'size_guid_form':size_guid_form,
		"vendor_menu":True,
		"admin_menu":False,
	}
	return render(request, template_name, context)


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def update_my_product(request, id):
	template_name = "dashboard/seller/create_my_product.html"
	product = Product.objects.get(id=id)
	if request.method == "POST":
		form = ProductForm(request.POST, request.FILES or None, instance=product)
		ProductImageForm = get_product_image_formset(0)
		ProductSizeGuidForm = get_product_size_guid_formset(0)
		try:
			size_measurement = ProductSizeMeasurementForm(request.POST, instance=product.productsizemeasurement)
		except Exception as e:
			size_measurement = ProductSizeMeasurementForm(request.POST)
		size_guid_form = ProductSizeGuidForm(request.POST, prefix='productsizeguide_set', instance=product)
		image_form = ProductImageForm(request.POST, request.FILES or None, prefix='productimage_set', instance=product)
		if form.is_valid() and image_form.is_valid() and size_guid_form.is_valid() and size_measurement.is_valid():
			# form.instance.vendor = request.user.vendor
			form = form.save()

			size_measurement = size_measurement.save(commit=False)
			size_measurement.product = form
			size_measurement.save()

			with transaction.atomic():
				image_form.instance = form
				image_form = image_form.save()

				size_guid_form.instance = form
				size_guid_form = size_guid_form.save()

			return redirect("/dashboard/vendor/my-active-product/")
		else:
			print(form.errors)
			print(image_form.errors)
	else:
		form = ProductForm(instance=product)
		ext = 0 if product.productimage_set.count() > 1 else 1
		ext2 = 0 if product.productsizeguide_set.count() > 1 else 1
		ProductImageForm = get_product_image_formset(ext)
		image_form = ProductImageForm(instance=product)

		ProductSizeGuidForm = get_product_size_guid_formset(ext2)
		size_guid_form = ProductSizeGuidForm(instance=product)
		try:
			size_measurement = ProductSizeMeasurementForm(instance=product.productsizemeasurement)
		except Exception as e:
			size_measurement = ProductSizeMeasurementForm()

	context = {
		"form":form,
		'image_form': image_form,
		'size_measurement':size_measurement,
		'size_guid_form':size_guid_form,
		"vendor_menu":True,
		"admin_menu":False,
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def update_my_product_admin(request, id):
	template_name = "dashboard/seller/create_my_product.html"
	product = Product.objects.get(id=id)
	if request.method == "POST":
		form = ProductForm(request.POST, request.FILES or None, instance=product)
		ProductImageForm = get_product_image_formset(0)
		ProductSizeGuidForm = get_product_size_guid_formset(0)
		try:
			size_measurement = ProductSizeMeasurementForm(request.POST, instance=product.productsizemeasurement)
		except Exception as e:
			size_measurement = ProductSizeMeasurementForm(request.POST)
		size_guid_form = ProductSizeGuidForm(request.POST, prefix='productsizeguide_set', instance=product)
		image_form = ProductImageForm(request.POST, request.FILES or None, prefix='productimage_set', instance=product)
		if form.is_valid() and image_form.is_valid() and size_guid_form.is_valid() and size_measurement.is_valid():
			# form.instance.vendor = request.user.vendor
			form = form.save()

			size_measurement = size_measurement.save(commit=False)
			size_measurement.product = form
			size_measurement.save()

			with transaction.atomic():
				image_form.instance = form
				image_form = image_form.save()

				size_guid_form.instance = form
				size_guid_form = size_guid_form.save()

			return redirect("/dashboard/admin/products/")
		else:
			print(form.errors)
			print(image_form.errors)
	else:
		form = ProductForm(instance=product)
		ext = 0 if product.productimage_set.count() > 1 else 1
		ext2 = 0 if product.productsizeguide_set.count() > 1 else 1
		ProductImageForm = get_product_image_formset(ext)
		image_form = ProductImageForm(instance=product)

		ProductSizeGuidForm = get_product_size_guid_formset(ext2)
		size_guid_form = ProductSizeGuidForm(instance=product)
		try:
			size_measurement = ProductSizeMeasurementForm(instance=product.productsizemeasurement)
		except Exception as e:
			size_measurement = ProductSizeMeasurementForm()

	context = {
		"form":form,
		'image_form': image_form,
		'size_measurement':size_measurement,
		'size_guid_form':size_guid_form,
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)



@login_required(login_url='/account/vendor/login/')
@vendor_permission_requird
def deu_payment(request):
	template_name = "dashboard/seller/deu_payment.html"
	total_amount = 0
	pending_total_amount = 0
	today = datetime.now().date()
	for un_released_order in VendorOrder.objects.filter(vendor__user=request.user, is_complete=True, is_payment_released=False, is_paid=False, is_payment_request_sent=False):
		if un_released_order.get_payment_released_date() <= today:
			un_released_order.is_payment_released = True
			un_released_order.save()

	vendor_payable_orders = VendorOrder.objects.filter(vendor__user=request.user, is_paid=False, is_payment_released=True, is_complete=True, is_payment_request_sent=False)
	for vorder in vendor_payable_orders:
		total_amount = total_amount + vorder.order_subtotal_amount()

	pending_payment_rquests = VendorPaymentRequest.objects.filter(user=request.user, is_paid=False)
	for pending_payment in pending_payment_rquests:
		pending_total_amount = pending_total_amount + pending_payment.pay_amount
	
	context = {
		"vendor_menu":True,
		"admin_menu":False,
		"vendor_payable_orders":vendor_payable_orders,
		"total_amount":total_amount,
		"pending_payment_rquests":pending_payment_rquests,
		"pending_total_amount":pending_total_amount,
	}
	return render(request, template_name, context)


@login_required(login_url='/account/vendor/login/')
@vendor_permission_requird
def send_payment_request(request):
	total_amount = 0
	orders_id = []
	vendor_payable_orders = VendorOrder.objects.filter(vendor__user=request.user, is_paid=False, is_payment_released=True, is_complete=True, is_payment_request_sent=False)
	for vorder in vendor_payable_orders:
		total_amount = total_amount + vorder.order_subtotal_amount()
		orders_id.append(vorder.main_order.id_no)
		vorder.is_payment_request_sent = True
		vorder.save()

	VendorPaymentRequest.objects.create(
		user = request.user,
		pay_amount = total_amount,
		orders_id = ", ".join(orders_id)
	)
	messages.success(request, 'Payment Request Sent')
	return redirect(request.META.get('HTTP_REFERER'))


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def load_payment_request(request, id):
	data = dict()
	request_obj = VendorPaymentRequest.objects.get(id=id)
	template_name = "dashboard/seller/payment_request_details.html"
	form = VendorPaymentRequestForm()
	context = {
		"request_obj":request_obj,
		"form":form,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def payment_history(request):
	paid_total_amount = 0
	template_name = "dashboard/seller/payment_history.html"
	today = datetime.now().date()
	for un_released_order in VendorOrder.objects.filter(vendor__user=request.user, is_complete=True, is_payment_released=False, is_paid=False, is_payment_request_sent=False):
		if un_released_order.get_payment_released_date() <= today:
			un_released_order.is_payment_released = True
			un_released_order.save()

	paid_payment_rquests = VendorPaymentRequest.objects.filter(user=request.user, is_paid=True)
	for paid_payment in paid_payment_rquests:
		paid_total_amount = paid_total_amount + paid_payment.pay_amount
	
	context = {
		"vendor_menu":True,
		"admin_menu":False,
		"paid_payment_rquests":paid_payment_rquests,
		"paid_total_amount":paid_total_amount,
	}
	return render(request, template_name, context)


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def update_vendor_profile(request):
	template_name = "dashboard/seller/vendor_profile.html"
	vendor = Vendor.objects.get(id=request.user.vendor.id)
	if request.method == "POST":
		form = CreateVendor(request.POST, instance=vendor)
		if form.is_valid():
			form.save()
			print("saved")
	else:
		form = CreateVendor(instance=vendor)

	context = {
		"vendor_menu":True,
		"admin_menu":False,
		"form":form,
		"vendor":vendor,
	}

	return render(request, template_name, context)


@vendor_permission_requird
@login_required(login_url='/account/vendor/login/')
def vendor_change_password_view(request):
	template_name ="dashboard/seller/vendor_change_password.html"
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
		"vendor_menu":True,
		"admin_menu":False,
		"password":True, 
		"form": form
	}
	return render(request, template_name, context)


# FOR SUPER USER
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def admin_dashboard_home(request):
	template_name = "dashboard/owner/dashboard_home.html"
	orders = Order.objects.all()
	orders_total = orders.filter(is_complete=True)
	orders_today = orders_total.filter(created_at=timezone.now())
	try:
		orders_sell = sum([item.order_subtotal_amount() for item in orders_total])
		orders_today_sell = sum([item.order_subtotal_amount() for item in orders_today])
	except Exception as e:
		orders_sell = 0
		orders_today_sell = 0
	
	pending_orders = orders.filter(is_complete=False, is_paid=True)

	context = {
		"orders_total":orders_total.count(),
		"orders_sell":orders_sell,
		"orders_today":orders_today.count(),
		"orders_today_sell":orders_today_sell,
		"pending_orders":pending_orders,
		"vendor_menu":False,
		"admin_menu":True,	
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def admin_change_password_view(request):
	template_name ="dashboard/owner/admin_change_password.html"
	if request.method == 'POST':
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			messages.success(request, "Your password was successfully updated!")
		else:
			messages.error(request, "Please correct the error below.")
	else:
		form = PasswordChangeForm(request.user)

	context = {
		"vendor_menu":False,
		"admin_menu":True,
		"password":True, 
		"form": form
	}
	return render(request, template_name, context)


# CATEGORYS
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_categorys(request):
	template_name = "dashboard/owner/product_categorys.html"
	categorys = Category.objects.all().order_by("-id")
	sub_categorys = SubCategory.objects.all().order_by("-id")
	product_categorys = ProductCategory.objects.all().order_by("-id")

	cat_form = CategoryForm()
	subcat_form = SubCategoryForm()
	productcat_form = ProductCategoryForm()

	context = {
		"vendor_menu":False,
		"admin_menu":True,
		"categorys":categorys,
		"sub_categorys":sub_categorys,
		"product_categorys":product_categorys,
		"cat_form":cat_form,
		"subcat_form":subcat_form,
		"productcat_form":productcat_form,
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def category_create(request):
	if request.method == "POST":
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save()

	return redirect("/dashboard/admin/categorys/")

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def category_update(request,id):
	data = dict()
	category = Category.objects.get(id=id)
	if request.method == "POST":
		form = CategoryForm(request.POST, instance=category)
		if form.is_valid():
			form.save()
			return redirect("/dashboard/admin/categorys/")

	template_name = "dashboard/owner/category_update.html"
	context = {
		"form": CategoryForm(instance=category),
		"category":category,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)


# SUB CATEGORY
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def subcategory_create(request):
	if request.method == "POST":
		form = SubCategoryForm(request.POST)
		if form.is_valid():
			form.save()

	return redirect("/dashboard/admin/categorys/")

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def subcategory_update(request,id):
	data = dict()
	subcategory = SubCategory.objects.get(id=id)
	if request.method == "POST":
		form = SubCategoryForm(request.POST, instance=subcategory)
		if form.is_valid():
			form.save()
			return redirect("/dashboard/admin/categorys/")

	template_name = "dashboard/owner/subcategory_update.html"
	context = {
		"form": SubCategoryForm(instance=subcategory),
		"subcategory":subcategory,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)

# PRODUCT CATEGORY
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_category_create(request):
	if request.method == "POST":
		form = ProductCategoryForm(request.POST)
		if form.is_valid():
			form.save()

	return redirect("/dashboard/admin/categorys/")

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_category_update(request,id):
	data = dict()
	product_category = ProductCategory.objects.get(id=id)
	if request.method == "POST":
		form = ProductCategoryForm(request.POST, instance=product_category)
		if form.is_valid():
			form.save()
			return redirect("/dashboard/admin/categorys/")

	template_name = "dashboard/owner/product_category_update.html"
	context = {
		"form": ProductCategoryForm(instance=product_category),
		"product_category":product_category,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)

#COLOR AND SIZE
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_colors_and_sizes(request):
	template_name = "dashboard/owner/product_colors_and_sizes.html"
	sizes = ProductSize.objects.all().order_by("-id")
	colors = ProductColor.objects.all().order_by("-id")
	size_form = ProductSizeForm()
	color_form = ProductColorForm()
	context = {
		"vendor_menu":False,
		"admin_menu":True,
		"colors":colors,
		"sizes":sizes,
		"color_form":color_form,
		"size_form":size_form,
	}
	return render(request, template_name, context)

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_size_create(request):
	if request.method == "POST":
		form = ProductSizeForm(request.POST)
		if form.is_valid():
			form.save()

	return redirect("/dashboard/admin/product-colors-and-sizes/")

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_size_update(request, id):
	data = dict()
	size = ProductSize.objects.get(id=id)
	if request.method == "POST":
		form = ProductSizeForm(request.POST, instance=size)
		if form.is_valid():
			form.save()
			return redirect("/dashboard/admin/product-colors-and-sizes/")

	template_name = "dashboard/owner/product_size_update.html"
	context = {
		"form": ProductSizeForm(instance=size),
		"size":size,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)



@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_color_create(request):
	if request.method == "POST":
		form = ProductColorForm(request.POST)
		if form.is_valid():
			form.save()

	return redirect("/dashboard/admin/product-colors-and-sizes/")

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_color_update(request, id):
	data = dict()
	color = ProductColor.objects.get(id=id)
	if request.method == "POST":
		form = ProductColorForm(request.POST, instance=color)
		if form.is_valid():
			form.save()
			return redirect("/dashboard/admin/product-colors-and-sizes/")

	template_name = "dashboard/owner/product_color_update.html"
	context = {
		"form": ProductColorForm(instance=color),
		"color":color,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)


# PRODUCTS
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_list(request):
	template_name = "dashboard/owner/product_list.html"
	context = {
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_request(request):
	template_name = "dashboard/owner/product_request.html"
	context = {
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def declined_product_request(request):
	template_name = "dashboard/owner/declined_product_request.html"
	context = {
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def hidden_product_list(request):
	template_name = "dashboard/owner/hidden_product_list.html"
	context = {
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)


class AllProductListJson(BaseDatatableView):
	order_columns = [
		"id",
		"image",
		"name",
		"Vendor",
		"category",
		"price",
		"discount_percentage",
		"discount_percentage",
		"size__size",
		"color__color",
		"productcommissionpercentage",
		"stock",
		"id",
	]

	def get_initial_queryset(self):
		self.condition = self.request.GET.get("condition")
		print(self.condition)
		if self.condition == "active":
			print(Product.objects.filter(approved=True, deactivate=False, rejected=False).order_by("-id"))
			return Product.objects.filter(approved=True, deactivate=False, rejected=False).order_by("-id")
		if self.condition == "unapproved":
			return Product.objects.filter(approved=False, deactivate=False, rejected=False).order_by("-id")
		if self.condition == "rejected":
			return Product.objects.filter(rejected=True).order_by("-id")
		if self.condition == "deactivate":
			return Product.objects.filter(approved=True, deactivate=True, rejected=False).order_by("-id")

	def filter_queryset(self, qs):
		search = self.request.POST.get('search[value]', None)
		if search:
			qs = qs.filter(
				Q(name__icontains=search)|
				Q(price__icontains=search)|
				Q(discount_percentage__icontains=search)|
				Q(category__name__icontains=search)|
				Q(category__sub_category__name__icontains=search)|
				Q(category__sub_category__category__name__icontains=search)|
				Q(size__size__icontains=search)|
				Q(color__color__icontains=search)|
				Q(stock__icontains=search)|
				Q(width__icontains=search)|
				Q(height__icontains=search)|
				Q(depth__icontains=search)|
				Q(weight__icontains=search)
		    ).distinct()

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			if self.condition == "active":
				action_buttons = '''
				<button class="btn btn-info btn-sm" target_url="/dashboard/admin/product_option/{}/" 
				onclick="loadOption(this);">Option</button>
				<a href="/product/{}/" target="_blank">
				<button class="btn btn-info btn-sm">View</button>
				</a>
				<a href="/dashboard/admin/my-product/update/{}/">
					<button type="button" class="btn btn-info btn-sm">Edit</button>
				</a>
				'''.format(item.id, item.slug, item.id)

			if self.condition == "unapproved":
				action_buttons = '''
				<button class="btn btn-info btn-sm" target_url="/dashboard/admin/product_option/{}/" 
				onclick="loadOption(this);">Option</button>
				<a href="/product/{}/" target="_blank">
				<button class="btn btn-info btn-sm">View</button>
				</a>
				<a href="/dashboard/admin/my-product/update/{}/">
					<button type="button" class="btn btn-info btn-sm">Edit</button>
				</a>
				'''.format(item.id, item.slug, item.id)

			if self.condition == "rejected":
				action_buttons = '''
				<button class="btn btn-info btn-sm" target_url="/dashboard/admin/product_option/{}/" 
				onclick="loadOption(this);">Option</button>
				<a href="/product/{}/" target="_blank">
				<button class="btn btn-info btn-sm">View</button>
				</a>
				<a href="/dashboard/admin/my-product/update/{}/">
					<button type="button" class="btn btn-info btn-sm">Edit</button>
				</a>
				'''.format(item.id, item.slug, item.id)

			if self.condition == "deactivate":
				action_buttons = '''
				<a href="/product/{}/">
				<button class="btn btn-info btn-sm">View</button>
				</a>
				<a href="/dashboard/admin/my-product/update/{}/">
					<button type="button" class="btn btn-info btn-sm">Edit</button>
				</a>
				'''.format(item.slug, item.id)

			try:
				product_image_html = '<img src="{}" style="width: 30px;">'.format(item.image_sm.url)
			except Exception as e:
				product_image_html = '<img src="{}" style="width: 30px;">'.format(item.image.url)

			try:
				product_commission = item.productcommissionpercentage.commission
			except Exception as e:
				product_commission = "-"


			json_data.append([
				item.id,
				product_image_html,
				"{}".format(item.name),
				"{}".format(item.vendor.company_name),
				"{}".format(item.category),
				"${}".format(item.price),
				"{}%".format(item.discount_percentage),
				"${}".format(item.get_sell_price()),
				", ".join(item.get_size_list()) if item.size else "-",
				", ".join(item.get_color_list()) if item.color else "-",
				product_commission,
				item.stock,
				action_buttons
			])
		return json_data


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_option(request, id):
	data = dict()
	product = Product.objects.get(id=id)
	template_name = "dashboard/owner/product_option_modal.html"
	try:
		pcp = ProductCommissionPercentage.objects.get(product=product)
	except Exception as e:
		pcp = ProductCommissionPercentage.objects.create(product=product)

	form = ProductCommissionPercentageForm(instance=pcp)
	context = {
		"product":product,
		"form":form,
	}
	data['option_html'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_commission_update(request, id):
	product = Product.objects.get(id=id)
	if request.method == "POST":
		form = ProductCommissionPercentageForm(request.POST,instance=product.productcommissionpercentage)
		if form.is_valid():
			form.save()

		tax = request.POST.get("tax")
		product.tax_percentage = Decimal(tax)
		product.approved = True
		product.rejected = False
		product.save()

	return redirect(request.META.get('HTTP_REFERER'))

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def product_rejected(request, id):
	product = Product.objects.get(id=id)
	product.rejected = True
	product.approved = False
	product.save()
	return redirect(request.META.get('HTTP_REFERER'))

# VENDOR
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def vendor_list(request):
	template_name = "dashboard/owner/vendor_list.html"
	context = {
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def deactivate_vendor_list(request):
	template_name = "dashboard/owner/deactivate_vendor_list.html"
	context = {
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)


class VendorListJson(BaseDatatableView):
	order_columns = [
		"id",
		"company_name",
		"full_name",
		"email",
		"phone",
		"mobile",
		"id",
		"id",
	]

	def get_initial_queryset(self):
		self.active_status = self.request.GET.get("active")
		return Vendor.objects.filter(active=self.active_status).order_by("-id")

	def filter_queryset(self, qs):
		search = self.request.POST.get('search[value]', None)
		if search:
			qs = qs.filter(
				Q(id__icontains=search)|
				Q(full_name__icontains=search)|
				Q(company_name__icontains=search)|
				Q(email__icontains=search)|
				Q(phone__icontains=search)|
				Q(mobile__icontains=search)|
				Q(country__icontains=search)|
				Q(state__icontains=search)|
				Q(city__icontains=search)|
				Q(zipcode__icontains=search)|
				Q(address__icontains=search)
		    ).distinct()

		return qs

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			if self.active_status == "True":
				action_button = '''
					<a href="/dashboard/admin/vendor_active_deactive/{}/">
						<button type="button" class="btn btn-info btn-sm">Deactivate</button>
					</a>
					<a href="javascript:;" onclick=vendorDetails(this); data_url="/dashboard/admin/vendor_details/{}/">
						<button type="button" class="btn btn-info btn-sm">view</button>
					</a>
				'''.format(item.id, item.id)
			else:
				action_button = '''
					<a href="/dashboard/admin/vendor_active_deactive/{}/">
						<button type="button" class="btn btn-info btn-sm">Make Active</button>
					</a>
					<a href="javascript:;" onclick=vendorDetails(this); data_url="/dashboard/admin/vendor_details/{}/">
						<button type="button" class="btn btn-info btn-sm">view</button>
					</a>
				'''.format(item.id, item.id)

			json_data.append([
				item.id,
				item.company_name,
				item.full_name,
				item.email,
				item.phone,
				item.mobile,
				item.address,
				action_button
			])
		return json_data


@login_required(login_url='/account/vendor/login/')
def vendor_details(request, id):
	data = dict()
	template_name = "dashboard/owner/vendor_details.html"
	vendor = Vendor.objects.get(id=id)
	vendor_docs = VendorDocument.objects.filter(vendor=vendor)
	form = VendorDocumentForm()
	context = {
		"vendor":vendor,
		"vendor_docs":vendor_docs,
		"form":form,
	}
	data['vendor_details'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)


def vendor_document_save(request, id):
	if request.method == "POST":
		vendor = Vendor.objects.get(id=id)
		form = VendorDocumentForm(request.POST, request.FILES)
		if form.is_valid():
			form = form.save(commit=False)
			form.vendor = vendor
			form.save()
	return redirect(request.META.get('HTTP_REFERER'))



@login_required(login_url='/account/vendor/login/')
def vendor_active_deactive(request, id):
	vendor = Vendor.objects.get(id=id)
	vendor.active = not vendor.active
	vendor.save()
	return redirect(request.META.get('HTTP_REFERER'))


# USERS
@login_required(login_url='/account/vendor/login/')
def user_list(request):
	template_name = "dashboard/owner/user_list.html"
	page_number = request.GET.get('page')
	all_users = User.objects.all().order_by("-id")
	paginator = Paginator(all_users, 20)
	users = paginator.get_page(page_number)
	context = {
		"users":users,
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)


# ORDERS
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def orders_list(request):
	template_name = "dashboard/owner/orders_list.html"
	dates = []
	start_date = request.POST.get("start_date")
	end_date = request.POST.get("end_date")
	dates.append(start_date)
	dates.append(end_date)

	if start_date and end_date:
		orders = Order.objects.filter(is_paid=True, is_complete=True, created_at__date__range=dates)
	else:
		orders = Order.objects.filter(is_paid=True, is_complete=True)

	total_order = orders.count()
	total_sell = 0
	total_tax = 0
	total_delivery = 0

	for order in orders:
		if order.is_valid_promo():
			total_sell = Decimal(total_sell) + order.get_order_subtotal_with_promo()
			total_tax = total_tax + order.get_tax_total_with_promo()
			total_delivery = total_delivery + order.get_delivery_total()
		else:
			total_sell = total_sell + Decimal(order.order_subtotal_amount())
			total_tax = total_tax + order.get_tax_total()
			total_delivery = total_delivery + order.get_delivery_total()

	context = {
		"vendor_menu":False,
		"admin_menu":True,
		"start_date":start_date,
		"end_date":end_date,
		"total_order":total_order,
		"total_sell":total_sell,
		"total_tax":total_tax,
		"total_delivery":total_delivery,
	}
	return render(request, template_name, context)

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def pending_orders_list(request):
	template_name = "dashboard/owner/pending_orders_list.html"
	context = {
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def cancel_orders_list(request):
	template_name = "dashboard/owner/cancel_orders_list.html"
	orders_list = CancelOrder.objects.all().order_by("-id")
	context = {
		"orders_list":orders_list,
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)


#admin order
class OrderListJson(BaseDatatableView):
	order_columns = [
		"id_no",
		"user",
		"created_at",
		"users",
		"users",
		"users",
		"users"
	]

	def get_initial_queryset(self):
		condition = self.request.GET.get("condition")
		if  condition == "pending":
			return Order.objects.filter(is_paid=True, is_complete=False).order_by("-id")
		else:
			dates = []
			start_date = self.request.GET.get("start_date")
			end_date = self.request.GET.get("end_date")
			dates.append(start_date)
			dates.append(end_date)
			if start_date and end_date:
				return Order.objects.filter(is_paid=True, is_complete=True, created_at__date__range=dates).order_by("-id")
			else:
				return Order.objects.filter(is_paid=True, is_complete=True).order_by("-id")

	def filter_queryset(self, qs):
		return qs
		# try:
		#     search = literal_eval(self.request.POST.get('search[value]', None))
		# except Exception as e:
		#     search = None

		# if search:
		#     qs = qs.filter(
		#         Q(specific_id__icontains=search['value'])|
		#         Q(patient_name__icontains=search['value'])|
		#         Q(cycle__icontains=search['value'])
		#     )

	def prepare_results(self, qs):
		json_data = []
		for item in qs:
			button = '<button class="btn btn-info btn-sm" onclick="loadOption(this)" target_url="/dashboard/admin/admin_orders/{}/details/">View</button>'.format(item.id)
			try:
				order_total = item.get_order_total()
			except Exception as e:
				order_total = 0

			json_data.append([
				item.id_no,
				item.payment_id,
				item.user.username,
				item.created_at.strftime("%m-%d-%Y"),
				item.get_vendor_list(),
				"{:.2f}".format(order_total),
				item.delivery_method,
				button
			])
		return json_data


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def orders_details(request, id):
	data = dict()
	template_name = "dashboard/owner/orders_drtails.html"
	order = Order.objects.get(id=id)
	form = OrderStatusForm(instance=order.orderstatus)
	context = {
		"order":order,
		"form":form,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def cancel_orders_details(request, id):
	data = dict()
	template_name = "dashboard/owner/cancel_orders_details.html"
	order_product = CancelOrder.objects.get(id=id)
	# form = OrderStatusForm(instance=order.orderstatus)
	context = {
		"order_product":order_product,
		# "form":form,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def cancel_orders_accept(request, id):
	if request.method == "POST":
		amount = request.POST.get("cancel_amount")
		order_product = CancelOrder.objects.get(id=id)
		order_product.cancel_amount = amount
		order_product.is_accepted = True
		order_product.save()

	return redirect(request.META.get('HTTP_REFERER'))

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def cancel_orders_regect(request, id):
	order_product = CancelOrder.objects.get(id=id)
	order_product.is_rejected = True
	order_product.save()
	return redirect(request.META.get('HTTP_REFERER'))


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def orders_mark_as_shipment(request, id):
	order = Order.objects.get(id=id)
	if request.method == "POST":
		form = OrderStatusForm(request.POST, instance=order.orderstatus)
		if form.is_valid():
			form.save()
			print("form valid")

			order.is_complete = True
			order.save()
			for vorder in order.vendororder_set.all():
				vorder.is_complete = True
				vorder.save()
		else:
			print(form.errors)


	return redirect("/dashboard/admin/all-orders/")


#Coupons
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def coupons(request):
	template_name = "dashboard/owner/coupons.html"
	coupons = CouponCode.objects.all().order_by("-id")
	form = CouponCodeForm()
	context = {
		"vendor_menu":False,
		"admin_menu":True,
		"coupons":coupons,
		"form":form,
	}
	return render(request, template_name, context)

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def coupons_create(request):
	if request.method == "POST":
		form = CouponCodeForm(request.POST)
		if  form.is_valid():
			form.save()
	return redirect("/dashboard/admin/coupons/")


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def coupons_update(request, id):
	data = dict()
	coupon = CouponCode.objects.get(id=id)
	if request.method == "POST":
		form = CouponCodeForm(request.POST, instance=coupon)
		if  form.is_valid():
			form.save()
		return redirect("/dashboard/admin/coupons/")

	template_name = "dashboard/owner/coupon_update.html"
	context = {
		"form": CouponCodeForm(instance=coupon),
		"coupon":coupon,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)

# SETTINGS
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def dashboard_properties(request):
	template_name = "dashboard/owner/properties.html"
	logo_title_obj = SiteLogoAndTitle.objects.last()
	if logo_title_obj:
		logo_form = SiteLogoAndTitleForm(instance=logo_title_obj)
	else:
		logo_form = SiteLogoAndTitleForm()

	context = {
		"vendor_menu":False,
		"admin_menu":True,
		"logo_form":logo_form,
		"logo_title_obj":logo_title_obj,
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def dashboard_properties_logo_create_update(request):
	logo_title_obj = SiteLogoAndTitle.objects.last()
	if logo_title_obj:
		logo_form = SiteLogoAndTitleForm(request.POST, request.FILES or None, instance=logo_title_obj)
	else:
		logo_form = SiteLogoAndTitleForm(request.POST, request.FILES or None)

	if  logo_form.is_valid():
		logo_form.save()

	return redirect("/dashboard/admin/properties/")



@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def dashboard_shipping_method(request):
	template_name = "dashboard/owner/shipping_method.html"
	free_shipping_obj = FreeShippingSettings.objects.last()
	glossary_obj = GroceryShippingArea.objects.last()
	shipping_price = ShippingPriceSettings.objects.last()
	if glossary_obj:
		glossary_form = GroceryShippingAreaForm(instance=glossary_obj)
	else:
		glossary_form = GroceryShippingAreaForm()

	if free_shipping_obj:
		free_form = FreeShippingSettingsForm(instance=free_shipping_obj)
	else:
		free_form = FreeShippingSettingsForm()

	if shipping_price:
		shipping_form = ShippingPriceSettingsForm(instance=shipping_price)
	else:
		shipping_form = ShippingPriceSettingsForm()

	context = {
		"free_shipping_obj":free_shipping_obj,
		"shipping_form":shipping_form,
		"shipping_price":shipping_price,
		"glossary_obj":glossary_obj,
		"glossary_form":glossary_form,
		"free_form":free_form,
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def dashboard_free_shipping_create_or_update(request):
	free_shipping_obj = FreeShippingSettings.objects.last()
	if request.method == "POST":
		if free_shipping_obj:
			form = FreeShippingSettingsForm(request.POST, instance=free_shipping_obj)
		else:
			form = FreeShippingSettingsForm(request.POST)
		if  form.is_valid():
			form.save()
	return redirect("/dashboard/admin/shipping-method/")


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def dashboard_shipping_price_create_or_update(request):
	shipping_price = ShippingPriceSettings.objects.last()
	if request.method == "POST":
		if shipping_price:
			form = ShippingPriceSettingsForm(request.POST, instance=shipping_price)
		else:
			form = ShippingPriceSettingsForm(request.POST)

		if form.is_valid():
			form.save()

	return redirect("/dashboard/admin/shipping-method/")


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def dashboard_glossary_zipcode_create_or_update(request):
	grocery_obj = GroceryShippingArea.objects.last()
	if request.method == "POST":
		if grocery_obj:
			form = GroceryShippingAreaForm(request.POST, instance=grocery_obj)
		else:
			form = GroceryShippingAreaForm(request.POST)
		if  form.is_valid():
			form.save()
	return redirect("/dashboard/admin/shipping-method/")


#DASHBOARD SLIDER
@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def dashboard_slider(request):
	template_name = "dashboard/owner/slider.html"
	sliders = ProductSlider.objects.all()
	form = SliderForm()
	context = {
		"sliders":sliders,
		"vendor_menu":False,
		"admin_menu":True,
		"form":form,
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def dashboard_slider_create(request):
	if request.method == "POST":
		form = SliderForm(request.POST, request.FILES or None)
		if  form.is_valid():
			form.save()
	return redirect("/dashboard/admin/sliders/")


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def dashboard_slider_update(request, id):
	data = dict()
	slider = ProductSlider.objects.get(id=id)
	if request.method == "POST":
		form = SliderForm(request.POST, request.FILES or None, instance=slider)
		if  form.is_valid():
			form.save()
		return redirect("/dashboard/admin/sliders/")

	template_name = "dashboard/owner/slider_update.html"
	context = {
		"form": SliderForm(instance=slider),
		"slider":slider,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def dashboard_slider_delete(request, id):
	slider = ProductSlider.objects.get(id=id)
	slider.delete()
	return redirect("/dashboard/admin/sliders/")



@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def mobile_apps_view(request):
	template_name = "dashboard/owner/mobile_apps_view.html"
	apps = MobileApps.objects.last()
	if request.method == "POST":
		if apps:
			form = MobileAppsForm(request.POST,instance=apps)
		else:
			form = MobileAppsForm(request.POST)

		if form.is_valid():
			form.save()

	if apps:
		form = MobileAppsForm(instance=apps)
	else:
		form = MobileAppsForm()

	context = {
		"form":form,
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def about_us_view(request):
	template_name = "dashboard/owner/about_us_view.html"
	about = AboutUs.objects.last()
	if request.method == "POST":
		if about:
			form = AboutUsForm(request.POST,instance=about)
		else:
			form = AboutUsForm(request.POST)

		if form.is_valid():
			form.save()

	if about:
		form = AboutUsForm(instance=about)
	else:
		form = AboutUsForm()

	context = {
		"form":form,
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def conract_us_view(request):
	template_name = "dashboard/owner/conract_us_view.html"
	contact = ContactUs.objects.last()
	if request.method == "POST":
		if contact:
			form = ContactUsForm(request.POST,instance=contact)
		else:
			form = ContactUsForm(request.POST)

		if form.is_valid():
			form.save()

	if contact:
		form = ContactUsForm(instance=contact)
	else:
		form = ContactUsForm()

	context = {
		"form":form,
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def faq_view(request):
	form = FAQForm()
	faqs = FAQ.objects.all().order_by("-id")
	template_name = "dashboard/owner/faq_view.html"
	if request.method == "POST":
		form = FAQForm(request.POST)
		if form.is_valid():
			form.save()
	context = {
		"form":form,
		"vendor_menu":False,
		"admin_menu":True,
		"faqs":faqs,
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def load_faq_view(request, id):
	data = dict()
	faq = FAQ.objects.get(id=id)
	template_name = "dashboard/owner/faq_update_view.html"
	form = FAQForm(instance=faq)
	context = {
		"form":form,
		"faq":faq,
		"vendor_menu":False,
		"admin_menu":True,
	}
	# data['update_html'] = render_to_string(template_name, context, request=request)
	return render(request, template_name, context)

@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def update_faq_view(request, id):
	faq = FAQ.objects.get(id=id)
	if request.method == "POST":
		form = FAQForm(request.POST, instance=faq)
		if form.is_valid():
			form.save()

	return redirect("/dashboard/admin/faq-view/")



@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def privacy_policy_view(request):
	template_name = "dashboard/owner/privacy_policy_view.html"
	privacy_policy = PrivacyPolicy.objects.last()
	if request.method == "POST":
		if privacy_policy:
			form = PrivacyPolicyForm(request.POST,instance=privacy_policy)
		else:
			form = PrivacyPolicyForm(request.POST)

		if form.is_valid():
			form.save()

	if privacy_policy:
		form = PrivacyPolicyForm(instance=privacy_policy)
	else:
		form = PrivacyPolicyForm()

	context = {
		"form":form,
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)


@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def terms_of_use_view(request):
	template_name = "dashboard/owner/terms_of_use_view.html"
	terms_of_use = TermsOfUse.objects.last()
	if request.method == "POST":
		if terms_of_use:
			form = TermsOfUseForm(request.POST,instance=terms_of_use)
		else:
			form = TermsOfUseForm(request.POST)

		if form.is_valid():
			form.save()

	if terms_of_use:
		form = TermsOfUseForm(instance=terms_of_use)
	else:
		form = TermsOfUseForm()

	context = {
		"form":form,
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)



@super_user_permission_requird
@login_required(login_url='/account/vendor/login/')
def refund_return_policy_view(request):
	template_name = "dashboard/owner/refund_return_policy_view.html"
	refund_return_policy = RefundReturnPolicy.objects.last()
	if request.method == "POST":
		if refund_return_policy:
			form = RefundReturnPolicyForm(request.POST,instance=refund_return_policy)
		else:
			form = RefundReturnPolicyForm(request.POST)

		if form.is_valid():
			form.save()

	if refund_return_policy:
		form = RefundReturnPolicyForm(instance=refund_return_policy)
	else:
		form = RefundReturnPolicyForm()

	context = {
		"form":form,
		"vendor_menu":False,
		"admin_menu":True,
	}
	return render(request, template_name, context)

# VENDOR PAYMAT BY ADMIN
@login_required(login_url='/account/vendor/login/')
@super_user_permission_requird
def vendor_deu_payment(request):
	template_name = "dashboard/owner/deu_payment.html"
	total_amount = 0
	pending_total_amount = 0
	today = datetime.now().date()
	for un_released_order in VendorOrder.objects.filter(is_complete=True, is_payment_released=False, is_paid=False, is_payment_request_sent=False):
		if un_released_order.get_payment_released_date() <= today:
			un_released_order.is_payment_released = True
			un_released_order.save()

	vendor_payable_orders = VendorOrder.objects.filter(is_paid=False, is_payment_released=True, is_complete=True, is_payment_request_sent=False)
	for vorder in vendor_payable_orders:
		total_amount = total_amount + vorder.order_subtotal_amount()

	pending_payment_rquests = VendorPaymentRequest.objects.filter(is_paid=False)
	for pending_payment in pending_payment_rquests:
		pending_total_amount = pending_total_amount + pending_payment.pay_amount
	
	context = {
		"vendor_menu":False,
		"admin_menu":True,
		"vendor_payable_orders":vendor_payable_orders,
		"total_amount":total_amount,
		"pending_payment_rquests":pending_payment_rquests,
		"pending_total_amount":pending_total_amount,
	}
	return render(request, template_name, context)


@login_required(login_url='/account/vendor/login/')
@super_user_permission_requird
def load_vendor_payment_request(request, id):
	data = dict()
	request_obj = VendorPaymentRequest.objects.get(id=id)
	template_name = "dashboard/owner/payment_request_details.html"
	form = VendorPaymentRequestForm()
	context = {
		"request_obj":request_obj,
		"form":form,
	}
	data['html_form'] = render_to_string(template_name, context, request=request)
	return JsonResponse(data)


@login_required(login_url='/account/vendor/login/')
@super_user_permission_requird
def pay_vendor_payment_request(request, id):
	if request.method == "POST":
		request_obj = VendorPaymentRequest.objects.get(id=id)
		form = VendorPaymentRequestForm(request.POST, instance=request_obj)
		if form.is_valid():
			form = form.save()
			form.is_paid = True
			form.save()

	return redirect("/dashboard/admin/vendor-payment-history/")




@login_required(login_url='/account/vendor/login/')
@super_user_permission_requird
def vendor_payment_history(request):
	paid_total_amount = 0
	template_name = "dashboard/owner/payment_history.html"

	paid_payment_rquests = VendorPaymentRequest.objects.filter(is_paid=True)
	for paid_payment in paid_payment_rquests:
		paid_total_amount = paid_total_amount + paid_payment.pay_amount
	
	context = {
		"vendor_menu":False,
		"admin_menu":True,
		"paid_payment_rquests":paid_payment_rquests,
		"paid_total_amount":paid_total_amount,
	}
	return render(request, template_name, context)




