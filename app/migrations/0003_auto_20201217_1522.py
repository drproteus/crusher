# Generated by Django 3.1.4 on 2020-12-17 15:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_auto_20201217_1503"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="metadata",
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name="lineitem",
            name="service_date",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="Vessel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
                (
                    "mmsi",
                    models.CharField(
                        help_text="Maritime Mobile Service Identity", max_length=9
                    ),
                ),
                ("metadata", models.JSONField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="app.client"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Request",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "state",
                    models.IntegerField(
                        choices=[
                            (0, "Received"),
                            (1, "In Progress"),
                            (-1, "Rejected"),
                            (2, "Processed"),
                        ],
                        default=0,
                    ),
                ),
                ("metadata", models.JSONField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="app.client"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("metadata", models.JSONField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "origin_request",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="app.request",
                    ),
                ),
                (
                    "vessel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="app.vessel"
                    ),
                ),
            ],
        ),
    ]
