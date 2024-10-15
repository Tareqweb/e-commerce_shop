from django.shortcuts import render
from django.core.paginator import Paginator
from products.models import Product, Category, SubCategory, ProductCategory ,ProductSize, ProductColor
from .models import Vendor
from django.db.models import Q
from iteration_utilities import unique_everseen
# Create your views here.

def vendor_details(request,id):
	template_name = "vendors/vendor_details.html"
	vendor = Vendor.objects.get(id=id)
	page_number = request.GET.get('page')
	all_products = Product.objects.filter(vendor=vendor).order_by("-id")
	paginator = Paginator(all_products, 40)
	products = paginator.get_page(page_number)

	inner_categorys = list(unique_everseen(all_products.filter(vendor=vendor).values_list("category__name", flat=True)))
	sub_categorys = list(unique_everseen(all_products.filter(vendor=vendor).values_list("category__sub_category__name", flat=True)))
	categorys = list(unique_everseen(all_products.filter(vendor=vendor).values_list("category__sub_category__category__name", flat=True)))

	print(inner_categorys)
	print(sub_categorys)
	print(categorys)

	# categorys = Category.objects.all().order_by("position")
	# sub_categorys = SubCategory.objects.all().order_by("-id")
	# inner_categorys = ProductCategory.objects.all().order_by("-id")

	# product_sizes = ProductSize.objects.all()
	# product_colors = ProductColor.objects.all()

	sizes = []
	colors = []
	for product in all_products:
		for c in product.color.all():
			colors.append(c.color)

		for s in product.size.all():
			sizes.append(s.size)


	product_sizes = list(unique_everseen(sizes))
	product_colors = list(unique_everseen(colors))

	context = {
		"products":products,
		"vendor":vendor,
		"total_product": all_products.count(),
		"categorys":categorys,
		"sub_categorys":sub_categorys,
		"inner_categorys":inner_categorys,
		"product_sizes":product_sizes,
		"product_colors":product_colors,
	}
	return render(request, template_name, context)



def product_vendor_filter(request,id):
	vendor = Vendor.objects.get(id=id)
	template_name = "vendors/vendor_filter_products.html"
	search_q = request.GET.get('q')
	search_filter = request.GET.get('filter')
	page_number = request.GET.get('page')

	category_list = []
	subcategory_list = []
	innercaegory_list = []
	size_list = []
	color_list = []
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
		print(color_list)
	if price_min and price_max:
		price_range.append(price_min)
		price_range.append(price_max)



	all_products = Product.objects.filter(vendor=vendor, approved=True, deactivate=False, rejected=False)


	inner_categorys = list(unique_everseen(all_products.values_list("category__name", flat=True)))
	sub_categorys = list(unique_everseen(all_products.values_list("category__sub_category__name", flat=True)))
	categorys = list(unique_everseen(all_products.values_list("category__sub_category__category__name", flat=True)))

	# product_sizes = ProductSize.objects.all()
	# product_colors = ProductColor.objects.all()


	sizes = []
	colors = []
	for product in all_products:
		for c in product.color.all():
			colors.append(c.color)

		for s in product.size.all():
			sizes.append(s.size)


	product_sizes = list(unique_everseen(sizes))
	product_colors = list(unique_everseen(colors))


	if search_filter:
		print("Filter")
		all_products = all_products.filter(
			Q(price__range=price_range) &
			Q(category__sub_category__category__name__in=category_list)|
			Q(category__sub_category__name__in=subcategory_list)|
			Q(category__name__in=innercaegory_list)|
			Q(size__size__in=size_list)|
			Q(color__color__in=color_list)
			).distinct().order_by("?")

	
	paginator = Paginator(all_products, 40)
	products = paginator.get_page(page_number)

	context = {
		"vendor":vendor,
		"products":products,
		"categorys":categorys,
		"sub_categorys":sub_categorys,
		"inner_categorys":inner_categorys,
		"product_sizes":product_sizes,
		"product_colors":product_colors,
		"category_list":category_list,
		"subcategory_list":subcategory_list,
		"innercaegory_list":innercaegory_list,
		"size_list":size_list,
		"color_list":color_list,
		"price_min":price_min,
		"price_max":price_max,
		"search_filter":search_filter,
		"total_product":len(products),
	}
	return render(request, template_name, context)
