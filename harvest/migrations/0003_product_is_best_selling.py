# Generated by Django 5.0.3 on 2024-08-13 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0002_product_rating_product_review_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_best_selling',
            field=models.BooleanField(default=False),
        ),
    ]