# Generated by Django 2.2.16 on 2021-01-31 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20210126_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userotp',
            name='email',
            field=models.EmailField(max_length=250),
        ),
    ]
