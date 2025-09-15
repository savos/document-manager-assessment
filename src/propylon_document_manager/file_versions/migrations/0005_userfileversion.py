from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("file_versions", "0004_remove_fileversion_path"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserFileVersion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "fileversion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="file_versions.fileversion",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="file_versions.user",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "file_versions_user_fileversion",
            },
        ),
    ]
