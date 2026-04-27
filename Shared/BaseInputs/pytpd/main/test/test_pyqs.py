#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for pyqs.py (main executable)
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar
from unittest.mock import Mock
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from gadget.gizmo import with_
from gadget.disk import Chdir
from main.pyqs import *
from os.path import join, dirname, abspath
import sys
import glob


class TestArgs(TestCase):

    def test_noargs(self):
        # no args
        cmd = f'pyqs.py'.split()
        with MockVar(sys, "argv", cmd):
            with self.assertRaises(SystemExit):
                PyQsArgs().main()

        # invalid args
        cmd = f'pyqs.py oops'.split()
        with MockVar(sys, "argv", cmd):
            with self.assertRaises(SystemExit):
                with CaptureStdoutLog() as p:
                    self.assertEqual(PyQsArgs().main(), 2)
            self.assertIn('Unknown command', p.getvalue())


class TestInteg(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True)
    def test_basic(self):
        Merge.clear()

        # Two qs.py files in the testprogram, full run
        cmd = f'pyqs.py merge'.split()
        with MockVar(sys, "argv", cmd):
            PyQsArgs().main()

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR::test1">
        <flowResult>
            <occurrence default="true"><portData port="1" status="Pass"/></occurrence>
        </flowResult>
    </response>

    <response testInstance="ARR::test2">
        <flowResult>
            <occurrence default="true"><portData port="1" status="Pass"/></occurrence>
        </flowResult>
    </response>

    <response testInstance="SCN::test3">
        <flowResult>
            <occurrence default="true"><portData port="1" status="Pass"/></occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(File('final_qs.xml').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True)
    def test_basic_one(self):
        Merge.clear()

        # Two qs.py files in the testprogram, full run
        cmd = f'pyqs.py Modules/ARR/qs.py -mtpl Modules/ARR/array.mtpl'.split()
        with MockVar(sys, "argv", cmd):
            PyQsArgs().main()

        expect = '''
<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="HappyPathFlow" type="flow" >
    <response testInstance="ARR::test1">
        <flowResult>
            <occurrence default="true"><portData port="1" status="Pass"/></occurrence>
        </flowResult>
    </response>

    <response testInstance="ARR::test2">
        <flowResult>
            <occurrence default="true"><portData port="1" status="Pass"/></occurrence>
        </flowResult>
    </response>

</virtualdut>
</Quicksim>
'''
        self.assertTextEqual(File('final_qs.xml').read(), expect)

    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    @with_(MockVar, Convert, 'get_import', Mock(return_value="from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, triggerData, patternData"))
    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple7', chdir=True)
    def test_convert_merge(self):
        # Convert a golden quicksim xml into module qs files
        # Run merge and get the final qs - this checks how all the objects interact with each other

        # setup: cleanup first
        for item in glob.glob('Modules/*/*.py'):
            File(item).unlink()

        # part1 - convert xml to qs
        cmd = f'pyqs.py {UT_DIR_REPO}/pyqs_files/ARLS_QuickSim_Base_golden.xml -convert'.split()
        with MockVar(sys, "argv", cmd):
            PyQsArgs().main()

        # check it
        final = []
        for ff in sorted(glob.glob('Modules/*/*.py')):
            final.append(File(ff).read())
        File('concat.txt').rewrite('\n'.join(final), 'unittest')
        self.assertGoldEqual('concat.txt', f'{UT_DIR_REPO}/pyqs_files/ARLS_QuickSim_Base.py.gold')

        # put this file in Modules/SCN/qs.py
        final = ['from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, triggerData, patternData\n',
                 "SetModule('SCN')\n"]
        for line in File('concat.txt').raw():
            if not line.startswith(('from pyqs import', 'SetModule(')):
                final.append(line)
        File('Modules/SCN/qs.py').rewrite(''.join(final), 'unittest')

        # part2 - Run the merge. It is not really merging many py files, just one .py file: SCN
        Merge.clear()
        cmd = f'pyqs.py merge'.split()
        with MockVar(sys, "argv", cmd):
            PyQsArgs().main()
        self.assertGoldEqual('final_qs.xml', f'{UT_DIR_REPO}/pyqs_files/ARLS_QuickSim_Base.merge.xml.gold')


