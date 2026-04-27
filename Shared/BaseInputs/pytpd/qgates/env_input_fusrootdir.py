#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
r"""
This Qgate is special checking when test program running on x10.
All fuse root dir (or any path with I:\ drive) pointing from I: drive need to define in HDMT_TPL_INPUT_FILES.
TOS will copy all fuse root dir defined in HDMT_TPL_INPUT_FILES as part of MCA.
"""
import setenv  # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.tputil import remove_ip
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
import sys


class EnvInputFusRootDir(QGateBase):
    def main(self):

        # Define dict to store all fus root dir (key) and I: drive path (value).
        idrive_dict = {}
        inputfile_list = []

        # These are special env variables that does not need to be in HDMT_TPL_INPUT_FILES
        ignore_vars = {'HDMT_TPAPPS_ROOT_PRIME',
                       'HDMT_TPAPPS_ROOT_EVG',
                       'NPR_FOLDER_PATH',
                       'FSM_FILE_PATH',
                       'HASH_PATH',
                       'P3_PRODUCT_FOLDERS',    # debug only var
                       'PRIME_DLL_PATH',        # special var used by pytpd to copy to UserCode
                       'CTTR_DOWNLOADS_DIR'}

        # Parsing ENV file in to a dictionary.
        envdict = self.tpobj.env.get_env_dict()

        # read all vars with I:\ drive path
        for varname in envdict:
            if varname == 'HDMT_TPL_INPUT_FILES':
                # Evaluate the ENV content and save target param into a list
                inputfile_list = self.tpobj.env.get_contents(varname, islist=True)
                continue

            # uncomment this to do "blacklist"
            # if varname in ignore_vars:
            #     continue

            if 'FUSE_ROOT' not in varname:
                continue

            if varname.endswith(('_PAT_PATH', '_PLIST_PATH')):
                continue

            if 'ALEPH_FILES' in varname:
                continue

            for item in self.tpobj.env.get_contents(varname, islist=True):
                if item.startswith('I:'):
                    idrive_dict[item] = varname

        # process it
        for item in sorted(idrive_dict):
            # exact match
            if item in inputfile_list:
                self.add_pass(279, "BASE")
                continue

            # partial match
            for path in inputfile_list:
                if path in item:    # partial match
                    self.add_pass(279, "BASE")
                    break
            else:
                fail_message = f'{idrive_dict[item]}: {item} is missing definition from HDMT_TPL_INPUT_FILES var.'
                self.add_error(279, "ENV", fail_message)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    EnvInputFusRootDir(TestProgram(sys.argv[1])).run()
