from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("file_versions", "0005_userfileversion"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userfileversion",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="userfileversion",
            name="updated_at",
        ),
        migrations.RemoveField(
            model_name="userfileversion",
            name="deleted_at",
        ),
    ]
