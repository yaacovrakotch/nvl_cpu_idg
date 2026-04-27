#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for checkers
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File
from gadget.disk import Chdir
from main.tpflwipfy import *
from os.path import join, dirname, abspath


class TestFlwIpfy(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_scopemodules(self):
        with TempDir(name=True, chdir=True, delete=True):
            # get tpl dir and then use later to chdir to it
            tpl = UT_DIR + '/MTLdotflwipfy/TPL/'
            with Chdir(tpl):  # use Chdir(<dir>) so code returns to tmp once done
                obj = FlwIpfy()
                obj.scopemodules()

                self.assertEqual(obj.ipcpu, {'IP_CPU_BASE', 'TPI_ENDIPCPU_XXX', 'TPI_END_XXX_IPCPU',
                                             'IP_CPU_CONCURRENT_FLOWS', 'TPI_PWRUP_CXX', 'TPI_PRESI_CXX',
                                             'TPI_PRESI2_CXX', 'TPI_BASE_IPCPU', 'DRV_RESET_CXX'})
                self.assertEqual(obj.ippch, {'IP_PCH_BASE', 'IP_PCH_CONCURRENT_FLOWS', 'TPI_PWRUP_HXX',
                                             'TPI_END_XXX_IPPCH', 'DRV_RESET_GXX', 'TPI_PRESI_PXX',
                                             'TPI_BASE_IPPCH', 'TPI_ENDIPPCH_XXX'})

    def test_flwipfier(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:  # IP_CPU runs fresh
            env = join(tdir, 'EnvironmentFile_CLASS_TGLU42.env')
            File(env).touch('', mkdir=True, newfile=True)

            flwd = join(tdir, 'Modules/IP_CPU_BASE/IP_CPU_BASE.mtpl')
            File(flwd).touch('', mkdir=True, newfile=True)

            flwd = join(tdir, 'Modules/TPI_PRESI2_CXX/TPI_PRESI2_CXX.flw')
            flwd_data = """<?xml version="1.0"?>
<!DOCTYPE HDMTFlowItemCoor[]>
<HDMTFlowItemCoor>
  <FlowItem name="Flows::TPI_PRESI2_CXX_BEGCPU.CTRL_X_PAUSE_K_BEGCPU_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI2_CXX_CATF1.CTRL_X_PAUSE_K_CATF1_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI2_CXX_CATF2.CTRL_X_PAUSE_K_CATF2_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
</HDMTFlowItemCoor>
"""
            File(flwd).touch(flwd_data, mkdir=True, newfile=True)

            flwd = join(tdir, 'Modules/TPI_PRESI_CXX/TPI_PRESI_CXX.flw')
            flwd_data = """<?xml version="1.0"?>
<!DOCTYPE HDMTFlowItemCoor[]>
<HDMTFlowItemCoor>
  <FlowItem name="Flows::TPI_PRESI_CXX_BEGCPU.CTRL_X_PAUSE_K_BEGCPU_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI_CXX_CATF1.CTRL_X_PAUSE_K_CATF1_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI_CXX_CATF2.CTRL_X_PAUSE_K_CATF2_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
</HDMTFlowItemCoor>
"""
            File(flwd).touch(flwd_data, mkdir=True, newfile=True)

            ipmods = {'IP_CPU_BASE', 'TPI_PRESI_CXX', 'TPI_PRESI2_CXX'}
            obj = FlwIpfy()
            obj.flwipfier(ipmods, 'IP_CPU')

        with TempDir(name=True, chdir=True, delete=True) as tdir:  # IP_PCH fresh runs
            env = join(tdir, 'EnvironmentFile_CLASS_TGLU42.env')
            File(env).touch('', mkdir=True, newfile=True)

            flwd = join(tdir, 'Modules/TPI_PRESI2_PXX/TPI_PRESI2_PXX.flw')
            flwd_data = """<?xml version="1.0"?>
<!DOCTYPE HDMTFlowItemCoor[]>
<HDMTFlowItemCoor>
  <FlowItem name="Flows::TPI_PRESI2_PXX_BEGCPU.CTRL_X_PAUSE_K_BEGCPU_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI2_PXX_CATF1.CTRL_X_PAUSE_K_CATF1_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI2_PXX_CATF2.CTRL_X_PAUSE_K_CATF2_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
</HDMTFlowItemCoor>
"""
            File(flwd).touch(flwd_data, mkdir=True, newfile=True)

            flwd = join(tdir, 'Modules/TPI_PRESI_PXX/TPI_PRESI_PXX.flw')
            flwd_data = """<?xml version="1.0"?>
<!DOCTYPE HDMTFlowItemCoor[]>
<HDMTFlowItemCoor>
  <FlowItem name="Flows::TPI_PRESI_PXX_BEGCPU.CTRL_X_PAUSE_K_BEGCPU_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI_PXX_CATF1.CTRL_X_PAUSE_K_CATF1_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI_PXX_CATF2.CTRL_X_PAUSE_K_CATF2_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
</HDMTFlowItemCoor>
"""
            File(flwd).touch(flwd_data, mkdir=True, newfile=True)

            ipmods = {'TPI_PRESI_PXX', 'TPI_PRESI2_PXX'}
            obj = FlwIpfy()
            obj.flwipfier(ipmods, 'IP_PCH')

        with TempDir(name=True, chdir=True, delete=True) as tdir:  # IP_PCH .flw.old already exists
            env = join(tdir, 'EnvironmentFile_CLASS_TGLU42.env')
            File(env).touch('', mkdir=True, newfile=True)

            flwd = join(tdir, 'Modules/TPI_PRESI2_PXX/TPI_PRESI2_PXX.flw')
            flwd_data = """<?xml version="1.0"?>
<!DOCTYPE HDMTFlowItemCoor[]>
<HDMTFlowItemCoor>
  <FlowItem name="Flows::TPI_PRESI2_PXX_BEGCPU.CTRL_X_PAUSE_K_BEGCPU_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI2_PXX_CATF1.CTRL_X_PAUSE_K_CATF1_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI2_PXX_CATF2.CTRL_X_PAUSE_K_CATF2_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
</HDMTFlowItemCoor>
"""
            File(flwd).touch(flwd_data, mkdir=True, newfile=True)

            flwd = join(tdir, 'Modules/TPI_PRESI2_PXX/TPI_PRESI2_PXX.flw.old')  # create .flw.old so it exists in else
            flwd_data = """<?xml version="1.0"?>
<!DOCTYPE HDMTFlowItemCoor[]>
<HDMTFlowItemCoor>
  <FlowItem name="Flows::TPI_PRESI2_PXX_BEGCPU.CTRL_X_PAUSE_K_BEGCPU_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI2_PXX_CATF1.CTRL_X_PAUSE_K_CATF1_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI2_PXX_CATF2.CTRL_X_PAUSE_K_CATF2_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
</HDMTFlowItemCoor>
"""
            File(flwd).touch(flwd_data, mkdir=True, newfile=True)

            flwd = join(tdir, 'Modules/TPI_PRESI_PXX/TPI_PRESI_PXX.flw')
            flwd_data = """<?xml version="1.0"?>
<!DOCTYPE HDMTFlowItemCoor[]>
<HDMTFlowItemCoor>
  <FlowItem name="Flows::TPI_PRESI_PXX_BEGCPU.CTRL_X_PAUSE_K_BEGCPU_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI_PXX_CATF1.CTRL_X_PAUSE_K_CATF1_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
  <FlowItem name="Flows::TPI_PRESI_PXX_CATF2.CTRL_X_PAUSE_K_CATF2_X_X_X_X_PLACEHOLDER" X="100" Y="20" />
</HDMTFlowItemCoor>
"""
            File(flwd).touch(flwd_data, mkdir=True, newfile=True)

            ipmods = {'TPI_PRESI_PXX', 'TPI_PRESI2_PXX'}
            obj = FlwIpfy()
            obj.flwipfier(ipmods, 'IP_PCH')


LOC = join(dirname(abspath(__file__)))
if __name__ == '__main__':  # pragma: no cover
    unittest.main()
