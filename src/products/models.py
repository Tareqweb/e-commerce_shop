from django.db import models
from vendors.models import Vendor
from django.contrib.auth.models import User
from django.utils.text import slugify
from PIL import Image
from io import BytesIO
from django.core.files import File
from ckeditor_uploader.fields import RichTextUploadingField
# Create your models here.


class Category(models.Model):
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
	position = models.PositiveIntegerField(default=0)
	show_product_by_subcategory = models.BooleanField(default=False)
	express_shipping = models.BooleanField(default=False)
	hide_category = models.BooleanField(default=False)
	category_filter = models.BooleanField(default=True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super().save(*args, **kwargs)



	def product_count(self):
		return Product.objects.filter(
			category__sub_category__category=self,
			approved=True,
			deactivate=False,
			rejected=False
			).count()

	def get_product_list(self):
		return Product.objects.filter(
			category__sub_category__category=self,
			approved=True,
			deactivate=False,
			rejected=False
			).order_by("?")[:18]

	def get_product_list_api(self):
		return Product.objects.filter(
			category__sub_category__category=self,
			approved=True,
			deactivate=False,
			rejected=False
			).order_by("?")

class SubCategory(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)
	hide_sub_category = models.BooleanField(default=False)

	def __str__(self):
		return "{} - {}".format(self.category.name, self.name)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	def product_count(self):
		return Product.objects.filter(
			category__sub_category=self,
			approved=True,
			deactivate=False,
			rejected=False
			).count()

	def get_product_list(self):
		return Product.objects.filter(
			category__sub_category=self,
			approved=True,
			deactivate=False,
			rejected=False
			).order_by("?")[:18]

	def get_product_list_api(self):
		return Product.objects.filter(
			category__sub_category=self,
			approved=True,
			deactivate=False,
			rejected=False
			).order_by("?")


class ProductCategory(models.Model):
	sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200, unique=True, null=True, blank=True)

	def __str__(self):
		return "{} - {} - {}".format(self.sub_category.category.name,self.sub_category.name ,self.name)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super().save(*args, **kwargs)


	def product_count(self):
		return Product.objects.filter(
			category=self,
			approved=True,
			deactivate=False,
			rejected=False
			).count()

	def get_product_list(self):
		return Product.objects.filter(
			category=self,
			approved=True,
			deactivate=False,
			rejected=False
			).order_by("?")[:18]


	def get_product_list_api(self):
		return Product.objects.filter(
			category=self,
			approved=True,
			deactivate=False,
			rejected=False
			).order_by("?")

class ProductSize(models.Model):
	size = models.CharField(max_length=200)
	
	def __str__(self):
		return self.size


class ProductColor(models.Model):
	color = models.CharField(max_length=200)

	def __str__(self):
		return self.color


