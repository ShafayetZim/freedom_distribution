# Generated by Django 4.0.2 on 2022-09-06 06:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0054_salereturn_brand'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='client',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='contact',
        ),
        migrations.AddField(
            model_name='purchase',
            name='brand',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='brand_fk5', to='store.brand'),
        ),
    ]
