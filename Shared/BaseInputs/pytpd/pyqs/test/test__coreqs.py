#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unitest for pyqs core
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV  # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
from tp.testprogram import TestProgram
from pyqs._coreqs import *
from main.test.test_pyqs import TestInteg        # Do not remove
import pyqs._coreqs as coreqs
from unittest.mock import patch, MagicMock
from main.pyqs import PyQsArgs
import sys


class TestPortInject(TestCase):

    def test_input_type(self):
        obj = PortInject("a", "b", "c")
        self.assertEqual(obj.inputlist, ['a', 'b', 'c'])

        obj = PortInject(["a", "b", "c"])
        self.assertEqual(obj.inputlist, ['a', 'b', 'c'])

    def test_basic(self):
        # case: Two modules
        # case: Two instance in argument
        Merge.clear()

        # ======= Start of Code
        SetModule('ARR_CORE')
        PortInject('test1', 'test2')
        SetModule('SCN_CORE')
        PortInject('test5')
        # ======= End Code

        obj = Merge(None)

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR_CORE::test1">
        <flowResult>
            <occurrence default="true"><portData port="1" status="Pass"/></occurrence>
        </flowResult>
    </response>

    <response testInstance="ARR_CORE::test2">
        <flowResult>
            <occurrence default="true"><portData port="1" status="Pass"/></occurrence>
        </flowResult>
    </response>

    <response testInstance="SCN_CORE::test5">
        <flowResult>
            <occurrence default="true"><portData port="1" status="Pass"/></occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

        # case: two PortInject
        Merge.clear()
        # ======= Start of Code
        SetModule('ARR_CORE')
        PortInject('test1')
        PortInject('test2')
        SetModule('SCN_CORE')
        PortInject('test5')
        # ======= End Code
        self.assertTextEqual(obj.main(), expect)

        # case: two PortInject in a list
        Merge.clear()
        # ======= Start of Code
        SetModule('ARR_CORE')
        PortInject(['test1', 'test2'])
        SetModule('SCN_CORE')
        PortInject('test5')
        # ======= End Code
        self.assertTextEqual(obj.main(), expect)

    def test_port2(self):
        # good template to copy from
        Merge.clear()

        # ======= Start of Code
        SetModule('ARR_CORE')
        PortInject('test1:2')
        # ======= End Code

        obj = Merge(None)

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR_CORE::test1">
        <flowResult>
            <occurrence default="true"><portData port="2" status="Pass"/></occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)


