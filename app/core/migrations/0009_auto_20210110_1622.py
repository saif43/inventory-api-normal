# Generated by Django 2.2.17 on 2021-01-10 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_merge_20210110_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendortrasnscation',
            name='product_received',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customertrasnscation',
            name='customer_detail',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_detail_1', to='core.Customer'),
        ),
        migrations.AlterField(
            model_name='customertrasnscationbill',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_detail_2', to='core.Customer'),
        ),
    ]
