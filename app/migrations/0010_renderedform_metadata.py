# Generated by Django 3.1.4 on 2020-12-23 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20201222_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='renderedform',
            name='metadata',
            field=models.JSONField(null=True),
        ),
    ]
