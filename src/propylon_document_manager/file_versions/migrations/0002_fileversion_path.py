from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("file_versions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="fileversion",
            name="path",
            field=models.CharField(max_length=256, null=True),
        ),
    ]
