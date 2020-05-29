# Generated by Django 3.0.6 on 2020-05-29 07:14

import ckeditor.fields
import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import djmoney.models.fields
import listings.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', ckeditor.fields.RichTextField()),
                ('picture', models.ImageField(upload_to=listings.models.listing_upload_path)),
                ('pieces', models.IntegerField(default=1)),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[('USD', 'US Dollar')], default='USD', editable=False, max_length=3)),
                ('price', djmoney.models.fields.MoneyField(decimal_places=2, default_currency='USD', max_digits=14)),
                ('created', models.DateField(default=django.utils.timezone.now)),
                ('sold', models.BooleanField(default=False)),
                ('slug', models.SlugField(editable=False)),
                ('search_vector', django.contrib.postgres.search.SearchVectorField(blank=True, editable=False, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='listings.Category')),
                ('materials', models.ManyToManyField(blank=True, to='listings.Material')),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.Order')),
            ],
            options={
                'ordering': ['-price'],
            },
        ),
        migrations.AddIndex(
            model_name='listing',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_vector'], name='listings_li_search__219da8_gin'),
        ),
    ]
