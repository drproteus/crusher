# Generated by Django 3.1.4 on 2020-12-17 14:59

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=256)),
                ('email', models.EmailField(blank=True, max_length=256)),
                ('mobile', models.CharField(blank=True, max_length=256)),
                ('mailing_address', models.TextField(blank=True)),
                ('billing_address', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.IntegerField(choices=[(0, 'Draft'), (1, 'Open'), (2, 'Paid Partial'), (3, 'Paid Full'), (4, 'Closed'), (-1, 'Void')], default=0)),
                ('initial_balance', models.DecimalField(decimal_places=2, default=0, max_digits=32)),
                ('paid_balance', models.DecimalField(decimal_places=2, default=0, max_digits=32)),
                ('due_date', models.DateTimeField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.client')),
            ],
        ),
        migrations.CreateModel(
            name='SKU',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=256)),
                ('data', models.JSONField()),
                ('default_quantity', models.DecimalField(decimal_places=2, default=Decimal('1'), max_digits=32)),
                ('default_price', models.DecimalField(decimal_places=2, default=Decimal('1'), max_digits=32)),
                ('minium_quantity', models.DecimalField(decimal_places=2, max_digits=32, null=True)),
                ('minimum_price', models.DecimalField(decimal_places=2, max_digits=32, null=True)),
                ('maximum_quantity', models.DecimalField(decimal_places=2, max_digits=32, null=True)),
                ('maximum_price', models.DecimalField(decimal_places=2, max_digits=32, null=True)),
                ('units', models.CharField(blank=True, default='unit', max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            managers=[
                ('staff', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=32)),
                ('price', models.DecimalField(decimal_places=2, max_digits=32)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=32)),
                ('posted_date', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='app.invoice')),
                ('sku', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.sku')),
            ],
        ),
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=32)),
                ('memo', models.TextField(blank=True)),
                ('posted_date', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credits', to='app.invoice')),
                ('line_item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.lineitem')),
            ],
        ),
    ]
