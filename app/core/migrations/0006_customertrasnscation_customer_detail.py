# Generated by Django 2.2.16 on 2021-01-07 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20201231_1357'),
    ]

    operations = [
        migrations.AddField(
            model_name='customertrasnscation',
            name='customer_detail',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_detail', to='core.Customer'),
        ),
    ]
