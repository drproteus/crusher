# Generated by Django 3.1.4 on 2020-12-22 21:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_formtemplate_default_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='renderedform',
            name='rendering_client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rendered_forms', to='app.client'),
        ),
    ]
