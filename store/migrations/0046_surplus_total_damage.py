# Generated by Django 4.0.2 on 2022-08-28 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0045_charge_note_saledue_note_saleproducts_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='surplus',
            name='total_damage',
            field=models.FloatField(max_length=15, null=True),
        ),
    ]