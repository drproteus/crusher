# Generated by Django 3.1.4 on 2020-12-20 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_auto_20201220_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='name',
            field=models.CharField(default='foo', max_length=256),
            preserve_default=False,
        ),
    ]
