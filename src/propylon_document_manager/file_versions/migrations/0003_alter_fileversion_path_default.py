from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("file_versions", "0002_fileversion_path"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fileversion",
            name="path",
            field=models.CharField(max_length=256, null=True, default=None),
        ),
    ]
