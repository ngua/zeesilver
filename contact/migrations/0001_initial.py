# Generated by Django 3.0.6 on 2020-05-28 06:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=14, validators=[django.core.validators.RegexValidator('^\\(?[2-9]\\d{2}\\)?\\s?\\d{3}(?:\\-|\\s)?\\d{4}$', message='Please enter a valid US phone number, including area code')])),
                ('subject', models.CharField(choices=[('SALES', 'Sales'), ('RETURNS', 'Returns'), ('CUSTOM', 'Custom'), ('OTHER', 'Other')], default='SALES', max_length=8)),
                ('message', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
