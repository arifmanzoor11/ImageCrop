import sys
import os

INTERP = os.path.expanduser("/home/YOUR_CPANEL_USERNAME/virtualenv/imageresizer/3.9/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from app import app as application