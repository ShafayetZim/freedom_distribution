# Generated by Django 4.0.2 on 2022-08-24 10:17

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0037_damagesale_damageproduct'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('delete_flag', models.IntegerField(default=0)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'List of Expense',
            },
        ),
        migrations.CreateModel(
            name='Surplus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('month', models.CharField(choices=[('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], default=1, max_length=12)),
                ('total_sale', models.FloatField(max_length=15)),
                ('total_cost', models.FloatField(max_length=15)),
                ('total_expense', models.FloatField(max_length=15)),
                ('margin', models.FloatField(default=0, max_length=15)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'List of Surplus',
            },
        ),
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.CharField(max_length=100)),
                ('total_amount', models.FloatField(max_length=15)),
                ('date', models.DateField(default=datetime.date.today)),
                ('expense', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense_fk', to='store.expense')),
                ('surplus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surplus_fk', to='store.surplus')),
            ],
            options={
                'verbose_name_plural': 'List of Charges',
            },
        ),
    ]
