#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for template_common.py

Steps:
1. For module qgate, remove "qgates." in "from qgates." since py file and unitest are on the same folder.
2. Replace TestCheckerNameHere to the name of the checker class
3. Run coverage and see what code is not tested
4. To run, execute this file "test_template_common.py -v"

"""
import sys
try:
    from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.mask_pin_chk import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import shutil


class TestMaskTDOPins(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env').pickle_init()
        obj = MaskTDOChk(tpobj)
        obj.main()

        # check results, one fail and one pass

        expect = [{'id': 230,
                   'message': 'RESET_X_FUNC_E_BEGGT_X_INF_X_X_CDT_ROOT_AON_BBS_PRIME is masking '
                              'a TDO pin (XXGPP_H_9_UART0_TXD), please mask this pin in the PLIST',
                   'module': 'DRV_RESET_GXX'}]
        self.assertEqual(obj.result, expect)
        self.assertEqual(len(obj.passed), 37)

    def test_mocked_case2(self):
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple4a'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            pinfile = r'''Version 1.0;

        PinDescription
        {
                Resource HPCC.dpin
                {
                    AUDCLK;
                    BUDCLK;
                    XXGPP_A_14_ESPI_CS2_B;
                    PROBE_TRIG_GCD_TAP_1;

                        Group all_dmn
                        {
                                AUDCLK
                        }
                        Group gcd_tap_all
                        {
                            XXGPP_A_14_ESPI_CS2_B,
                            PROBE_TRIG_GCD_TAP_1
                }
                }
               DomainDefinitions
                {
                        Domain ALL
                        {
                                all_dmn
                        }
                }
        }
        '''
            File('TPL/Shared/BaseInputs/PinDefinitions.pin').touch(pinfile, mkdir=True, newfile=True)
            tpobj = TestProgram(envfile)
            # obj = MaskTDOChk(tpobj)
            data = [('PTH_DTS_CXX', 'test_instance1', {'mask_pins': 'XX_EDM_SOC XX_EDM_IOE XX_CORE_DLVR_VIEWANA_0 XX_CORE_DLVR_VIEWANA_1 XXRTCX1 pkgp_shops_upper_grp59 XXGPP_A_14_ESPI_CS2_B'},
                     {999: 'SBFT_ATOM_VMIN_K_LTTCSOC_X_VCCSA_F3_2500_L2DRAGON_1507'}),
                    ('PTH_DTS_GXX', 'test_instance2', {
                        'MaskPins': 'XX_EDM_SOC,XX_EDM_IOE, XX_CORE_DLVR_VIEWANA_0, XX_CORE_DLVR_VIEWANA_1, XXRTCX1, pkgp_shops_upper_grp59, XXGPP_A_14_ESPI_CS2_B'},
                     {999: 'SBFT_ATOM_VMIN_K_LTTCSOC_X_VCCSA_F3_2500_L2DRAGON_1507'}),
                    ('PTH_DTS_VXX', 'test_instance2', {
                        'MaskPins': 'XX_EDM_SOC'},
                     {999: 'SBFT_ATOM_VMIN_K_LTTCSOC_X_VCCSA_F3_2500_L2DRAGON_1507'}),
                    ('PTH_DTS_YXX', 'test_instance4', {
                        'MaskPins': 'XX_EDM_SOC, IP_PCH::gcd_tap_all'},
                     {999: 'SBFT_ATOM_VMIN_K_LTTCSOC_X_VCCSA_F3_2500_L2DRAGON_1507'}),
                    ('PTH_DTS_WXX', 'test_instance3', {
                        'mask_pins': ' IP_PCH::gcd_tap_all ,XX_EDM_SOC'},
                     {999: 'SBFT_ATOM_VMIN_K_LTTCSOC_X_VCCSA_F3_2500_L2DRAGON_1507'})]
            with MockVar(tpobj.mtpl, "iter_flows", Mock(return_value=data)):
                obj = MaskTDOChk(tpobj)
                obj.main()
                # pprint(obj.result)
            expect = [{'id': 230,
                       'message': 'test_instance1 is masking a TDO pin (XXGPP_A_14_ESPI_CS2_B), '
                                  'please mask this pin in the PLIST',
                       'module': 'PTH_DTS_CXX'},
                      {'id': 230,
                       'message': 'test_instance2 is masking a TDO pin (XXGPP_A_14_ESPI_CS2_B), '
                                  'please mask this pin in the PLIST',
                       'module': 'PTH_DTS_GXX'},
                      {'id': 230,
                       'message': 'test_instance4 is masking a TDO pin (XXGPP_A_14_ESPI_CS2_B) from '
                                  '(gcd_tap_all) pingroup, please mask this pin in the PLIST',
                       'module': 'PTH_DTS_YXX'},
                      {'id': 230,
                       'message': 'test_instance3 is masking a TDO pin (XXGPP_A_14_ESPI_CS2_B) from '
                                  '(gcd_tap_all) pingroup, please mask this pin in the PLIST',
                       'module': 'PTH_DTS_WXX'}]
            self.assertEqual(obj.result, expect)
            self.assertEqual(len(obj.passed), 2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
