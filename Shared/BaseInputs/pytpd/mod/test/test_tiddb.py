#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for tiddb.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO    # must be first import for unittests
from mod.tiddb import *
from tp.testprogram import TestProgram, Env
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.files import File, TempDir
from gadget.printmore import Dumper
from unittest.mock import Mock
from os.path import join, abspath


class TestTidDb(TestCase):

    def test_basic(self):
        tp = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        tp.init()
        obj = TidDb(tp)
        print('=== Data below')
        Dumper(obj.tids)

        self.assertEqual(len(obj.tids), 8)
        self.assertEqual(obj.tids['2371469_00'], {('SCN', 'EDC', 'nom', 'NONE', 'iCFuncTest', 'CCB')})

        data = obj.summary_mod_tid()
        self.assertEqual({k: data[k][0] for k in data},
                         {'ARR,nom,NONE,EDC': {'1466650_00', '1466649_00'},
                          'SCN,nom,NONE,EDC': {'2371468_00', '2371469_00', '2371433_00', '2371470_00', '2371471_00', '2371465_00'}})

        self.assertEqual({k: data[k][1] for k in data},
                         {'ARR,nom,NONE,EDC': {'COR': 'nom', 'EKL': 'EDC', 'FRQ': 'NONE', 'MOD': 'ARR'},
                          'SCN,nom,NONE,EDC': {'COR': 'nom', 'EKL': 'EDC', 'FRQ': 'NONE', 'MOD': 'SCN'}})

        self.assertEqual({k: data[k][2] for k in data},
                         {'ARR,nom,NONE,EDC': {'CCB', 'CCA'},
                          'SCN,nom,NONE,EDC': {'CCB', 'CCA'}})

    def test_dump(self):
        tp = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        tp.init()
        obj = TidDb(tp)

        # load_tid and dump_tid
        with TempDir(name=True) as tdir:
            fn = join(tdir, 'a.csv')
            obj.dump(fn)

            newobj = TidDb(tp, init=False)
            newobj.load(fn)
            self.assertEqual(obj.tids, newobj.tids)
            self.assertEqual(obj.inst, newobj.inst)
            self.assertEqual(len(open(fn).read().split('\n')), 24)

            print('=== tid dump')
            print(open(fn).read())

            # specific module
            fn = join(tdir, 'b.csv')
            obj.dump(fn, re.compile('^ARR'))
            self.assertEqual(len(open(fn).read().split('\n')), 10)

    def test_dumpfile(self):
        tp = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        tp.init()
        obj = TidDb(tp)

        # load_tid and dump_tid
        with TempDir(name=True) as tdir:
            fn = join(tdir, 'c.csv')
            obj.dumpfile(fn)

            print('=== tid dump')
            print(open(fn).read())

            # specific module
            fn = join(tdir, 'd.csv')
            obj.dumpfile(fn, re.compile('^ARR'))
            self.assertEqual(len(open(fn).read().split('\n')), 4)

    def test_empty(self):
        # Cornercase found on MTL Integ3 where no patterns exist
        tp = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        tp.init()
        with MockVar(tp.mtpl, 'iter_flows', Mock(return_value=[])):
            obj = TidDb(tp)
        self.assertEqual(len(obj.tids), 0)

    def test_get(self):
        tp = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        tp.init()
        obj = TidDb(tp)

        # tid
        self.assertEqual(obj.get_tid('2371469_00'), {('SCN', 'EDC', 'nom', 'NONE', 'iCFuncTest', 'CCB')})
        self.assertEqual(obj.get_tid('2371469_01'), set())

        # inst
        result = obj.get_inst('ARR', 'CCA')
        result['PLISTFILE'] = Env.xpath(result['PLISTFILE'])
        self.assertEqual(result,
                         {'PLISTFILE': Env.xpath(abspath(f'{UT_DIR_REPO}/Simple1/TPL/plists/Shops.plist')),
                          'TEMPLATE': 'iCSimpleScoreboardTest',
                          '_BIN': '',
                          'ifpm_modifygroups': '',
                          'level': 'BASE::DDR_univ_lvl_nom_lvl',
                          'patlist': 'shops_L_list',
                          'timings': 'BASE::cpu_func_sdr_univ_sta_univ_univ_b100_t100_d100'})
        self.assertEqual(obj.get_inst('a', '1'), {})

    def test_missing_pat(self):
        tp = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        tp.init()
        tp.mtpl.edata['ARR']['CCA']['patlist'] = 'notfound'
        obj = TidDb(tp)
        print('=== Data below')
        Dumper(obj.tids)

        self.assertEqual(len(obj.tids), 7)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
