# Generated by Django 3.0.6 on 2020-05-15 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0004_auto_20200515_0528'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='listing',
            options={'ordering': ['-price']},
        ),
    ]