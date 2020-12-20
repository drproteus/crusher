# Generated by Django 3.1.4 on 2020-12-20 13:41

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("app", "0027_contact_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("object_uid", models.UUIDField()),
                ("attached_file", models.FileField(upload_to="")),
                ("metadata", models.JSONField(null=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
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
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="app.client",
                    ),
                ),
                (
                    "contact_mentions",
                    models.ManyToManyField(
                        related_name="task_mentions", to="app.Contact"
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="job",
            name="origin_request",
        ),
        migrations.DeleteModel(
            name="Request",
        ),
        migrations.AddField(
            model_name="job",
            name="origin_task",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="app.task"
            ),
        ),
    ]
