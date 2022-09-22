# Generated by Django 4.0.2 on 2022-09-08 06:48

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0059_alter_saleproducts_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(max_length=100)),
                ('note', models.CharField(blank=True, max_length=250, null=True)),
                ('delete_flag', models.IntegerField(default=0)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(default=datetime.date.today)),
            ],
            options={
                'verbose_name_plural': 'List of Banks',
            },
        ),
        migrations.CreateModel(
            name='BankTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(max_length=100)),
                ('type', models.CharField(choices=[('1', 'Deposit'), ('2', 'Withdraw')], default=1, max_length=2)),
                ('delete_flag', models.IntegerField(default=0)),
                ('date', models.DateField(default=datetime.date.today)),
            ],
            options={
                'verbose_name_plural': 'List of Bank Transaction',
            },
        ),
        migrations.CreateModel(
            name='Investment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invest', models.FloatField(max_length=250)),
                ('delete_flag', models.IntegerField(default=0)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(default=datetime.date.today)),
            ],
            options={
                'verbose_name_plural': 'List of Investment',
            },
        ),
        migrations.CreateModel(
            name='OnlineTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(max_length=250)),
                ('note', models.CharField(max_length=250)),
                ('delete_flag', models.IntegerField(default=0)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(default=datetime.date.today)),
            ],
            options={
                'verbose_name_plural': 'List of Expose',
            },
        ),
    ]
