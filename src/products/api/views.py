from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from products.models import (
	Category, 
	Product,
	SubCategory,
	ProductCategory
	)
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from dashboard.models import GroceryShippingArea, ProductSlider
from django.db.models import Q
# from rest_framework.permissions import IsAuthenticated




class HomeView(APIView):
	def get(self, request, format=None):
		content = {'category':[]}
		for category in Category.objects.all().order_by("position"):
			if category.show_product_by_subcategory:
				for subcategory in category.subcategory_set.all():
					if subcategory.product_count() > 0:
						category_dict = {}
						category_dict["name"] = subcategory.name
						category_dict["id"] = subcategory.id
						category_dict["is_sub_category"] = True
						category_dict["products"] = []
						for product in subcategory.get_product_list():
							product_list = {}
							product_list["name"] = product.name[:25]
							product_list["id"] = product.id
							product_list["price"] = product.price
							product_list["sell_price"] = product.sell_price
							product_list["is_discounted"] = True if product.discount_percentage > 0 else False
							product_list["discount_percentage"] = product.discount_percentage
							product_list["image"] = "{}{}".format(self.request.build_absolute_uri('/')[:-1],product.image_sm.url)
							category_dict["products"].append(product_list)
						content['category'].append(category_dict)

			else:
				if category.product_count() > 0:
					category_dict = {}
					category_dict["name"] = category.name
					category_dict["id"] = category.id
					category_dict["is_sub_category"] = False
					category_dict["products"] = []
					for product in category.get_product_list():
						product_list = {}
						product_list["name"] = product.name[:25]
						product_list["id"] = product.id
						product_list["price"] = product.price
						product_list["sell_price"] = product.sell_price
						product_list["is_discounted"] = True if product.discount_percentage > 0 else False
						product_list["discount_percentage"] = product.discount_percentage
						product_list["image"] = "{}{}".format(self.request.build_absolute_uri('/')[:-1],product.image_sm.url)
						category_dict["products"].append(product_list)
					content['category'].append(category_dict)
		return Response(content)


class ProductDetailsView(APIView):
	def get(self, request, pk, format=None):
		content = {}
		try:
			product = Product.objects.get(pk=pk)
		except Exception as e:
			product = None

		if product:
			content["name"] = product.name
			content["id"] = product.id
			content["price"] = product.price
			content["sell_price"] = product.sell_price
			content["is_discounted"] = True if product.discount_percentage > 0 else False
			content["discount_percentage"] = product.discount_percentage
			content["vendor"] = product.vendor.get_name()
			content["vendor_id"] = product.vendor.id
			content["category_id"] = product.category.id
			content["category_name"] = product.category.name
			content["short_description"] = product.short_description
			content["description"] = product.description
			content["is_show_size"] = product.is_size()
			content["is_show_color"] = product.is_color()
			content["is_out_of_stock"] = True if product.stock < 2 else False
			content["stock"] = product.stock
			content["images"] = []
			content["size"] = product.get_size_list()
			content["color"] = product.get_color_list()
			content["images"].append({
				"image_url": "{}{}".format(self.request.build_absolute_uri('/')[:-1],product.image.url),
				"color": ""
				})
			for img in product.productimage_set.all():
				content["images"].append({
					"image_url": "{}{}".format(self.request.build_absolute_uri('/')[:-1],img.image.url),
					"color": img.color.color if img.color else ""
					})
		return Response(content)


@api_view(['GET'])
def category_list_api_view(request):
	category_list = []
	categorys = Category.objects.all().order_by("position")
	for category in categorys:
		category_list.append({
			"id": category.id,
			"name": category.name,
		})
	return Response(category_list)


