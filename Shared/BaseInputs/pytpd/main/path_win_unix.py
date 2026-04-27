#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
path_win_unix.py - Converts unix path to windows path and viceversa

Usage:
   # Display windows path equivalent of unixpath|unixfile
   path_win_unix.py <unixpath|unixfile>

   # Display unix path equivalent of windows path
   path_win_unix.py -unix    # paste the windows path with backslash in prompt
"""
import setenv      # must be first in the imports
from gadget.vepargs import Args, TA_StoreTrue, TA_All
from gadget.dictmore import DictDot
from gadget.helperclass import OPT
from gadget.errors import ErrorUser
from mod.setting import cfg
from os.path import exists
import os
import re


class PArgs(Args):   # parent: ArgsBase

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('path or file')
        cfg.unix = TA_StoreTrue('Ignore case')
        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        if OPT.unix:
            ToUnix().print(OPT.all)
        elif OPT.all and exists(OPT.all[0]):
            ToWindows().print(OPT.all[0])
        else:
            ToUnix().print(OPT.all)


class ToWindows:

    def __init__(self):
        # Get all softlinks
        self.map = {}   # {'/nfs/pdx/disks/mve_sctp_003': '/intel/engineering/dev/sctp'}

        # special hardcoded paths
        self.map['/nfs/site/disks/mfg_user_jqdelosr_001'] = '/intel/tpvalidation/jqdelosr/user'

        # standard /intel paths
        for path in cfg.path_root_links:
            for ff in os.listdir(path):
                if ff in cfg.path_root_links[path]:
                    continue    # ignore these
                target = f'{path}/{ff}'
                if os.path.islink(target):
                    linkpath = os.readlink(target)
                    linkpath = linkpath[:-1] if linkpath.endswith('/') else linkpath
                    self.map[linkpath] = target

        # from pprint import pprint
        # pprint(self.map)
        # exit(0)

    def to_logical(self, rpath):
        """Return logical path"""

        # check exact match first
        if rpath in self.map:
            return self.map[rpath]

        # iterate to all the disk maps
        for disk in self.map:
            if rpath.startswith(f'{disk}/'):
                return rpath.replace(disk, self.map[disk])

        raise ErrorUser(f'Cannot get logical path of [{rpath}]',
                        f'If path has mapping in I:\\ drive, pls configure in cfg.path_root_links the root path.')

    def to_win(self, path):
        """Return the windows path"""
        rpath = os.path.realpath(path)

        logical = self.to_logical(rpath)
        assert rpath == os.path.realpath(logical), f'{rpath} vs {os.path.realpath(logical)} does not match (from {logical})'
        winpath = logical.replace('/intel/', 'I:\\').replace('/', '\\')
        return winpath

    def print(self, path):
        """
        Print the windows path. Only the letter need backslash. Use forward slash for the rest,
        so that we can also use it in unix
        """
        print(self.to_win(path).replace('\\', '/').replace(':/', ':\\'))


class ToUnix:

    @classmethod
    def keyboard(cls):   # pragma: no cover
        return input("Enter Windows Path: ")

    def to_unix(self, in_list):
        if not in_list:
            in_str = self.keyboard()
        else:
            in_str = in_list[0]

        upath = in_str.replace('\\', '/').replace('I:/', '/intel/').replace('i:/', '/intel/')
        upath = upath.replace('L:/', '/intel/engineering/dev/')      # Assumed

        # full path logical
        res = re.search('^(//.*)/(intel/.*)', upath)
        if res:
            return f'/{res.group(2)}'

        # full path disk
        res = re.search(r'^(//[\w\-\.]+)/(.*)', upath)
        if res:
            return f'/nfs/site/disks/{res.group(2)}'

        return upath

    def print(self, in_list):
        print(self.to_unix(in_list))


if __name__ == '__main__':  # pragma: no cover
    PArgs(desc=__doc__).main()
