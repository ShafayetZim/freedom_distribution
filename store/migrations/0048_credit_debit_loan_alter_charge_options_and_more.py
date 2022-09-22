# Generated by Django 4.0.2 on 2022-08-29 07:06

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0047_remove_brand_category_remove_products_category_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('delete_flag', models.IntegerField(default=0)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'List of Credit',
            },
        ),
        migrations.CreateModel(
            name='Debit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('delete_flag', models.IntegerField(default=0)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'List of Debit',
            },
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100)),
                ('note', models.CharField(blank=True, max_length=250, null=True)),
                ('due_amount', models.FloatField(max_length=15)),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(default=datetime.date.today)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_fk', to='store.employee')),
            ],
            options={
                'verbose_name_plural': 'List of Loans',
            },
        ),
        migrations.AlterModelOptions(
            name='charge',
            options={'verbose_name_plural': 'List of Surplus Charges'},
        ),
        migrations.AddField(
            model_name='surplus',
            name='total_extra',
            field=models.FloatField(max_length=15, null=True),
        ),
        migrations.CreateModel(
            name='LoanDebit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.CharField(max_length=100)),
                ('total_amount', models.FloatField(max_length=15)),
                ('date', models.DateField(default=datetime.date.today)),
                ('debit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debit_fk', to='store.credit')),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loan_fk2', to='store.loan')),
            ],
            options={
                'verbose_name_plural': 'List of Loans Debited',
            },
        ),
        migrations.CreateModel(
            name='LoanCredit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.CharField(max_length=100)),
                ('total_amount', models.FloatField(max_length=15)),
                ('date', models.DateField(default=datetime.date.today)),
                ('credit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credit_fk', to='store.credit')),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loan_fk', to='store.loan')),
            ],
            options={
                'verbose_name_plural': 'List of Loans Credited',
            },
        ),
    ]