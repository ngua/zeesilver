# Generated by Django 3.0.6 on 2020-05-29 07:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import localflavor.us.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=14, validators=[django.core.validators.RegexValidator('^\\(?[2-9]\\d{2}\\)?\\s?\\d{3}(?:\\-|\\s)?\\d{4}$', message='Please enter a valid US phone number, including area code')])),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('street_address', models.CharField(max_length=127)),
                ('city', models.CharField(max_length=32)),
                ('state', localflavor.us.models.USStateField(max_length=2)),
                ('zip_code', localflavor.us.models.USZipCodeField(max_length=10)),
                ('shipped_on', models.DateTimeField(null=True)),
                ('tracking', models.CharField(blank=True, max_length=127)),
                ('number', models.CharField(blank=True, max_length=16, null=True, unique=True)),
                ('status', models.PositiveIntegerField(choices=[(1, 'Unpaid'), (2, 'Paid'), (3, 'Shipped'), (0, 'Canceled')], default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('square_payment_id', models.CharField(max_length=64)),
                ('square_order_id', models.CharField(max_length=64)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=32)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='shop.Order')),
            ],
        ),
    ]
