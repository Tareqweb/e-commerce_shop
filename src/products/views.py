from django.shortcuts import render, redirect
from django.contrib import messages
from .models import (
	Product, 
	Category, 
	SubCategory, 
	ProductCategory, 
	ProductWishList,
	ProductSize,
	ProductColor,
	ProductReview,
	RecentlyViewedProducts
	)
from vendors.models import Vendor
from orders.models import Cart
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from dashboard.models import GroceryShippingArea

# Create your views here.

def product_global_filter(request):
	template_name = "products/filter_products.html"
	search_q = request.GET.get('q')
	search_filter = request.GET.get('filter')
	page_number = request.GET.get('page')

	category_list = []
	subcategory_list = []
	innercaegory_list = []
	size_list = []
	color_list = []
	brand_list = []
	price_range = []

	category = request.GET.get('category')
	subcategory = request.GET.get('subcategory')
	innercaegory = request.GET.get('innercaegory')
	size = request.GET.get('size')
	color = request.GET.get('color')
	brand = request.GET.get('brand')
	price_min = request.GET.get('price_min')
	price_max = request.GET.get('price_max')

	if category:
		category_list = category.split(",")
	if subcategory:
		subcategory_list = subcategory.split(",")
	if innercaegory:
		innercaegory_list = innercaegory.split(",")
	if size:
		size_list = size.split(",")
	if color:
		color_list = color.split(",")
	if brand:
		brand_list = brand.split(",")
	if price_min and price_max:
		price_range.append(price_min)
		price_range.append(price_max)



	all_products = Product.objects.filter(approved=True, deactivate=False, rejected=False)

	if search_q:
		print("Search")
		all_products = all_products.filter(
			Q(name__icontains=search_q)|
			Q(short_description__icontains=search_q)|
			Q(description__icontains=search_q)|
			Q(vendor__full_name__icontains=search_q)|
			Q(vendor__phone__icontains=search_q)|
			Q(vendor__mobile__icontains=search_q)|
			Q(vendor__company_name__icontains=search_q)
			).distinct().order_by("?")

	elif search_filter:
		print("Filter")
		all_products = all_products.filter(
			Q(price__range=price_range) &
			Q(category__sub_category__category__name__in=category_list)|
			Q(category__sub_category__name__in=subcategory_list)|
			Q(category__name__in=innercaegory_list)|
			Q(size__size__in=size_list)|
			Q(color__color__in=color_list)|
			Q(vendor__company_name__in=brand_list)
			).distinct().order_by("?")

	
	paginator = Paginator(all_products, 40)
	products = paginator.get_page(page_number)

	categorys = Category.objects.all().order_by("position")
	sub_categorys = SubCategory.objects.all().order_by("-id")
	inner_categorys = ProductCategory.objects.all().order_by("-id")

	product_sizes = ProductSize.objects.all()
	product_colors = ProductColor.objects.all()
	vendors = Vendor.objects.filter(active=True)

	context = {
		"products":products,
		"categorys":categorys,
		"sub_categorys":sub_categorys,
		"inner_categorys":inner_categorys,
		"product_sizes":product_sizes,
		"product_colors":product_colors,
		"vendors":vendors,
		"search_q":search_q,
		"category_list":category_list,
		"subcategory_list":subcategory_list,
		"innercaegory_list":innercaegory_list,
		"size_list":size_list,
		"color_list":color_list,
		"brand_list":brand_list,
		"price_min":price_min,
		"price_max":price_max,
		"search_filter":search_filter,
		"total_product":len(products),
	}
	return render(request, template_name, context)



def search_product(request):
	template_name = "products/search_products.html"
	page_number = request.GET.get('page')
	search_q = request.GET.get('q')
	if search_q:
		all_products = Product.objects.filter(
			Q(name__icontains=search_q)|
			Q(short_description__icontains=search_q)|
			Q(description__icontains=search_q)|
			Q(vendor__full_name__icontains=search_q)|
			Q(vendor__phone__icontains=search_q)|
			Q(vendor__mobile__icontains=search_q)|
			Q(vendor__company_name__icontains=search_q)
			).distinct().order_by("?")
	else:
		all_products = Product.objects.all().order_by("?")

	paginator = Paginator(all_products, 40)
	products = paginator.get_page(page_number)
	context = {
		"products":products,
		"search_q":search_q,
	}
	return render(request, template_name, context)


def product_details(request, slug):
	template_name = "products/product_details.html"
	product = Product.objects.get(slug=slug)
	grocery_obj = GroceryShippingArea.objects.last()
	releted_products = Product.objects.filter(category=product.category).order_by("?")
	recently_views = []

	if request.user.is_authenticated:
		recently_views = RecentlyViewedProducts.objects.filter(user=request.user).order_by("?")
		
		if not RecentlyViewedProducts.objects.filter(user=request.user, product=product).exists():
			RecentlyViewedProducts.objects.create(user=request.user, product=product)



	context= {
		"product":product,
		"grocery_obj":grocery_obj,
		"releted_products":releted_products[:16],
		"recently_views": recently_views[:16]
	}
	return render(request, template_name,context)

def check_zip_code(request, zipcode):
	data = dict()
	grocery_obj = GroceryShippingArea.objects.last()
	if grocery_obj:
		grocery_area = grocery_obj.zipcodes.split(",")
	else:
		grocery_area = []

	if zipcode in grocery_area:
		data['message'] = "<span style='color:blue'>CONGRATULATIONS!</span> we delivery in this area".format(zipcode)
		data['status'] = True
	else:
		data['message'] = "<span style='color:red'>SORRY!</span> we are not delivery in this area right now.".format(zipcode)

	return JsonResponse(data)

