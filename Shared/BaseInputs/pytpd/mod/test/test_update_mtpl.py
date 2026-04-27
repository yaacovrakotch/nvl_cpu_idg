#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for indicators
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, Mock, is_ut_option
from gadget.files import TempName, TempDir
from gadget.gizmo import MockVar, with_
from mod.update_mtpl import *
from tp.testprogram import TestProgram
from gadget.errors import ErrorUser
import mod.indicators as indicators
from pprint import pprint


class TestUM(TestCase):

    def test_initialize(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env').init()

        # module
        obj = FlowUpdater(tp, None, "ARR")
        self.assertEqual(obj.dutflow.keys(), {'ARR::INIT1', 'ARR::MAIN1'})
        self.assertEqual(list(obj.dutflow_order), ['ARR::MAIN1', 'ARR::INIT1'])

        # programflows
        obj = FlowUpdater(tp, None, "")
        self.assertEqual(obj.dutflow.keys(), {'MAIN', 'INIT'})
        self.assertEqual(list(obj.dutflow_order), ['MAIN', 'INIT'])

    def test_programflow_udi(self):
        # update, delete, insert on programflows
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True):
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            targ = tp.get_final_mtpl()
            obj = FlowUpdater(tp, targ, '')
            obj.insert('MAIN', None, None,
                       'main3a', 'PTH::MAIN2', {1: {'PREVIOUS': True}})
            obj.delete('MAIN', 'main3')
            obj.update('MAIN', 'main2', {2: {'PassFail': 'Fail'}})
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_pf1_udi.mtpl.gold')

    def test_update(self):
        # update two ports of Simple3 array
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True):
            targ = 'Modules/ARR/array.mtpl'
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, 'ARR')
            # pprint(obj.dutflow)
            obj.update('MAIN1', 'CCB', {0: {'GoTo': 'CCC',
                                            'SetBin': 'SoftBins.b99.something',
                                            'PassFail': 'Fail'},
                                        1: {'IncrementCounters': 'ARR_CCF::n90450005_fail_XSA_CCF_AUX_E_CHKCLRF6_080816_VUNCORE_F6_40mV_ADDED_FACT_0;',
                                            'GoTo': 'CCD'}})
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_array_update.mtpl.gold')

    def test_delete1(self):
        # delete CCA - start - port1
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True):
            targ = 'Modules/ARR/array.mtpl'
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, 'ARR')
            obj.delete('MAIN1', 'CCA')
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_array_delete1.mtpl.gold')

        # delete CCA - start - port0
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True):
            targ = 'Modules/ARR/array.mtpl'
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, 'ARR')
            obj.delete('MAIN1', 'CCA', 0)
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_array_delete1a.mtpl.gold')

    def test_delete2(self):
        # delete CCB - middle - port1
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True):
            targ = 'Modules/ARR/array.mtpl'
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, 'ARR')
            obj.delete('MAIN1', 'CCB')
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_array_delete2.mtpl.gold')

    def test_delete3(self):
        # delete CCD - last - port1
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True):
            targ = 'Modules/ARR/array.mtpl'
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, 'ARR')
            obj.delete('MAIN1', 'CCD')
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_array_delete3.mtpl.gold')

    def test_insert1(self):
        # insert CCB1 in middle
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True):
            targ = 'Modules/ARR/array.mtpl'
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, 'ARR')
            # pprint(obj.dutflow)
            obj.insert('MAIN1', 'CCB', 1,
                       'CCB1', 'TPIE_PgmRules', {1: {'PREVIOUS': True,
                                                     'PassFail': 'Pass'},
                                                 2: {'PassFail': 'Fail',
                                                     'GoTo': 'CCC'}})
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_array_insert1.mtpl.gold')

    def test_insert2(self):
        # insert CCB1 at end
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True):
            targ = 'Modules/ARR/array.mtpl'
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, 'ARR')
            # pprint(obj.dutflow)
            obj.insert('MAIN1', 'CCD', 1,
                       'CCB1', 'TPIE_PgmRules', {1: {'PREVIOUS': True,
                                                     'PassFail': 'Pass'}})
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_array_insert2.mtpl.gold')

    def test_insert3(self):
        # insert CCB1 at start
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True):
            targ = 'Modules/ARR/array.mtpl'
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, 'ARR')
            # pprint(obj.dutflow)
            obj.insert('MAIN1', None, None,
                       'CCB1', 'TPIE_PgmRules', {1: {'PREVIOUS': True,
                                                     'PassFail': 'Pass'}})
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_array_insert3.mtpl.gold')

    def test_write(self):
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True):
            # Module
            targ = 'Modules/ARR/array.mtpl'
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, 'ARR')
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_array.mtpl.gold')

            # Again, read the rewritten one, should be no change
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, 'ARR')
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_array.mtpl.gold')

            # Program flows
            targ = 'POR_TP/TGLH81/ProgramFlowsTestPlan/ProgramFlows.mtpl'
            File(f'{UT_DIR_REPO}/misc_files/ProgramFlows_FlowItem.mtpl').copy(targ)   # This has DUTFlow case and @EDC case
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, None)
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_programflows.mtpl.gold')

            # Again, Program flows
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()
            obj = FlowUpdater(tp, targ, None)
            obj.write()
            self.assertGoldEqual(targ, f'{UT_DIR_REPO}/misc_files/flow_updater_programflows.mtpl.gold')

            # Check if testinstance is after DUTFlow
            File(targ).touch('''
blah;
Test Vmin Abc
{
}

DUTFlow blah
{
   DUTFlowItem {
   }
}

Test Vmin Ghi
{
}

FlowDefs
{
}
''', newfile=True)
            raw = File(targ).raw()
            result = obj._get_instances(raw)
            expect = '''
blah;
Test Vmin Abc
{
}

Test Vmin Ghi
{
}
'''
            self.assertTextEqual('\n'.join(result), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    @with_(TempDir, chdir=True)
    def test_integration_write(self):
        # module
        tp = TestProgram(f'{UT_DIR}/MTLXXXXXXX39A0KSXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env').pickle_init()
        mtpl = f'{UT_DIR}/MTLXXXXXXX39A0KSXXX/Modules/FUN_CORE_C2P/FUN_CORE_C2P_CLASS_P28G1_CLASS_P28G1_g.mtpl'
        obj = FlowUpdater(tp, mtpl, 'FUN_CORE_C2P')
        File(mtpl).copy('./fun.mtpl')
        obj.mtplfile = 'fun.mtpl'
        obj.write()
        self.assertGoldEqual('fun.mtpl', f'{UT_DIR}/misc_files/fun_flow_updater.mtpl.gold')

        # programflows
        mtpl = f'{UT_DIR}/MTLXXXXXXX39A0KSXXX/POR_TP/Class_MTL_P28/ProgramFlowsTestPlan/ProgramFlows.mtpl'
        obj = FlowUpdater(tp, mtpl, None)
        File(mtpl).copy('./programflows.mtpl')
        obj.mtplfile = 'programflows.mtpl'
        obj.write()
        self.assertGoldEqual('programflows.mtpl', f'{UT_DIR}/misc_files/programflows_flow_updater.mtpl.gold')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
