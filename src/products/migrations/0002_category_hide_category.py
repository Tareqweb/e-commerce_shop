# Generated by Django 3.1.3 on 2021-03-09 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='hide_category',
            field=models.BooleanField(default=False),
        ),
    ]
