# Generated by Django 4.0.2 on 2022-06-15 05:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_alter_purchase_client_alter_sales_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleproducts',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category_fk', to='store.category'),
        ),
    ]
