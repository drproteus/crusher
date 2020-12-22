# Generated by Django 3.1.4 on 2020-12-18 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0015_auto_20201218_1354"),
    ]

    operations = [
        migrations.AddField(
            model_name="sku",
            name="contacts",
            field=models.ManyToManyField(related_name="skus", to="app.Contact"),
        ),
        migrations.AddField(
            model_name="sku",
            name="related_skus",
            field=models.ManyToManyField(
                related_name="_sku_related_skus_+", to="app.SKU"
            ),
        ),
    ]
