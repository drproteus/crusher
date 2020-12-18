# Generated by Django 3.1.4 on 2020-12-18 13:54

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20201218_0040'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='sku',
            managers=[
                ('services', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RemoveField(
            model_name='client',
            name='billing_address',
        ),
        migrations.RemoveField(
            model_name='client',
            name='email',
        ),
        migrations.RemoveField(
            model_name='client',
            name='mailing_address',
        ),
        migrations.RemoveField(
            model_name='client',
            name='mobile',
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=256)),
                ('last_name', models.CharField(max_length=256)),
                ('title', models.CharField(blank=True, max_length=32)),
                ('role', models.CharField(blank=True, max_length=256)),
                ('primary_email', models.CharField(blank=True, max_length=256)),
                ('phone_number', models.CharField(blank=True, max_length=256)),
                ('mailing_address', models.TextField(blank=True)),
                ('billing_address', models.TextField(blank=True)),
                ('metadata', models.JSONField(null=True)),
                ('connections', models.ManyToManyField(related_name='_contact_connections_+', to='app.Contact')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='contact',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.contact'),
        ),
        migrations.AddField(
            model_name='request',
            name='contact_mentions',
            field=models.ManyToManyField(related_name='request_mentions', to='app.Contact'),
        ),
    ]
