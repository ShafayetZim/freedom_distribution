# Generated by Django 4.0.2 on 2022-09-02 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0050_rename_due_onlineadvance_total_amount_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='onlinecredit',
            options={'verbose_name_plural': 'List of Advance Credited'},
        ),
    ]