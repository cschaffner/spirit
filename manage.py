#!/usr/bin/env python
import os
import sys
sys.path.append(r'/Applications/eclipse/plugins/org.python.pydev_2.7.0.2012110722/pysrc')

import pydevd
pydevd.patch_django_autoreload(
patch_remote_debugger=True, #Connect to the remote debugger.
patch_show_console=True
)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spirit.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
