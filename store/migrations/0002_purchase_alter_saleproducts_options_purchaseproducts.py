# Generated by Django 4.0.2 on 2022-06-12 05:45

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('client', models.CharField(max_length=250)),
                ('contact', models.CharField(blank=True, max_length=250, null=True)),
                ('total_amount', models.FloatField(max_length=15)),
                ('tendered', models.FloatField(max_length=15)),
                ('status', models.CharField(choices=[('0', 'Pending'), ('1', 'In-progress'), ('2', 'Done'), ('3', 'Picked Up')], default=0, max_length=2)),
                ('payment', models.CharField(choices=[('0', 'Unpaid'), ('1', 'Paid')], default=0, max_length=2)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'List of Purchase',
            },
        ),
        migrations.AlterModelOptions(
            name='saleproducts',
            options={'verbose_name_plural': 'List of Sale Products'},
        ),
        migrations.CreateModel(
            name='PurchaseProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buy', models.FloatField(default=0, max_length=15)),
                ('price', models.FloatField(default=0, max_length=15)),
                ('quantity', models.FloatField(default=0, max_length=15)),
                ('free_quantity', models.FloatField(default=0, max_length=15)),
                ('total_amount', models.FloatField(max_length=15)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pproduct_fk', to='store.products')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_fk2', to='store.purchase')),
            ],
            options={
                'verbose_name_plural': 'List of Purchase Products',
            },
        ),
    ]
