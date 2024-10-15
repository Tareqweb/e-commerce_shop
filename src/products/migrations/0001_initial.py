# Generated by Django 3.1.3 on 2021-02-18 14:32

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vendors', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True)),
                ('show_product_by_subcategory', models.BooleanField(default=False)),
                ('express_shipping', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('slug', models.SlugField(blank=True, max_length=250, null=True, unique=True)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=19)),
                ('discount_percentage', models.PositiveIntegerField(default=0)),
                ('tax_percentage', models.PositiveIntegerField(default=0)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=19)),
                ('sell_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=19)),
                ('image', models.ImageField(upload_to='product_image')),
                ('image_sm', models.ImageField(blank=True, null=True, upload_to='product_image')),
                ('short_description', models.TextField(blank=True, null=True)),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
                ('stock', models.PositiveIntegerField(default=500)),
                ('width', models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True)),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True)),
                ('depth', models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved', models.BooleanField(default=False)),
                ('deactivate', models.BooleanField(default=False)),
                ('rejected', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ProductColor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductWishList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductSizeMeasurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductSizeGuide',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guide_col1', models.CharField(blank=True, max_length=200, null=True)),
                ('guide_col2', models.CharField(blank=True, max_length=200, null=True)),
                ('guide_col3', models.CharField(blank=True, max_length=200, null=True)),
                ('guide_col4', models.CharField(blank=True, max_length=200, null=True)),
                ('guide_col5', models.CharField(blank=True, max_length=200, null=True)),
                ('guide_col6', models.CharField(blank=True, max_length=200, null=True)),
                ('guide_col7', models.CharField(blank=True, max_length=200, null=True)),
                ('guide_col8', models.CharField(blank=True, max_length=200, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor_order_id', models.CharField(max_length=100)),
                ('star', models.PositiveIntegerField()),
                ('comment', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='review_product_image')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_image')),
                ('color', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.productcolor')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCommissionPercentage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commission', models.DecimalField(decimal_places=2, default=2.0, max_digits=19)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True)),
                ('sub_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.subcategory')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productcategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.ManyToManyField(blank=True, to='products.ProductColor'),
        ),
        migrations.AddField(
            model_name='product',
            name='size',
            field=models.ManyToManyField(blank=True, to='products.ProductSize'),
        ),
        migrations.AddField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendors.vendor'),
        ),
    ]