def category_details(request, slug):
	template_name = "products/product_category_view.html"
	page_number = request.GET.get('page')
	products = []
	category_name = ""

	try:
		category = Category.objects.get(slug=slug)
	except Exception as e:
		category = None

	if category:
		all_products = Product.objects.filter(category__sub_category__category=category, approved=True, deactivate=False, rejected=False)
		paginator = Paginator(all_products, 40)
		products = paginator.get_page(page_number)
		category_name = category.name
		filter_show = category.category_filter

	categorys = Category.objects.all().order_by("position")
	sub_categorys = SubCategory.objects.all().order_by("-id")
	inner_categorys = ProductCategory.objects.all().order_by("-id")

	product_sizes = ProductSize.objects.all()
	product_colors = ProductColor.objects.all()
	vendors = Vendor.objects.filter(active=True)
	
	context = {
		"products":products,
		"category_name":category_name,
		"categorys":categorys,
		"sub_categorys":sub_categorys,
		"inner_categorys":inner_categorys,
		"product_sizes":product_sizes,
		"product_colors":product_colors,
		"vendors":vendors,
		"filter_show":filter_show
	}

	return render(request, template_name,context)

def sub_category_details(request, slug):
	template_name = "products/product_category_view.html"
	page_number = request.GET.get('page')
	products = []
	category_name = ""
	try:
		category = SubCategory.objects.get(slug=slug)
	except Exception as e:
		category = None

	if category:
		all_products = Product.objects.filter(category__sub_category=category, approved=True, deactivate=False, rejected=False)
		paginator = Paginator(all_products, 40)
		products = paginator.get_page(page_number)
		category_name = category.name
		filter_show = category.category.category_filter

	categorys = Category.objects.all().order_by("position")
	sub_categorys = SubCategory.objects.all().order_by("-id")
	inner_categorys = ProductCategory.objects.all().order_by("-id")

	product_sizes = ProductSize.objects.all()
	product_colors = ProductColor.objects.all()
	vendors = Vendor.objects.filter(active=True)
	
	context = {
		"products":products,
		"filter_show":filter_show,
		"category_name":category_name,
		"categorys":categorys,
		"sub_categorys":sub_categorys,
		"inner_categorys":inner_categorys,
		"product_sizes":product_sizes,
		"product_colors":product_colors,
		"vendors":vendors,
	}

	return render(request, template_name,context)

def product_category_details(request, slug):
	template_name = "products/product_category_view.html"
	page_number = request.GET.get('page')
	products = []
	category_name = ""
	try:
		category = ProductCategory.objects.get(slug=slug)
	except Exception as e:
		category = None

	if category:
		all_products = Product.objects.filter(category=category, approved=True, deactivate=False, rejected=False)
		paginator = Paginator(all_products, 40)
		products = paginator.get_page(page_number)
		category_name = category.name
		filter_show = category.sub_category.category.category_filter

	categorys = Category.objects.all().order_by("position")
	sub_categorys = SubCategory.objects.all().order_by("-id")
	inner_categorys = ProductCategory.objects.all().order_by("-id")

	product_sizes = ProductSize.objects.all()
	product_colors = ProductColor.objects.all()
	vendors = Vendor.objects.filter(active=True)
	
	context = {
		"products":products,
		"filter_show":filter_show,
		"category_name":category_name,
		"categorys":categorys,
		"sub_categorys":sub_categorys,
		"inner_categorys":inner_categorys,
		"product_sizes":product_sizes,
		"product_colors":product_colors,
		"vendors":vendors,
	}
	return render(request, template_name,context)



def add_to_wishlist(request, id):
	product = Product.objects.get(id=id)
	try:
		redirect_url = request.META.get('HTTP_REFERER')
	except Exception as e:
		redirect_url = "/product/{}/".format(product.slug)
	try:
		ProductWishList.objects.create(
			user=request.user,
			product=product
			)
		messages.success(request, 'Added To WishList')
	except Exception as e:
		print(e)
		
	return redirect(redirect_url)


def remove_from_wishlist(request, id):
	product = Product.objects.get(id=id)
	try:
		redirect_url = request.META.get('HTTP_REFERER')
	except Exception as e:
		redirect_url = "/product/{}/".format(product.slug)
	try:
		ProductWishList.objects.filter(
			user=request.user,
			product=product
			).last().delete()
	except Exception as e:
		print(e)
	return redirect(redirect_url)



def daily_deals(request):
	template_name = "products/product_category_view.html"
	page_number = request.GET.get('page')
	products = []
	category_name = "Daily Deals"
	all_products = Product.objects.filter(approved=True, deactivate=False, rejected=False, discount_percentage__gt=0)
	paginator = Paginator(all_products, 40)
	products = paginator.get_page(page_number)

	categorys = Category.objects.all().order_by("position")
	sub_categorys = SubCategory.objects.all().order_by("-id")
	inner_categorys = ProductCategory.objects.all().order_by("-id")

	product_sizes = ProductSize.objects.all()
	product_colors = ProductColor.objects.all()
	vendors = Vendor.objects.filter(active=True)
	
	context = {
		"products":products,
		"category_name":category_name,
		"categorys":categorys,
		"sub_categorys":sub_categorys,
		"inner_categorys":inner_categorys,
		"product_sizes":product_sizes,
		"product_colors":product_colors,
		"vendors":vendors,
	}
	return render(request, template_name,context)

