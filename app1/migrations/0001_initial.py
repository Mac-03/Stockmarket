# Generated by Django 5.1.4 on 2025-01-18 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_name', models.CharField(max_length=50)),
                ('current_price', models.FloatField()),
                ('target_price', models.FloatField()),
                ('stop_loss_price', models.FloatField()),
            ],
        ),
    ]
