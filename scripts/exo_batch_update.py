
# import modules used here -- sys is a very standard one
import sys, argparse, logging
import os

try:
    from .settings import *
except SystemError:
    from scripts.settings import *

try:
    from .settings_local import *
except SystemError:
    try:
        from scripts.settings_local import *
    except ImportError:
        pass
    pass


for instrument in INSTRUMENTS_LIST:
    os.system('python3.5 ./exo_builder.py -v -B 2011-06-01 {0}'.format(instrument))