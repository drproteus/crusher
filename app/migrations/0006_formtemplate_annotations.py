# Generated by Django 3.1.4 on 2020-12-22 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_renderedform_rendering_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="formtemplate",
            name="annotations",
            field=models.JSONField(null=True),
        ),
    ]