class Product(models.Model):
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
	name = models.CharField(max_length=250)
	slug = models.SlugField(max_length=250, unique=True, null=True, blank=True)
	price = models.DecimalField(max_digits=19, decimal_places=2, default=0.00)
	discount_percentage = models.PositiveIntegerField(default=0)
	tax_percentage = models.PositiveIntegerField(default=0)
	tax_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0.00)
	sell_price = models.DecimalField(max_digits=19, decimal_places=2, default=0.00)
	image = models.ImageField(upload_to="product_image")
	image_sm = models.ImageField(upload_to='product_image', null=True, blank=True)
	category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
	short_description = models.TextField(null=True, blank=True)
	description = RichTextUploadingField()
	size = models.ManyToManyField(ProductSize, blank=True)
	color = models.ManyToManyField(ProductColor, blank=True)
	stock = models.PositiveIntegerField(default=500)
	

	width  = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True) #cm
	height  = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True) #cm
	depth = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True) #cm
	weight = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True) #ib

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	approved = models.BooleanField(default=False)
	deactivate = models.BooleanField(default=False)
	rejected = models.BooleanField(default=False)

	def __init__(self, *args, **kwargs):
		super(Product, self).__init__(*args, **kwargs)
		self.old_image = self.image

	def get_price(self):
		if self.is_discount_available():
			return self.sell_price
		else:
			return self.price

	def __str__(self):
		return self.name

	def get_sell_price(self):
		price = self.price
		sell_price = self.discount_percentage * self.price / 100
		return price - sell_price

	def is_discount_available(self):
		if self.discount_percentage > 0 and self.price > 0 and self.sell_price:
			return True
		else:
			return False

	def get_tax_amount(self):
		return self.tax_percentage * self.get_sell_price() / 100

	def is_size(self):
		return True if self.size.count() > 0 else False

	def is_color(self):
		return True if self.color.count() > 0 else False

	def get_releted_products(self):
		return self.category.product_set.exclude(id=self.id).order_by("?")[:6]

	def get_size_list(self):
		return self.size.values_list('size', flat=True)

	def get_color_list(self):
		return self.color.values_list('color', flat=True)

	def total_order(self):
		return self.vendororderproduct_set.count()

	def total_review_star(self):
		try:
			return self.productreview_set.aggregate(star=models.Sum(models.F('star'), output_field=models.FloatField()))['star'] / self.total_review()
		except Exception as e:
			return 0

	def total_review_list(self):
		return self.productreview_set.all()

	def total_review(self):
		return self.productreview_set.count()

	def total_5_review(self):
		return self.productreview_set.filter(star=5).count()

	def total_5_review_percentage(self):
		try:
			return self.total_5_review() * 100 / self.total_review_list().count()
		except Exception as e:
			return 0

	def total_4_review(self):
		return ProductReview.objects.filter(product=self, star=4).count()

	def total_4_review_percentage(self):
		try:
			return self.total_4_review() * 100 / self.total_review_list().count()
		except Exception as e:
			return 0

	def total_3_review(self):
		return ProductReview.objects.filter(product=self, star=3).count()

	def total_3_review_percentage(self):
		try:
			return self.total_3_review() * 100 / self.total_review_list().count()
		except Exception as e:
			return 0

	def total_2_review(self):
		return ProductReview.objects.filter(product=self, star=2).count()

	def total_2_review_percentage(self):
		try:
			return self.total_2_review() * 100 / self.total_review_list().count()
		except Exception as e:
			return 0

	def total_1_review(self):
		return ProductReview.objects.filter(product=self, star=1).count()

	def total_1_review_percentage(self):
		try:
			return self.total_1_review() * 100 / self.total_review_list().count()
		except Exception as e:
			return 0

	def image_compression(self,image):
		sm_size = 480, 480
		# new_image_name = image.name.split("/")[-1].split(".")[0]
		new_image_name = slugify(image.name.split(".")[0])

		base_image = Image.open(image)

		fill_color = '#ffffff'
		if base_image.mode in ('RGBA', 'LA'):
			background = Image.new(base_image.mode[:-1], base_image.size, fill_color)
			background.paste(base_image, base_image.split()[-1])
			base_image = background

		im2 = base_image.copy()

		im_lg = BytesIO()
		im_sm = BytesIO()

		base_image.save(im_lg, format="webp", optimize=True, quality=75)

		im2.thumbnail(sm_size)
		im2.save(im_sm, format="webp", quality=85)

		new_name_lg = "{}_l.webp".format(new_image_name)
		new_name_sm = "{}_m.webp".format(new_image_name)

		base_img = File(im_lg, name=new_name_lg)
		sm_image = File(im_sm, name=new_name_sm)

		return base_img, sm_image

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		self.sell_price = self.price - self.discount_percentage * self.price / 100
		self.tax_amount = self.tax_percentage * self.sell_price / 100

		if not self.pk:
			base_img, sm_image = self.image_compression(self.image)
			self.image = base_img
			self.image_sm = sm_image
		else:
			if not self.old_image == self.image:
				base_img, sm_image = self.image_compression(self.image)
				self.image = base_img
				self.image_sm = sm_image
			else:
				print("yesss same")

		super().save(*args, **kwargs)


class ProductCommissionPercentage(models.Model):
	product = models.OneToOneField(Product, on_delete=models.CASCADE)
	commission = models.DecimalField(max_digits=19, decimal_places=2, default=2.00)

	def __str__(self):
		return self.product.name


class ProductSizeGuide(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	guide_col1 = models.CharField(max_length=200, null=True, blank=True)
	guide_col2 = models.CharField(max_length=200, null=True, blank=True)
	guide_col3 = models.CharField(max_length=200, null=True, blank=True)
	guide_col4 = models.CharField(max_length=200, null=True, blank=True)
	guide_col5 = models.CharField(max_length=200, null=True, blank=True)
	guide_col6 = models.CharField(max_length=200, null=True, blank=True)
	guide_col7 = models.CharField(max_length=200, null=True, blank=True)
	guide_col8 = models.CharField(max_length=200, null=True, blank=True)

	def __str__(self):
		return self.product.name

class ProductSizeMeasurement(models.Model):
	product = models.OneToOneField(Product, on_delete=models.CASCADE)
	content = RichTextUploadingField(null=True, blank=True)

	def __str__(self):
		return self.product.name


class ProductImage(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	image = models.ImageField(upload_to="product_image", null=True, blank=True)
	color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, null=True, blank=True)
	def __str__(self):
		return self.product.name


class ProductReview(models.Model):
	vendor_order_id = models.CharField(max_length=100)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	star = models.PositiveIntegerField()
	comment = models.TextField(null=True, blank=True)
	image = models.ImageField(upload_to="review_product_image", null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.product.name


class ProductWishList(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)

	def __str__(self):
		return self.product.name


class RecentlyViewedProducts(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)

	def __str__(self):
		return self.product.name






