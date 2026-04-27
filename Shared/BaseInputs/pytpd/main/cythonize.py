#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Cythonize the project

Usage:
cythonize.py outdir      # outdir must be empty

Strategy:
1. One tp/testprogram.so. This has all .py combined.
2. Several gadget/<module>.so. Thus, create .pxd and do cimport

TODO:
1. refactor so that gadget/*.pyx will compile as-is (no cpdef). eg. special methods has not attributes
2. routine to create .pxd automatically
3. routine to add cimport
4. routine to combine files in testprogram.py
5. routine to add cdef into 'cdef class' (ie, self.<attributes>)
6. routine to add cdef into cpdef (ie, local variables)

The following routines does not need to by cythonized. They don't involve high loop count.
-rwxr-x--- 1 jqdelosr gdlusers   679 Aug  9 09:30 gadget/idle.py
-rwxr-x--- 1 jqdelosr gdlusers 37604 Nov  6 17:50 gadget/ut.py
-rwxr-x--- 1 jqdelosr gdlusers 40282 Nov  7 17:10 gadget/vepargs.py
-rwxr-x--- 1 jqdelosr gdlusers 11172 Nov  6 17:52 gadget/data_host.py
-rwxr-x--- 1 jqdelosr gdlusers 56327 Nov  6 17:50 gadget/shell.py
-rwxr-x--- 1 jqdelosr gdlusers 31047 Aug  9 09:30 gadget/pylog.py
-rwxr-x--- 1 jqdelosr gdlusers 25845 Oct 22 09:19 gadget/disk.py
-rwxr-x--- 1 jqdelosr gdlusers 19361 Nov  6 17:50 gadget/errors.py
-rwxr-x--- 1 jqdelosr gdlusers  5423 Nov  6 17:50 gadget/lockfile.py
-rwxr-x--- 1 jqdelosr gdlusers 35187 Nov  6 17:50 gadget/sepshelve.py
-rwxr-x--- 1 jqdelosr gdlusers 35834 Nov  7 08:36 gadget/helperclass.py

The following will by cythonized:
-rwxr-x--- 1 jqdelosr gdlusers 44204 Oct 22 09:19 gadget/gizmo.py       # bec of isany and Elapsed()
-rwxr-x--- 1 jqdelosr gdlusers 13671 Oct 22 09:19 gadget/printmore.py   # bec of PctIndicator
-rwxr-x--- 1 jqdelosr gdlusers 70912 Nov  6 17:50 gadget/files.py
-rwxr-x--- 1 jqdelosr gdlusers 38927 Nov  6 17:50 gadget/dictmore.py
-rwxr-x--- 1 jqdelosr gdlusers 44765 Nov  6 17:50 gadget/strmore.py
-rw-r----- 1 jqdelosr gdlusers 27045 Nov  7 12:01 gadget/tputil.py
"""

from setenv import ROOT_ENV      # must be first in the imports
from gadget.vepargs import Args, TA_All
from gadget.helperclass import OPT
from gadget.dictmore import DictDot
from gadget.disk import scandir_mtime, mkdirs
from gadget.files import File
from os.path import dirname, realpath, basename, isdir
import sys
import os


class CyArg(Args):   # parent: ArgsBase
    """
    Main wrap
    """
    root = dirname(dirname(realpath(sys.argv[0])))

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('Outputdir')
        return cfg

    def main(self):
        """
        Main entry point
        """
        if not OPT.all:
            self.do_else()

        assert isdir(OPT.all[0]), f'{OPT.all[0]} must be a directory.'
        Cythonize().main(OPT.all[0])


class Cythonize:
    """
    Cythonize the project

    Performance: main/tp_audit.py /tmp/cy_bench/TPL/EnvironmentFile.env -stat -nopickle
    py3 python:    -i- Elapsed: 13.548 Secs: vmsize: 319580 kB
    direct cython: -i- Elapsed: 11.162 Secs: vmsize: 345016 kB   (15% improvement) (.py to .pyx only, no cpdef)
    """

    def main(self, outdir):
        """
        Cythonize all .py files and output to directory

        """
        assert not os.listdir(outdir), f'{outdir} is not empty. Expecting empty dir'

        for path, _ in scandir_mtime(ROOT_ENV):
            if '.git/' in path or path.endswith('.pyc'):    # Skip these
                continue
            npath = path.replace(ROOT_ENV, outdir)

            if ('/test/' in npath or
                    (not npath.endswith('.py')) or
                    (basename(npath) in ('setenv.py', 'vepargs.py', 'helperclass.py')) or
                    (basename(dirname(npath)) in ('main', 'gadget', 'settings'))):

                # copy as-is
                mkdirs(dirname(npath))
                File(path).copy(npath)

                # do something special with main
                if basename(dirname(npath)) == 'main':
                    File(npath).touch(self._proc_cy_main(npath), newfile=True)

                # special file to convert
                if basename(npath) == 'tputil.py':
                    File(npath).unlink()
                    File(f'{npath}x').touch(self._proc_py_cython(path), mkdir=True).chmod('0750')
            else:
                File(f'{npath}x').touch(self._proc_py_cython(path), mkdir=True).chmod('0750')

    def _proc_cy_main(self, fname):
        """Add the pyximport to main pats"""
        result = []
        for line in File(fname).chomp():
            if line.startswith('import setenv'):
                result.append(line)
                result.append('import pyximport')
                result.append('pyximport.install(inplace=True, build_in_temp=True, language_level=3)')
                result.append('')
                continue
            result.append(line)
        return '\n'.join(result)

    def _proc_py_cython(self, fname):    # pragma: no cover
        """Process one py file - cython"""
        result = []
        print(f'Processing {fname}')
        prev = ''

        all_lines = [line for line in File(fname).chomp()]

        valid = True
        for lno, line in enumerate(all_lines):
            ln = line.strip()

            # class line
            if line.startswith('class '):
                if (True or           # cdef class means defining class attributes
                        'metaclass=' in line or
                        'defaultdict' in line):
                    valid = False
                else:
                    valid = True
                    line = f'cdef {line}'

            # def line
            if line.startswith('def '):
                valid = True   # always valid

            if (ln.startswith('def ') and valid and
                    (not prev.startswith('@')) and             # cannot have decorators
                    (not ln.startswith(('def __',              # cannot be special funcs
                                        'def evaluate',        # func has lambda
                                        'def summary_mod_tid',  # func has lambda
                                        'def _mapping'))) and  # func has dictionary lambda in it
                    ('*' not in ln) and                        # cannot have args expansion and kw expansion
                    (' -> ' not in ln) and                     # cannot have return type annotation (This can be moved later)
                    (not self.is_yield(all_lines, lno)) and    # cannot have yield
                    (not line.startswith('        def '))):    # cannot be func defined inside func
                line = line.replace('def ', 'cpdef ', 1)

            result.append(line)
            prev = ln
        return '\n'.join(result)

    def is_yield(self, all_lines, lno):
        """Returns True if there is yeld before any def"""
        for idx in range(lno + 1, len(all_lines)):
            if 'yield' in all_lines[idx]:
                return True
            if all_lines[idx].strip().startswith('def '):
                return False
        return False


# Performance of cpython vs pypy
# test_ituff       26        27   =
# test_tpaudit     31        45   x
# test_slim        47        28   /
# test_mtpl        21        16   /
# test_testprogram 29        30   =
# test_timlvl      14        17   x
# test_plist       4.3        7   x


if __name__ == '__main__':  # pragma: no cover
    CyArg(desc=__doc__).main()