@api_view(['GET'])
def sub_category_list_api_view(request, id):
	subcategory_list = {}
	category = Category.objects.get(id=id)
	subcategory_list = {
		"id": category.id,
		"name": category.name,
		"subcategorys": []
	}
	for subcategory in category.subcategory_set.all():
		subcat = {
			"id": subcategory.id,
			"name": subcategory.name,
			"innercategorys":[]
		}

		for innercategory in subcategory.productcategory_set.all():
			subcat['innercategorys'].append({
				"id": innercategory.id,
				"name": innercategory.name,
			})


		subcategory_list["subcategorys"].append(subcat)

	return Response(subcategory_list)


class ProductCategoryDetailsView(APIView):

	def get(self, request, pk, format=None):
		content = {
			'products':[]
		}
		
		category = Category.objects.get(id=pk)

		if category.product_count() > 0:
			content["name"] = category.name
			content["cat_id"] = category.id

			page_number = self.request.GET.get('page')
			paginator = Paginator(category.get_product_list_api(), 20)
			products = paginator.get_page(page_number)
			content['total_page_number'] = paginator.num_pages
			content['current_number'] = int(page_number) if page_number else 1
			content['total_page'] = paginator.num_pages
			content['current_page'] = self.request.build_absolute_uri("?")[:-1] + "/?page={}".format(int(page_number) if page_number else 1)
			content['next_page'] = self.request.build_absolute_uri("?")[:-1] + "/?page={}".format(int(page_number)+1 if page_number else 2)

			for product in products:
				product_list = {}
				product_images = []
				product_list["name"] = product.name[:25]
				product_list["id"] = product.id
				product_list["price"] = product.price
				product_list["sell_price"] = product.sell_price
				product_list["is_discounted"] = True if product.discount_percentage > 0 else False
				product_list["discount_percentage"] = product.discount_percentage
				product_list["image"] = "{}{}".format(self.request.build_absolute_uri('/')[:-1],product.image.url)
				
				content["products"].append(product_list)

		return Response(content)


class ProductSubCategoryDetailsView(APIView):
	def get(self, request, pk, format=None):
		content = {
			'products':[],
		}

		subcategory = SubCategory.objects.get(id=pk)

		if subcategory.product_count() > 0:
			content["name"] = subcategory.name
			content["cat_id"] = subcategory.id

			page_number = self.request.GET.get('page')
			paginator = Paginator(subcategory.get_product_list_api(), 20)
			products = paginator.get_page(page_number)
			content['total_page_number'] = paginator.num_pages
			content['current_number'] = int(page_number) if page_number else 1
			content['total_page'] = paginator.num_pages
			content['current_page'] = self.request.build_absolute_uri("?")[:-1] + "/?page={}".format(int(page_number) if page_number else 1)
			content['next_page'] = self.request.build_absolute_uri("?")[:-1] + "/?page={}".format(int(page_number)+1 if page_number else 2)

			for product in products:
				product_list = {}
				product_images = []
				product_list["name"] = product.name[:25]
				product_list["id"] = product.id
				product_list["price"] = product.price
				product_list["sell_price"] = product.sell_price
				product_list["is_discounted"] = True if product.discount_percentage > 0 else False
				product_list["discount_percentage"] = product.discount_percentage
				product_list["image"] = "{}{}".format(self.request.build_absolute_uri('/')[:-1],product.image.url)


				content["products"].append(product_list)

		return Response(content)



