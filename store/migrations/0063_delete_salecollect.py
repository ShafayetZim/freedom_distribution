# Generated by Django 4.0.2 on 2022-09-12 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0062_saledue_new_saledue_previous'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SaleCollect',
        ),
    ]