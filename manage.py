#!/usr/bin/env python
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "propylon_document_manager.site.settings.local"
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django  # noqa
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )

        raise

    # Ensure the "src" directory is on ``sys.path`` so Django can
    # locate the ``propylon_document_manager`` package.
    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path / "src"))

    execute_from_command_line(sys.argv)
