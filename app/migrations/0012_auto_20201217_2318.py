# Generated by Django 3.1.4 on 2020-12-17 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0011_auto_20201217_2135"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="billing_address",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="client",
            name="email",
            field=models.EmailField(blank=True, default="", max_length=256),
        ),
        migrations.AlterField(
            model_name="client",
            name="mailing_address",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="client",
            name="mobile",
            field=models.CharField(blank=True, default="", max_length=256),
        ),
        migrations.AlterField(
            model_name="vessel",
            name="mmsi",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Maritime Mobile Service Identity",
                max_length=9,
            ),
        ),
    ]
