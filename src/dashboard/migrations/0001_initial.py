# Generated by Django 3.1.3 on 2021-02-18 14:32

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutUs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
            ],
        ),
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('office_location', models.TextField()),
                ('office_address', models.TextField()),
                ('office_phone', models.TextField()),
                ('office_email', models.TextField()),
                ('working_hour', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CouponCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon_code', models.CharField(max_length=250, unique=True)),
                ('coupon_amount', models.DecimalField(decimal_places=2, default=0, max_digits=19)),
                ('coupon_amount_in', models.CharField(choices=[('Percentage', 'Percentage'), ('Money', 'Money')], default='Percentage', max_length=250)),
                ('deactivate', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
            ],
        ),
        migrations.CreateModel(
            name='FreeShippingSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=49.0, max_digits=19)),
                ('shipping_name', models.CharField(default='Express shipping', max_length=200)),
                ('delivery_time', models.CharField(default='8 - 10 days', max_length=200)),
                ('zipcodes', models.TextField(blank=True, null=True)),
                ('apply_for_all', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='GroceryShippingArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zipcodes', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='MobileApps',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('android_app_url', models.CharField(max_length=250)),
                ('ios_app_url', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='PrivacyPolicy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductSlider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True, null=True)),
                ('button_name', models.CharField(blank=True, default='Shop Now', max_length=250, null=True)),
                ('button_link', models.URLField(blank=True, max_length=250, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='slider_image')),
                ('show_button', models.BooleanField(default=True)),
                ('show_slider', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='RefundReturnPolicy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
            ],
        ),
        migrations.CreateModel(
            name='ShippingPriceSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_lte_10', models.DecimalField(decimal_places=2, default=0, max_digits=19)),
                ('amount_lte_20', models.DecimalField(decimal_places=2, default=0, max_digits=19)),
                ('amount_lte_30', models.DecimalField(decimal_places=2, default=0, max_digits=19)),
                ('amount_lte_40', models.DecimalField(decimal_places=2, default=0, max_digits=19)),
                ('amount_lte_50', models.DecimalField(decimal_places=2, default=0, max_digits=19)),
            ],
        ),
        migrations.CreateModel(
            name='SiteLogoAndTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logo')),
                ('title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TermsOfUse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField()),
            ],
        ),
        migrations.CreateModel(
            name='VendorPaymentRelease',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.PositiveIntegerField(default=15)),
            ],
        ),
        migrations.CreateModel(
            name='VendorPaymentRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pay_by', models.CharField(max_length=250)),
                ('pay_amount', models.DecimalField(decimal_places=2, default=0, max_digits=19)),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
                ('orders_id', models.TextField(blank=True, null=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]