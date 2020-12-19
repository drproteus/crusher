# Generated by Django 3.1.4 on 2020-12-19 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20201219_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit',
            name='invoice',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='applied_credits', to='app.invoice'),
            preserve_default=False,
        ),
    ]
