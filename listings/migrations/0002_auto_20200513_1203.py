# Generated by Django 3.0.6 on 2020-05-13 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='listing',
            name='materials',
        ),
        migrations.AddField(
            model_name='listing',
            name='materials',
            field=models.ManyToManyField(blank=True, to='listings.Material'),
        ),
    ]
