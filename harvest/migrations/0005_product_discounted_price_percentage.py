# Generated by Django 5.0.3 on 2024-08-15 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0004_searchquery'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discounted_price_percentage',
            field=models.IntegerField(default=0),
        ),
    ]
