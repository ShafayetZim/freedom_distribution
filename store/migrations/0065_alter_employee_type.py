# Generated by Django 4.0.2 on 2022-09-25 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0064_saledue_date_saledue_date_added_saledue_date_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='type',
            field=models.CharField(choices=[('1', 'Salesman'), ('2', 'Deliveryman'), ('3', 'Manager'), ('4', 'AIC'), ('5', 'Other')], default=1, max_length=2),
        ),
    ]