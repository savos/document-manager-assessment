from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("file_versions", "0006_remove_userfileversion_datestamps"),
    ]

    operations = [
        migrations.AddField(
            model_name="fileversion",
            name="digest_hex",
            field=models.CharField(
                blank=True,
                help_text="SHA-256 digest for the stored file in hexadecimal format.",
                max_length=64,
                null=True,
            ),
        ),
    ]
