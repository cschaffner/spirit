#!/usr/bin/env python
import os
import sys

sys.path.append(r'/Applications/eclipse/plugins/org.python.pydev_2.7.0.2013032300/pysrc')
 
# import pydevd
#  
# pydevd.patch_django_autoreload(
# patch_remote_debugger=True, #Connect to the remote debugger.
# patch_show_console=True
# )

sys.path.append('/Users/chris/Sites/spirit/spirit')


#print sys.path

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spirit.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