class ProductInnerCategoryDetailsView(APIView):
	def get(self, request, pk, format=None):
		content = {
		'products':[]
		}

		try:
			innercategory = ProductCategory.objects.get(id=pk)
		except Exception as e:
			innercategory = None

		if innercategory.product_count() > 0:
			content["name"] = innercategory.name
			content["cat_id"] = innercategory.id

			page_number = self.request.GET.get('page')
			paginator = Paginator(innercategory.get_product_list_api(), 20)
			products = paginator.get_page(page_number)
			content['total_page_number'] = paginator.num_pages
			content['current_number'] = int(page_number) if page_number else 1
			content['total_page'] = paginator.num_pages
			content['current_page'] = self.request.build_absolute_uri("?")[:-1] + "/?page={}".format(int(page_number) if page_number else 1)
			content['next_page'] = self.request.build_absolute_uri("?")[:-1] + "/?page={}".format(int(page_number)+1 if page_number else 2)
			
			for product in products:
				product_list = {}
				product_list["name"] = product.name[:25]
				product_list["id"] = product.id
				product_list["price"] = product.price
				product_list["sell_price"] = product.sell_price
				product_list["is_discounted"] = True if product.discount_percentage > 0 else False
				product_list["discount_percentage"] = product.discount_percentage
				product_list["image"] = "{}{}".format(self.request.build_absolute_uri('/')[:-1],product.image.url)
				

				content["products"].append(product_list)

		return Response(content)


@api_view(['GET'])
def daily_deals_api_view(request,min,max):
	content = {
		"products": []
	}
	page_number = request.GET.get('page')
	all_products = Product.objects.filter(approved=True, deactivate=False, rejected=False, discount_percentage__gte=min, discount_percentage__lte=max)
	paginator = Paginator(all_products, 20)
	products = paginator.get_page(page_number)

	content['total_page_number'] = paginator.num_pages
	content['current_number'] = int(page_number) if page_number else 1
	content['total_page'] = paginator.num_pages
	content['current_page'] = request.build_absolute_uri("?")[:-1] + "/?page={}".format(int(page_number) if page_number else 1)
	content['next_page'] = request.build_absolute_uri("?")[:-1] + "/?page={}".format(int(page_number)+1 if page_number else 2)
	
	for product in products:
		product_list = {}
		product_list["name"] = product.name[:25]
		product_list["id"] = product.id
		product_list["price"] = product.price
		product_list["sell_price"] = product.sell_price
		product_list["is_discounted"] = True if product.discount_percentage > 0 else False
		product_list["discount_percentage"] = product.discount_percentage
		product_list["image"] = "{}{}".format(request.build_absolute_uri('/')[:-1],product.image.url)

		content["products"].append(product_list)

	return Response(content)


@api_view(['POST'])
def verify_zip_code_api_view(request):
	if request.method == "POST":
		zip_code = request.data.get("code")
		grocery_obj = GroceryShippingArea.objects.last()
		if grocery_obj:
			grocery_area = grocery_obj.zipcodes.split(",")
		else:
			grocery_area = []

		if zip_code in grocery_area:
			return Response({"status": "success"})
		else:
			return Response({"status": "faild"})

	return Response({"status": "Bad Request"})


@api_view(['GET'])
def sliders_api_view(request):
	content = []
	sliders = ProductSlider.objects.all().order_by("-id")
	for slider in sliders:
		content.append({
			"image": "{}{}".format(request.build_absolute_uri('/')[:-1],slider.image.url)
			}) 

	return Response(content)



class ProductSearchView(APIView):
	def get(self, request, format=None):
		q = self.request.GET.get('q')
		content = {
			'products':[],
			'keyword': q
		}

		products = Product.objects.filter(
			Q(name__icontains=q)|
			Q(short_description__icontains=q)|
			Q(description__icontains=q)|
			Q(vendor__full_name__icontains=search_q)|
			Q(vendor__phone__icontains=search_q)|
			Q(vendor__mobile__icontains=search_q)|
			Q(vendor__company_name__icontains=q)
			).distinct().order_by("?")

		for product in products:
			product_list = {}
			product_list["name"] = product.name[:25]
			product_list["id"] = product.id
			product_list["price"] = product.price
			product_list["sell_price"] = product.sell_price
			product_list["is_discounted"] = True if product.discount_percentage > 0 else False
			product_list["discount_percentage"] = product.discount_percentage
			product_list["image"] = "{}{}".format(self.request.build_absolute_uri('/')[:-1],product.image.url)
			

			content["products"].append(product_list)

		return Response(content)


