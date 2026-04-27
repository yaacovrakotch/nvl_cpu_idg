#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
import sys
import setenv
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from gadget.tputil import (OtplFile, get_modulename)
from collections import defaultdict


class DuplicateTestName(QGateBase):

    def main(self):
        """
        Checks the test names in all mtpl to see if there is duplicate test name
        """
        # print("Version0.1.6")

        module_list = []
        dup_modules = defaultdict(set)
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            module = get_modulename(mtpl)
            module_list.append(module)
            module_dict = self.get_test_name(mtpl, module)
            for module in module_dict.keys():
                test_list = module_dict[module]
                for test in test_list:
                    test_count = test_list.count(test)
                    if test_count > 1:
                        if test not in dup_modules[module]:
                            dup_modules[module].add(test)

        found = set()
        for key in dup_modules:
            print("Current key is:{}".format(key))
            msg = f'{key} has duplicated test: {dup_modules[key]}'

            if msg not in found:
                self.add_error(238, key, msg)
                found.add(msg)

        for module in (set(module_list) - set(dup_modules.keys())):
            if module is not None:
                self.add_pass(238, module)

    def get_test_name(self, mtpl, module):
        """
        Get Test name from one mtpl
        :param mtpl: str mtpl path
        :parma module: str module name
        return dictionary {module:test_name}
        """

        # Get all test name from all mtpls
        dict_tname_module = {}  # {module : test_name}
        dict_tname_module = defaultdict(list)
        for lno, line in OtplFile(mtpl).readline():
            if line.startswith(('Test ', 'CSharpTest ')):
                test_name = line.split()[-1]
                dict_tname_module[module].append(test_name)

        return dict_tname_module


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    DuplicateTestName(TestProgram(sys.argv[1])).run()
    # env_path = "/intel/hdmxprogs/mtl/MTLXXXXC1H39C50S348/POR_TP/Class_MTL_P28/EnvironmentFile.env"
    # env_path = "/intel/tpvalidation/engtools/tptools/mtl/unittests/SimpleMTL_jning2/POR_TP/Class_MTL_P28/EnvironmentFile.env"
    # DuplicateTestName(TestProgram(env_path)).run()