class TestConvert(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic(self):
        text = '''<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>

<virtualdut name="ARLSBBaseValidation" type="flow" >
    <response testInstance="FUS_ISEED_YXX::FUSE_X_SCREEN_K_START_X_X_X_X_UNIT_INFO_DECODE">
        <flowResult injectTime="Before">
           <occurrence default="true">
              <portData port="3" status="Pass"/>
           </occurrence>
           <occurrence default="true" start="1" stop="2">
              <portData port="3" status="Fail"/>
           </occurrence>
        </flowResult>

        <plistResult>
             <occurrence default="true" status="Pass">
                 <ctvData burst="0" pin="IP_PCH::XXGPP_SC_21_TDO" value="1001"/>
             </occurrence>
       </plistResult>

    </response>

    <response testInstance="FUS_ISEED_YXX::FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUSPOSTUNLOCK" plist="gcd_dfxagg_read_hvm_status_csr">
        <plistResult>
             <occurrence default="true" status="Pass">
                 <ctvData burst="0" pin="IP_PCH::XXGPP_SC_21_TDO" value="100"/>
                 <ctvData burst="0" pin="IP_PCH::XXGPP_SC_21_TDO" value="200"/>
             </occurrence>
       </plistResult>
   </response>

</virtualdut>
</Quicksim>
'''
        File('a.xml').touch(text)

        cmd = f'pyqs.py a.xml -convert'.split()
        with MockVar(sys, "argv", cmd):
            result = PyQsArgs().main()

        expect = '''
from pyqs import PortInject, ManualInject, SetModule, ctvData, portData, pinData, thermalData, userVar, cycleData, triggerData, patternData
SetModule('FUS_ISEED_YXX')
ManualInject("FUSE_X_SCREEN_K_START_X_X_X_X_UNIT_INFO_DECODE",
    flowResult={'injectTime': 'Before'},
    occurrence={'default': 'true'},
    actions=[
        portData(port="3", status="Pass"),
    ])
ManualInject("FUSE_X_SCREEN_K_START_X_X_X_X_UNIT_INFO_DECODE",
    flowResult={'injectTime': 'Before'},
    occurrence={'default': 'true', 'start': '1', 'stop': '2'},
    actions=[
        portData(port="3", status="Fail"),
    ])
ManualInject("FUSE_X_SCREEN_K_START_X_X_X_X_UNIT_INFO_DECODE",
    plistResult={},
    actions=[
        ctvData(burst="0", pin="IP_PCH::XXGPP_SC_21_TDO", value="1001"),
    ])
ManualInject("FUSE_X_CTVDECODER_K_START_X_X_X_X_TAP_STATUSPOSTUNLOCK",
    plist="gcd_dfxagg_read_hvm_status_csr",
    plistResult={},
    actions=[
        ctvData(burst="0", pin="IP_PCH::XXGPP_SC_21_TDO", value="100"),
        ctvData(burst="0", pin="IP_PCH::XXGPP_SC_21_TDO", value="200"),
    ])
'''
        self.assertTextEqual(File('Modules/FUS_ISEED_YXX/qs.py').read(), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, Convert, 'get_import', Mock(return_value="from pyqs"))
    def test_cycledata(self):
        text = '''<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>
<virtualdut name="LLCVNNAONEND_RECOVERY" type="flow" >
<response testInstance="ARR_CCF_C68::SSA_CCF_SB_K_END_080808_VNNAON_VNOM_LFM_LLCDATA" plist="arr_cdie_end_pbist_ccf_stf_ks_chk_fx_eccoff_ssa_llc_dat_list">
<plistResult>
<occurrence default="true">
<patternData pattern="g3974033W6085252A_NZ_VDPAxCA056_Hm7g1j00xxx0p_gxxx080808kxxxxxxxxxx_sDPAA2PxxATC004J2bx_x00_llc_dat_pmovi_x_x">
    <domainData name="ACPU_TAP_ALL">
        <cycleData address="682"  >
            <pinData pin="ZZ_SORT_CDIE_TAP_TDO" value="0"/>
            <!--<pinData pin="ZZ_SORT_CDIE_TAP_TDO" value="0"/> -->
        </cycleData>
    </domainData>
</patternData>
<patternData pattern="x">
    <domainData name="ACPU_TAP_ALL">
        <cycleData address="682"  >
            <pinData pin="ZZ_SORT_CDIE_TAP_TDO" value="0"/>
            <pinData pin="ZZ_SORT_CDIE_TAP_TD1" value="0"/>
        </cycleData>
    </domainData>
</patternData>
</occurrence>
</plistResult>
</response>
</virtualdut>
</Quicksim>
'''
        File('a.xml').touch(text)

        cmd = f'pyqs.py a.xml -convert'.split()
        with MockVar(sys, "argv", cmd):
            result = PyQsArgs().main()

        expect = '''
from pyqs
SetModule('ARR_CCF_C68')
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
        patternData(
            domainData="ACPU_TAP_ALL",
            pattern="x",
            actions=[
                cycleData(682, actions=[
                    pinData(pin="ZZ_SORT_CDIE_TAP_TDO", value="0"),
                    pinData(pin="ZZ_SORT_CDIE_TAP_TD1", value="0"),
                ]),
            ]),
    ])
'''
        self.assertTextEqual(File('Modules/ARR_CCF_C68/qs.py').read(), expect)

    @with_(TempDir, chdir=True)
    def test_error(self):
        text = '''<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>

<virtualdut name="ARLSBBaseValidation" type="flow" >
<response testInstance="DLVR_X_ANADC_K_BEGCPUPKG_X_X_X_X_MRVSXTOP" plist="pth_cdie_begin_dlvr_mrvtopbuftrim_list">
  <plistResult>
    <occurrence default="true" status="Pass">
      <ctvData burst="0" pin="IP_CPU::XXDDRDQ_IL512_NIL512_LP30_2_TDO" value="1001"/>
    </occurrence>
  </plistResult>
</response>
</virtualdut>
</Quicksim>
'''
        File('a.xml').touch(text)

        cmd = f'pyqs.py a.xml -convert'.split()
        with MockVar(sys, "argv", cmd):
            with self.assertRaisesRegex(ErrorInput, 'Missing module scope'):
                PyQsArgs().main()

    @with_(TempDir, chdir=True)
    @with_(MockVar, Convert, 'get_import', Mock(return_value="from pyqs"))
    def test_pattern(self):
        text = '''<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>

<virtualdut name="ARLSBBaseValidation" type="flow" >
<response testInstance="IP_CPU::FUS_ISEED_YXX::DLVR_X_ANADC_K_BEGCPUPKG_X_X_X_X_MRVSXTOP" plist="pth_cdie_begin_dlvr_mrvtopbuftrim_list">
  <plistResult>
    <occurrence default="true" status="Pass">
      <ctvData burst="0" pin="IP_CPU::XXDDRDQ_IL512_NIL512_LP30_2_TDO" value="1001"/>

      <patternData pattern="g0417338C">
        <domainData name="ACPU_TAP_ALL">
          <triggerData type="LevelsTC" name="Trigger1"/>
          <triggerData type="LevelsTC" name="Trigger1"/>
        </domainData>
      </patternData>

    </occurrence>
  </plistResult>
</response>
</virtualdut>
</Quicksim>
'''
        File('a.xml').touch(text)

        cmd = f'pyqs.py a.xml -convert'.split()
        with MockVar(sys, "argv", cmd):
            result = PyQsArgs().main()

        expect = '''
from pyqs
SetModule('IP_CPU::FUS_ISEED_YXX')
ManualInject("DLVR_X_ANADC_K_BEGCPUPKG_X_X_X_X_MRVSXTOP",
    plist="pth_cdie_begin_dlvr_mrvtopbuftrim_list",
    plistResult={},
    actions=[
        ctvData(burst="0", pin="IP_CPU::XXDDRDQ_IL512_NIL512_LP30_2_TDO", value="1001"),
        patternData(
            domainData="ACPU_TAP_ALL",
            pattern="g0417338C",
            actions=[
                triggerData(name="Trigger1", type="LevelsTC"),
                triggerData(name="Trigger1", type="LevelsTC"),
            ]),
    ])
'''
        self.assertTextEqual(File('Modules/FUS_ISEED_YXX/qs.py').read(), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, Convert, 'get_import', Mock(return_value="from pyqs"))
    def test_pattern1(self):
        text = '''<?xml version="1.0" encoding="utf-8" ?>
<Quicksim>

<virtualdut name="ARLSBBaseValidation" type="flow" >
<response testInstance="IP_CPU::FUS_ISEED_YXX::DLVR_X_ANADC_K_BEGCPUPKG_X_X_X_X_MRVSXTOP" plist="pth_cdie_begin_dlvr_mrvtopbuftrim_list">
  <plistResult>
    <occurrence default="true" status="Pass">
      <ctvData burst="0" pin="IP_CPU::XXDDRDQ_IL512_NIL512_LP30_2_TDO" value="1001"/>

      <patternData pattern="g0417338C">
        <domainData name="ACPU_TAP_ALL">
          <triggerData type="LevelsTC" name="Trigger1"/>
        </domainData>
      </patternData>
      <patternData pattern="g0417338D">
        <domainData name="ACPU_TAP_ALL">
          <triggerData type="LevelsTC" name="Trigger1"/>
        </domainData>
      </patternData>

    </occurrence>
  </plistResult>
</response>
</virtualdut>
</Quicksim>
'''
        File('a.xml').touch(text)

        cmd = f'pyqs.py a.xml -convert'.split()
        with MockVar(sys, "argv", cmd):
            result = PyQsArgs().main()

        expect = '''
from pyqs
SetModule('IP_CPU::FUS_ISEED_YXX')
ManualInject("DLVR_X_ANADC_K_BEGCPUPKG_X_X_X_X_MRVSXTOP",
    plist="pth_cdie_begin_dlvr_mrvtopbuftrim_list",
    plistResult={},
    actions=[
        ctvData(burst="0", pin="IP_CPU::XXDDRDQ_IL512_NIL512_LP30_2_TDO", value="1001"),
        patternData(
            domainData="ACPU_TAP_ALL",
            pattern="g0417338C",
            actions=[
                triggerData(name="Trigger1", type="LevelsTC"),
            ]),
        patternData(
            domainData="ACPU_TAP_ALL",
            pattern="g0417338D",
            actions=[
                triggerData(name="Trigger1", type="LevelsTC"),
            ]),
    ])
'''
        self.assertTextEqual(File('Modules/FUS_ISEED_YXX/qs.py').read(), expect)

    def test_to_keyeqval(self):
        obj = Convert(None)
        self.assertEqual(obj.to_keyeqval({'base': '0110', 'pin': 'xxy'}),
                         'base="0110", pin="xxy"')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
