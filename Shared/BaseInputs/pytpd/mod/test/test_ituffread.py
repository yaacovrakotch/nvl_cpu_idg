#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for ituffread
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest
from mod.ituffread import *
from gadget.gizmo import count_iter
from gadget.dictmore import keys_atlevel
from gadget.files import TempDir
from pprint import pprint


class TestItuff(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        lot = f'{UT_DIR}/ituff_test_paths/Unzipped_Multi'
        ituff = Ituff()
        ituff.read_lot(lot, '_1A_')
        self.assertEqual(len(ituff.files), 3)
        self.assertEqual(len(ituff.data), 25)
        self.assertEqual(count_iter(keys_atlevel(ituff.data, 1)), 75)
        self.assertEqual(len(ituff.tdata), 25)   # units only
        self.assertEqual(count_iter(keys_atlevel(ituff.tdata, 1)), 0)

        # Check the lot
        self.assertEqual(len(ituff.lot), 27)
        self.assertEqual(ituff.lot['lotid'], 'J118019F2')

        expect = ['DFF_OPTYPE_PBIC_S1',
                  'DFF_WRITE_OPTYPE_PBIC_S1',
                  'DFF_READ_OPTYPE_QA_S2',
                  'StartOfDeviceCallback_GSDS::GSDSFactory',
                  'PostInitCallback_GEN_DEDC_tt::DEDCRVModeCheckPostInit,GEN_PyLicense_tt::PyLicenseCallback,Trace::Trace',
                  'LotStartCallback_GEN_DEDC_tt::DEDCRVModeCheckLotStart,GEN_FAST_tt::InfraFileInfo,GEN_Init_tt::GroupDefinitionFileInfo,GSDS::GSDSFactory,Trace::Trace',
                  'LotEndCallback_GSDS::GSDSFactory']
        self.assertEqual(ituff.lot['comnt'], expect)

    def test_ut_read_lot(self):
        # unittest given a mocked up ituff file
        with TempDir(name=True) as tdir:
            File(f'{tdir}/a.itf').touch('''7_lbeg
7_filcret_20210505024544
7_fmtver_Evg
7_dsrcprg_HDMTG2_evg5040200_306010709999
7_comnt_ULT_DB_REQD
6_lbeg
''')
            ituff = Ituff()
            ituff.read_lot(tdir, '')
            pprint(ituff.lot)
            self.assertEqual(ituff.lot, {'comnt': 'ULT_DB_REQD',
                                         'dsrcprg': 'HDMTG2_evg5040200_306010709999',
                                         'filcret': '20210505024544',
                                         'fmtver': 'Evg'})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_read_default(self):
        # Default read
        itf = f'{UT_DIR}/ituff_test_paths/Unzipped_Multi/J119060CR_6248_1B_ALL'
        data = Ituff().read(itf).data
        pprint(data)
        self.assertEqual(data, {'81U27F9700992': {'binn': '90535391', 'curfbin': '5391', 'ttime': '7.9834'},
                                '81U27F9701006': {'binn': '90535391', 'curfbin': '5391', 'ttime': '7.0723'},
                                '81U27F9701820': {'binn': '90535391', 'curfbin': '5391', 'ttime': '7.0633'},
                                '81U27F9701833': {'binn': '90535391', 'curfbin': '5391', 'ttime': '151.3048'},
                                '81U27F9701862': {'binn': '90535391', 'curfbin': '5391', 'ttime': '151.3006'},
                                '81U27F9702076': {'binn': '90535391', 'curfbin': '5391', 'ttime': '7.0386'}})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_multiple(self):
        # both single=, and multiple=
        itf = f'{UT_DIR}/ituff_test_paths/Unzipped_Multi/J119060CR_6248_1B_ALL'

        data = Ituff(single=['3_binn_'], multiple=['2_comnt_mrslt_temperature_']).read(itf).data
        xpect = {'81U27F9700992': {'binn': '90535391',
                                   'comnt': ['mrslt_temperature_TDAU_CH_CORE_1_98.9000',
                                             'mrslt_temperature_TDAU_CH_C6_1_99.0000',
                                             'mrslt_temperature_TDAU_CH_SA_1_99.0000']},
                 '81U27F9701006': {'binn': '90535391',
                                   'comnt': ['mrslt_temperature_TDAU_CH_CORE_1_99.0000',
                                             'mrslt_temperature_TDAU_CH_C6_1_98.9000',
                                             'mrslt_temperature_TDAU_CH_SA_1_99.1000']},
                 '81U27F9701820': {'binn': '90535391',
                                   'comnt': ['mrslt_temperature_TDAU_CH_CORE_1_99.0000',
                                             'mrslt_temperature_TDAU_CH_C6_1_98.8000',
                                             'mrslt_temperature_TDAU_CH_SA_1_99.0000']},
                 '81U27F9701833': {'binn': '90535391',
                                   'comnt': ['mrslt_temperature_TDAU_CH_CORE_1_98.5000',
                                             'mrslt_temperature_TDAU_CH_C6_1_98.6000',
                                             'mrslt_temperature_TDAU_CH_SA_1_98.5000']},
                 '81U27F9701862': {'binn': '90535391',
                                   'comnt': ['mrslt_temperature_TDAU_CH_CORE_1_98.9000',
                                             'mrslt_temperature_TDAU_CH_C6_1_98.9000',
                                             'mrslt_temperature_TDAU_CH_SA_1_99.1000']},
                 '81U27F9702076': {'binn': '90535391',
                                   'comnt': ['mrslt_temperature_TDAU_CH_CORE_1_99.1000',
                                             'mrslt_temperature_TDAU_CH_C6_1_99.0000',
                                             'mrslt_temperature_TDAU_CH_SA_1_99.0000']}}
        self.assertEqual(data, xpect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_tname(self):
        itf = f'{UT_DIR}/ituff_test_paths/Unzipped_Multi/J119060CR_6248_1B_ALL'

        # single token mode
        ituff = Ituff(tsingle=['0_mrslt_'], tname='CheckDieForce_TDAU_CH_CORE').read(itf)
        xpect = {'81U27F9700992': {'CheckDieForce_TDAU_CH_CORE': '99.5000'},
                 '81U27F9701006': {'CheckDieForce_TDAU_CH_CORE': '99.9000'},
                 '81U27F9701820': {'CheckDieForce_TDAU_CH_CORE': '100.1000'},
                 '81U27F9701833': {'CheckDieForce_TDAU_CH_CORE': '101.1000'},
                 '81U27F9701862': {'CheckDieForce_TDAU_CH_CORE': '100.8000'},
                 '81U27F9702076': {'CheckDieForce_TDAU_CH_CORE': '99.8000'}}
        self.assertEqual(ituff.tdata, xpect)
        self.assertEqual(ituff.data, {x: {} for x in xpect})     # empty
        self.assertEqual(len(ituff.lot), 27)

        # single token, regex
        data = Ituff(tsingle=['0_mrslt_'], retname='CheckDieForce_.*_CH_CORE').read(itf).tdata
        self.assertEqual(data, xpect)

        # multiple token mode
        data = Ituff(tmultiple=['2_comnt_mrslt_'], tname='CheckDieForce_TDAU_CH_SA').read(itf).tdata
        xpect = {'81U27F9700992': {'CheckDieForce_TDAU_CH_SA': ['mrslt_TDAU_CH_CORE_1_99.5000',
                                                                'mrslt_TDAU_CH_C6_1_99.5000',
                                                                'mrslt_TDAU_CH_SA_1_99.4000']},
                 '81U27F9701006': {'CheckDieForce_TDAU_CH_SA': ['mrslt_TDAU_CH_CORE_1_99.9000',
                                                                'mrslt_TDAU_CH_C6_1_99.8000',
                                                                'mrslt_TDAU_CH_SA_1_100.0000']},
                 '81U27F9701820': {'CheckDieForce_TDAU_CH_SA': ['mrslt_TDAU_CH_CORE_1_100.2000',
                                                                'mrslt_TDAU_CH_C6_1_99.9000',
                                                                'mrslt_TDAU_CH_SA_1_100.1000']},
                 '81U27F9701833': {'CheckDieForce_TDAU_CH_SA': ['mrslt_TDAU_CH_CORE_1_101.1000',
                                                                'mrslt_TDAU_CH_C6_1_101.1000',
                                                                'mrslt_TDAU_CH_SA_1_101.1000']},
                 '81U27F9701862': {'CheckDieForce_TDAU_CH_SA': ['mrslt_TDAU_CH_CORE_1_100.8000',
                                                                'mrslt_TDAU_CH_C6_1_100.9000',
                                                                'mrslt_TDAU_CH_SA_1_100.8000']},
                 '81U27F9702076': {'CheckDieForce_TDAU_CH_SA': ['mrslt_TDAU_CH_CORE_1_99.8000',
                                                                'mrslt_TDAU_CH_C6_1_99.6000',
                                                                'mrslt_TDAU_CH_SA_1_99.7000']}}
        self.assertEqual(data, xpect)
        data = Ituff(tmultiple=['2_comnt_mrslt_'], retname='CheckDieF.*_TDAU_CH_SA').read(itf).tdata
        self.assertEqual(data, xpect)

        # two tokens
        ituff = Ituff(tmultiple=['2_mrslt_', '2_msunit_'], tname='CONT_X_VCCCONT_K_START_X_X_X_X_VCC_STG_HC_VCC_STG_HC')
        data = ituff.read(itf).tdata
        xpect = {'81U27F9700992': {'TPI_VCC::CONT_X_VCCCONT_K_START_X_X_X_X_VCC_STG_HC_VCC_STG_HC': ['0.00743675',
                                                                                                     'A']},
                 '81U27F9701006': {'TPI_VCC::CONT_X_VCCCONT_K_START_X_X_X_X_VCC_STG_HC_VCC_STG_HC': ['0.00587463',
                                                                                                     'A']},
                 '81U27F9701820': {'TPI_VCC::CONT_X_VCCCONT_K_START_X_X_X_X_VCC_STG_HC_VCC_STG_HC': ['0.00448799',
                                                                                                     'A']},
                 '81U27F9701833': {'TPI_VCC::CONT_X_VCCCONT_K_START_X_X_X_X_VCC_STG_HC_VCC_STG_HC': ['0.00450325',
                                                                                                     'A']},
                 '81U27F9701862': {'TPI_VCC::CONT_X_VCCCONT_K_START_X_X_X_X_VCC_STG_HC_VCC_STG_HC': ['0.00578117',
                                                                                                     'A']},
                 '81U27F9702076': {'TPI_VCC::CONT_X_VCCCONT_K_START_X_X_X_X_VCC_STG_HC_VCC_STG_HC': ['0.00550652',
                                                                                                     'A']}}
        self.assertEqual(data, xpect)

        # all tnames
        data = Ituff(tsingle=['2_mrslt_'], tname='').read(itf).tdata
        self.assertEqual(count_iter(keys_atlevel(data, 1)), 594)

        # two kinds
        ituff = Ituff(tmultiple=['2_comnt_mrslt_', '0_mrslt_'], retname='(CheckDieForce_TDAU_CH_SA|CheckDieForce_TDAU_CH_CORE)')
        data = ituff.read(itf).tdata
        self.assertEqual(count_iter(keys_atlevel(data, 0)), 6)
        self.assertEqual(count_iter(keys_atlevel(data, 1)), 12)
        self.assertEqual(count_iter(keys_atlevel(data, 2)), 30)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_combined(self):
        itf = f'{UT_DIR}/ituff_test_paths/Unzipped_Multi/J119060CR_6248_1B_ALL'

        ituff = Ituff(single=['3_ttime_'], tsingle=['0_mrslt_'], tname='CheckDieForce_TDAU_CH_CORE')
        ituff.read(itf)
        self.assertEqual(len(ituff.lot), 27)

        xpect = {'81U27F9700992': {'CheckDieForce_TDAU_CH_CORE': '99.5000'},
                 '81U27F9701006': {'CheckDieForce_TDAU_CH_CORE': '99.9000'},
                 '81U27F9701820': {'CheckDieForce_TDAU_CH_CORE': '100.1000'},
                 '81U27F9701833': {'CheckDieForce_TDAU_CH_CORE': '101.1000'},
                 '81U27F9701862': {'CheckDieForce_TDAU_CH_CORE': '100.8000'},
                 '81U27F9702076': {'CheckDieForce_TDAU_CH_CORE': '99.8000'}}
        self.assertEqual(ituff.tdata, xpect)

        xpect = {'81U27F9700992': {'ttime': '7.9834'},
                 '81U27F9701006': {'ttime': '7.0723'},
                 '81U27F9701820': {'ttime': '7.0633'},
                 '81U27F9701833': {'ttime': '151.3048'},
                 '81U27F9701862': {'ttime': '151.3006'},
                 '81U27F9702076': {'ttime': '7.0386'}}
        self.assertEqual(ituff.data, xpect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
