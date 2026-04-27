#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
pymtpl main

pymtpl.py <sourcecode.py>                                # Given sourcecode.py, generate the .mtpl
pymtpl.py -genmethods "<path/to/dlls,path2/to/dlls,etc> -genmethodsoutdir <output_dir>   # Generate new_por_methods.py
pymtpl.py -env <path/EnvironmentFile.env> -genpy <path_to_mtpl>   # Generate pymtpl from mtpl
pymtpl.py -install                                        # Install PyMTPL in the current directory
pymtpl.py -up                                             # Update PyMTPL in the current directory
pymtpl.py -install -s                                     # Install PyMTPL, skip por_methods generation
pymtpl.py -up -s                                          # Update PyMTPL, skip por_methods generation
"""
import setenv      # must be first in the imports
from gadget.vepargs import Args, TA_StoreBool, TA_All, TA_StoreTrue, TA_StoreDir, TA_StoreFile, TA_Store, TA_KeyVal
from gadget.dictmore import DictDot
from gadget.errors import ErrorInput, confirm, Check
from gadget.helperclass import OPT
from pymtpl.core import PyMtpl
from pymtpl.gen_methods import GenMethods
from pymtpl.mtpl2py import GenPy
from pymtpl.autobinctrupdate import UpdateAutobinAndAutoCtrJson
from gadget.tputil import log_usage
from mod.setting import cfg
from pymtpl.update_pymtpl import PyMTPLUpdater
import sys

# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class PyMtplArgs(Args):   # parent: ArgsBase

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('Source code')
        cfg.genpy = TA_StoreFile('mtpl file', metavar='mtplfile')
        cfg.genmethods = TA_Store('Ordered DLL paths and flag to generate por_methods.py', metavar='genmethods')
        cfg.class90hbsbxx = TA_Store('Switch to tell Pymtpl which Initialize to use', metavar='class90hbsbxx')
        cfg.genmethodsoutdir = TA_Store('CMD: Call generate methods', metavar='genmethodsoutdir')
        cfg.bindef = TA_StoreFile('Bindef file', metavar='bindef')
        cfg.updateautobinctr = TA_StoreTrue('Switch to update autobinctr jsons', metavar='updateautobinctr')
        cfg.inputmtpl = TA_StoreFile('mtpl file for extracting bin ctr info from', metavar='inputmtplfile')
        cfg.product = TA_Store('Product Name. Default is nvl. Used with mtpl2py', metavar='dmrclass')
        cfg.set_defaults = TA_KeyVal('Override any BaseDefault attribute(s) for mtpl2py, e.g. -set_defaults autosetbins=False -set_defaults tos=3', metavar='key=value')
        cfg.env = TA_StoreFile('Env file', metavar='envfile')  # Still needed for other modes
        cfg.skip_path_updater = TA_StoreTrue('Skip the Python path updater for Visual Studio', metavar='skip_path_updater')
        cfg.install = TA_StoreTrue('Install PyMTPL in the current directory', metavar='install')
        cfg.up = TA_StoreTrue('Update PyMTPL in the current directory', metavar='up')
        cfg.s = TA_StoreTrue('Skip por_methods.py generation during install/update', metavar='s')
        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        Check.check_get_caller_lno()
        log_usage('pymtpl', cfg)

        if OPT.install:
            updater = PyMTPLUpdater().main(install=True, skip_por_methods=OPT.s)
            return 6

        if OPT.up:
            updater = PyMTPLUpdater().main(install=False, skip_por_methods=OPT.s)
            return 7

        if OPT.genpy:
            GenPy(OPT.genpy).main()
            return 3

        if OPT.updateautobinctr:
            confirm(OPT.inputmtpl, 'Incorrect usage, this mode needs mtpl file in input',
                    'Usage: pymtpl.py -updateautobinctr -inputmtpl <input_mtpl_file>')
            UpdateAutobinAndAutoCtrJson(OPT.inputmtpl).main()
            return 4

        if OPT.genmethods:
            confirm(OPT.genmethodsoutdir, 'Incorrect usage, this mode needs output directory',
                    'Usage: pymtpl.py -genmethods "<path/to/dlls,path2/to/dlls,etc> -genmethodsoutdir <output_dir>"')
            dll_paths = [p.strip() for p in OPT.genmethods.split(',')]
            GenMethods(
                sys.argv[0],
                dll_paths,  # Pass the list instead of a single path
            ).main(OPT.genmethodsoutdir)
            return 5

        if not OPT.all:
            raise ErrorInput('Incorrect usage', 'Usage: pymtpl.py <source_code.py>')

        # main code
        PyMtpl().main()
        return 2


if __name__ == '__main__':  # pragma: no cover
    PyMtplArgs(desc=__doc__).main()
