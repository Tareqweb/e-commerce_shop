# Generated by Django 3.1.3 on 2021-04-16 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliveryaddress',
            name='is_billing_info',
        ),
    ]