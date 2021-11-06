#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def initialize_debugger():
    import debugpy
    if not os.getenv("RUN_MAIN") and os.getenv("ENV") == "DEBUG":
        debugpy.listen(("0.0.0.0", 5678))
        sys.stdout.write("Start the VS Code debugger now, waiting...\n")
        debugpy.wait_for_client()
        sys.stdout.write("Debugger attached, starting server...\n")

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    initialize_debugger()
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
