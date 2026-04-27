#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
This Qgate is to verify that the PRIME_BASE_VERSION in env file is consistent with Nuget.Config

"""
import sys
import setenv

from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import json
import os


class PrimeChecker(QGateBase):

    def main(self):
        """Entry point of checker"""
        path_env = self.tpobj.envfile
        print(path_env)
        path_nuget_config = f'{self.tpobj.tpldir}/NuGet.Config'
        # put your checker code here. Replace below code!
        self.get_env_evg_versions(path_env, path_nuget_config)
        # self.get_nuget_evg_versions()

    def get_env_evg_versions(self, path_env, path_nuget_config):
        """
        Parsing Env file for evg version
        """
        env_evergreen_version = self.tpobj.env.get_item('PRIME_BASE')
        self.get_nuget_evg_versions(env_evergreen_version, path_nuget_config)

    def get_nuget_evg_versions(self, env_evergreen_version, path_nuget_config):
        """Parsing Nuget file for evg version"""

        # path_nuget_config = f'{self.tpobj.tpldir}/NuGet.Config'

        if not os.path.exists(path_nuget_config):
            print("Nuget.Config does not exist")
            return

        with open(path_nuget_config, 'r') as fnlines:
            lines = fnlines.readlines()
            pass

        for lno, line in enumerate(lines):
            line = line.strip('\t')
            line = line.strip('\n')
            # print (line)
            if 'key="DDG"' in line or 'key="Prime"' in line:
                if env_evergreen_version in line:
                    self.add_pass(224, f'BASE')
                else:
                    self.add_error(224, 'BASE', (f'Prime versions dont match between env and nuget.config: '
                                                 f'Expecting {env_evergreen_version} in nuget.config line#{lno + 1}'))


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    PrimeChecker(TestProgram(sys.argv[1]).pickle_init()).run()


# 221
# add testcase for all products other than ARL
# Check other examples which uses base not module
# C:\Users\vmohite\Git_Intel\Qgate_branch\applications.manufacturing.ate-test.tp-tools.pytpd\qgates
# add problem statement in comments:

# Get Prime version from env file
# Read Nuget.config to get the Prime base version
# Compare


# path_env = r"C:\temp\ARLXXXXXXX60A0ZSXXX\POR_TP\Class_ARL_H68\EnvironmentFile.env"
# path_nuget_config = r"C:\temp\ARLXXXXXXX60A0ZSXXX\NuGet.Config"
#
# with open (path_env, 'r') as flines:
#    lines = flines.readlines()
#    pass
#
# for line in lines:
#    line = line.strip('\t')
#    line = line.strip('\n')
#    #print (line)
#    if line.startswith('PRIME_BASE'):
#        env_evergreen_version = line.split('\"')[1]
#        print(env_evergreen_version)
#
# with open (path_nuget_config, 'r') as fnlines:
#    lines = fnlines.readlines()
#    pass
#
# for line in lines:
#    line = line.strip('\t')
#    line = line.strip('\n')
#    #print (line)
#    if line.__contains__("Prime" and "tmmlibs"):
#        pass
#        nuget_evergreen_version = line.split('\\')[12]
#
#        print(nuget_evergreen_version)
#
# if env_evergreen_version == nuget_evergreen_version:
#    print("Prime versions Match")
#
# else:
#
#    print("Prime versions does not match")
#
