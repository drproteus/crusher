# Generated by Django 3.1.4 on 2020-12-16 21:59

import app.models
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Item', max_length=256)),
                ('email', models.EmailField(blank=True, max_length=256)),
                ('mobile', models.CharField(blank=True, max_length=256)),
                ('mailing_address', models.TextField(blank=True)),
                ('billing_address', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.IntegerField(choices=[(app.models.InvoiceState['DRAFT'], 0), (app.models.InvoiceState['OPEN'], 1), (app.models.InvoiceState['PAID_PARTIAL'], 2), (app.models.InvoiceState['PAID_FULL'], 3), (app.models.InvoiceState['CLOSED'], 4), (app.models.InvoiceState['VOID'], -1)], default=app.models.InvoiceState['DRAFT'])),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.client')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Item', max_length=256)),
                ('description', models.TextField(blank=True)),
                ('stock', models.DecimalField(decimal_places=2, default=Decimal('1'), max_digits=32)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(default='Leonard', max_length=256)),
                ('last_name', models.CharField(default='McCoy', max_length=256)),
                ('designation', models.CharField(default='Chief Medical Officer', max_length=256)),
                ('email', models.EmailField(blank=True, max_length=256)),
                ('mobile', models.CharField(blank=True, max_length=256)),
                ('mailing_address', models.TextField(blank=True)),
                ('billing_address', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SKU',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=256)),
                ('default_quantity', models.DecimalField(decimal_places=2, default=Decimal('1'), max_digits=32)),
                ('default_rate', models.DecimalField(decimal_places=2, default=Decimal('1'), max_digits=32)),
                ('units', models.CharField(blank=True, max_length=32)),
                ('item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.item')),
                ('staff', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.staff')),
            ],
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=32)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=32)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=32)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='app.invoice')),
                ('sku', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.sku')),
            ],
        ),
    ]
