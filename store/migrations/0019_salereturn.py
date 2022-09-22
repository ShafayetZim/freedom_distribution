# Generated by Django 4.0.2 on 2022-08-02 06:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_saleproducts_damage_quantity_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleReturn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buy', models.FloatField(default=0, max_length=15)),
                ('price', models.FloatField(default=0, max_length=15)),
                ('quantity', models.FloatField(default=0, max_length=15)),
                ('free_quantity', models.FloatField(default=0, max_length=15)),
                ('good_quantity', models.FloatField(default=0, max_length=15)),
                ('damage_quantity', models.FloatField(default=0, max_length=15)),
                ('sign', models.FloatField(default=0, max_length=15)),
                ('total_amount', models.FloatField(max_length=15)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_fk2', to='store.products')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_fk3', to='store.sales')),
            ],
            options={
                'verbose_name_plural': 'List of Sale Returns',
            },
        ),
    ]