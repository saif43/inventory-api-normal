# Generated by Django 2.2.17 on 2021-01-10 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_vendortrasnscation_bill'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendortrasnscationbill',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Customer'),
        ),
        migrations.AlterField(
            model_name='customertrasnscationbill',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Customer'),
        ),
    ]
