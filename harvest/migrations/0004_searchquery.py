# Generated by Django 5.0.3 on 2024-08-15 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0003_product_is_best_selling'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.CharField(max_length=255)),
                ('search_count', models.PositiveIntegerField(default=0)),
                ('last_searched', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]