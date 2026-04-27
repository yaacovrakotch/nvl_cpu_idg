#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for testprogram.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from tp.testprogram import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.files import File, TempDir
from gadget.shell import IS_UNIX, IS_WIN
from gadget.disk import Chdir, mkdirs
from gadget.helperclass import CaptureStdoutLog
from gadget.dictmore import keys_atlevel
from gadget.printmore import Dumper
from gadget.errors import ErrorUser
from unittest.mock import Mock
from main.tp_diff import Diff
from os.path import realpath
import tp.testprogram as testprogram


class TestTP(TestCase):

    def test_basic(self):
        with TempDir(name=True) as tdir:
            code1 = """Version 1.0;

ProgramStyle = Modular;
TestPlan Flows;
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code1, mkdir=True)
            code2 = """Version 1.0;
Test iCSimpleScoreboardTest CCF_XXXXX
{
        base_number = 2160;
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code2, mkdir=True)
            File('%s/env.env' % tdir).touch()
            File('%s/a.tpl' % tdir).touch()
            File('%s/all.xml' % tdir).touch()
            tp = TestProgram('%s/env.env' % tdir, allplist='%s/all.xml' % tdir)

            # no stpl found
            with self.assertRaisesRegex(ErrorInput, 'No .stpl file found in'):
                tp.get_stpl()

            # normal case
            tp._ut_write_stpl()
            self.assertXpathEqual(tp.get_final_mtpl(), join(tdir, '.', 'ProgramFlows.mtpl'))
            self.assertEqual(sorted(tp.get_all_mtpl_from_stpl()), [join(tdir, './Modules/ARR/a.mtpl')])
            self.assertEqual(tp.get_file_allplist(), join(tdir, 'all.xml'))
            self.assertEqual(len(tp.get_file_allplist_real()), 1)
            self.assertEqual(tp.testplan_base, 'DEFAULTBASE')

        # No ProgramFlows.mtpl
        with TempDir(name=True) as tdir:
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code2, mkdir=True)
            File('%s/env.env' % tdir).touch()
            tp = TestProgram('%s/env.env' % tdir, tpl='')._ut_write_stpl()
            self.assertEqual(tp.get_final_mtpl(), None)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_realtp(self):
        tp = TestProgram(f'{UT_DIR}/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        self.assertEqual(len(list(tp.get_all_mtpl_files())), 80)
        self.assertEqual(len(list(tp.get_all_mtpl_from_stpl())), 80)
        self.assertXpathEqual(tp.tpl, join(UT_DIR + '/TGLXXXXRXH35H00S025/TPL', 'BaseTestPlan.tpl'))
        self.assertEqual(basename(tp.get_stpl()), 'SubTestPlan_CLASS_TGLH81.stpl')
        self.assertXpathEqual(tp.get_final_mtpl(), join(UT_DIR + '/TGLXXXXRXH35H00S025/TPL',
                                                        './ProgramFlowsTestPlan/ProgramFlows.mtpl'))

        # with bom group
        tp = TestProgram(f'{UT_DIR}/ICLXXXXXXH58G2XS904/TPL/EnvironmentFile_CLASS_ICL_42_U.env')
        # tp.plists.set_plist_list()
        # self.assertEqual(len(tp.plists.get_plist_list()), 152)
        self.assertEqual(len(list(tp.get_all_mtpl_files())), 485)
        self.assertEqual(len(list(tp.get_all_mtpl_from_stpl())), 117)
        self.assertEqual(basename(tp.get_stpl()), 'SubTestPlan_CLASS_ICL_42_U.stpl')

        # some tests
        self.assertXpathEqual(tp.fullpath_tp('./Modules/blah'),
                              f'{UT_DIR}/ICLXXXXXXH58G2XS904/TPL/./Modules/blah')

    def test_get_tp_name(self):
        with TempDir(name=True) as tdir:
            expected_name = 'myTPname'
            tp_dir = join(tdir, 'TPL', expected_name)
            mkdirs(tp_dir)

            # .env file to specify the TestProgram location
            env_file = join(tp_dir, 'EnvironmentFile.env')
            File(env_file).touch("# Env contents")
            File('%s/a.tpl' % tdir).touch()
            File('%s/all.xml' % tdir).touch()
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(mkdir=True)
            tp = TestProgram(env_file)
            self.assertEqual(tp.get_tp_name(), expected_name)

            # Some random file used
            envfile = join(tp_dir, 'sample.txt')
            File(envfile).touch("# Text")
            self.assertEqual(TestProgram(envfile).get_tp_name(), expected_name)

            # Just the directory is used - with and without the TPL subdir
            self.assertEqual(TestProgram(tp_dir).get_tp_name(), expected_name)
            self.assertEqual(TestProgram(dirname(tp_dir)).get_tp_name(), expected_name)

            # Non-existant file used
            with self.assertRaises(ErrorInput):
                TestProgram(join(tp_dir, 'some_bad.txt'))

            # No Environment file found
            with self.assertRaises(ErrorInput):
                File(env_file).unlink()
                TestProgram(tp_dir)

            # TORCH Paths look like: <idrive>/RPLS8P5A0H10G11S043/POR_TP/RPL_1ST_SILICON/EnvirontmentFile.env
            tp_dir = join(tdir, 'hdmxprogs', 'tst', expected_name, 'POR_TP', 'SOMEDIR')
            envfile = join(tp_dir, 'EnvironmentFile.env')
            File(envfile).touch('# Text', mkdir=True)
            File('%s/a.tpl' % tp_dir).touch()
            File('%s/all.xml' % tp_dir).touch()
            File('%s/Modules/ARR/a.mtpl' % tp_dir).touch(mkdir=True)
            self.assertEqual(TestProgram(envfile).get_tp_name(), expected_name)

            # Sort TP Path: /intel/hdmxpats/tgl/sort_tp/tgl_sds/TGLSDSCA1H11U01S921/EnvironmentFile.env
            tp_dir = join(tdir, 'hdmxpats', 'tst', 'sort_tp', 'tst_sds', expected_name)
            envfile = join(tp_dir, 'EnvironmentFile.env')
            File(envfile).touch('# Text', mkdir=True)
            File('%s/a.tpl' % tp_dir).touch()
            File('%s/all.xml' % tp_dir).touch()
            File('%s/Modules/ARR/a.mtpl' % tp_dir).touch(mkdir=True)
            self.assertEqual(TestProgram(envfile).get_tp_name(), expected_name)

        tp1 = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        self.assertEqual(tp1.get_tp_name(), 'Simple1')

    def test_tpname_to_path(self):
        with TempDir(name=True) as tdir:
            expected_name = 'myTPname'
            tp_dir = join(tdir, 'TPL', expected_name)
            mkdirs(tp_dir)

            # .env file to specify the TestProgram location
            env_file = join(tp_dir, 'EnvironmentFile.env')
            File(env_file).touch("# Env contents")

            ipath_test = join(tdir, 'SampleTPArea')
            for name in ['TSTABC12345', 'TSTDEF98765', 'TSTXXX00000']:
                mkdirs(join(ipath_test, name))

            with MockVar(TestProgram, '_get_idrives', Mock(return_value=[ipath_test])), \
                    MockVar(TestProgram, '_derive_tpl', Mock(return_value='')),\
                    MockVar(TestProgram, '_check_exists', Mock(return_value='')), \
                    MockVar(TestProgram, '_derive_moddir', Mock(return_value='')), \
                    MockVar(TestProgram, '_derive_shareddir', Mock(return_value='')):
                tp = TestProgram(env_file)
                tp_name = 'TSTABC12345'
                self.assertEqual(tp.tpname_to_path(tp_name), join(ipath_test, tp_name))

                tp_name = 'unknown'
                with self.assertRaises(ErrorInput):
                    tp.tpname_to_path(tp_name)

                tp_name = 'TSTXYZ00000'
                expected_tp = 'TSTXXX00000'
                self.assertEqual(tp.tpname_to_path(tp_name), join(ipath_test, expected_tp))

    def test_tpname_bom(self):
        with Chdir(f'{UT_DIR_REPO}/SimpleNVL'):
            tp = TestProgram('TGLH81')
            self.assertEqual(tp.envfile, os.path.realpath(f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'))

    def test_derive_tpl(self):
        tp1 = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        self.assertEqual(tp1.testplan_base, 'BASE')
        self.assertXpathEqual(tp1.tpl, abspath(UT_DIR_REPO) + '/Simple1/TPL/BaseTestPlan.tpl')

        with TempDir(name=True) as tdir:
            # success case for unittest purposes
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            TestProgram(envfile, tpl='')

            # found no tpl
            with self.assertRaisesRegex(AssertionError, 'No .tpl found in'):
                TestProgram(envfile)

            # two tpl found
            File(join(tdir, 'a.tpl')).touch()
            File(join(tdir, 'b.tpl')).touch()
            with self.assertRaisesRegex(AssertionError, 'Found two .tpl in'):
                TestProgram(envfile)

            # _check_exist
            tp = TestProgram(envfile, tpl='')
            # case1 - None
            self.assertEqual(tp._check_exist(None, None), None)
            # case2 - fullpath
            File(join(tdir, 'a.xml')).touch()
            self.assertEqual(tp._check_exist(join(tdir, 'a.xml'), None), join(tdir, 'a.xml'))
            # case3 - relative path
            self.assertEqual(tp._check_exist('a.xml', tdir), join(tdir, 'a.xml'))
            # case4 - not exist
            with Chdir(tdir):
                with self.assertRaisesRegex(ErrorInput, 'Input file b.xml does not exist'):
                    tp._check_exist('b.xml', tdir)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_all_mtpl_from_stpl(self):
        # no intradut - no scoping
        env = UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env'
        tp = TestProgram(env, stpl='SubTestPlan_CLASS_TGLH81.stpl')
        self.assertEqual(len(tp.get_all_mtpl_from_stpl()), 80)

        # with intradut - scoping
        env = UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env'
        tp = TestProgram(env, stpl=UT_DIR + '/TGLXXXXBXH14P00S109/TPL/SubTestPlan_CLASS_TGLU42.stpl')
        self.assertEqual(len(tp.get_all_mtpl_from_stpl()), 143)
        self.assertEqual(len(tp.get_all_mtpl_from_stpl('IP_CPU')), 64)
        self.assertEqual(len(tp.get_all_mtpl_from_stpl('IP_PCH')), 24)

        # two finals
        env = UT_DIR + '/mtt_tp/POR_TP/Class_MTL_P68/EnvironmentFile.env'
        tp = TestProgram(env)
        self.assertEqual(len(tp.get_all_mtpl_from_stpl()), 144)

    def test_get_family_name(self):
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True, name=True) as tdir:
            # case1 - PTL case: POR_TP/PTL_H_CLASS/
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
            self.assertEqual(tp.get_family_name(), 'tgl')

            # case2 - NVL case
            File('POR_TP/TGLH81').rename('Class_NVL_S28')
            tp = TestProgram('POR_TP/Class_NVL_S28/EnvironmentFile.env')
            self.assertEqual(tp.get_family_name(), 'nvl')

            # case3: everybody else (but bom_based=False)
            self.assertEqual(tp.get_family_name(bom_based=False), 'sim')

    def test_get_imp_from_tpl(self):
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True, name=True) as tdir:
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
            File('a.tpl').touch('Import "Common_BOM.imp";\n')
            tp.tpl = 'a.tpl'

            # Simple case - 1
            File('Shared/BaseInputs/Common/Common_Torch/Common_BOM.imp').touch(mkdir=True)
            self.assertEqual(sorted(Env.xpath(os.path.relpath(f)) for f in tp._get_imp_from_tpl()), [f'Shared/BaseInputs/Common/Common_Torch/Common_BOM.imp'])

            # Novalake case - 1
            File('Shared/BaseInputs/Common/Common_Class_NVL_S52C/Common_BOM.imp').touch(mkdir=True)
            File('Shared/BaseInputs/Common/Common_Class_NVL_S28C/Common_BOM.imp').touch(mkdir=True)
            self.assertEqual(sorted(Env.xpath(os.path.relpath(f)) for f in tp._get_imp_from_tpl()), [f'Shared/BaseInputs/Common/Common_Torch/Common_BOM.imp'])

            # error case - not found
            File('Shared/BaseInputs/Common/Common_Torch/Common_BOM.imp').unlink()
            with self.assertRaisesRegex(AssertionError, 'Expecting 1 for Common_BOM.imp.'):
                tp._get_imp_from_tpl()

            # Novalake new method case - a valid BOM in Common folder
            File('Shared/BaseInputs/Common/Common_TGLH81/Common_BOM.imp').touch(mkdir=True)
            self.assertEqual(sorted(Env.xpath(os.path.relpath(f)) for f in tp._get_imp_from_tpl()), [f'Shared/BaseInputs/Common/Common_TGLH81/Common_BOM.imp'])

        # New dielet case - there are other .imp files in dielet BOM folders.
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True, name=True) as tdir:
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
            File('a.tpl').touch('''
            Import "Common_BOM.imp";\n
            Import "CPU_BOM.imp";\n''')
            tp.tpl = 'a.tpl'

            File('Shared/BaseInputs/Common/Common_TGLH81/Common_BOM.imp').touch(mkdir=True)
            File('Shared/BaseInputs/Common/Common_TGLH82/Common_BOM.imp').touch(mkdir=True)
            File('Shared/BaseInputs/Common/Common_TGLH83/Common_BOM.imp').touch(mkdir=True)
            File('BaseInputs/CPU/CPU_TGLH81/CPU_BOM.imp').touch(mkdir=True)
            File('BaseInputs/CPU/CPU_TGLH82/CPU_BOM.imp').touch(mkdir=True)
            File('BaseInputs/CPU/CPU_TGLH83/CPU_BOM.imp').touch(mkdir=True)
            self.assertEqual(sorted(Env.xpath(os.path.relpath(f)) for f in tp._get_imp_from_tpl()),
                             ['BaseInputs/CPU/CPU_TGLH81/CPU_BOM.imp',
                              'Shared/BaseInputs/Common/Common_TGLH81/Common_BOM.imp'])

        # NVPP case
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True, name=True) as tdir:
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
            File('a.tpl').touch(r'Import "Shared\BaseInputs\Common\Common_Torch\Common_BOM.imp";\n')
            tp.tpl = 'a.tpl'

            # Simple case - 1
            File('Shared/BaseInputs/Common/Common_Torch/Common_BOM.imp').touch(mkdir=True)
            self.assertEqual(tp._get_imp_from_tpl(), [f'{tdir}/Shared/BaseInputs/Common/Common_Torch/Common_BOM.imp'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_import_files(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        result = tp.get_import_files('tim')
        self.assertEqual({Env.xpath(x) for x in result},
                         {Env.xpath(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/TimingsSequences.tim'),
                          Env.xpath(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/./Modules/IP_PCH_BASE/TimingsSequences_IP_PCH.tim'),
                          Env.xpath(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/./Modules/IP_CPU_BASE/TimingsSequences_IP_CPU.tim')
                          })
        result = tp.get_import_files('tcg')
        self.assertEqual(len(result), 101)

        # Torch
        tp = TestProgram(f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON/EnvironmentFile.env')
        result = tp.get_import_files('usrv')
        self.assertEqual(len(result), 94)

        result = tp.get_import_files('usrv', withmodule=True)
        result_v = [x for x in result.values()]
        self.assertEqual(result_v[0], ('BASE', f'{UT_DIR}/RPLS8P5A0H10P60S051/Shared/Common/Common.imp'))

        # fail case
        with TempDir(name=True) as tdir:
            # case1: invalid eval on uservar ==========================
            code = """
Import bb.usrv
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code, mkdir=True)
            code = """
Import aa.usrv
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
UserVars ARR
{
        Integer v1 = -1;
}
"""
            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            File('%s/Modules/ARR/bb.usrv' % tdir).touch(code, mkdir=True)
            tp = TestProgram(envfile)._ut_write_stpl()
            with self.assertRaisesRegex(ErrorInput, 'is not found from'):
                tp.usrv.get_usrv_map()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(TempDir, startcopy=f'{UT_DIR}/san_unit_test/Simple6_tos4_floating_test_PrimeHptpTIming_patmod_call', chdir=True)
    def test_get_import_files_with_dot_slash(self):
        tp = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
        tp.is_tos4 = True
        result = tp.get_import_files('tcg')
        self.assertEqual(tp.get_scope(f'{UT_DIR}/Modules/ARR/array.tcg', 'default'), 'ARR')

    @unittest.skip("invalid test")    # Since Torch intradut requires both defined if both package and ip
    def test_mutex_plistall(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        with TempDir(name=True, chdir=True) as tdir:
            tp.tpldir = tdir
            tp.envdir = tdir
            File('PLIST_ALL.xml').touch("""<HdmtReferenceFile>
  <IPReference name="IP_PCH" path=".\\PLIST_ALL_IP_PCH.xml" />
  <IPReference name="IP_CPU" path=".\\PLIST_ALL_IP_CPU.xml" />
  <PList>
    <PListFile name="drv_mcp.plist" />
    <PListFile name="OPIO_FELB.plist" />
  </PList>
</HdmtReferenceFile>""")
            File('PLIST_ALL_IP_PCH.xml').touch("""<HdmtReferenceFile>
  <PList>
    <PListFile name="drv_mcp.plist" />
  </PList>
</HdmtReferenceFile>""")
            File('PLIST_ALL_IP_CPU.xml').touch("""<HdmtReferenceFile>
  <PList>
    <PListFile name="uniq.plist" />
  </PList>
</HdmtReferenceFile>""")
            with self.assertRaisesRegex(AssertionError, 'Error: drv_mcp.plist is defined twice in ./PLIST_ALL_IP_PCH.xml'):
                tp.plists.get_plist_list()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_plist_ip(self):
        tp = TestProgram(f'{UT_DIR}/SimpleMTL_jning2/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        self.assertEqual(len(tp.get_file_allplist_real()), 3)
        self.assertEqual(len(tp.get_file_allplist_real()), 3)        # run again
        tp = TestProgram(f'{UT_DIR}/SimpleMTL_jning2/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        self.assertEqual(len(tp.get_plist2ip()), 258)
        self.assertEqual(set(tp.get_plist2ip().values()), {None, 'IP_CPU', 'IP_PCH'})    # run again

    def test_get_plist_from_tpconfig(self):
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3', chdir=True, name=True) as tdir:
            # this tpconfig is from SRF
            text = '''<?xml version="1.0" encoding="utf-8"?>
<Configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <TestProgram>
    <ProductCodeName>SRF</ProductCodeName>
    <TestProgramDescriptiveName>Class Test Program for Sierra Forest</TestProgramDescriptiveName>
    <TeamEmailAddress>mdcx-an-tpi@intel.com</TeamEmailAddress>
    <SortClassType>CLASS</SortClassType>
    <TPNameUservar>SCVars.TP_PROGRAM_NAME</TPNameUservar>
    <TpTag />
  </TestProgram>

  <TestProgramFiles>
    <BaseTplPath>..\\..\\TplFile.tpl</BaseTplPath>
    <ENVPath>EnvironmentFile.env</ENVPath>
    <STPLPath>SubTestPlan.stpl</STPLPath>
    <RootPath>..\\..\\</RootPath>
    <TPIESignaturePath>..\\..\\TPIE.Signature</TPIESignaturePath>
  </TestProgramFiles>

  <LTLTestProgramNameToSocketMapping>
    <TPToSocketMapping TPNameUservar="TestProgramName.LCCSP_C0" SocketFile="..\\..\\Shared\\Common\\Socket_SRF_SP.soc" />
    <TPToSocketMapping TPNameUservar="TestProgramName.XDCCAP_A0" SocketFile="..\\..\\Shared\\Common\\Socket_SRF_AP.soc" />
  </LTLTestProgramNameToSocketMapping>

  <SupportedBomGroups FlowMatrixPath="..\\..\\Shared\\Common\\FlowMatrix.flm.xml">
      <BomGroup name="XDCCAP_A0" plist="all_XDCCAP_A0.plist.xml" slimplist="all_XDCCAP_A0.plist.xml" soc="..\\..\\Shared\\Common\\Socket_SRF_AP.soc" env="EnvironmentFile_XDCCAP_A0.env"/>
      <BomGroup name="LCCSP_C0" plist="all_LCCSP_C0.plist.xml" slimplist="all_LCCSP_C0.plist.xml" soc="..\\..\\Shared\\Common\\Socket_SRF_SP.soc" env="EnvironmentFile_LCCSP_C0.env"/>
  </SupportedBomGroups>

  <Recipes>
    <Seeds DirectoryName="I:\\engineering\\dev\\sctp\recipe_gen\\hdmx\\srf\\seed\\{latest}" />
    <LocationsStandard FileName="..\\..\\Shared\\Common\\RecipeSettings\\MPS_LocationStandard.xlsx" />
    <Settings FileName="..\\..\\Shared\\Common\\RecipeSettings\recipeGenerationSettings.xml" />
  </Recipes>

    <Export>
        <PostExportScript Path="..\\..\\Scripts\\launch-torch-export-scripts.exe" CustomArgs="-debug True" Timeout="900" Enabled="True"/>
    </Export>

  <TPCustomAttributes>
    <TPSeries>a</TPSeries>
    <TPLead>a</TPLead>
  </TPCustomAttributes>
</Configuration>
'''
            File('POR_TP/TGLH81/CLASS_TGLH81.tpconfig').touch(text, newfile=True)
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
            self.assertXpathEqual(tp._get_plist_from_tpconfig('LCCSP_C0'), f'{abspath(tdir)}/POR_TP/TGLH81/all_LCCSP_C0.plist.xml')
            self.assertEqual(tp._get_plist_from_tpconfig('XY'), None)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_plistall_notfound(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        with TempDir(name=True, chdir=True) as tdir:
            tp.tpldir = tdir
            tp.envdir = tdir
            File('PLIST_ALL1.xml').touch("""<HdmtReferenceFile>
  <PList>
    <PListFile name="drv_mcp.plist" />
    <PListFile name="OPIO_FELB.plist" />
  </PList>
</HdmtReferenceFile>""")
            with self.assertRaisesRegex(ErrorInput, 'Cannot find'):
                tp.plists.get_plist_list()

    def test_bom_from_env(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        self.assertEqual(tp.get_bom_from_env(), '')
        tp.envfile = '/path/EnvironmentFile_CLASS_P68G2_TRCFAILED.env'
        self.assertEqual(tp.get_bom_from_env(), 'CLASS_P68G2')
        tp.envfile = 'EnvironmentFile_CLASS_P68G2.env'
        self.assertEqual(tp.get_bom_from_env(), 'CLASS_P68G2')
        tp.envfile = 'EnvironmentFile_CLASS_P68G2_CHKFAILED.env'
        self.assertEqual(tp.get_bom_from_env(), 'CLASS_P68G2')
        tp.envfile = 'EnvironmentFile_CLASS_P68G2_TRCFAILED_CHKFAILED.env'
        self.assertEqual(tp.get_bom_from_env(), 'CLASS_P68G2')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_bom(self):
        # env based
        tp = TestProgram(f'{UT_DIR}/SRHXXXXAXH00G40S127/EnvironmentFile_CLASS_HBM.env')
        self.assertEqual(tp.get_bom(), 'CLASS_HBM')

        # stpl based
        tp = TestProgram(f'{UT_DIR}/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        self.assertEqual(tp.get_bom(), 'CLASS_TGLH81')

        # binmatrix based
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        with MockVar(tp, "get_stpl", Mock(return_value='')):
            self.assertEqual(tp.get_bom(), 'MTL_GCD128_SDS')

        # Torch
        tp = TestProgram(f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON/EnvironmentFile.env')
        self.assertEqual(tp.get_bom(), 'CLASS_RPL8161S')

        # none found
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env')
        with MockVar(tp, "get_stpl", Mock(return_value='')):
            self.assertEqual(tp.get_bom(), '')

        # bomfolder
        tp = TestProgram(f'{UT_DIR_REPO}/SimpleNVL')
        self.assertEqual(tp.get_bomfolder(), 'TGLH81')

        # torch case sensitive
        with TempDir(startcopy=f'{UT_DIR_REPO}/SimpleNVL5', name=True) as tdir:
            tp = TestProgram(f'{tdir}/POR_TP/TGLH81/EnvironmentFile.env')
            self.assertEqual(tp.get_bom(), 'CLASS_TGLH81')

            # File(f'{tdir}/POR_TP/TGLH81').rename('Class_TGLH81')
            # tp = TestProgram(f'{tdir}/POR_TP/Class_TGLH81/EnvironmentFile.env')
            # self.assertEqual(tp.get_bom(), 'Class_TGLH81')

            self.assertEqual(tp.get_file_allplist(fnameonly=True), f'{tdir}/POR_TP/TGLH81/PLIST_ALL.xml')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_bin_matrix(self):
        # default bomgroup
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        self.assertEqual(tp.bin_matrix(),
                         {'1001': {'BOMGroupName': 'MTL_GCD128_SDS',
                                   'FlowIndex': '1',
                                   'QDF/SSPEC': 'Q8A3',
                                   'olb_bin': '1',
                                   'olb_bin_type': 'B'}})

        # single element everything
        top = {"BinMatrix": {
            "BOMGroupTable": {
                "BOMGroup":
                {
                    "name": "MTL_GCD128_SDS",
                    "ActiveFlowList": {
                        "Flow": {
                            "index": "1",
                            "bin": "1001",
                            "binName": "p1001",
                            "Attribute":
                            {
                                "name": "BOMGroupName",
                                "_text": "MTL_GCD128_SDS"
                            },
                        }
                    }
                }
            }
        }
        }
        self.assertEqual(tp.bin_matrix(_dd=top),
                         {'1001': {'BOMGroupName': 'MTL_GCD128_SDS'}})

        # list element everything
        top = {"BinMatrix": {
            "BOMGroupTable": {
                "BOMGroup": [
                    {
                        "name": "MTL_GCD128_SDS",
                        "ActiveFlowList": {
                            "Flow": [{
                                     "index": "1",
                                     "bin": "1001",
                                     "binName": "p1001",
                                     "Attribute":
                                     [{
                                         "name": "BOMGroupName",
                                         "_text": "MTL_GCD128_SDS",
                                         "unit": "volts"
                                     }],
                                     }]
                        }
                    }]
            }
        }
        }
        self.assertEqual(tp.bin_matrix(_dd=top),
                         {'1001': {'BOMGroupName': 'MTL_GCD128_SDSvolts'}})

        # TGL real binmatrix
        tp = TestProgram(f'{UT_DIR}/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        result = tp.bin_matrix('CLASS_TGLH81')
        self.assertEqual(len(result), 6)
        self.assertEqual(len(list(keys_atlevel(result, 1))), 456)

        result2 = tp.bin_matrix(tp.get_bom())    # empty case
        self.assertEqual(result, result2)

        # invalid bom group given
        with self.assertRaisesRegex(AssertionError, 'is not found in'):
            tp.bin_matrix('notfound')

        # SRH bom
        tp = TestProgram(f'{UT_DIR}/SRHXXXXAXH00G40S127/EnvironmentFile_CLASS_HBM.env')
        result = tp.bin_matrix(tp.get_bom())
        self.assertEqual(len(list(keys_atlevel(result, 1))), 732)

        # No binmatrix
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1a/TPL/EnvironmentFile.env')
        self.assertEqual(tp.bin_matrix(), {})

        # Torch TP
        tp = TestProgram(f'{UT_DIR}/mtl_18B_torch/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        result = tp.bin_matrix(tp.get_bom())
        self.assertEqual(tp.get_bom(), 'CLASS_P68G2')
        self.assertEqual(len(list(keys_atlevel(result, 1))), 500)

        # Torch TP no binmatrix
        tp = TestProgram(f'{UT_DIR}/MTGEBTH64T237464T1/EnvironmentFile_!ENG!.env')
        result = tp.bin_matrix(tp.get_bom())
        self.assertEqual(result, {})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_read_tpconfig(self):
        # TPIE
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        self.assertEqual(tp.read_tpconfig('TPNameUservar', default='yay'), 'yay')

        # Torch - asis found
        tp = TestProgram(f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON/EnvironmentFile.env')
        expect = ['RunTimeLibraryVars.A0TPName', 'RunTimeLibraryVars.iCGL_TpAltName']
        self.assertEqual(tp.read_tpconfig('TPNameUservar', default='yay', asis=True), expect)

        # Torch - asis not found
        self.assertEqual(tp.read_tpconfig('TPNameUservar2', default=['yay'], asis=True), ['yay'])

        # Torch - default found, with replace
        key = 'LTLTestProgramNameToSocketMapping.TPToSocketMapping.SocketFile'
        self.assertEqual(tp.read_tpconfig(key, default='yay'), '../../Shared/Common/S8161_LGA_HDMT.soc')
        # Torch - default notfound
        key = 'LTLTestProgramNameToSocketMapping.TPToSocketMapping.SocketFile'
        self.assertEqual(tp.read_tpconfig(f'{key}notfound', default=None), None)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_name(self):
        tp = TestProgram(f'{UT_DIR}/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        self.assertEqual(tp.get_name(), 'TGLTP')    # From uservar, without pgmrules
        with MockVar(tp.usrv, 'get_var', Mock(return_value='')):
            self.assertEqual(tp.get_name(), 'TGLHAQ2R0H35H00S025')    # From uservar, without pgmrules

        self.assertEqual(tp.find_file('PGMRule_Base.txt'), f'{UT_DIR}/TGLXXXXRXH35H00S025/TPL/PGMRule_Base.txt')
        self.assertEqual(tp.find_file('notfound.txt'), None)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple8', chdir=True)
    def test_name2(self):
        tp = TestProgram(f'TPL/EnvironmentFile.env')
        self.assertEqual(tp.get_name(), 'Simple1')    # without pgmrule

        File('./TPL/UservarDefinitions.usrv').touch('''
Version 1.0;

UserVars SCVars
{
   String SC_DEVICE = "4TXNCV";
   String TP_PROGRAM_NAME = "BLAH1";
}
''', newfile=True)
        tp = TestProgram(f'TPL/EnvironmentFile.env')
        self.assertEqual(tp.get_name(), 'BLAH1')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_ipname(self):
        tp = TestProgram(f'{UT_DIR}/MTLXXXXXXX19M0KSXXX/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        self.assertEqual(tp.get_ipname('ARR_CORE_C68'), 'IP_CPU')
        self.assertEqual(tp.get_ipname('SCN_GT_GXX'), 'IP_PCH')
        self.assertEqual(tp.get_ipname('DRV_RESET_SXN'), None)
        self.assertEqual(len(tp.get_mod2ip_map()), 161)

    def test_get_mod2ip_map(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env')
        expect = {'ARR': 'IP_CPU', 'TPI_BASEPRIM_XXX': None, 'PTH': None, 'SCN': None}
        self.assertEqual(tp.get_mod2ip_map(), expect)
        self.assertEqual(tp.get_mod2ip_map(), expect)
        self.assertEqual(tp.get_mod2ip_map(), expect)

    def test_scope(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        self.assertEqual(tp.get_scope('.', 'default'), 'default')   # This will initialize tp._scope
        self.assertEqual(tp._scope, {'ARR/array.mtpl': 'ARR', 'SCN/scan.mtpl': 'SCN'})
        self.assertEqual(tp.get_scope('/blah/Modules/ARR/array.mtpl', 'default'), 'ARR')
        self.assertEqual(tp.get_scope('/blah/Modules/ARR/a.tcg', 'default'), 'ARR')

        tp._scope = {'ProgramFlowsTestPlan/IP_CPU_CONCURRENT_FLOWS.mtpl': 'CPU',
                     'ProgramFlowsTestPlan/IP_PCH_CONCURRENT_FLOWS.mtpl': 'PCH'}
        self.assertEqual(tp.get_scope('/blah/ProgramFlowsTestPlan/IP_CPU_CONCURRENT_FLOWS.mtpl', 'default'),
                         'CPU')
        self.assertEqual(tp.get_scope('/blah/ProgramFlowsTestPlan/IP_PCH_CONCURRENT_FLOWS.mtpl', 'default'),
                         'PCH')
        self.assertEqual(tp.get_scope('/blah/ProgramFlowsTestPlan/IP_QQQ_CONCURRENT_FLOWS.mtpl', 'default'),
                         'default')
        self.assertEqual(tp.get_scope('/blah/Shared/IP_QQQ_CONCURRENT_FLOWS.mtpl', 'default'),
                         'default')

    @with_(TempDir, chdir=True)
    def test_read_scope(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple6/POR_TP/TGLH81/EnvironmentFile.env')

        # normal case
        File('ok.mtpl').touch('''
   TestPlan ok;
blah
blah
''')
        tpobj._read_scope('./ok.mtpl')
        self.assertEqual(tpobj._scope, {'./ok.mtpl': 'ok'})

        # error case
        File('abc.mtpl').touch()
        with self.assertRaisesRegex(ErrorInput, 'TestPlan line not found'):
            tpobj._read_scope('abc.mtpl')

        # no error case - imp file (Found in lnl tp)
        File('abc.imp').touch()
        tpobj._read_scope('abc.imp')

    def test_pickle_key(self):
        # test that pickle mtime ignores Reports/ folder
        envfile = UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env'
        tpobj = TestProgram(envfile)
        with TempDir(name=True, chdir=True) as tdir:
            tpobj.tpldir = tdir
            File('POR_TP/Class_MTL/Reports/random').touch(mkdir=True)
            self.assertEqual(tpobj.pickle_key()['mtimes'], 0)

            File('Reports/something/random').touch(mkdir=True)
            self.assertGreater(tpobj.pickle_key()['mtimes'], 100)

    def test_pickle(self):
        envfile = UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env'
        tp1 = TestProgram(envfile)
        tp1.init()

        with TempDir(name=True) as tdir, MockVar(cfg, 'pickle_dir', tdir):
            tp2 = TestProgram(envfile).pickle_init()     # create pickle
            tp3 = TestProgram(envfile).pickle_init()     # load from pickle
            self.assertEqual(len(os.listdir(tdir)), 1)   # 1 pickle file

            # pickling error - should display the pickle file
            fnames = glob.glob(f'{tdir}/*')
            File(fnames[0]).touch('a', newfile=True)
            with self.assertRaises(pickle.UnpicklingError):
                TestProgram(envfile).pickle_init()     # load from pickle

        obj = Diff([tp1, tp2])
        with CaptureStdoutLog() as p:
            obj.tid_diff()
            obj.tim_diff()
            obj.lvl_diff()

        print(p.getvalue())
        result = [x for x in p.getvalue().split('\n') if x == 'No change']
        self.assertEqual(len(result), 3)     # No diff

        obj = Diff([tp1, tp3])
        with CaptureStdoutLog() as p:
            obj.tid_diff()
            obj.tim_diff()
            obj.lvl_diff()
        result = [x for x in p.getvalue().split('\n') if x == 'No change']
        self.assertEqual(len(result), 3)     # No diff

        # incorrect usage
        tp = TestProgram(envfile)
        tp.pickle_init()
        with self.assertRaisesRegex(ErrorInput, 'Incorrect use'):
            tp.get_all_mtpl_files()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_buildtype(self):
        with Chdir(f'{UT_DIR_REPO}/Simple3'):
            tp = TestProgram(Env.get_envfile())
            self.assertEqual(tp.get_buildtype(), 'POR_TP')
            self.assertFalse(tp.is_eng_tp())

        with Chdir(f'{UT_DIR}/torch_mvtp'):
            tp = TestProgram(Env.get_envfile())
            self.assertEqual(tp.get_buildtype(), 'ENG_TP')
            self.assertTrue(tp.is_eng_tp())

        with TempDir(name=True, chdir=True):
            File('POR_TP/Class_MTL_P68/EnvironmentFile.env').touch(mkdir=True)
            File('ENG_TP/Class_MTL_P68/EnvironmentFile.env').touch(mkdir=True)
            self.assertEqual(Env.get_envfile(), './POR_TP/Class_MTL_P68/EnvironmentFile.env')

        with TempDir(name=True, chdir=True):
            File('EnvironmentFile.env').touch(mkdir=True)
            self.assertEqual(Env.get_envfile(), './EnvironmentFile.env')

        # Two env file
        with TempDir(name=True, chdir=True):
            File('POR_TP/blah/EnvironmentFile.env').touch(mkdir=True)
            File('POR_TP/blah/EnvironmentFile1.env').touch(mkdir=True)
            with self.assertRaisesRegex(ErrorUser, 'Found 2 env file'):
                Env.get_envfile()
            self.assertEqual(Env.get_envfile(firstonly=True), './POR_TP/blah/EnvironmentFile.env')

        # No env file
        with TempDir(name=True, chdir=True):
            with self.assertRaisesRegex(ErrorUser, 'Found 0 env file'):
                Env.get_envfile()

    def test_get_builduser(self):
        with TempDir(name=True, chdir=True) as tdir:
            envfile = '%s/env.env' % tdir
            File('%s/Modules/ARR/a.mtpl' % tdir).touch('', mkdir=True)
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            ir = join(tdir, 'Reports/Integration_Report.txt')
            ir_data = """
[Program Identification]
#-------------------------------------------------------------------------------
<Program Type>    Module Validation
<Program Family>  Meteorlake
<Subfamily>       Class MTL P1
<Base TP Name>    19E_sherlock
<TP Revision>     shilpa 07/05/22_11:23:17_AM
#-------------------------------------------------------------------------------
"""
            File(ir).touch(ir_data, mkdir=True, newfile=True)
            self.assertEqual(tp.get_builduser(), ('shilpa', False))

        with TempDir(name=True, chdir=True) as tdir:
            envfile = '%s/env.env' % tdir
            File('%s/Modules/ARR/a.mtpl' % tdir).touch('', mkdir=True)
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            ir = join(tdir, 'Reports/Integration_Report.txt')
            ir_data = """
#-------------------------------------------------------------------------------
<Program Type>    Release Candidate
<Program Family>  Meteorlake
<Subfamily>       Class MTL P1
<Base TP Name>    12Hp9
<TP Revision>     holeary 07/05/22_11:23:17_AM
#-------------------------------------------------------------------------------
"""
            File(ir).touch(ir_data, mkdir=True, newfile=True)
            self.assertEqual(tp.get_builduser(), ('holeary', True))

        with TempDir(name=True, chdir=True) as tdir:
            envfile = '%s/env.env' % tdir
            File('%s/Modules/ARR/a.mtpl' % tdir).touch('', mkdir=True)
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            ir = join(tdir, 'Reports/Integration_Report.txt')
            ir_data = """
#-------------------------------------------------------------------------------
<Program Type>    Release Candidate
<Program Family>  Meteorlake
<Subfamily>       Class MTL P1
<Base TP Name>    12Hp9
<TP Revision>     grace 07/05/22_11:23:17_AM
#-------------------------------------------------------------------------------
"""
            File(ir).touch(ir_data, mkdir=True, newfile=True)
            self.assertEqual(tp.get_builduser(), ('grace', False))

        with TempDir(name=True, chdir=True) as tdir:
            envfile = '%s/env.env' % tdir
            File('%s/Modules/ARR/a.mtpl' % tdir).touch('', mkdir=True)
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            ir = join(tdir, 'Reports/Integration_Report.txt')
            ir_data = """
[Program Identification]
#-------------------------------------------------------------------------------
<Program Type>    Module Validation
<Program Family>  Meteorlake
<Subfamily>       Class MTL P1
<Base TP Name>    19E_sherlock
<TP Revision>      07/05/22_11:23:17_AM
#-------------------------------------------------------------------------------
"""
            File(ir).touch(ir_data, mkdir=True, newfile=True)
            with self.assertRaisesRegex(ErrorCheck, 'Unable to acquire PDE from integ report'):
                tp.get_builduser()

        with TempDir(name=True, chdir=True) as tdir:  # integration report is not present
            envfile = '%s/env.env' % tdir
            File('%s/Modules/ARR/a.mtpl' % tdir).touch('', mkdir=True)
            File(envfile).touch()
            tp = TestProgram(envfile, tpl='')._ut_write_stpl()
            with self.assertRaisesRegex(ErrorCheck, 'TPIE integration report file is missing'):
                tp.get_builduser()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_module_folder_names(self):
        tp = TestProgram(f'{UT_DIR}/mtl_18B_torch/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        result = list(tp.get_module_folder_names())
        self.assertEqual(len(result), 138)
        self.assertIn('TPI_SMP_GXX', result)

        # unittest
        data = ['Modules/ARR/ARR.mtpl',
                'Modules/ARR1/ARR1.mtpl',
                'Modules/TPI/TPI_VCC/TPI_VCC.mtpl',
                'Modules/TPI/TPI_VCC1/TPI_VCC1.mtpl',
                'ProgramFlowsTestPlan/DRV/DRV1/DRV_RST.mtpl']

        with MockVar(tp, 'get_all_mtpl_from_stpl', Mock(return_value=data)):
            self.assertEqual(list(tp.get_module_folder_names()),
                             ['ARR', 'ARR1', 'TPI_VCC', 'TPI_VCC1'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_shareddir(self):
        # tpie
        tp = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        self.assertEqual(tp.shareddir, tp.tpldir)

        # Torch - one dir
        tp = TestProgram(f'{UT_DIR}/mtl_18B_torch/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        self.assertEqual(basename(tp.shareddir), "Shared")

        # Torch - multi dir, with tpconfig SOCPath
        tp = TestProgram(f'{UT_DIR}/mtl_18B_torch/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            tp.tpldir = tdir
            tp.envfile = f'{tdir}/PORTP/blah/blah.env'
            self.assertEqual(tp._derive_shareddir(), f'{tdir}/Shared')

        # Torch - multi dir, without tpconfig SOCpath, aka uses default /Shared
        tp = TestProgram(UT_DIR + '/Simple1/TPL/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            tp.is_tpie = False
            tp.tpldir = tdir
            tp.envfile = f'{tdir}/PORTP/blah/blah.env'
            self.assertEqual(tp._derive_shareddir(), f'{tdir}/Shared')

    def test_is_torch(self):
        with TempDir(name=True) as tdir, \
                MockVar(TestProgram, '_derive_moddir', Mock(return_value='')), \
                MockVar(TestProgram, '_derive_shareddir', Mock(return_value='')):
            env = join(tdir, 'some', 'dir', 'ff.env')
            tpl = join(dirname(env), 'ff.tpl')
            File(env).touch(mkdir=True)
            File(tpl).touch()
            tp = TestProgram(env)
            self.assertFalse(tp.is_torch_based_product())

            mkdirs(join(tdir, 'Modules'))
            self.assertFalse(tp.is_torch_based_product())

            mkdirs(join(tdir, 'Shared'))
            self.assertFalse(tp.is_torch_based_product())

            mkdirs(join(tdir, 'POR_TP'))
            self.assertTrue(tp.is_torch_based_product())

        tp = TestProgram(UT_DIR_REPO + '/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        self.assertTrue(tp.is_torch_based_product())

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6', chdir=True)
    def test_ptl(self):
        # .tpl is in POR DIR
        # error in .usrv eval, but light=True should not evaluate it
        File('BaseTestPlan.tpl').move('POR_TP/TGLH81')
        File('Shared/BaseInputs/UservarDefinitions2.usrv').rename('UservarDefinitions.usrv')
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init(light=True)
        self.assertEqual(tpobj.env.get_contents('~HDMT_TP_BASE_DIR'), os.getcwd())
        result = list(tpobj.mtpl.iter_flows('MAIN', idict=True))
        self.assertEqual(len(result), 8)

        # below must error
        with self.assertRaisesRegex(ErrorInput, 'outcome conditions are all False'):
            TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple6tos4', chdir=True)
    def test_tos4(self):
        tpobj = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env').init()
        self.assertEqual(len(tpobj.get_all_mtpl_from_stpl()), 3)
        self.assertEqual(tpobj._is_tos4(), True)

        # special tag request by BI
        File(tpobj.tpl).touch('\nVersion 1.0;\n# TOS3 TP\n# more stuff', newfile=True)
        self.assertEqual(tpobj._is_tos4(), False)

        # default
        File(tpobj.tpl).touch('\nVersion 1.0;# more stuff', newfile=True)
        self.assertEqual(tpobj._is_tos4(), False)

    def test_get_stpl(self):
        with TempDir(name=True, chdir=True) as tdir:
            File('POR_TP/xyz/EnvironmentFile.env').touch(mkdir=True)
            File('POR_TP/xyz/random.stpl').touch()
            File('POR_TP/xyz/abc.stpl').touch()
            File('POR_TP/xyz/SubTestPlan.stpl').touch()
            File('BaseTestPlan.tpl').touch()

            # default name - nvl
            tpobj = TestProgram('POR_TP/xyz/EnvironmentFile.env')
            self.assertXpathEqual(tpobj.get_stpl(), f'{abspath(tdir)}/POR_TP/xyz/SubTestPlan.stpl')

            # first one
            File('POR_TP/xyz/SubTestPlan.stpl').unlink()
            tpobj = TestProgram('POR_TP/xyz/EnvironmentFile.env')
            self.assertXpathEqual(tpobj.get_stpl(), f'{abspath(tdir)}/POR_TP/xyz/abc.stpl')

            # specified one
            tpobj = TestProgram('POR_TP/xyz/EnvironmentFile.env', stpl='POR_TP/xyz/random.stpl')
            self.assertXpathEqual(tpobj.get_stpl(), f'{abspath(tdir)}/POR_TP/xyz/random.stpl')
            tpobj = TestProgram('POR_TP/xyz/EnvironmentFile.env', stpl='random.stpl')
            self.assertXpathEqual(tpobj.get_stpl(), f'{abspath(tdir)}/POR_TP/xyz/random.stpl')

    def test_dummy_tpobj(self):
        sw = Elapsed()
        tpobj = TestProgram.dummy_tpobj()
        tpobj.init()
        print(f'tpldir={tpobj.tpldir}')
        print(f'Elapsed: {sw}')
        self.assertTrue(tpobj.is_tos4)


class TestLoc(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        tp.usrv.set_data()
        with TempDir(name=True) as tdir:
            tp.tpldir = tdir
            File(join(tdir, 'LocationsSets.txt')).touch('''
CLASSHOT = 6218
COLD = 6219:CLASSCOLD
ALL = CLASSHOT + COLD
''', newfile=True)
            tp.locset.set_data()
            self.assertEqual(dict(tp.locset._allmap),
                             {'ALL': {'CLASSHOT', 'CLASSCOLD'},
                              'CLASSCOLD': {'CLASSCOLD'},
                              'CLASSHOT': {'CLASSHOT'},
                              'COLD': {'CLASSCOLD'}})
            self.assertEqual(dict(tp.locset._loc_code),
                             {'CLASSCOLD': {'6219'}, 'CLASSHOT': {'6218'}})
            self.assertEqual(dict(tp.locset._code_loc),
                             {'6218': {'CLASSHOT'}, '6219': {'CLASSCOLD'}})
            self.assertEqual(tp.locset.num_to_location('CLASSHOT'), 'CLASSHOT')
            self.assertEqual(tp.locset.num_to_location('6218'), 'CLASSHOT')

            # 2nd case
            tp.locset.locset_file = None
            File(join(tdir, 'LocationsSets.txt')).touch('''
CLASSHOT = 6218
COLD = 6219:CLASSCOLD
ALL = CLASSHOT + COLD
AL1 = CLASSHOT
ANN = ALL + AL1
''', newfile=True)
            tp.locset.set_data()
            self.assertEqual(dict(tp.locset._allmap),
                             {'AL1': {'CLASSHOT'},
                              'ALL': {'CLASSCOLD', 'CLASSHOT'},
                              'ANN': {'CLASSCOLD', 'CLASSHOT'},
                              'CLASSCOLD': {'CLASSCOLD'},
                              'CLASSHOT': {'CLASSHOT'},
                              'COLD': {'CLASSCOLD'}})

            # error eval
            tp.locset.locset_file = None
            File(join(tdir, 'LocationsSets.txt')).touch('''
CLASSHOT = 6218
COLD = 6219:CLASSCOLD,QA
ALL = CLASSHOT + COLD
''', newfile=True)
            with self.assertRaisesRegex(ErrorInput, 'Error on var COLD'):
                tp.locset.set_data()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_is_valid(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env', location='HOT')
        with TempDir(name=True) as tdir:
            tp.tpldir = tdir
            File(join(tdir, 'LocationsSets.txt')).touch('''
HOT = 6218
A = 6219:COLD
QA = 6220:QA
ALL = HOT + A + QA
''', newfile=True)
            tp.locset.set_data()
            self.assertEqual(tp.locset._allmap['ALL'], {'COLD', 'QA', 'HOT'})
            self.assertEqual(tp.locset.is_valid('ALL', None, None), True)
            self.assertEqual(tp.locset.is_valid('COLD', None, None), False)
            self.assertEqual(tp.locset.is_valid('COLD/HOT', None, None), True)
            self.assertEqual(tp.locset.is_valid('ALL/-HOT', None, None), False)
            self.assertEqual(tp.locset.is_valid('ALL/-COLD', None, None), True)
            self.assertEqual(tp.locset.is_valid('ALL/-COLD/-QA', None, None), True)
            self.assertEqual(tp.locset.is_valid('ALL/-A/-QA/-HOT', None, None), False)
            with self.assertRaisesRegex(ErrorInput, 'Error on input'):
                tp.locset.is_valid('ALL/-QQ', None, None)

        # no location code
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        tp.locset.set_data()

        # display
        tp.pgmrules._cnt_apply = 0
        tp.pgmrules.disp(None, 'some message')
        self.assertEqual(tp.pgmrules._cnt_apply, 0)

        with CaptureStdoutLog() as p:
            tp.pgmrules.disp('1', 'some message')
        self.assertEqual(tp.pgmrules._cnt_apply, 1)
        self.assertEqual(p.getvalue(), '')

        with CaptureStdoutLog() as p, MockVar(OPT, 'pgmrule_disp', True):
            tp.pgmrules.disp('1', 'some message')
        self.assertEqual(tp.pgmrules._cnt_apply, 2)
        self.assertEqual(p.getvalue(), 'some message\n')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_usrv(self):
        # only usrv exist
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            tp.tpldir = tdir
            File(join(tdir, 'LocationsSets.usrv')).touch('''
Version 1.0;
UserVars LocationSets
{
   Const String RCH_HVM = "[6163:CLASSHOT],[6167:CLASSHOT]";
   Const String RCH_RV = "[5163:CLASSHOT],[5167:CLASSHOT]";
   Const String DFF_SET_EN = __shared__ ::LocationSets.RCH_HVM + "," + __shared__ ::LocationSets.RCH_HVM ;
   Const String DFF_SET_EN2 = __shared__::LocationCategory.RCH_HVM + "," + __shared__ ::LocationSets.RCH_HVM ;
}
''', newfile=True)
            tp.locset.set_data()
            self.assertEqual(basename(tp.locset.locset_file), 'LocationsSets.usrv')
            self.assertEqual(len(tp.locset._loc_code), 1)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_realtp_torch(self):
        # torch
        tp = TestProgram(f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON/EnvironmentFile.env')
        tp.locset.set_data()
        self.assertEqual(tp.locset.location, 'CLASSHOT')
        self.assertEqual(basename(tp.locset.locset_file), 'LocationsSets.txt')     # prioritized, both exist
        self.assertEqual(len(tp.locset._allmap), 126)
        self.assertEqual(len(tp.locset._loc_code), 11)
        self.assertEqual(len(tp.locset._code_loc), 106)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_realtp(self):
        # class loc set
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        tp.locset.set_data()
        # Dumper(tp.locset._allmap)
        self.assertEqual(len(tp.locset._allmap), 124)
        self.assertEqual(len(tp.locset._loc_code), 11)
        self.assertEqual(len(tp.locset._code_loc), 104)
        self.assertEqual(tp.locset.location, 'CLASSHOT')    # Derived location
        self.assertEqual(basename(tp.locset.locset_file), 'LocationsSets.txt')

        # is_valid
        self.assertEqual(tp.locset.is_valid('ALL', None, None), True)
        self.assertEqual(tp.locset.is_valid('CLASSCOLD', None, None), False)
        input = 'ALL/-RC_S1/-PBIC_DAB/-PBIC_S2/-FIF_S1/-FC_S1/-FC_S2/-QA_S1/-EQAM_S1/-ALL_SORT'
        self.assertEqual(tp.locset.is_valid(input, None, None), False)
        self.assertEqual(tp.locset.is_valid('ALL/-PHM', None, None), True)
        self.assertEqual(tp.locset.is_valid('PHM', None, None), False)
        self.assertEqual(tp.locset.is_valid('CHOT', None, None), True)

        with self.assertRaisesRegex(AssertionError, 'location=VERYHOT is not valid, in line#1 of abc'):
            tp.locset.is_valid('VERYHOT', 1, 'abc')

        # sort loc set
        tp = TestProgram(f'{UT_DIR}/TGLSDSCA8H12H011947/EnvironmentFile.env')
        tp.locset.set_data()
        self.assertEqual(len(tp.locset._allmap), 108)
        self.assertEqual(len(tp.locset._loc_code), 77)
        self.assertEqual(len(tp.locset._code_loc), 130)
        self.assertEqual(tp.locset.location, 'ALL_SDS')

        # invalid location
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env', location='VERYHOT')
        with self.assertRaisesRegex(ErrorInput, 'location=VERYHOT is not valid'):
            tp.locset.set_data()


class TestPgm(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_read(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            tp.tpldir = tdir
            # case#1 - basic
            fname = File(join(tdir, 'case1.txt')).touch('''
bypass_global = "-1,2:1,2",   Template ,   ARR_CCF::LSA_CCF1 : *,*,*,*,*,*,*,*,*,*,*,*,ALL
bypa.global = "0,1:2,3" , Template ,            LSA_CCF1 : 1,2,3,4,5,6,7,8,9,0,1,2,13
''')
            mod_tn = ('ARR', 'test1')
            result = tp.pgmrules._read_pgm_files(fname.get_name(), mod_tn)
            self.maxDiff = None
            expect = {('ARR', 'test1', fname.get_name()):
                      [{'var': 'bypass_global',
                        'val': '-1,2:1,2',
                        'typ': 'Template',
                        'tn': 'ARR_CCF::LSA_CCF1',
                        'lno': 2,
                        'elem': [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', 'ALL']},
                       {'var': 'bypa.global',
                        'val': '0,1:2,3',
                        'typ': 'Template',
                        'tn': 'LSA_CCF1',
                        'lno': 3,
                        'elem': [None, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '1', '2', '13']}
                       ]}
            self.assertDictEqual(dict(result), expect)

            # case#2  - (good template, copy this section for more cases, just change case2.txt to new filename
            fname = File(join(tdir, 'case2.txt')).touch('''
preplist = "VDAC!SetVDACFromHardwareLevels",   Template,   IP_CPU::MIO_DDR_*:*_AMEAS_* : *,*,*,*,*,*,*,*,*,*,*,*,ALL
''')
            result = tp.pgmrules._read_pgm_files(fname.get_name(), mod_tn)
            expect = {'var': 'preplist',
                      'val': 'VDAC!SetVDACFromHardwareLevels',
                      'typ': 'Template',
                      'tn': 'IP_CPU::MIO_DDR_*:*_AMEAS_*',
                      'lno': 2,
                      'elem': [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', 'ALL'],
                      }
            self.assertEqual(result[('ARR', 'test1', fname.get_name())][0], expect)

            # case#3 - extra 8th option
            fname = File(join(tdir, 'case3.txt')).touch('''
preplist = "VDAC!SetVDACFromHardwareLevels",   Template,   IP_CPU::MIO_DDR_*:*_AMEAS_* : *,*,*,*,*,*,*,*,*,*,*,*,ALL,*
''')
            result = tp.pgmrules._read_pgm_files(fname.get_name(), mod_tn)
            expect = {'var': 'preplist',
                      'val': 'VDAC!SetVDACFromHardwareLevels',
                      'typ': 'Template',
                      'tn': 'IP_CPU::MIO_DDR_*:*_AMEAS_*',
                      'lno': 2,
                      'elem': [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', 'ALL,*'],
                      }
            self.assertEqual(result[('ARR', 'test1', fname.get_name())][0], expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_read_invalid(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        with TempDir(name=True) as tdir:
            tp.tpldir = tdir
            fname = File(join(tdir, 'pgm1.txt')).touch('''
# missing one element below
bypass_global = 1,   Template ,   ARR_CCF::LSA_CCF1 : *,*,*,*,*,*,*,*,*,*,*,ALL
''')
            mod_tn = ('ARR', 'test1')
            with self.assertRaisesRegex(ErrorInput, 'Invalid pgm line'):
                tp.pgmrules._read_pgm_files(fname.get_name(), mod_tn)

            # KEY_DEFINITION pgm rules is ignored
            fname = File(join(tdir, 'pgm2.txt')).touch('''
KEY_DEFINITION blah blah
bypass_global = 1,   Template ,   ARR_CCF::LSA_CCF1 : *,*,*,*,*,*,*,*,*,*,*,*,ALL
''')
            tp.pgmrules._read_pgm_files(fname.get_name(), mod_tn)
            self.assertEqual(tp.pgmrules._data, {})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_other(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')

        # scoping unittest
        self.assertEqual(tp.pgmrules._get_scoping_usrv('a::b::c', 'd::e::f'), 'c.f')
        self.assertEqual(tp.pgmrules._get_scoping_usrv('c', 'f'), 'c.f')
        self.assertEqual(tp.pgmrules._get_scoping_usrv('NONE', 'f'), 'f')

    def test_basic(self):
        safety = [None]
        tp1 = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        tp2 = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        tp2.init(patload=False)
        tp2.check_init()

        def run():
            # template, exist
            result1 = tp1.mtpl.get_instance('ARR', 'CCA')
            result2 = tp2.mtpl.get_instance('ARR', 'CCA')
            self.assertEqual(result1.get('bypass_global', 'NA'), '0')
            self.assertEqual(result2.get('bypass_global', 'NA'), '3')

            # template, special case
            result1 = tp1.mtpl.get_instance('ARR', 'CCB')
            result2 = tp2.mtpl.get_instance('ARR', 'CCB')
            self.assertEqual(result1.get('bypass_global', 'NA'), 'NA')
            self.assertEqual(result2.get('bypass_global', 'NA'), '4')

            # template, uservar
            result1 = tp1.mtpl.get_instance('SCN', 'CCA')
            result2 = tp2.mtpl.get_instance('SCN', 'CCA')
            self.assertEqual(result1.get('bypass_global', 'NA'), 'BYPASSVars.BYPASS_in_ENGINEERING_MODE')
            self.assertEqual(result2.get('bypass_global', 'NA'), '5')

            # globals, global, number
            result1 = tp1.usrv.get_var('cl_qa_flag')
            result2 = tp2.usrv.get_var('cl_qa_flag')
            self.assertEqual(result1, 1)
            self.assertEqual(result2, 55)

            # globals, specific block, string
            result1 = tp1.usrv.get_var('BYPASSVars.bypvar')
            result2 = tp2.usrv.get_var('BYPASSVars.bypvar')
            self.assertEqual(result1, 'orig')
            self.assertEqual(result2, 'new1')
            self.assertEqual(tp1.get_name(), 'Simple1')
            self.assertEqual(tp2.get_name(), 'Simple1Real')

            # timings
            result1 = tp1.timing.get_tc_param('BASE::tc1', 'p_vcc_gb_type')
            result2 = tp2.timing.get_tc_param('BASE::tc1', 'p_vcc_gb_type')
            self.assertEqual(result1, '0.2')
            self.assertEqual(result2, '99V')
            result1 = tp1.timing.get_tc_value('BASE::tc1', 'p_vcc_gb_type')
            result2 = tp2.timing.get_tc_value('BASE::tc1', 'p_vcc_gb_type')
            self.assertEqual(result1, 0.2)
            self.assertEqual(result2, 99)
            result1 = tp1.timing.get_tc_value('BASE::tc1', 'tester_gb_hc')
            result2 = tp2.timing.get_tc_value('BASE::tc1', 'tester_gb_hc')
            self.assertEqual(result1, 0.2)
            self.assertEqual(result2, 5445)   # must be evaluated
            result1 = tp1.timing.get_tc_value('BASE::tc2', 'p_vcc_gb_type')
            result2 = tp2.timing.get_tc_value('BASE::tc2', 'p_vcc_gb_type')
            self.assertEqual(result1, 0.1)
            self.assertEqual(result2, 0.1)    # must be unaffected

            # levels
            result1 = tp1.levels.get_tc_param('BASE::tc1', 'p_lvl')
            result2 = tp2.levels.get_tc_param('BASE::tc1', 'p_lvl')
            self.assertEqual(result1, '1.2')
            self.assertEqual(result2, '88V')
            result1 = tp1.levels.get_tc_value('BASE::tc1', 'p_lvl')
            result2 = tp2.levels.get_tc_value('BASE::tc1', 'p_lvl')
            self.assertEqual(result1, 1.2)
            self.assertEqual(result2, 88)
            result1 = tp1.levels.get_tc_value('BASE::tc1', 'c_vccddq_vload_prog')
            result2 = tp2.levels.get_tc_value('BASE::tc1', 'c_vccddq_vload_prog')
            self.assertEqual(result1, 3.2)
            self.assertEqual(result2, 144)   # must be evaluated
            result1 = tp1.levels.get_tc_value('BASE::tc2', 'p_lvl')
            result2 = tp2.levels.get_tc_value('BASE::tc2', 'p_lvl')
            self.assertEqual(result1, 0.1)
            self.assertEqual(result2, 0.1)    # must be unaffected

            # safety marker, to indicate routine is run
            safety[0] = True

        run()

        # re-init (aka, re-apply and re-evaluate)
        tp2.init(skip=False)
        run()   # should be same result

        # Successful iterate all flows non-bypass
        result1 = tp1.mtpl.get_instance('SCN', 'CCA')
        self.assertEqual(result1.get('bypass_global', 'NA'), 'BYPASSVars.BYPASS_in_ENGINEERING_MODE')
        tp1.mtpl.eval_params()
        result1 = tp1.mtpl.get_instance('SCN', 'CCA', evaluated=True)
        self.assertEqual(result1.get('bypass_global', 'NA'), -1)

        result = list(tp1.mtpl.iter_flows(bypass=True, uniq=False))
        self.assertEqual(len(result), 7)
        result = list(tp2.mtpl.iter_flows(bypass=True, uniq=False))
        self.assertEqual(len(result), 7)

        # make sure mini-routine is run
        self.assertEqual(safety[0], True)

        # Do another init - should skip
        res = tp2.init()
        self.assertTrue(res is tp2)
        self.assertEqual(len(tp2.pgmrules.get_pgm_files()), 2)

    def test_apply_item_global(self):
        tp = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        tp.locset.set_data()
        tp.usrv.set_data()
        obj = tp.pgmrules
        m_t_f = ('ARR', 'sometest', 'somefile')
        mapfunc = obj._mapping()

        pgmdict = dict(var='bypvar',
                       val='ut3',
                       typ='global',
                       tn='ARR::BYPASSVars',
                       lno=2,
                       elem=None)

        # case1 - location unspecified
        pgmdict['elem'] = [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*']
        obj._apply_item(pgmdict, m_t_f, mapfunc)
        self.assertEqual(tp.usrv.get_var('BYPASSVars.bypvar'), 'ut3')

    def test_apply_item(self):
        # unittests for filters part of apply_item
        tp = TestProgram(UT_DIR_REPO + '/Simple1/TPL/EnvironmentFile.env')
        tp.locset.set_data()
        obj = tp.pgmrules
        m_t_f = ('MOD1', 'TestName', 'somefile')
        mapfunc = obj._mapping()

        pgmdict = dict(var='bypass_global',
                       val='3',
                       typ='Template',
                       tn='ARR::CCA',
                       lno=2,
                       elem=None)

        # case1 - location unspecified
        pgmdict['elem'] = [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), None)

        # case2 - location
        pgmdict['elem'] = [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', 'CLASSHOT']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), None)
        pgmdict['elem'] = [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', 'PHM']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), 13)

        # case3 - SC_DEVICE
        pgmdict['elem'] = [None, '*', '4', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), None)
        pgmdict['elem'] = [None, '*', '3', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), 2)

        # case4 - fabid
        pgmdict['elem'] = [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', 'Q', '*', '*']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), 11)
        pgmdict['elem'] = [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', 'X', '*', '*']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), None)

        # case5 - fabid slash
        pgmdict['elem'] = [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', 'M/X/Q', '*', '*']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), None)
        pgmdict['elem'] = [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', 'M/Q', '*', '*']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), 11)

        # case6 - fabid minus
        pgmdict['elem'] = [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '-Q', '*', '*']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), None)
        pgmdict['elem'] = [None, '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '-X', '*', '*']
        self.assertEqual(obj._apply_item(pgmdict, m_t_f, mapfunc), 11)


class TestEnv(TestCase):

    def test_get_item(self):
        env = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        obj = Env(env)

        # exist case
        self.assertEqual(obj.get_item('EVERGREEN_SCHEMA_DIR'), '~HDMT_TPL_DIR\\Supersedes\\code;$HDMT_TPL_INPUT_FILES')

        # non exist case
        with self.assertRaisesRegex(AssertionError, 'is not found'):
            obj.get_item('EVERGREEN_SCHEMA_DIRX')

        # default case
        self.assertEqual(obj.get_item('EVERGREEN_SCHEMA_DIRX', default='A'), 'A')

    def test_get_nvlrzl_env(self):
        self.assertEqual(Env.get_nvlrzl_env(f'{UT_DIR}/Simple3a'), [])
        with TempDir(name=True, chdir=True) as tdir:
            File(f'POR_TP/Class_NVL_S28C/EnvironmentFile.env').touch(mkdir=True)
            File(f'POR_TP/Class_RZL_S28C/EnvironmentFile.env').touch(mkdir=True)
            self.assertEqual(Env.get_nvlrzl_env(),
                             ['./POR_TP/Class_NVL_S28C/EnvironmentFile.env', './POR_TP/Class_RZL_S28C/EnvironmentFile.env'])

    def test_get_root_dir(self):
        # case1 sort
        sort_root = f'{UT_DIR_REPO}/Simple1/TPL'
        env = f'{sort_root}/EnvironmentFile.env'
        self.assertTrue(exists(env))
        self.assertXpathEqual(Env.get_root_dir(env), abspath(sort_root))

        # case2 class
        class_root = f'{UT_DIR_REPO}/Simple3a'
        env = f'{class_root}/POR_TP/TGLH81/EnvironmentFile.env'
        self.assertTrue(exists(env))
        self.assertXpathEqual(Env.get_root_dir(env), abspath(class_root))

        # case3 not found
        notfound = f'{UT_DIR_REPO}/Simple3a/NOTFOUND/POR_TP/TGLH81/EnvironmentFile.env'
        self.assertFalse(exists(notfound))     # not exist
        with self.assertRaisesRegex(ErrorInput, 'Modules/ folder cannot be found'):
            Env.get_root_dir(notfound)

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_paths(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        tp.env.set_env()
        self.assertEqual(len(tp.env._order), 50)
        self.assertEqual(len(tp.env.get_env_dict()), 49)
        self.assertEqual(len(tp.env.get_env_dict(stackval=True)), 0)
        self.assertEqual(tp.env.convert_fullpath('~MSIOTC_PATMODIFY_PATH/sio_tc_itpp_patmod.xml'),
                         '/intel/tpvalidation/engtools/tptools/mtl/unittests/env_reorder/hdmxpats/tgl/MsioTC/RevTTR0.2/p1/cfg/sio_tc_itpp_patmod.xml')

        obj = tp.env
        # to_winpath
        self.assertEqual(obj.to_winpath('/intel/hdmxpats/tgl/Mscan/RevTTC0.0/p1'),
                         'I:\\hdmxpats\\tgl\\Mscan\\RevTTC0.0\\p1')
        self.assertEqual(obj.to_winpath('/intel/hdmxpats/tgl/Mscan/RevTTC0.0/p1', sort=True),
                         'I:\\program\\1274\\eng\\hdmtpats\\tgl\\Mscan\\RevTTC0.0\\p1')
        self.assertEqual(obj.to_winpath('/intel/hdmxpats/tlp/Mscan/RevTTC0.0/p1', sort=True),
                         'I:\\program\\1273\\eng\\hdmtpats\\tlp\\Mscan\\RevTTC0.0\\p1')
        self.assertEqual(obj.to_winpath('./Mscan/RevTTC0.0/p1', sort=True),
                         '.\\Mscan\\RevTTC0.0\\p1')

        # to_unixpath
        self.assertEqual(obj.to_unixpath('I:\\program\\1273\\eng\\hdmtpats\\tlp\\Mscan\\RevTTC0.0\\p1'),
                         '/intel/hdmxpats/tlp/Mscan/RevTTC0.0/p1')
        self.assertEqual(obj.to_unixpath('I://program//1273//eng//hdmtpats//tlp//Mscan\\RevTTC0.0\\p1'),
                         '/intel/hdmxpats/tlp/Mscan/RevTTC0.0/p1')
        self.assertEqual(obj.to_unixpath('I:\\program\\1274\\eng\\hdmtpats\\tgl\\Mscan\\RevTTC0.0\\p1'),
                         '/intel/hdmxpats/tgl/Mscan/RevTTC0.0/p1')
        self.assertEqual(obj.to_unixpath('I:\\hdmxpats\\tgl\\Mscan\\RevTTC0.0\\p1'),
                         '/intel/hdmxpats/tgl/Mscan/RevTTC0.0/p1')
        self.assertEqual(obj.to_unixpath('I:/tpjdr/abc'),
                         '/intel/tpjdr/abc')    # catch all

        with self.assertRaisesRegex(ErrorInput, 'item is not found in env'):
            obj.get_contents('not_exist')

        # tp_winpath fullpath
        with MockVar(testprogram, 'IS_WIN', True):
            # found
            data = r'\\amr.corp.intel.com\ec\proj\mdl\jf\intel\tpvalidation\intel\jqdelosr'
            with MockVar(testprogram, 'realpath', Mock(return_value=data)):
                self.assertEqual(obj.to_winpath('./Mscan/RevTTC0.0/p1', idrive=True),
                                 r'I:\tpvalidation\intel\jqdelosr')

            # not found - as-is
            data = r'\\amr.corp.intel.com\blah\tpvalidation\jqdelosr'
            with MockVar(testprogram, 'realpath', Mock(return_value=data)):
                self.assertEqual(obj.to_winpath('./Mscan/RevTTC0.0/p1', idrive=True),
                                 r'.\Mscan\RevTTC0.0\p1')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_contents(self):
        tp = TestProgram(f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON/EnvironmentFile.env')

        # case: evaluate $env vars
        paths = tp.env.get_contents('HDST_PLIST_PATH').split(';')
        self.assertEqual(len(paths), 122)
        paths = tp.env.get_contents('HDST_PLIST_PATH', islist=True)
        self.assertEqual(len(paths), 122)

        # case: $include
        paths = tp.env.get_contents('HDMT_TPL_INPUT_FILES').split(';')
        self.assertEqual(len(paths), 64)

        # case: Torch all.plist.xml
        self.assertEqual(len(tp.plists.get_plist_list()), 95)

        # case: default
        paths = tp.env.get_contents('NOTFOUND', default='yikes')
        self.assertEqual(paths, 'yikes')

        # case: evaluated vs non-evaluated
        result = tp.env.get_contents('HDST_PLIST_PATH').split(';')
        self.assertEqual(result[0].replace('\\', '/'), f'{tp.tpldir}/Shared/Common/Supersedes/patterns')
        self.assertEqual(len(result), 122)
        with self.assertRaisesRegex(ErrorCockpit, 'Max number of iteration'):
            tp.env.get_contents('HDST_PLIST_PATH', _max=0)

        result = tp.env.get_contents('HDST_PLIST_PATH', as_is=True).split(';')
        self.assertEqual(result[0].replace('\\', '/'), f'~HDMT_TPL_DIR/Shared/Common/Supersedes/patterns')
        self.assertEqual(len(result), 3)

        # case: same variable used in Env and shared
        self.assertEqual(tp.env.get_contents('OTPL_JDR'), 'abc;ghi')

        # used but not defined
        tp.env.set_item('NEW_VAR', '/blah/$NOT_FOUND')
        with self.assertRaisesRegex(ErrorInput, 'is not defined but used'):
            tp.env.get_contents('NEW_VAR')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_convert_fullpath(self):
        obj = Env(Env.xpath('/intel/hdmxprogs/tgl/TGLXXXXBXH13Y00S017/TPL/EnvironmentFile.env'))

        # relative path
        self.assertXpathEqual(obj.convert_fullpath('./Modules/SIO_TCSS_ALL1/InputFiles'),
                              '/intel/hdmxprogs/tgl/TGLXXXXBXH13Y00S017/TPL/Modules/SIO_TCSS_ALL1/InputFiles')

        # env path
        obj = Env(Env.xpath('/intel/hdmxprogs/tgl/TGLXXXXBXH13Y00S017/TPL/EnvironmentFile.env'))
        self.assertXpathEqual(obj.convert_fullpath('~MSCNSOC_PATMODIFY_PATH/merged_iascan.class.hvm.sa.xml'),
                              '/intel/hdmxpats/tgl/MscnSOC/RevTTB0.2/p34/cfg/merged_iascan.class.hvm.sa.xml')

        # env path - not found case
        with self.assertRaisesRegex(ErrorInput, 'is not found in'):
            obj.convert_fullpath('~NOTFOUND/merged_iascan.class.hvm.sa.xml')

        # fullpath
        self.assertXpathEqual(obj.convert_fullpath('/blah/blah'), '/blah/blah')

    @unittest.skipIf(IS_WIN, 'unix only')
    def test_xpath_unix(self):
        self.assertEqual(Env.xpath('/intel'), '/intel')
        self.assertEqual(Env.xpath('/intel/notfound'), '/intel/notfound')
        self.assertEqual(Env.xpath('I:\\hdmxpats\\tgl\\Mscan\\RevTTC0.0\\p1'),
                         '/intel/hdmxpats/tgl/Mscan/RevTTC0.0/p1')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(IS_UNIX, 'windows only')
    def test_xpath_win(self):
        self.assertEqual(Env.xpath('/intel'), 'I:')
        self.assertEqual(Env.xpath('/intel/notfound'), 'I:/notfound')
        result = Env.xpath('I:\\hdmxpats\\tgl\\MGarr')
        self.assertEqual(result, 'I:/hdmxpats/tgl/MGarr')
        self.assertTrue(exists(result))

        with Chdir('i:/tpvalidation/jqdelosr'):
            self.assertEqual(Env.to_winpath('.', idrive=True), r'I:\tpvalidation\jqdelosr')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_rebuild_nochange(self):
        # rebuild should have no changes in env file, except spaces and extra line at end
        tp = TestProgram(f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        tp.env.set_env()
        with TempDir(name=True) as tdir:
            fname = f'{tdir}/res.env'
            File(fname).touch(tp.env.rebuild())
            result = [x.replace(' ', '').replace('\t', '') for x in File(tp.env.envfile).chomp()]
            expect = [x.replace(' ', '') for x in File(fname).chomp()] + ['']
            self.assertTextEqual('\n'.join(result), '\n'.join(expect))

    def test_rebuild(self):   # get_item() and set_item()
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf)

        # multi-line
        with TempDir(name=True) as tdir:
            tp.env.envfile = f'{tdir}/a.env'
            File(tp.env.envfile).touch(r"""### Env. File
USER_CODE_DLLS_PATH = "$PRIME_USER_CODE_DLL_DIR";

HDMT_TPAPPS_ROOT_EVG = "I:\tpapps\tmmlibs";

HDMT_TPAPPS_ROOT_PRIME = "I:\tpapps\tmmlibs";

HDST_PAT_PATH = "~HDMT_TPL_DIR\Supersedes\patterns;" +
                                "porig1;" +
                                "porig2;" +
                                "porig3";

HDST_PLIST_PATH = "~HDMT_TPL_DIR\Supersedes\patterns;" +
                                "orig1;" +
                                "orig2;" +
                                "orig3";
""")
            tp.env.set_env()

            repl = ['line1', 'line2', 'line3', 'line4']
            tp.env.set_item('HDST_PAT_PATH', repl)
            expect = r"""### Env. File
USER_CODE_DLLS_PATH = "$PRIME_USER_CODE_DLL_DIR";

HDMT_TPAPPS_ROOT_EVG = "I:\tpapps\tmmlibs";

HDMT_TPAPPS_ROOT_PRIME = "I:\tpapps\tmmlibs";

HDST_PAT_PATH = "line1;" +
    "line2;" +
    "line3;" +
    "line4";

HDST_PLIST_PATH = "~HDMT_TPL_DIR\Supersedes\patterns;" +
    "orig1;" +
    "orig2;" +
    "orig3";
"""
            self.assertTextEqual(tp.env.rebuild(), expect)
            self.assertEqual(tp.env.get_item('HDST_PAT_PATH', islist=True), repl)
            repl = 'line1;line2;line3;line4'
            tp.env.set_item('HDST_PAT_PATH', repl)
            self.assertTextEqual(tp.env.rebuild(), expect)
            self.assertEqual(tp.env.get_item('HDST_PAT_PATH'), repl)

            # single-line
            result = tp.env.set_item('HDMT_TPAPPS_ROOT_EVG', ['newa'])
            expect = r"""### Env. File
USER_CODE_DLLS_PATH = "$PRIME_USER_CODE_DLL_DIR";

HDMT_TPAPPS_ROOT_EVG = "newa";

HDMT_TPAPPS_ROOT_PRIME = "I:\tpapps\tmmlibs";

HDST_PAT_PATH = "line1;" +
    "line2;" +
    "line3;" +
    "line4";

HDST_PLIST_PATH = "~HDMT_TPL_DIR\Supersedes\patterns;" +
    "orig1;" +
    "orig2;" +
    "orig3";
"""
            self.assertTextEqual(tp.env.rebuild(), expect)

            # Two lines, $include, new item
            tp.env._order.append('$include "blah";')
            tp.env.set_item('HDMT_TPAPPS_ROOT_EVG', ['newa', 'newb'])
            tp.env.set_item('FUSEVAR', '')   # new item and empty
            expect = r"""### Env. File
USER_CODE_DLLS_PATH = "$PRIME_USER_CODE_DLL_DIR";

HDMT_TPAPPS_ROOT_EVG = "newa;" +
    "newb";

HDMT_TPAPPS_ROOT_PRIME = "I:\tpapps\tmmlibs";

HDST_PAT_PATH = "line1;" +
    "line2;" +
    "line3;" +
    "line4";

HDST_PLIST_PATH = "~HDMT_TPL_DIR\Supersedes\patterns;" +
    "orig1;" +
    "orig2;" +
    "orig3";

# $include "blah";
FUSEVAR = "";
"""
            self.assertTextEqual(tp.env.rebuild(), expect)

            # del_item
            self.assertEqual(len(tp.env._order), 8)
            self.assertTrue('FUSEVAR' in tp.env._order)
            self.assertTrue('FUSEVAR' in tp.env._env_dict)
            tp.env.del_item('FUSEVAR')
            self.assertEqual(len(tp.env._order), 7)
            self.assertFalse('FUSEVAR' in tp.env._order)
            self.assertFalse('FUSEVAR' in tp.env._env_dict)

    def test_rebuild2(self):   # get_item() and set_item()
        tpf = f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env'
        tp = TestProgram(tpf)

        # multi-line
        with TempDir(name=True) as tdir:
            tp.env.envfile = f'{tdir}/a.env'
            File(tp.env.envfile).touch(r"""### Env. File
USER_CODE_DLLS_PATH = "$PRIME_USER_CODE_DLL_DIR";

NPR_FOLDER_PATH = "aaa;bbb";
ABC = "aa\a;bb\a";
""")
            tp.env.set_env()

            expect = r"""### Env. File
USER_CODE_DLLS_PATH = "$PRIME_USER_CODE_DLL_DIR";

NPR_FOLDER_PATH = "aaa;" +
    "bbb";

ABC = "aa\a;bb\a";
"""
            self.assertTextEqual(tp.env.rebuild(['ABC']), expect)

            expect = r"""### Env. File
USER_CODE_DLLS_PATH = "$PRIME_USER_CODE_DLL_DIR";

NPR_FOLDER_PATH = "aaa;bbb";

ABC = "aa\a;" +
    "bb\a";
"""
            self.assertTextEqual(tp.env.rebuild(), expect)

    def test_rebuild_tos4_sort(self):   # get_item() and set_item()
        tpf = f'{UT_DIR_REPO}/Simple6tos4/POR_TP/TGLH81/EnvironmentFile.env'
        tp = TestProgram(tpf)

        # multi-line
        with TempDir(name=True) as tdir:
            tp.is_tos4 = True
            tp.env.envfile = f'{tdir}/a.env'
            File(tp.env.envfile).touch(r"""### Env. File
TP_STRUCTURE = "TORCH_TO_SORT";

SUPERSEDE_CODE_DIR = "~HDMT_TP_BASE_DIR\\Shared\\Common\\Supersedes\\code";
""")
            tp.env.set_env()

            expect = r"""### Env. File
TP_STRUCTURE = "TORCH_TO_SORT";

SUPERSEDE_CODE_DIR = "~HDMT_TP_BASE_DIR\\Shared\\Common\\Supersedes\\code";
"""
            self.assertTextEqual(tp.env.rebuild(), expect)

    def test_rebuild_tos4_class(self):   # get_item() and set_item()
        tpf = f'{UT_DIR_REPO}/Simple6tos4/POR_TP/TGLH81/EnvironmentFile.env'
        tp = TestProgram(tpf)

        with TempDir(name=True) as tdir:
            tp.is_tos4 = True
            tp.env.envfile = f'{tdir}/b.env'
            File(tp.env.envfile).touch(r"""### Env. File
TP_STRUCTURE = "TORCH";

SUPERSEDE_CODE_DIR = "~HDMT_TP_BASE_DIR\\Shared\\Common\\Supersedes\\code";
""")
            tp.env.set_env()

            expect = r"""### Env. File
TP_STRUCTURE = "TORCH";

SUPERSEDE_CODE_DIR = "~HDMT_TP_BASE_DIR//Shared//Common//Supersedes//code";
"""
            self.assertTextEqual(tp.env.rebuild(), expect)

    def test_rebuild_tos4(self):   # get_item() and set_item()
        tpf = f'{UT_DIR_REPO}/Simple6tos4/POR_TP/TGLH81/EnvironmentFile.env'
        tp = TestProgram(tpf)

        # multi-line
        with TempDir(name=True) as tdir:
            tp.env.envfile = f'{tdir}/a.env'
            File(tp.env.envfile).touch(r"""### Env. File
USER_CODE_DLLS_PATH = "$PRIME_USER_CODE_DLL_DIR";

NPR_FOLDER_PATH = "aaa;bbb";
_PATMOD = "blah";
ABC = "I:/a/b/c;I:\g\h\i";
""")
            tp.env.set_env()

            expect = r"""### Env. File
USER_CODE_DLLS_PATH = "$PRIME_USER_CODE_DLL_DIR";

NPR_FOLDER_PATH = "aaa;bbb";

_PATMOD = "blah";

ABC = "I:/a/b/c;" +
    "I:/g/h/i";
"""
            self.assertTextEqual(tp.env.rebuild(), expect)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_hdmt_tpl_dir(self):
        # TPIE
        tp = TestProgram(f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        self.assertEqual(tp.tpldir, f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL')
        self.assertEqual(tp.envdir, f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL')
        self.assertTrue(tp.is_tpie)

        # Torch
        tp = TestProgram(f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON/EnvironmentFile.env')
        self.assertEqual(tp.tpldir, f'{UT_DIR}/RPLS8P5A0H10P60S051')
        self.assertEqual(tp.envdir, f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON')
        self.assertFalse(tp.is_tpie)

        # relative path TPIE
        with Chdir(f'{UT_DIR}/TGLXXXXBXH14P00S109'):
            tp = TestProgram('TPL/EnvironmentFile.env')
            self.assertEqual(tp.tpldir, realpath(f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL'))
            self.assertEqual(tp.envdir, realpath(f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL'))
            self.assertTrue(tp.is_tpie)

        # relative path Torch
        with Chdir(f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON'):
            tp = TestProgram('EnvironmentFile.env')
            self.assertEqual(tp.tpldir, realpath(f'{UT_DIR}/RPLS8P5A0H10P60S051'))
            self.assertEqual(tp.envdir, realpath(f'{UT_DIR}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON'))
            self.assertFalse(tp.is_tpie)

    @with_(TempDir, chdir=True)
    def test_find_env_file(self):
        # not found case
        File('abc.txt').touch()
        with self.assertRaisesRegex(ErrorInput, 'Unable to locate'):
            TestProgram._find_env_file('.')

        # found case
        File('EnvironmentFile.env').touch()
        self.assertXpathEqual(TestProgram._find_env_file('.'), './EnvironmentFile.env')

        # invalid dir case
        with self.assertRaisesRegex(ErrorInput, 'Unable to locate'):
            TestProgram._find_env_file('/notfound')

        # prioritize on POR_TP folder
        File('EnvironmentFile.env').unlink()
        File('POR_TP/Class_NVL_S28C/EnvironmentFile.env').touch(mkdir=True)
        File('Shared/POR_TP/Class_NVL_S28C/EnvironmentFile.env').touch(mkdir=True)
        File('Shared/POR_TP/Class_NVL_S52C/EnvironmentFile.env').touch(mkdir=True)
        File('Shared/POR_TP/Class_NVL_HX28C/EnvironmentFile.env').touch(mkdir=True)
        self.assertXpathEqual(TestProgram._find_env_file('.'), './POR_TP/Class_NVL_S28C/EnvironmentFile.env')

        # NVL AHMT case
        File('tpx/POR_TP/CLASS_AHMT_POR/EnvironmentFile.env').touch(mkdir=True)
        self.assertXpathEqual(TestProgram._find_env_file('tpx'), 'tpx/POR_TP/CLASS_AHMT_POR/EnvironmentFile.env')
        File('tpx/POR_TP/Class_NVL_S28C/EnvironmentFile.env').touch(mkdir=True)
        self.assertXpathEqual(TestProgram._find_env_file('tpx'), 'tpx/POR_TP/Class_NVL_S28C/EnvironmentFile.env')

    def test_read(self):
        tpobj = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        with TempDir(chdir=True):
            lines = """
    CASE1 =
          "path_case1";
    HDST_CASE1_PATH = "$CASE1";

    CASE2 =
          "path_case1;" +
          "path_case2";
    HDST_CASE2_PATH =
             "$CASE2";
    CASE5 = "a;" + "b;"+"c;"+ "d;";
    CASE6 = "a;" + "b;"+"c;"+
       "d;";
    """
            fname = 'a.env'
            File(fname).touch(lines)
            tpobj.env.envfile = fname
            tpobj.env.set_env()
            pprint(tpobj.env.get_env_dict())
            self.assertEqual(tpobj.env.get_env_dict(),
                             {'CASE1': 'path_case1',
                              'CASE2': 'path_case1;path_case2',
                              'HDST_CASE1_PATH': '$CASE1',
                              'HDST_CASE2_PATH': '$CASE2',
                              'CASE5': 'a;b;c;d;',
                              'CASE6': 'a;b;c;d;',
                              }
                             )


class TestOther(TestCase):

    def test_setenv(self):
        # make sure setenv_unittest is the same across all
        first = None
        for ff in glob.glob(join(ROOT_ENV, '*/test/setenv_unittest.py')):
            result = File(ff).sha1()
            if first is None:
                first = (result, ff)
            self.assertEqual(result, first[0], f'Expecting to be the same: {ff} vs {first[1]}')


class TestShared(TestCase):
    """Shared with test_programfamily"""

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_real(self):
        # many env file
        obj = ProgramFamily(f'{UT_DIR}/ICLXXXXXXH58G2XS904/TPL').init_all_env()
        self.assertEqual(len(list(obj)), 5)
        stpl = {x.get_stpl() for x in obj}
        self.assertEqual(len(stpl), 5)
        self.assertEqual(len({x.plists for x in obj}), 5)
        self.assertEqual(len(obj.get_all_stpls()), 5)

        # many stpl file
        obj = ProgramFamily(f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL').init_all_stpl()
        self.assertEqual(len(list(obj)), 2)
        stpl = {x.get_stpl() for x in obj}
        self.assertEqual(len(stpl), 2)

        # many env file
        obj = ProgramFamily(f'{UT_DIR}/ICXXXXXAXH10G10S922').init_all_env()
        self.assertEqual(len(list(obj)), 3)
        stpl = {x.get_stpl() for x in obj}
        self.assertEqual(len(stpl), 3)

        # manual
        tplist = [TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env'),
                  TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')]
        obj = ProgramFamily(UT_DIR + '/TGLXXXXRXH35H00S025/TPL').init_manual(tplist)
        self.assertEqual(len(list(obj)), 2)
        stpl = {x.get_stpl() for x in obj}
        self.assertEqual(len(stpl), 2)

        # env file is specified
        obj = ProgramFamily(UT_DIR + '/TGLXXXXBXH14P00S109/TPL').init_all_stpl('EnvironmentFile.env')
        self.assertEqual(len(list(obj)), 2)
        stpl = {x.get_stpl() for x in obj}
        self.assertEqual(len(stpl), 2)
        self.assertEqual(len({x.plists for x in obj}), 1)    # unique plist objects

        # others
        self.assertEqual(len(obj.get_all_stpls()), 2)
        self.assertTrue(isinstance(obj.any_tp(), TestProgram))
        obj2 = ProgramFamily(UT_DIR + '/TGLXXXXBXH14P00S109/TPL')
        self.assertEqual(obj2.any_tp(), None)


class TestFamily(TestCase):

    def test_basic(self):
        with TempDir(name=True) as tdir:
            code1 = """Version 1.0;

ProgramStyle = Modular;
TestPlan Flows;
"""
            File('%s/ProgramFlows.mtpl' % tdir).touch(code1, mkdir=True)
            code2 = """Version 1.0;
Test iCSimpleScoreboardTest CCF_XXXXX
{
        base_number = 2160;
}
"""
            File('%s/Modules/ARR/a.mtpl' % tdir).touch(code2, mkdir=True)
            File('%s/env.env' % tdir).touch()
            File('%s/a.tpl' % tdir).touch()
            File('%s/all.xml' % tdir).touch()
            tp = TestProgram('%s/env.env' % tdir, allplist='%s/all.xml' % tdir)

            # no stpl found
            with self.assertRaisesRegex(ErrorInput, 'No .stpl file found in'):
                tp.get_stpl()

            # normal case
            tp._ut_write_stpl()
            self.assertEqual(Env.xpath(tp.get_final_mtpl()), Env.xpath(join(tdir, '.', 'ProgramFlows.mtpl')))
            self.assertEqual(sorted(tp.get_all_mtpl_from_stpl()), [join(tdir, './Modules/ARR/a.mtpl')])

            # ProgramFamily
            obj = ProgramFamily(tdir).init_manual([tp])
            self.assertEqual([x[1] for x in obj.mtpl.iter_tests()], ['CCF_XXXXX'])
            self.assertEqual(obj.mtpl.get_modules(), ['ARR'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_tgl42(self):
        envfile = UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env'
        pf = ProgramFamily(dirname(envfile)).init_all_stpl(envfile)
        self.assertEqual({basename(tp.get_stpl()) for tp in pf.iter_tp()},
                         {'SubTestPlan_CLASS_TGLU42.stpl', 'SubTestPlan_CLASS_TGLY42.stpl'})


class Val(TestCase):
    """Validation routines"""

    def all_tp(self):
        list_tp = []
        list_tp.append('/intel/hdmxprogs/icl/ICLXXXXXXH58G2XS904/TPL/EnvironmentFile_CLASS_ICL_42_U.env')
        list_tp.append(f'{UT_DIR}/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        list_tp.append(f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        list_tp.append('/intel/hdmxprogs/icx/ICXXXXXAXH10G10S922/EnvironmentFile_CLASS_HCCSP.env')
        list_tp.append('/intel/hdmxpats/tgl/sort_tp/tgl_sds/TGLSDSCA8H12H011947/EnvironmentFile.env')
        return list_tp

    def edckil(self):
        for tpenv in self.all_tp():
            print(f"== {tpenv}")
            tp = TestProgram(tpenv)
            tp.mtpl.set_tn_attrib()
            result = defaultdict(int)
            for md, tn, data, ports in tp.mtpl.iter_flows('MAIN', passonly=False, bypass=False, keyparam='patlist', idict=True, pdict=True):
                result[data['_EDCKIL']] += 1
            print(result)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
