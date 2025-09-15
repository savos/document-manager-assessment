from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("file_versions", "0003_alter_fileversion_path_default"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="fileversion",
            name="path",
        ),
    ]

