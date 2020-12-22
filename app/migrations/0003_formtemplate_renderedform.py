# Generated by Django 3.1.4 on 2020-12-22 01:34

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20201222_0124'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormTemplate',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('fields', models.JSONField(null=True)),
                ('template_file', models.FileField(upload_to='')),
                ('metadata', models.JSONField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('clients', models.ManyToManyField(related_name='forms', to='app.Client')),
            ],
        ),
        migrations.CreateModel(
            name='RenderedForm',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('rendered_file', models.FileField(upload_to='')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.formtemplate')),
            ],
        ),
    ]
