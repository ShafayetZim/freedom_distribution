# Generated by Django 4.0.2 on 2022-06-12 06:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_rename_buy_price_saleproducts_buy'),
    ]

    operations = [
        migrations.RenameField(
            model_name='products',
            old_name='buy_price',
            new_name='buy',
        ),
    ]
