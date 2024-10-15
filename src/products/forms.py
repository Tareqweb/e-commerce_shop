from django import forms
from django.forms import ModelForm, inlineformset_factory
from .models import (
	Product, 
	ProductImage, 
	Category, 
	SubCategory, 
	ProductCategory,
	ProductSize,
	ProductColor,
    ProductCommissionPercentage,
    ProductSizeGuide,
    ProductSizeMeasurement,
    ProductReview
	)


class ProductSizeForm(forms.ModelForm):
    class Meta:
        model = ProductSize
        exclude = ()

class ProductCommissionPercentageForm(forms.ModelForm):
    class Meta:
        model = ProductCommissionPercentage
        exclude = ['product']


class ProductColorForm(forms.ModelForm):
    class Meta:
        model = ProductColor
        exclude = ()


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['vendor', 'slug', 'approved', 'sell_price', 'tax_amount']
        widgets = {
            'image': forms.FileInput()
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        exclude = ['product', 'image_sm']
        widgets = {
            'image': forms.FileInput()
        }

class ProductSizeGuideForm(forms.ModelForm):
    class Meta:
        model = ProductSizeGuide
        exclude = ['product']

class ProductSizeMeasurementForm(forms.ModelForm):
    class Meta:
        model = ProductSizeMeasurement
        exclude = ['product']


def get_product_image_formset(ext): 
	return inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=ext)

def get_product_size_guid_formset(ext): 
    return inlineformset_factory(Product, ProductSizeGuide, form=ProductSizeGuideForm, extra=ext)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ['slug']

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        exclude = ['slug']


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        exclude = ['slug']


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        exclude = ['user', 'product', 'vendor_order_id']



