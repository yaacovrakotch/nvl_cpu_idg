#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Updates the mconfig file given the pconfig file:

cd <testprogram_path>/Modules
mconfig_update.py <module_dir> -ref <dir>
"""
import setenv      # must be first in the imports
from gadget.vepargs import Args, TA_All, TA_StoreDir
from gadget.helperclass import OPT
from gadget.dictmore import DictDot
from gadget.files import File
from gadget.tputil import log_usage
from gadget.pylog import log
from os.path import exists
from mod.setting import cfg
import re


class MConfig(Args):   # parent: ArgsBase

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('see usage')
        cfg.ref = TA_StoreDir('Reference directory')
        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        log_usage('mconfig_update', cfg)
        if not OPT.all or (not OPT.ref):
            self.do_else()

        for mod in OPT.all:
            self.one_mod(mod, OPT.ref)
        log.info('-i- mconfig_update.py completed.')

    def one_mod(self, mdir, ref):
        """

        :param mdir: Module dir
        :param ref: Reference TP
        :return:
        """
        target = f'{mdir}/module.mconfig'
        assert exists(target), f'{target} is not found! Pls check.'

        # read the mconfig
        with open(target, 'r') as fh:
            olines = list(fh)

        # read the pconfig
        pconfig = f'{ref}/Modules/{mdir}/patterns.pconfig'
        if not exists(pconfig):
            print(f'-i- Not exist: {pconfig}. Ignoring this module.')
            return
        with open(pconfig, 'r') as fh:
            nlines = list(fh)

        # Strategy: use the patterns.pconfig, add IPline and new tags
        self.ipline(olines, nlines)
        self.newtags(olines, nlines)
        File(target).rewrite(''.join(nlines), 'MConfig()')

    def newtags(self, olines, nlines):
        """Add the new tags"""
        # get IPName
        ipname = None
        for line in olines:
            if 'IPName' in line:
                ipname = line

        # insert first line
        for line in nlines:
            if 'xml version' in line:
                nlines.insert(1, '<ModuleConfiguration>\n')

        # insert last lines
        nlines.append('\n')
        if ipname:
            nlines.append(ipname)
        nlines.append('</ModuleConfiguration>\n')

    def ipline(self, olines, nlines):
        """Add the POR_TP IP in nlines"""
        iptag = None
        for line in olines:
            res = re.search(r'PORRoot.*(IP="\w+")', line)
            if res:
                iptag = res.group(1)

        if iptag:
            for idx in range(len(nlines)):
                if 'PORRoot' in nlines[idx] and 'IP=' not in nlines[idx]:
                    nlines[idx] = nlines[idx].replace('<PORRoot', f'<PORRoot {iptag}')

    def do_else(self):
        """
        Execute this if no valid command is specified
        do_else() in base class will just print the help message
        """
        print("Nothing to do.")
        print("")
        self.print_help()


if __name__ == '__main__':  # pragma: no cover
    MConfig(desc=__doc__).main()
