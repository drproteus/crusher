# Generated by Django 3.1.4 on 2020-12-22 01:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_formtemplate_renderedform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renderedform',
            name='template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='app.formtemplate'),
        ),
    ]