class TestManualInject(TestCase):

    def test_basic(self):
        Merge.clear()
        # ======= Start of Code
        SetModule('ARR_CORE')
        ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     plist="FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     plistResult={},
                     actions=[ctvData(captureDirection="RightToLeft", burst='0',
                                      pin="XXJTAG_TDO",
                                      value="1001000000000000101111000000000011110000101000010000010000110000")],
                     )
        ManualInject("Testinstance1",
                     plistResult={},
                     actions=[ctvData(pin='A', value='B')]
                     )

        # ======= End Code

        obj = Merge(None)

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR_CORE::FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS" plist="FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS">
        <plistResult>
            <occurrence default="true" status="Pass">
                <ctvData captureDirection="RightToLeft" pin="XXJTAG_TDO" value="1001000000000000101111000000000011110000101000010000010000110000" burst="0"/>
            </occurrence>
        </plistResult>
    </response>

    <response testInstance="ARR_CORE::Testinstance1">
        <plistResult>
            <occurrence default="true" status="Pass">
                <ctvData pin="A" value="B"/>
            </occurrence>
        </plistResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_occurrence_sep(self):
        # same testinstance same occurence
        Merge.clear()
        # ======= Start of Code
        SetModule('ARR_CORE')
        ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     dcResult={},
                     actions=[ctvData(pin='A', value='V')])
        ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     dcResult={},
                     actions=[ctvData(pin='A', value='V')])
        # ======= End Code

        obj = Merge(None)

        expect = '''<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR_CORE::FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS">
        <dcResult>
            <occurrence default="true" status="Pass">
                <ctvData pin="A" value="V"/>
            </occurrence>
        </dcResult>
    </response>

    <response testInstance="ARR_CORE::FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS">
        <dcResult>
            <occurrence default="true" status="Pass">
                <ctvData pin="A" value="V"/>
            </occurrence>
        </dcResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_multi2(self):
        # Multiple level2
        # Multiple level4a
        Merge.clear()
        # ======= Start of Code
        SetModule('ARR_CORE')
        ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     dcResult={},
                     actions=[ctvData(pin='A', value='V'),
                              ctvData(pin='B', value='Y')])
        ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     flowResult={},
                     actions=[ctvData(pin='C', value='V'),
                              ctvData(pin='D', value='Y')])
        # ======= End Code

        obj = Merge(None)

        expect = '''<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR_CORE::FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS">
        <dcResult>
            <occurrence default="true" status="Pass">
                <ctvData pin="A" value="V"/>
                <ctvData pin="B" value="Y"/>
            </occurrence>
        </dcResult>
        <flowResult>
            <occurrence default="true" status="Pass">
                <ctvData pin="C" value="V"/>
                <ctvData pin="D" value="Y"/>
            </occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_multi3(self):
        # Multiple level3
        Merge.clear()
        # ======= Start of Code
        SetModule('ARR_CORE')
        ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     thermalResult={'a': 1},
                     actions=[ctvData(pin='A', value='V')])
        ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     occurrence={'default': 'false'},
                     thermalResult={'a': 1},
                     actions=[ctvData(pin='C', value='V')])
        ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     thermalResult={},
                     actions=[ctvData(pin='D', value='V')])
        # ======= End Code

        obj = Merge(None)

        expect = '''<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR_CORE::FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS">
        <thermalResult a="1">
            <occurrence default="true" status="Pass">
                <ctvData pin="A" value="V"/>
            </occurrence>
            <occurrence default="false">
                <ctvData pin="C" value="V"/>
            </occurrence>
        </thermalResult>
        <thermalResult>
            <occurrence default="true" status="Pass">
                <ctvData pin="D" value="V"/>
            </occurrence>
        </thermalResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_thermal(self):
        # good template to copy from
        Merge.clear()

        # ======= Start of Code
        SetModule('ARR_CORE')
        ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     dcResult={},
                     actions=[thermalData(pin='IP_CPU::TDAU_CH_CORE', value='70'),
                              thermalData(pin='IP_PCH::TDAU_CH_GCD', value='70'),
                              thermalData(pin='IP_PCH::TDAU_CH_IOE', value='70'),
                              thermalData(pin='TDAU_CH_SOC', value='70')])
        # ======= End Code

        obj = Merge(None)

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR_CORE::FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS">
        <dcResult>
            <occurrence default="true" status="Pass">
                <thermalData pin="IP_CPU::TDAU_CH_CORE" value="70"/>
                <thermalData pin="IP_PCH::TDAU_CH_GCD" value="70"/>
                <thermalData pin="IP_PCH::TDAU_CH_IOE" value="70"/>
                <thermalData pin="TDAU_CH_SOC" value="70"/>
            </occurrence>
        </dcResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_pindata(self):
        # good template to copy from
        Merge.clear()

        # ======= Start of Code
        SetModule('TPI_SHOPS_XXX')
        ManualInject("SHOPS_X_SHOPSDC_K_START_X_X_X_X_PKGLOWERDIODES",
                     dcResult={},
                     actions=[pinData(pin="TYCHE_VIEWANA0", value="-0.033741"),
                              pinData(pin="TYCHE_VIEWANA1", value="-0.033741"),
                              pinData(pin="IP_PCH::XX_EDM_BASE", value="-0.784893", repeat='10'),
                              pinData(pin="IP_PCH::XXFUSEIOE_TM_IO_02", value="-0.784893"),
                              ]
                     )
        # ======= End Code

        obj = Merge(None)

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="TPI_SHOPS_XXX::SHOPS_X_SHOPSDC_K_START_X_X_X_X_PKGLOWERDIODES">
        <dcResult>
            <occurrence default="true" status="Pass">
                <pinData pin="TYCHE_VIEWANA0" value="-0.033741"/>
                <pinData pin="TYCHE_VIEWANA1" value="-0.033741"/>
                <pinData pin="IP_PCH::XX_EDM_BASE" value="-0.784893" repeat="10"/>
                <pinData pin="IP_PCH::XXFUSEIOE_TM_IO_02" value="-0.784893"/>
            </occurrence>
        </dcResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_uservar(self):
        # good template to copy from
        Merge.clear()

        # ======= Start of Code
        SetModule('YBS_UPSS')
        ManualInject("UPSS_X_YBSHYBRID_K_FACT_X_X_X_X_GENERATEINPUTS",
                     flowResult={'injectTime': 'before'},
                     actions=[userVar(name="YBS_UPSS.UPS_CRDIS_UPS0", value='"00000000000000000000000000000000000000"',
                                      type="String"),
                              userVar(name="YBS_UPSS.UPS_CHADIS_UPS0", value='"00000000000000000000000000000000000000"',
                                      type="String"),
                              ]
                     )
        # ======= End Code

        obj = Merge(None)

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="YBS_UPSS::UPSS_X_YBSHYBRID_K_FACT_X_X_X_X_GENERATEINPUTS">
        <flowResult injectTime="before">
            <occurrence default="true" status="Pass">
                <userVar name="YBS_UPSS.UPS_CRDIS_UPS0" value='"00000000000000000000000000000000000000"' type="String"/>
                <userVar name="YBS_UPSS.UPS_CHADIS_UPS0" value='"00000000000000000000000000000000000000"' type="String"/>
            </occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_portData(self):
        # good template to copy from
        Merge.clear()

        # ======= Start of Code
        SetModule('PTH_DLVR_CXX')
        ManualInject("DLVR_X_CTV_E_BEGCPUPKG_X_X_X_X_TAP2REG_DUMP",
                     flowResult={},
                     actions=[
                         portData(port="0", status="Fail"),
                     ]
                     )
        ManualInject("DLVR_X_CTV_E_BEGCPUPKG_X_X_X_X_TAP2REG_DUMP2",
                     flowResult={},
                     actions=[
                         portData(port="1", status="Pass"),
                     ]
                     )
        # ======= End Code

        obj = Merge(None)

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="PTH_DLVR_CXX::DLVR_X_CTV_E_BEGCPUPKG_X_X_X_X_TAP2REG_DUMP">
        <flowResult>
            <occurrence default="true" status="Pass">
                <portData port="0" status="Fail"/>
            </occurrence>
        </flowResult>
    </response>

    <response testInstance="PTH_DLVR_CXX::DLVR_X_CTV_E_BEGCPUPKG_X_X_X_X_TAP2REG_DUMP2">
        <flowResult>
            <occurrence default="true" status="Pass">
                <portData port="1" status="Pass"/>
            </occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_comment(self):
        # good template to copy from
        Merge.clear()

        # ======= Start of Code
        SetModule('YBS_UPSS')
        ManualInject("UPSS_X_YBSHYBRID_K_FACT_X_X_X_X_GENERATEINPUTS",
                     flowResult={'injectTime': 'before'},
                     actions=[
                         Comment(comment="THIS IS A COMMENT"),
                         userVar(name="YBS_UPSS.UPS_CRDIS_UPS0", value='"00000000000000000000000000000000000000"',
                                 type="String"),
                         userVar(name="YBS_UPSS.UPS_CHADIS_UPS0", value='"00000000000000000000000000000000000000"',
                                 type="String"),
                     ]
                     )
        # ======= End Code

        obj = Merge(None)

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="YBS_UPSS::UPSS_X_YBSHYBRID_K_FACT_X_X_X_X_GENERATEINPUTS">
        <flowResult injectTime="before">
            <occurrence default="true" status="Pass">
                <!-- THIS IS A COMMENT -->
                <userVar name="YBS_UPSS.UPS_CRDIS_UPS0" value='"00000000000000000000000000000000000000"' type="String"/>
                <userVar name="YBS_UPSS.UPS_CHADIS_UPS0" value='"00000000000000000000000000000000000000"' type="String"/>
            </occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_multipat(self):
        Merge.clear()
        # ======= Start of Code
        SetModule('ARR_CORE')
        ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS",
                     plistResult={},
                     actions=[patternData('g0', 'dom1', [triggerData('A', 'B'),
                                                         triggerData('C', 'D')]),
                              patternData('g0', 'dom2', [triggerData('E', 'B'),
                                                         triggerData('F', 'D')]),
                              patternData('g1', 'dom0', [cycleData('123', [pinData(pin='TAP', value='0')])])
                              ])
        # ======= End Code

        obj = Merge(None)

        expect = '''<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR_CORE::FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUS">
        <plistResult>
            <occurrence default="true" status="Pass">
                <patternData pattern="g0">
                    <domainData name="dom1">
                        <triggerData type="B" name="A"/>
                        <triggerData type="D" name="C"/>
                    </domainData>
                    <domainData name="dom2">
                        <triggerData type="B" name="E"/>
                        <triggerData type="D" name="F"/>
                    </domainData>
                </patternData>
                <patternData pattern="g1">
                    <domainData name="dom0">
                        <cycleData address="123">
                            <pinData pin="TAP" value="0"/>
                        </cycleData>
                    </domainData>
                </patternData>
            </occurrence>
        </plistResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_cycledata(self):
        Merge.clear()
        # ======= Start of Code
        SetModule('ARR_CORE')
        ManualInject("SSA_CCF_SB_K_END_080808_VNNAON_VNOM_LFM_LLCDATA",
                     plist="arr_cdie_end_pbist_ccf_stf_ks_chk_fx_eccoff_ssa_llc_dat_list",
                     plistResult={},
                     occurrence={'default': 'true'},
                     actions=[
                         patternData(
                             domainData="ACPU_TAP_ALL",
                             pattern="g3974033W6085252A_NZ_VDPAxCA056_Hm7g1j00xxx0p_gxxx080808kxxxxxxxxxx_sDPAA2PxxATC004J2bx_x00_llc_dat_pmovi_x_x",
                             actions=[
                                 cycleData(682, actions=[
                                     pinData(pin="ZZ_SORT_CDIE_TAP_TDO", value="0"),
                                 ]),
                             ]),
                     ])
        # ======= End Code

        obj = Merge(None)

        expect = '''<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR_CORE::SSA_CCF_SB_K_END_080808_VNNAON_VNOM_LFM_LLCDATA" plist="arr_cdie_end_pbist_ccf_stf_ks_chk_fx_eccoff_ssa_llc_dat_list">
        <plistResult>
            <occurrence default="true">
                <patternData pattern="g3974033W6085252A_NZ_VDPAxCA056_Hm7g1j00xxx0p_gxxx080808kxxxxxxxxxx_sDPAA2PxxATC004J2bx_x00_llc_dat_pmovi_x_x">
                    <domainData name="ACPU_TAP_ALL">
                        <cycleData address="682">
                            <pinData pin="ZZ_SORT_CDIE_TAP_TDO" value="0"/>
                        </cycleData>
                    </domainData>
                </patternData>
            </occurrence>
        </plistResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)


class TestAutoInject(TestCase):

    def test_ut(self):
        Merge.clear()

        # ======= Start of Code
        SetModule('ARR')
        simpleAuto('VminTC')
        # ======= End Code

        obj = Merge(TestProgram(f'{UT_DIR_REPO}/Simple7').init())

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR::CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1501">
        <flowResult>
            <occurrence default="true"></occurrence>
        </flowResult>
    </response>
    <response testInstance="ARR::CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1502">
        <flowResult>
            <occurrence default="true"></occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True)
    def test_auto_port1(self):
        Merge.clear()

        # modify the TP in tempdir
        File('./Modules/ARR/qs.py').unlink()
        File('./Modules/SCN/qs.py').unlink()
        File('./Modules/SCN/qs.py').touch()       # Empty qs.py file
        File('Shared/BaseInputs/Scripts/auto_port1_inject_list.txt').touch('iCFuncTest', mkdir=True)

        cmd = f'pyqs.py merge'.split()
        with MockVar(sys, "argv", cmd):
            PyQsArgs().main()

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="SCN::CCB">
        <flowResult>
            <occurrence default="true"><portData port="1" status="Pass"/></occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(File('final_qs.xml').read(), expect)

        # Run once
        obj = Merge(TestProgram('POR_TP/TGLH81/EnvironmentFile.env'))
        obj.read_port1_inject(obj.get_tpobj())
        self.assertEqual(obj.read_port1_inject(obj.get_tpobj()), 1)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True)
    def test_auto_port1_scope(self):
        Merge.clear()

        # modify the TP in tempdir
        File('./Modules/ARR/qs.py').unlink()
        File('./Modules/SCN/qs.py').unlink()
        File('./Modules/SCN/qs.py').touch()       # Empty qs.py file
        File('Shared/BaseInputs/Scripts/auto_port1_inject_list.txt').touch('iCFuncTest', mkdir=True)

        cmd = f'pyqs.py merge'.split()
        with MockVar(sys, "argv", cmd), \
                MockVar(TestProgram, 'get_ipname', Mock(return_value='IPX')):
            PyQsArgs().main()

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="IPX::SCN::CCB">
        <flowResult>
            <occurrence default="true"><portData port="1" status="Pass"/></occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(File('final_qs.xml').read(), expect)

        # Run once
        obj = Merge(TestProgram('POR_TP/TGLH81/EnvironmentFile.env'))
        obj.read_port1_inject(obj.get_tpobj())
        self.assertEqual(obj.read_port1_inject(obj.get_tpobj()), 1)

    def test_ut_dctest(self):
        Merge.clear()

        # ======= Start of Code
        SetModule('ARR')
        AutoIVCurve('*')
        # ======= End Code

        obj = Merge(TestProgram(f'{UT_DIR_REPO}/Simple7k').init())
        pprint(obj.main)
        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR::SHOPS_X_SHOPSDC_K_START_X_X_X_X_PKGLOWERDIODE_T7">
        <dcResult>
            <occurrence default="true">
                <pinData pin="VCC1" value="1.5"/>
                <pinData pin="VCC2" value="3.0"/>
            </occurrence>
        </dcResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_ut_dctest2(self):
        Merge.clear()

        # ======= Start of Code
        SetModule('ARR')
        AutoIVCurve('CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1501')
        # ======= End Code

        obj = Merge(TestProgram(f'{UT_DIR_REPO}/Simple7k').init())
        pprint(obj.main)
        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_AutoPortInjection(self):
        Merge.clear()

        # ======= Start of Code
        SetModule('ARR')
        AutoPort('VminTC')
        # ======= End Code

        obj = Merge(TestProgram(f'{UT_DIR_REPO}/Simple7').init())

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR::CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1501">
        <flowResult>
            <occurrence default="true">
                <portData port="1" status="Pass"/>
            </occurrence>
        </flowResult>
    </response>
    <response testInstance="ARR::CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1502">
        <flowResult>
            <occurrence default="true">
                <portData port="1" status="Pass"/>
            </occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)

    def test_AutoThermal(self):
        Merge.clear()

        # ======= Start of Code
        SetModule('ARR')
        AutoThermal('VminTC')
        AutoThermal('PrimeMixingDetectionTestMethod')
        # ======= End Code

        obj = Merge(TestProgram(f'{UT_DIR_REPO}/Simple7k').init())

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR::CA2TF_ATOM_VMAX_K_MAXAT_X_VATOM_F6_3800_FUSA_VMAX_RECOVERY_1502">
        <thermalResult>
            <occurrence default="true">
                <thermalData pin="A" value="105"/>
                <thermalData pin="B" value="105"/>
            </occurrence>
        </thermalResult>
    </response>


</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(obj.main(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
