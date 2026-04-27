#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Shortcut routines for python idle

Do not import this within vep2 module!

Usage:
CMD> python
Python 2.7 (r27:82500, Sep  7 2010, 14:21:36)
[GCC 4.5.0] on linux2
Type 'help', 'copyright', 'credits' or 'license' for more information.
>>> from gadget.idle import *
>>> h()     # display history
"""

from os.path import dirname, basename, isdir, join, exists, getsize
import os
import readline
from tp.testprogram import TestProgram
from pprint import pprint
from .printmore import *
from .gizmo import *


def h():  # pragma: no cover  - this module is not unittested
    """Display the history"""
    for i in range(readline.get_current_history_length()):
        print(readline.get_history_item(i))
