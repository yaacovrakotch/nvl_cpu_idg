#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This script will run right after TPIE build to IP_fy the .flw files or IP_CPU/IP_PCH scoped modules
PKG modules' .flw files will NOT be updated
"""
import setenv      # must be first in the imports
import glob
from os.path import dirname, basename, abspath
from gadget.errors import ErrorCheck
from gadget.files import File
from tp.testprogram import TestProgram
from os.path import exists
import shutil


class FlwIpfy:
    """
    Ipfy the .flw files from IP_CPU and IP_PCH scoped modules
    """

    def __init__(self):
        self.envs = glob.glob('./EnvironmentFile*.env')
        self.ipcpu = set()  # set of ip_cpu scoped modules
        self.ippch = set()  # set of ip_pch scoped modules

    def scopemodules(self):
        """
        Function runs env patch reorder to account for common subr in MTL
        :return: None
        """
        for f in self.envs:
            tp = TestProgram(f)
            bom = tp.get_bom_from_env()
            self.ipcpu.update({basename(dirname(x)) for x in tp.get_all_mtpl_from_stpl('IP_CPU')})  # ipcpu modules
            self.ippch.update({basename(dirname(x)) for x in tp.get_all_mtpl_from_stpl('IP_PCH')})  # ippch modules
        # call flwipfier()
        self.flwipfier(self.ipcpu, "IP_CPU")
        self.flwipfier(self.ippch, "IP_PCH")

        return

    def flwipfier(self, ipmods, scope):
        """
        Loop into all the ip_ scoped modules and update the .flw files
        :return: None
        """
        for mod in ipmods:
            if mod.startswith('IP_'):  # these are tpie generated modules, there are no .flw files in them
                continue

            fflw = glob.glob(f'./Modules/{mod}/{mod}*.flw')  # this is the .flw file
            for flw in fflw:
                oflw = f'{flw}.old'  # this is the .flw.old file * eg back up
                if exists(oflw):  # do not rerun .flw ipfy if .flw.old already exists
                    continue
                File(flw).copy(abspath(oflw))

                # replace the mod (module) to scope::mod
                with open(flw, 'r') as file:
                    flwdata = file.read()
                flwdata = flwdata.replace(f'{mod}', f'{scope}::{mod}')
                with open(flw, 'w') as file:
                    file.write(flwdata)

        return


if __name__ == '__main__':  # pragma: no cover
    obj = FlwIpfy()
    obj.scopemodules()
