# Generated by Django 2.2.16 on 2021-02-03 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20210131_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='customertrasnscation',
            name='status',
            field=models.CharField(default='Initialized', max_length=50),
        ),
    ]
