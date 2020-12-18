# Generated by Django 3.1.4 on 2020-12-18 16:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20201218_1449'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemSKU',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('app.sku',),
        ),
        migrations.CreateModel(
            name='ServiceSKU',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('app.sku',),
        ),
        migrations.CreateModel(
            name='TransportationSKU',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('app.sku',),
        ),
        migrations.AlterModelManagers(
            name='sku',
            managers=[
            ],
        ),
    ]
