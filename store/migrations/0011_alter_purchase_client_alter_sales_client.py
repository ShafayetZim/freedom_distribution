# Generated by Django 4.0.2 on 2022-06-14 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_sales_deliveryman_sales_road_sales_salesman'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='client',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='sales',
            name='client',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
