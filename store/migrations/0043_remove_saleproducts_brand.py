# Generated by Django 4.0.2 on 2022-08-25 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0042_saleproducts_brand'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saleproducts',
            name='brand',
        ),
    ]