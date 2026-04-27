#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for nvl_ahmt_chk.py
"""
from setenv_unittest import UT_DIR_REPO
from qgates.test.setenv_unittest import UT_DIR_REPO
from qgates.nvl_ahmt_chk import *
from gadget.ut import TestCase, unittest
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import patch, Mock
from gadget.gizmo import with_, MockVar
from tp.testprogram import TestProgram
import os


class AHMTCheckTest(TestCase):

    @with_(TempDir, chdir=True)
    def test_skip_non_ahmt_tp(self):
        # Test that the checker processes only AHMT modules
        File('POR_TP/Class_NVL_S28C/EnvironmentFile.env').touch('''
Version 1.0;
''', mkdir=True)

        tpobj = Mock()
        tpobj.envdir = 'POR_TP/Class_NVL_S28C'
        tpobj.mtpl = Mock()
        # Return a dictionary with non-AHMT modules only
        tpobj.mtpl.get_mod2fname = Mock(return_value={
            'REGULAR_MOD': 'Modules/TEST/REGULAR_MODULE/test.mtpl'
        })

        obj = AHMTCheck(tpobj)
        with CaptureStdoutLog() as output:
            obj.main()

        # Should complete without processing any modules (no AHMT modules found)
        self.assertEqual(len(obj.result), 0)

    @with_(TempDir, chdir=True)
    def test_extract_setbin_from_mtpl(self):
        # Test extracting SetBin values from mtpl file
        mtpl_content = '''
// This is a comment with SetBin b12345678_fail_TEST - should be skipped
SetBin SoftBins.b90440101_fail_MODULE_TEST_0;
SetBin SoftBins.b90440102_fail_MODULE_TEST_1;
# Another comment SetBin b99999999_fail_SKIP
/* Multi-line comment
SetBin SoftBins.b88888888_fail_SKIP;
*/
SetBin "SoftBins.b" + FlowMatrix.bin + "4401_fail_MTT_TEST";
SetBin SoftBins.b9744050_fail_THERMAL_7;
'''
        File('test.mtpl').touch(mtpl_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)
        bins = obj.extract_setbin_from_mtpl('test.mtpl')

        # Should extract 8-digit bins and skip commented ones
        self.assertIn('90440101', bins)
        self.assertIn('90440102', bins)
        self.assertIn('9744050', bins)
        self.assertIn('4401', bins)
        # Should NOT extract commented bins
        self.assertNotIn('12345678', bins)
        self.assertNotIn('99999999', bins)
        self.assertNotIn('88888888', bins)

    @with_(TempDir, chdir=True)
    def test_extract_bins_from_subbindef(self):
        # Test extracting bin numbers from SubBindef file (lines 186, 191)
        sbdefs_content = '''
Version 1.0;
SubBinDefs
{
    BinGroup SoftBins
    {
        # This is a comment
        LeafBin b90440101_fail_TEST    90440101    : "b90440101_fail_TEST",    b44_FAIL;
        LeafBin b90440102_fail_TEST2   90440102    : "b90440102_fail_TEST2",   b44_FAIL;
        // This is a C++ style comment
        LeafBin b9744050_fail_THERMAL  9744050     : "b9744050_fail_THERMAL",  b97_FAIL;
        Bin shortline
        LeafBin invalidline nonumber
        // LeafBin b99999999_commented  99999999     : "b99999999_commented",  b99_FAIL;
    }
}
'''
        File('test_dir/test.sbdefs').touch(sbdefs_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)
        with CaptureStdoutLog() as output:
            bins = obj.extract_bins_from_subbindef('test_dir/')

        self.assertIn('90440101', bins)
        self.assertIn('90440102', bins)
        self.assertIn('9744050', bins)
        # Should NOT include the commented bin
        self.assertNotIn('99999999', bins)
        # Should log extraction
        self.assertIn('Extracted', output.getvalue())

    @with_(TempDir, chdir=True)
    def test_extract_bins_from_subbindef_not_found(self):
        # Test when SubBindef file is not found
        tpobj = Mock()
        obj = AHMTCheck(tpobj)
        bins = obj.extract_bins_from_subbindef('nonexistent_dir/')

        self.assertIsNone(bins)

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_porroot(self):
        # Test parsing PORRoot from module.mconfig XML file (lines 276, 278, 280, 283)
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\nvl_nps\\MPclk" Rev="RevTPC4A0.1" Patch="p8">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
        <PORRoot Path="I:\\hdmxpats\\nvl_hub\\MHmio" Rev="RevTHHXXA0.0" Patch="p18">
            <PlistFiles>
                <PlistFile>test2.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
        <PORRoot Path="" Rev="" Patch="">
            <PlistFiles>
                <PlistFile>empty.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)
        paths = obj.parse_mconfig_porroot('module.mconfig')

        self.assertEqual(len(paths), 2)
        full_paths = [p['full_path'] for p in paths]
        self.assertIn('I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p8', full_paths)
        self.assertIn('I:/hdmxpats/nvl_hub/MHmio/RevTHHXXA0.0/p18', full_paths)

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_porroot_with_double_slashes(self):
        # Test that double slashes are normalized
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\nvl_nps\\MPsioTCSSDP\\" Rev="RevTPC4A0.0" Patch="p14">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)
        paths = obj.parse_mconfig_porroot('module.mconfig')

        # Should normalize double slashes
        self.assertEqual(len(paths), 1)
        full_paths = [p['full_path'] for p in paths]
        self.assertIn('I:/hdmxpats/nvl_nps/MPsioTCSSDP/RevTPC4A0.0/p14', full_paths)

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_porroot_file_not_found(self):
        # Test when mconfig file doesn't exist (lines 318-320)
        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            paths = obj.parse_mconfig_porroot('nonexistent_mconfig.xml')

        # Should log error about file not existing
        self.assertIn('mconfig file does not exist', output.getvalue())
        # Should return empty list
        self.assertEqual(len(paths), 0)

    @with_(TempDir, chdir=True)
    def test_check_ahmt_bins_pass(self):
        # Test when all AHMT bins exist in SubBindef
        mtpl_content = '''
SetBin SoftBins.b90440101_fail_MODULE_TEST;
SetBin SoftBins.b90440102_fail_MODULE_TEST2;
'''
        File('Modules/TEST_AHMT/test.mtpl').touch(mtpl_content, mkdir=True)

        sbdefs_content = '''
Version 1.0;
SubBinDefs
{
    BinGroup SoftBins
    {
        LeafBin b90440101_fail_TEST    90440101    : "b90440101_fail_TEST",    b44_FAIL;
        LeafBin b90440102_fail_TEST2   90440102    : "b90440102_fail_TEST2",   b44_FAIL;
        LeafBin b90440103_fail_TEST3   90440103    : "b90440103_fail_TEST3",   b44_FAIL;
    }
}
'''
        File('Modules/TEST/test.sbdefs').touch(sbdefs_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)
        obj.check_ahmt_bins_in_subbindef(
            'Modules/TEST_AHMT/test.mtpl',
            'Modules/TEST_AHMT/',
            'Modules/TEST/',
            'TEST_AHMT'
        )

        self.assertEqual(obj.passed, {(290, 'TEST_AHMT'): 1})
        self.assertEqual(len(obj.result), 0)

    @with_(TempDir, chdir=True)
    def test_check_ahmt_bins_fail(self):
        # Test when AHMT bins are missing in SubBindef
        mtpl_content = '''
SetBin SoftBins.b90440101_fail_MODULE_TEST;
SetBin SoftBins.b90440102_fail_MODULE_TEST2;
SetBin SoftBins.b90440104_fail_MODULE_TEST4;
'''
        File('Modules/TEST_AHMT/test.mtpl').touch(mtpl_content, mkdir=True)

        sbdefs_content = '''
Version 1.0;
SubBinDefs
{
    BinGroup SoftBins
    {
        LeafBin b90440101_fail_TEST    90440101    : "b90440101_fail_TEST",    b44_FAIL;
        LeafBin b90440103_fail_TEST3   90440103    : "b90440103_fail_TEST3",   b44_FAIL;
    }
}
'''
        File('Modules/TEST/test.sbdefs').touch(sbdefs_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)
        obj.check_ahmt_bins_in_subbindef(
            'Modules/TEST_AHMT/test.mtpl',
            'Modules/TEST_AHMT/',
            'Modules/TEST/',
            'TEST_AHMT'
        )

        self.assertEqual(len(obj.result), 1)
        self.assertIn('90440102', obj.result[0]['message'])
        self.assertIn('90440104', obj.result[0]['message'])
        self.assertEqual(obj.result[0]['id'], 290)
        self.assertEqual(obj.result[0]['module'], 'TEST_AHMT')

    @with_(TempDir, chdir=True)
    def test_check_porroot_in_envfile_pass(self):
        # Test when PORRoot paths exist in env file
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\nvl_nps\\MPclk" Rev="RevTPC4A0.1" Patch="p8">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/CLK_ISCLKAHMT_PXS/module.mconfig').touch(mconfig_content, mkdir=True)

        env_content = '''Version 1.0;

TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p8/plb;" +
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p8/pat;" +
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p7/pat;" +
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p6/pat;" +
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p5/pat;" +
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p4/pat;" +
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p3/pat;" +
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p2/pat;" +
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p1/pat;" +
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/p0/pat;" +
    "$TORCH_AUTO_PLIST_PATH";
'''
        File('EnvironmentFile.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'EnvironmentFile.env'

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/CLK_ISCLKAHMT_PXS/', 'CLK_ISCLKAHMT_PXS')

        # Should have some passes (might also have errors if TORCH section isn't found)
        self.assertEqual(len(obj.result), 0)
        # Check if there are any passes related to this module
        module_passes = [k for k in obj.passed.keys() if k[1] == 'CLK_ISCLKAHMT_PXS']
        self.assertGreater(len(module_passes), 0)

    @with_(TempDir, chdir=True)
    def test_check_porroot_in_envfile_fail(self):
        # Test when PORRoot paths are missing in env file
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\nvl_nps\\MPclk" Rev="RevTPC4A0.1" Patch="p8">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/CLK_ISCLKAHMT_PXS/module.mconfig').touch(mconfig_content, mkdir=True)

        env_content = '''Version 1.0;

TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/nvl_nps/MPother/RevTPC4A0.1/p8/plb;" +
    "$TORCH_AUTO_PLIST_PATH";
'''
        File('EnvironmentFile.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'EnvironmentFile.env'

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/CLK_ISCLKAHMT_PXS/', 'CLK_ISCLKAHMT_PXS')

        # Should have at least one error
        self.assertGreater(len(obj.result), 0)
        # Check that the error is about the missing paths
        has_path_error = any('MPclk' in str(r.get('message', '')) for r in obj.result)
        self.assertTrue(has_path_error)

        self.assertEqual(len(obj.result), 1)
        # Should mention paths missing (plb and all pat from p8-p0 will be missing)
        self.assertIn('PORRoot paths missing', obj.result[0]['message'])
        self.assertEqual(obj.result[0]['id'], 291)
        self.assertEqual(obj.result[0]['module'], 'CLK_ISCLKAHMT_PXS')

    @with_(TempDir, chdir=True)
    def test_check_porroot_no_mconfig(self):
        # Test when no module.mconfig file is found
        tpobj = Mock()
        tpobj.envfile = 'EnvironmentFile.env'

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/TEST_AHMT/', 'TEST_AHMT')

        # Should not add any errors or passes
        self.assertEqual(len(obj.result), 0)
        self.assertEqual(len(obj.passed), 0)

    @with_(TempDir, chdir=True)
    def test_check_porroot_no_porroot_in_mconfig(self):
        # Test when mconfig has no PORRoot elements
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/TEST_AHMT/module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'EnvironmentFile.env'

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/TEST_AHMT/', 'TEST_AHMT')

        # Should not add any errors or passes
        self.assertEqual(len(obj.result), 0)
        self.assertEqual(len(obj.passed), 0)

    @with_(TempDir, chdir=True)
    def test_check_porroot_no_double_slashes(self):
        # Test that paths with trailing slashes or empty components don't generate double slashes
        # This simulates the real-world case where PORRoot Path ends with slash
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\nvl_nps\\MPsioTCSSDP\\" Rev="RevTPC4A0.0" Patch="p3">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/SIO_TCSSDPAHMT_PCS/module.mconfig').touch(mconfig_content, mkdir=True)

        # Env file with correctly formatted paths (no double slashes)
        env_content = '''Version 1.0;

TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/nvl_nps/MPsioTCSSDP/RevTPC4A0.0/p3/plb;" +
    "I:/hdmxpats/nvl_nps/MPsioTCSSDP/RevTPC4A0.0/p3/pat;" +
    "I:/hdmxpats/nvl_nps/MPsioTCSSDP/RevTPC4A0.0/p2/pat;" +
    "I:/hdmxpats/nvl_nps/MPsioTCSSDP/RevTPC4A0.0/p1/pat;" +
    "I:/hdmxpats/nvl_nps/MPsioTCSSDP/RevTPC4A0.0/p0/pat;" +
    "$TORCH_AUTO_PLIST_PATH";
'''
        File('EnvironmentFile.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'EnvironmentFile.env'

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/SIO_TCSSDPAHMT_PCS/', 'SIO_TCSSDPAHMT_PCS')

        # Should have no errors - paths should match correctly without double slashes
        self.assertEqual(len(obj.result), 0)
        # Check if there are any passes related to this module
        module_passes = [k for k in obj.passed.keys() if k[1] == 'SIO_TCSSDPAHMT_PCS']
        self.assertGreater(len(module_passes), 0)

    @with_(TempDir, chdir=True)
    def test_check_porroot_patch_no_p_prefix(self):
        # Test coverage for line 273: patch doesn't start with 'p'
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\nvl_nps\\MPclk" Rev="RevTPC4A0.1" Patch="v8">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/CLK_ISCLKAHMT_PXS/module.mconfig').touch(mconfig_content, mkdir=True)

        env_content = '''Version 1.0;

TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/v8;" +
    "$TORCH_AUTO_PLIST_PATH";
'''
        File('EnvironmentFile.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'EnvironmentFile.env'

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/CLK_ISCLKAHMT_PXS/', 'CLK_ISCLKAHMT_PXS')

        # Should have no errors - full path should be checked
        self.assertEqual(len(obj.result), 0)
        module_passes = [k for k in obj.passed.keys() if k[1] == 'CLK_ISCLKAHMT_PXS']
        self.assertGreater(len(module_passes), 0)

    @with_(TempDir, chdir=True)
    def test_check_porroot_patch_invalid_number(self):
        # Test coverage for lines 268, 270: patch starts with 'p' but has invalid number
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\nvl_nps\\MPclk" Rev="RevTPC4A0.1" Patch="pXYZ">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/CLK_ISCLKAHMT_PXS/module.mconfig').touch(mconfig_content, mkdir=True)

        env_content = '''Version 1.0;

TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/nvl_nps/MPclk/RevTPC4A0.1/pXYZ;" +
    "$TORCH_AUTO_PLIST_PATH";
'''
        File('EnvironmentFile.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'EnvironmentFile.env'

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/CLK_ISCLKAHMT_PXS/', 'CLK_ISCLKAHMT_PXS')

        # Should have no errors - full path should be checked when ValueError occurs
        self.assertEqual(len(obj.result), 0)
        module_passes = [k for k in obj.passed.keys() if k[1] == 'CLK_ISCLKAHMT_PXS']
        self.assertGreater(len(module_passes), 0)

    @with_(TempDir, chdir=True)
    def test_check_porroot_with_explicit_env_object(self):
        # Covers branch where env object is explicitly present and fallback is skipped
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\test" Rev="RevA" Patch="p1">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/TEST_AHMT/module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        tpobj.env = Mock()
        tpobj.env.get_item = Mock(side_effect=lambda key, islist=True: {
            'TORCH_AUTO_PLIST_PATH': ['I:/hdmxpats/test/RevA/p1/plb'],
            'TORCH_AUTO_PAT_PATH': ['I:/hdmxpats/test/RevA/p1/pat', 'I:/hdmxpats/test/RevA/p0/pat']
        }.get(key, []))

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/TEST_AHMT/', 'TEST_AHMT')

        self.assertEqual(len(obj.result), 0)
        self.assertEqual(obj.passed[(291, 'TEST_AHMT')], 1)

    @with_(TempDir, chdir=True)
    def test_check_porroot_env_object_none_values_uses_fallback(self):
        # Covers to_path_list(None) branch and fallback parser execution
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\test" Rev="RevA" Patch="p0">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/TEST_AHMT/module.mconfig').touch(mconfig_content, mkdir=True)

        env_content = '''Version 1.0;

TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/test/RevA/p0/plb;" +
    "I:/hdmxpats/test/RevA/p0/pat;" +
    $TORCH_AUTO_PLIST_PATH;
'''
        File('EnvironmentFile.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.env = Mock()
        tpobj.env.get_item = Mock(return_value=None)
        tpobj.envfile = 'EnvironmentFile.env'

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/TEST_AHMT/', 'TEST_AHMT')

        self.assertEqual(len(obj.result), 0)
        self.assertEqual(obj.passed[(291, 'TEST_AHMT')], 1)

    @with_(TempDir, chdir=True)
    def test_check_porroot_env_object_string_and_invalid_type(self):
        # Covers to_path_list(str) and to_path_list(other) branches
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\test" Rev="RevA" Patch="v8">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/TEST_AHMT/module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        tpobj.env = Mock()
        tpobj.env.get_item = Mock(side_effect=lambda key, islist=True: {
            'TORCH_AUTO_PLIST_PATH': 'I:/hdmxpats/test/RevA/v8',
            'TORCH_AUTO_PAT_PATH': 123
        }.get(key, None))

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/TEST_AHMT/', 'TEST_AHMT')

        self.assertEqual(len(obj.result), 0)
        self.assertEqual(obj.passed[(291, 'TEST_AHMT')], 1)

    @with_(TempDir, chdir=True)
    def test_check_porroot_env_parse_exception_no_envfile(self):
        # Covers exception path for env.get_item and false branch for env_file exists check
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\test" Rev="RevA" Patch="p0">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/TEST_AHMT/module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        tpobj.env = Mock()
        tpobj.env.get_item = Mock(side_effect=Exception('Badly placed (.'))
        tpobj.envfile = 'does_not_exist.env'

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/TEST_AHMT/', 'TEST_AHMT')

        self.assertEqual(len(obj.result), 1)
        self.assertEqual(obj.result[0]['id'], 291)

    @with_(TempDir, chdir=True)
    def test_check_porroot_fallback_section_and_comment_branches(self):
        # Covers fallback parser branches for //[ section, [ section, comments, and invalid raw lines
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\test" Rev="RevA" Patch="p0">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/TEST_AHMT/module.mconfig').touch(mconfig_content, mkdir=True)

        env_content = '''Version 1.0;

TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/test/RevA/p0/plb;" +
//[CommentedSection]
    # ignore this line
    +
    $TORCH_AUTO_PLIST_PATH;
    "I:/hdmxpats/test/RevA/p0/pat;" +
[RealSection]
value = test;
'''
        File('EnvironmentFile.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'EnvironmentFile.env'

        obj = AHMTCheck(tpobj)
        obj.check_porroot_in_envfile('Modules/TEST_AHMT/', 'TEST_AHMT')

        self.assertEqual(len(obj.result), 0)
        self.assertEqual(obj.passed[(291, 'TEST_AHMT')], 1)

    @with_(TempDir, chdir=True)
    def test_main_integration(self):
        # Integration test for main function (covers line 38)
        # Create AHMT module structure
        mtpl_content = '''
SetBin SoftBins.b90440101_fail_MODULE_TEST;
'''
        File('Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL/MIO_DDR5DC_HXNVL.mtpl').touch(mtpl_content, mkdir=True)

        sbdefs_content = '''
Version 1.0;
SubBinDefs
{
    BinGroup SoftBins
    {
        LeafBin b90440101_fail_TEST    90440101    : "b90440101_fail_TEST",    b44_FAIL;
    }
}
'''
        File('Modules/MIO_DDR/MIO_DDR5DC_HXNVL/MIO_DDR5DC_HXNVL_SubBinDefinitions.sbdefs').touch(sbdefs_content, mkdir=True)

        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\nvl_hub\\MHmioDDR" Rev="RevTHHXXA0.0" Patch="p18">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL/module.mconfig').touch(mconfig_content, mkdir=True)

        env_content = '''Version 1.0;

TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p18/plb;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p18/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p17/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p16/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p15/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p14/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p13/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p12/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p11/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p10/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p9/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p8/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p7/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p6/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p5/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p4/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p3/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p2/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p1/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p0/pat;" +
    "$TORCH_AUTO_PLIST_PATH";
'''
        File('POR_TP/CLASS_AHMT_POR/EnvironmentFile.env').touch(env_content, mkdir=True)

        # Mock the TestProgram object
        tpobj = Mock()
        tpobj.envdir = 'POR_TP/CLASS_AHMT_POR'
        tpobj.envfile = 'POR_TP/CLASS_AHMT_POR/EnvironmentFile.env'
        tpobj.mtpl = Mock()
        tpobj.mtpl.get_mod2fname = Mock(return_value={
            'MIO_DDR5DC_HXXX': 'Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL/MIO_DDR5DC_HXNVL.mtpl'
        })

        obj = AHMTCheck(tpobj)
        obj.main()

        # Should have passes for both checks
        self.assertEqual(len(obj.result), 0)
        module_passes = [k for k in obj.passed.keys() if k[1] == 'MIO_DDR5DCAHMT_HXNVL']
        self.assertEqual(len(module_passes), 2)  # One for bins, one for PORRoot
        # Should pass both checks
        self.assertEqual(obj.passed, {(290, 'MIO_DDR5DCAHMT_HXNVL'): 1, (291, 'MIO_DDR5DCAHMT_HXNVL'): 1})
        self.assertEqual(len(obj.result), 0)

    @with_(TempDir, chdir=True)
    def test_extract_setbin_no_bins_found(self):
        # Test when no SetBin calls are found in mtpl file (lines 62-64)
        mtpl_content = '''
// Just comments
# No actual SetBin calls
/* More comments */
TestFlow test;
'''
        File('test_dir/test.mtpl').touch(mtpl_content, mkdir=True)
        File('porpath/.placeholder').touch('', mkdir=True)  # Create the porpath directory

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        # Call check_ahmt_bins_in_subbindef which will call extract_setbin_from_mtpl
        with CaptureStdoutLog() as output:
            obj.check_ahmt_bins_in_subbindef('test_dir/test.mtpl', 'test_dir/', 'porpath/', 'TEST_MOD')

        # Should log info about no SetBin calls found
        self.assertIn('No SetBin calls found', output.getvalue())
        # Should return early without adding errors
        self.assertEqual(len(obj.result), 0)

    @with_(TempDir, chdir=True)
    def test_extract_setbin_file_read_error(self):
        # Test error handling when reading mtpl file fails (lines 97-99)
        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            bins = obj.extract_setbin_from_mtpl('nonexistent_file.mtpl')

        # Should log error about reading file
        self.assertIn('AHMT mtpl file does not exist', output.getvalue())
        # Should return empty set
        self.assertEqual(len(bins), 0)

    @with_(TempDir, chdir=True)
    def test_extract_setbin_with_7digit_bins(self):
        # Test extraction of 7-digit bins that aren't part of 8-digit bins (lines 134-135, 144)
        mtpl_content = '''
SetBin SoftBins.b9744050_fail_THERMAL_7;
SetBin SoftBins.b9044010_fail_MODULE;
SetBin SoftBins.b90440101_fail_MODULE_TEST;
SetBin SoftBins.b1234567_fail_STANDALONE;
'''
        File('test.mtpl').touch(mtpl_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            bins = obj.extract_setbin_from_mtpl('test.mtpl')

        # Should extract both 7-digit and 8-digit bins
        self.assertIn('9744050', bins)
        self.assertIn('9044010', bins)  # 7-digit not part of 90440101
        self.assertIn('90440101', bins)
        self.assertIn('1234567', bins)  # Standalone 7-digit
        # Should log the extraction
        self.assertIn('Extracted', output.getvalue())
        self.assertIn('bins from', output.getvalue())

    @with_(TempDir, chdir=True)
    def test_extract_bins_subbindef_not_found(self):
        # Test when SubBindef file is not found (lines 167-168)
        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            bins = obj.extract_bins_from_subbindef('nonexistent_dir/')

        # Should log error about no .sbdefs file found
        self.assertIn('No .sbdefs file found', output.getvalue())
        # Should return None
        self.assertIsNone(bins)

    @with_(TempDir, chdir=True)
    def test_extract_bins_subbindef_multiple_files(self):
        # Test when multiple SubBindef files are found (line 172)
        sbdefs_content = '''
Version 1.0;
SubBinDefs
{
    BinGroup SoftBins
    {
        LeafBin b90440101_fail_TEST    90440101    : "b90440101_fail_TEST",    b44_FAIL;
    }
}
'''
        File('test_dir/file1.sbdefs').touch(sbdefs_content, mkdir=True)
        File('test_dir/file2.sbdefs').touch(sbdefs_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            bins = obj.extract_bins_from_subbindef('test_dir/')

        # Should log info about multiple files
        self.assertIn('Multiple .sbdefs files found', output.getvalue())
        # Should still extract bins from the first file
        self.assertIn('90440101', bins)

    @with_(TempDir, chdir=True)
    def test_extract_bins_subbindef_read_error(self):
        # Test error handling when .sbdefs file doesn't exist (line 182)
        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        # Test with non-existent directory
        with CaptureStdoutLog() as output:
            bins = obj.extract_bins_from_subbindef('nonexistent_dir/')

        # Should log error about missing file
        self.assertIn('No .sbdefs file found', output.getvalue())
        # Should return None
        self.assertIsNone(bins)

    @with_(TempDir, chdir=True)
    def test_extract_bins_subbindef_file_deleted(self):
        # Test edge case where glob finds file but it doesn't exist when checked (lines 191-193)
        # This could happen if file is deleted between glob and exists check
        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        # Create directory structure
        os.makedirs('test_dir', exist_ok=True)

        # Mock glob to return a file that doesn't exist
        with patch('glob.glob', return_value=['test_dir/nonexistent.sbdefs']):
            with CaptureStdoutLog() as output:
                bins = obj.extract_bins_from_subbindef('test_dir/')

            # Should log error about file not existing
            self.assertIn('SubBindef file does not exist', output.getvalue())
            # Should return None
            self.assertIsNone(bins)

    @with_(TempDir, chdir=True)
    def test_check_porroot_no_mconfig_file(self):
        # Test when no module.mconfig file is found (lines 193-195)
        tpobj = Mock()
        tpobj.envfile = 'test.env'
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            obj.check_porroot_in_envfile('empty_dir/', 'TEST_MOD')

        # Should log info about no mconfig file
        self.assertIn('No module.mconfig file found', output.getvalue())
        # Should return early without errors
        self.assertEqual(len(obj.result), 0)

    @with_(TempDir, chdir=True)
    def test_check_porroot_no_porroot_paths(self):
        # Test when mconfig has no PORRoot paths (lines 227-229)
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
    </Patterns>
</ModuleConfiguration>
'''
        File('test_dir/module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'test.env'
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            obj.check_porroot_in_envfile('test_dir/', 'TEST_MOD')

        # Should log info about no PORRoot paths
        self.assertIn('No PORRoot paths found', output.getvalue())
        # Should return early without errors
        self.assertEqual(len(obj.result), 0)

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_with_porroot(self):
        # Test successful PORRoot extraction (lines 276, 278)
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\nvl_nps\\MPtest" Rev="RevA" Patch="p1">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            paths = obj.parse_mconfig_porroot('module.mconfig')

        # Should log info about found PORRoot
        self.assertIn('Found PORRoot in mconfig', output.getvalue())
        # Should return the path
        self.assertEqual(len(paths), 1)
        full_paths = [p['full_path'] for p in paths]
        self.assertIn('I:/hdmxpats/nvl_nps/MPtest/RevA/p1', full_paths)

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_error(self):
        # Test error handling when parsing mconfig fails (line 280, 283)
        File('bad_mconfig.xml').touch('Invalid XML Content {{', mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            paths = obj.parse_mconfig_porroot('bad_mconfig.xml')

        # Should log error about parsing
        self.assertIn('Error parsing mconfig file', output.getvalue())
        # Should return empty list
        self.assertEqual(len(paths), 0)

    @with_(TempDir, chdir=True)
    def test_check_ahmt_bins_no_subbindef(self):
        # Test when SubBindef file is not found during check (lines 69-71)
        mtpl_content = '''
SetBin SoftBins.b90440101_fail_MODULE_TEST;
'''
        File('Modules/TEST_AHMT/test.mtpl').touch(mtpl_content, mkdir=True)
        # Create the non-AHMT directory but without .sbdefs file
        File('Modules/TEST/.placeholder').touch('', mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        # Call check with a path that has no sbdefs file
        obj.check_ahmt_bins_in_subbindef(
            'Modules/TEST_AHMT/test.mtpl',
            'Modules/TEST_AHMT/',
            'Modules/TEST/',
            'TEST_AHMT'
        )

        # Should add error 290 about SubBindef not found
        self.assertEqual(len(obj.result), 1)
        self.assertEqual(obj.result[0]['id'], 290)
        self.assertIn('SubBindef file not found', obj.result[0]['message'])

    @with_(TempDir, chdir=True)
    def test_check_ahmt_bins_nonexistent_porpath(self):
        # Test when non-AHMT counterpart directory doesn't exist
        mtpl_content = '''
SetBin SoftBins.b90440101_fail_MODULE_TEST;
'''
        File('Modules/TEST_AHMT/test.mtpl').touch(mtpl_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            # Call check with a path that doesn't exist
            obj.check_ahmt_bins_in_subbindef(
                'Modules/TEST_AHMT/test.mtpl',
                'Modules/TEST_AHMT/',
                'Modules/NONEXISTENT/',
                'TEST_AHMT'
            )

        # Should log info and skip gracefully without adding errors
        self.assertEqual(len(obj.result), 0)
        self.assertIn('Non-AHMT counterpart directory does not exist', output.getvalue())
        self.assertIn('Skipping SubBindef check', output.getvalue())

    @with_(TempDir, chdir=True)
    def test_check_porroot_env_file_missing_section(self):
        # Test when env file is missing TORCH_AUTO sections (line 291)
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\test" Rev="RevA" Patch="p1">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('test_dir/module.mconfig').touch(mconfig_content, mkdir=True)

        env_content = '''Version 1.0;
# No TORCH_AUTO sections
'''
        File('test.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'test.env'
        obj = AHMTCheck(tpobj)

        obj.check_porroot_in_envfile('test_dir/', 'TEST_MOD')

        # Should add error 291 about TORCH_AUTO section not found
        self.assertEqual(len(obj.result), 1)
        self.assertEqual(obj.result[0]['id'], 291)
        self.assertIn('TORCH_AUTO_PLIST_PATH section not found', obj.result[0]['message'])

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_partial_porroot(self):
        # Test PORRoot with only Path and Rev (no Patch) - covers lines 276, 278
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\test" Rev="RevA" Patch="">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            paths = obj.parse_mconfig_porroot('module.mconfig')

        # Should create path without patch
        self.assertEqual(len(paths), 1)
        full_paths = [p['full_path'] for p in paths]
        self.assertIn('I:/hdmxpats/test/RevA', full_paths)

    @with_(TempDir, chdir=True)
    def test_comprehensive_line_coverage(self):
        # Comprehensive test to ensure specific lines are covered: 38, 144, 186, 191, 276, 278, 280, 283
        # Line 38: if 'AHMT' in modfolder - covered by calling main() with AHMT folder
        # Line 144: 7-digit bin not part of 8-digit
        # Lines 186, 191: LeafBin parsing with valid bins
        # Lines 276, 278, 280, 283: PORRoot path building

        # Create AHMT module with bins
        mtpl_content = '''
SetBin SoftBins.b90440101_fail_MODULE_TEST;
SetBin SoftBins.b8765432_fail_STANDALONE;
'''
        File('Modules/TEST/TESTAHMT_MOD/test.mtpl').touch(mtpl_content, mkdir=True)

        sbdefs_content = '''
Version 1.0;
SubBinDefs
{
    BinGroup SoftBins
    {
        LeafBin b90440101_fail_TEST    90440101    : "b90440101_fail_TEST",    b44_FAIL;
        LeafBin b8765432_fail_STANDALONE   8765432    : "b8765432_fail_STANDALONE",   b87_FAIL;
    }
}
'''
        File('Modules/TEST/TEST_MOD/test.sbdefs').touch(sbdefs_content, mkdir=True)

        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\test" Rev="RevA" Patch="p1">
            <PlistFiles>
                <PlistFile>test.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
</ModuleConfiguration>
'''
        File('Modules/TEST/TESTAHMT_MOD/module.mconfig').touch(mconfig_content, mkdir=True)

        env_content = '''Version 1.0;

TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/test/RevA/p1/plb;" +
    "I:/hdmxpats/test/RevA/p1/pat;" +
    "I:/hdmxpats/test/RevA/p0/pat;" +
    $TORCH_AUTO_PLIST_PATH;
'''
        File('POR_TP/CLASS_AHMT/EnvironmentFile.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envdir = 'POR_TP/CLASS_AHMT'
        tpobj.envfile = 'POR_TP/CLASS_AHMT/EnvironmentFile.env'
        tpobj.mtpl = Mock()
        tpobj.mtpl.get_mod2fname = Mock(return_value={
            'TEST': 'Modules/TEST/TESTAHMT_MOD/test.mtpl'
        })

        obj = AHMTCheck(tpobj)
        with CaptureStdoutLog():
            obj.main()

        # Should have passes for both checks
        self.assertEqual(len(obj.result), 0)

    @with_(TempDir, chdir=True)
    def test_main_with_non_ahmt_modules(self):
        # Test line 38 FALSE case - module without AHMT in folder name
        # Create both AHMT and non-AHMT modules
        File('Modules/TEST/TESTAHMT_MOD/test_ahmt.mtpl').touch('SetBin SoftBins.b90440101_fail_TEST;', mkdir=True)
        File('Modules/TEST/REGULAR_MOD/test_regular.mtpl').touch('SetBin SoftBins.b90440102_fail_TEST;', mkdir=True)

        tpobj = Mock()
        tpobj.envdir = 'POR_TP/CLASS_AHMT'
        tpobj.mtpl = Mock()
        tpobj.mtpl.get_mod2fname = Mock(return_value={
            'TEST_AHMT': 'Modules/TEST/TESTAHMT_MOD/test_ahmt.mtpl',
            'TEST_REGULAR': 'Modules/TEST/REGULAR_MOD/test_regular.mtpl'
        })

        obj = AHMTCheck(tpobj)
        with CaptureStdoutLog():
            obj.main()

        # Should only process the AHMT module, skip the regular one

    @with_(TempDir, chdir=True)
    def test_7digit_bin_already_in_8digit(self):
        # Test line 144 FALSE case - 7-digit bin that IS part of 8-digit bin
        mtpl_content = '''
SetBin SoftBins.b90440101_fail_MODULE_TEST;
SetBin SoftBins.b9044010_fail_PARTIAL;
'''
        File('test.mtpl').touch(mtpl_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        bins = obj.extract_setbin_from_mtpl('test.mtpl')

        # Should only have the 8-digit bin, not the 7-digit substring
        self.assertIn('90440101', bins)
        # The 7-digit 9044010 should NOT be added because it's part of 90440101
        self.assertNotIn('9044010', bins)

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_alephfiles_valid(self):
        # Test parsing AlephFile elements from valid module.mconfig
        mconfig_content = '''<?xml version="1.0" encoding="utf-8"?>
<TestProgramSettings>
    <AlephFiles>
        <AlephFile>InputFiles/mio.nvlhub.reset.patmod.json</AlephFile>
        <AlephFile>InputFiles/test.patmod.json</AlephFile>
    </AlephFiles>
</TestProgramSettings>
'''
        File('module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog():
            alephfiles = obj.parse_mconfig_alephfiles('module.mconfig')

        self.assertEqual(len(alephfiles), 2)
        self.assertIn('InputFiles/mio.nvlhub.reset.patmod.json', alephfiles)
        self.assertIn('InputFiles/test.patmod.json', alephfiles)

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_alephfiles_no_alephfiles(self):
        # Test parsing module.mconfig with no AlephFiles section
        mconfig_content = '''<?xml version="1.0" encoding="utf-8"?>
<TestProgramSettings>
    <Patterns>
        <PORRoot Path="I:/hdmxpats" Rev="main" Patch="release"/>
    </Patterns>
</TestProgramSettings>
'''
        File('module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog():
            alephfiles = obj.parse_mconfig_alephfiles('module.mconfig')

        self.assertEqual(len(alephfiles), 0)

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_alephfiles_empty_elements(self):
        # Test parsing module.mconfig with empty AlephFile elements
        mconfig_content = '''<?xml version="1.0" encoding="utf-8"?>
<TestProgramSettings>
    <AlephFiles>
        <AlephFile>InputFiles/valid.json</AlephFile>
        <AlephFile>   </AlephFile>
        <AlephFile></AlephFile>
    </AlephFiles>
</TestProgramSettings>
'''
        File('module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog():
            alephfiles = obj.parse_mconfig_alephfiles('module.mconfig')

        # Should only get the valid one, empty ones should be filtered out
        self.assertEqual(len(alephfiles), 1)
        self.assertIn('InputFiles/valid.json', alephfiles)

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_alephfiles_parse_error(self):
        # Test parsing invalid XML
        mconfig_content = '''<?xml version="1.0" encoding="utf-8"?>
<TestProgramSettings>
    <AlephFiles>
        <AlephFile>InputFiles/test.json</AlephFile>
    <!-- Missing closing tag
</TestProgramSettings>
'''
        File('module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            alephfiles = obj.parse_mconfig_alephfiles('module.mconfig')

        # Should return empty list and log error
        self.assertEqual(len(alephfiles), 0)
        self.assertIn('-e- Error parsing mconfig file', output.getvalue())

    @with_(TempDir, chdir=True)
    def test_parse_mconfig_alephfiles_file_not_found(self):
        # Test when mconfig file doesn't exist (lines 374-376)
        tpobj = Mock()
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            alephfiles = obj.parse_mconfig_alephfiles('nonexistent_mconfig.xml')

        # Should log error about file not existing
        self.assertIn('mconfig file does not exist', output.getvalue())
        # Should return empty list
        self.assertEqual(len(alephfiles), 0)

    @with_(TempDir, chdir=True)
    def test_check_alephfiles_in_envfile_found(self):
        # Test checking AlephFiles that exist in env file
        mconfig_content = '''<?xml version="1.0" encoding="utf-8"?>
<TestProgramSettings>
    <AlephFiles>
        <AlephFile>InputFiles/mio.nvlhub.reset.patmod.json</AlephFile>
    </AlephFiles>
</TestProgramSettings>
'''
        env_content = '''Version 1.0;

TORCH_AUTO_ALEPH_FILES =
    "$MHDRV_PATMODIFY_PATH/merged_allplist_IPH_patmod.json;" +
    "~HDMT_TP_BASE_DIR/Modules/MIO_DDR/MIO_DDR5ACAHMT_HXNVL/InputFiles/mio.nvlhub.reset.patmod.json;" +
    $TORCH_AUTO_ALEPH_FILES;
'''
        File('Modules/TEST/TESTAHMT_MODULE/module.mconfig').touch(mconfig_content, mkdir=True)
        File('test.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'test.env'
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            obj.check_alephfiles_in_envfile('Modules/TEST/TESTAHMT_MODULE/', 'TESTAHMT_MODULE')

        # Should find the AlephFile in env and pass
        self.assertIn('AlephFile "InputFiles/mio.nvlhub.reset.patmod.json" from TESTAHMT_MODULE found in env file', output.getvalue())
        self.assertEqual(obj.passed[(292, 'TESTAHMT_MODULE')], 1)
        self.assertEqual(len(obj.result), 0)  # No errors

    @with_(TempDir, chdir=True)
    def test_check_alephfiles_in_envfile_not_found(self):
        # Test checking AlephFiles that don't exist in env file
        mconfig_content = '''<?xml version="1.0" encoding="utf-8"?>
<TestProgramSettings>
    <AlephFiles>
        <AlephFile>InputFiles/missing.patmod.json</AlephFile>
    </AlephFiles>
</TestProgramSettings>
'''
        env_content = '''Version 1.0;

TORCH_AUTO_ALEPH_FILES =
    "$MHDRV_PATMODIFY_PATH/merged_allplist_IPH_patmod.json;" +
    $TORCH_AUTO_ALEPH_FILES;
'''
        File('Modules/TEST/TESTAHMT_MODULE/module.mconfig').touch(mconfig_content, mkdir=True)
        File('test.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'test.env'
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            obj.check_alephfiles_in_envfile('Modules/TEST/TESTAHMT_MODULE/', 'TESTAHMT_MODULE')

        # Should not find the AlephFile and error
        self.assertIn('AlephFile "InputFiles/missing.patmod.json" from TESTAHMT_MODULE not found in env file', output.getvalue())
        self.assertEqual(len([r for r in obj.result if r['id'] == 292]), 1)
        self.assertIn('not found in env file', obj.result[0]['message'])

    @with_(TempDir, chdir=True)
    def test_check_alephfiles_in_envfile_multiple(self):
        # Test checking multiple AlephFiles
        mconfig_content = '''<?xml version="1.0" encoding="utf-8"?>
<TestProgramSettings>
    <AlephFiles>
        <AlephFile>InputFiles/file1.json</AlephFile>
        <AlephFile>InputFiles/file2.json</AlephFile>
        <AlephFile>InputFiles/missing.json</AlephFile>
    </AlephFiles>
</TestProgramSettings>
'''
        env_content = '''Version 1.0;

TORCH_AUTO_ALEPH_FILES =
    "~HDMT_TP_BASE_DIR/Modules/TEST/TESTAHMT_MODULE/InputFiles/file1.json;" +
    "~HDMT_TP_BASE_DIR/Modules/TEST/TESTAHMT_MODULE/InputFiles/file2.json;" +
    $TORCH_AUTO_ALEPH_FILES;
'''
        File('Modules/TEST/TESTAHMT_MODULE/module.mconfig').touch(mconfig_content, mkdir=True)
        File('test.env').touch(env_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'test.env'
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            obj.check_alephfiles_in_envfile('Modules/TEST/TESTAHMT_MODULE/', 'TESTAHMT_MODULE')

        # Should find 2 and miss 1
        self.assertEqual(obj.passed[(292, 'TESTAHMT_MODULE')], 2)
        self.assertEqual(len([r for r in obj.result if r['id'] == 292]), 1)  # 1 error

    @with_(TempDir, chdir=True)
    def test_check_alephfiles_in_envfile_no_mconfig(self):
        # Test when module.mconfig doesn't exist
        File('test.env').touch('Version 1.0;', mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'test.env'
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            obj.check_alephfiles_in_envfile('Modules/TEST/TESTAHMT_MODULE/', 'TESTAHMT_MODULE')

        # Should log error about missing mconfig
        self.assertIn('-e- module.mconfig not found', output.getvalue())

    @with_(TempDir, chdir=True)
    def test_check_alephfiles_in_envfile_no_alephfiles_in_mconfig(self):
        # Test when module.mconfig has no AlephFile elements
        mconfig_content = '''<?xml version="1.0" encoding="utf-8"?>
<TestProgramSettings>
    <Patterns>
        <PORRoot Path="I:/hdmxpats" Rev="main" Patch="release"/>
    </Patterns>
</TestProgramSettings>
'''
        File('Modules/TEST/TESTAHMT_MODULE/module.mconfig').touch(mconfig_content, mkdir=True)
        File('test.env').touch('Version 1.0;', mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'test.env'
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            obj.check_alephfiles_in_envfile('Modules/TEST/TESTAHMT_MODULE/', 'TESTAHMT_MODULE')

        # Should log info about no AlephFile elements found
        self.assertIn('-i- No AlephFile elements found', output.getvalue())

    @with_(TempDir, chdir=True)
    def test_check_alephfiles_in_envfile_env_read_error(self):
        # Test when env file can't be read
        mconfig_content = '''<?xml version="1.0" encoding="utf-8"?>
<TestProgramSettings>
    <AlephFiles>
        <AlephFile>InputFiles/test.json</AlephFile>
    </AlephFiles>
</TestProgramSettings>
'''
        File('Modules/TEST/TESTAHMT_MODULE/module.mconfig').touch(mconfig_content, mkdir=True)

        tpobj = Mock()
        tpobj.envfile = 'nonexistent.env'
        obj = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            obj.check_alephfiles_in_envfile('Modules/TEST/TESTAHMT_MODULE/', 'TESTAHMT_MODULE')

        # Should log error about reading env file
        self.assertIn('-e- Environment file does not exist', output.getvalue())

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_all_checks_pass_with_real_tp(self):
        # Integration test with a real simple TP where all 3 checks pass
        # Create AHMT module structure
        mtpl_content = '''
TestFlow test_flow;
SetBin SoftBins.b90440101_fail_MODULE_TEST;
SetBin SoftBins.b90440102_fail_MODULE_TEST2;
'''
        File('Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL/MIO_DDR5DC_HXNVL.mtpl').touch(mtpl_content, mkdir=True)

        # Create non-AHMT SubBindef with matching bins
        sbdefs_content = '''
Version 1.0;
SubBinDefs
{
    BinGroup SoftBins
    {
        LeafBin b90440101_fail_TEST    90440101    : "b90440101_fail_TEST",    b44_FAIL;
        LeafBin b90440102_fail_TEST2   90440102    : "b90440102_fail_TEST2",   b44_FAIL;
        LeafBin b90440103_fail_TEST3   90440103    : "b90440103_fail_TEST3",   b44_FAIL;
    }
}
'''
        File('Modules/MIO_DDR/MIO_DDR5DC_HXNVL/MIO_DDR5DC_HXNVL_SubBinDefinitions.sbdefs').touch(sbdefs_content, mkdir=True)

        # Create mconfig with PORRoot and AlephFile
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<TestProgramSettings>
    <ModuleConfiguration>
        <Patterns>
            <PORRoot Path="I:\\hdmxpats\\nvl_hub\\MHmioDDR" Rev="RevTHHXXA0.0" Patch="p18">
                <PlistFiles>
                    <PlistFile>test.plist</PlistFile>
                </PlistFiles>
            </PORRoot>
        </Patterns>
    </ModuleConfiguration>
    <AlephFiles>
        <AlephFile>InputFiles/mio.nvlhub.reset.patmod.json</AlephFile>
    </AlephFiles>
</TestProgramSettings>
'''
        File('Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL/module.mconfig').touch(mconfig_content, mkdir=True)

        # Append to existing environment file with matching TORCH_AUTO paths and AlephFile
        env_append = '''
TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p18/plb;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p18/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p17/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p16/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p15/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p14/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p13/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p12/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p11/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p10/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p9/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p8/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p7/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p6/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p5/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p4/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p3/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p2/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p1/pat;" +
    "I:/hdmxpats/nvl_hub/MHmioDDR/RevTHHXXA0.0/p0/pat;" +
    $TORCH_AUTO_PLIST_PATH;

TORCH_AUTO_ALEPH_FILES =
    "$MHDRV_PATMODIFY_PATH/merged_allplist_IPH_patmod.json;" +
    "~HDMT_TP_BASE_DIR/Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL/InputFiles/mio.nvlhub.reset.patmod.json;" +
    $TORCH_AUTO_ALEPH_FILES;
'''
        # Append to existing env file
        env_file = File('POR_TP/TGLH81/EnvironmentFile.env')
        existing_content = env_file.read()
        env_file.touch(existing_content + env_append)

        # Create TestProgram object
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()

        # Add AHMT module to tpobj manually
        with MockVar(tpobj.mtpl, 'get_mod2fname', Mock(return_value={
            'MIO_DDR5DC_HXNVL': 'Modules/MIO_DDR/MIO_DDR5DCAHMT_HXNVL/MIO_DDR5DC_HXNVL.mtpl'
        })):
            # Run the checker
            obj = AHMTCheck(tpobj)
            obj.main()

            # Verify all 3 checks passed
            self.assertEqual(len(obj.result), 0, f'Expected no errors but got: {obj.result}')
            # Check that we have passes for all 3 error codes
            module_passes = [k for k in obj.passed.keys() if k[1] == 'MIO_DDR5DCAHMT_HXNVL']
            self.assertEqual(len(module_passes), 3, f'Expected 3 passes but got {len(module_passes)}: {module_passes}')
            # Verify specific error codes passed
            self.assertEqual(obj.passed[(290, 'MIO_DDR5DCAHMT_HXNVL')], 1)  # AHMT bins check
            self.assertEqual(obj.passed[(291, 'MIO_DDR5DCAHMT_HXNVL')], 1)  # PORRoot check
            self.assertEqual(obj.passed[(292, 'MIO_DDR5DCAHMT_HXNVL')], 1)  # AlephFiles check

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_all_checks_fail_with_real_tp(self):
        # Integration test with a real simple TP where all 3 checks fail
        # Create AHMT module structure with bins that won't exist in SubBindef
        mtpl_content = '''
TestFlow test_flow;
SetBin SoftBins.b90440199_fail_MISSING;
SetBin SoftBins.b90440299_fail_MISSING2;
SetBin SoftBins.b90440399_fail_MISSING3;
'''
        File('Modules/CLK/CLK_ISCLKAHMT_PXS/CLK_ISCLK_PXS.mtpl').touch(mtpl_content, mkdir=True)

        # Create non-AHMT SubBindef WITHOUT the bins from AHMT
        sbdefs_content = '''
Version 1.0;
SubBinDefs
{
    BinGroup SoftBins
    {
        LeafBin b90440101_fail_TEST    90440101    : "b90440101_fail_TEST",    b44_FAIL;
        LeafBin b90440102_fail_TEST2   90440102    : "b90440102_fail_TEST2",   b44_FAIL;
    }
}
'''
        File('Modules/CLK/CLK_ISCLK_PXS/CLK_ISCLK_PXS_SubBinDefinitions.sbdefs').touch(sbdefs_content, mkdir=True)

        # Create mconfig with PORRoot and AlephFile that won't be in env
        mconfig_content = '''<?xml version="1.0" encoding="utf-8" ?>
<TestProgramSettings>
    <ModuleConfiguration>
        <Patterns>
            <PORRoot Path="I:\\hdmxpats\\nvl_nps\\MPclkMISSING" Rev="RevTPC4A0.1" Patch="p99">
                <PlistFiles>
                    <PlistFile>test.plist</PlistFile>
                </PlistFiles>
            </PORRoot>
        </Patterns>
    </ModuleConfiguration>
    <AlephFiles>
        <AlephFile>InputFiles/missing.aleph.file.json</AlephFile>
    </AlephFiles>
</TestProgramSettings>
'''
        File('Modules/CLK/CLK_ISCLKAHMT_PXS/module.mconfig').touch(mconfig_content, mkdir=True)

        # Append to environment file WITHOUT the required paths and AlephFile
        env_append = '''
TORCH_AUTO_PLIST_PATH =
    "I:/hdmxpats/nvl_nps/MPclkDIFFERENT/RevTPC4A0.1/p8/plb;" +
    "I:/hdmxpats/nvl_nps/MPclkDIFFERENT/RevTPC4A0.1/p8/pat;" +
    "I:/hdmxpats/nvl_nps/MPclkDIFFERENT/RevTPC4A0.1/p7/pat;" +
    $TORCH_AUTO_PLIST_PATH;

TORCH_AUTO_ALEPH_FILES =
    "$MHDRV_PATMODIFY_PATH/merged_allplist_IPH_patmod.json;" +
    "~HDMT_TP_BASE_DIR/Modules/OTHER/file.json;" +
    $TORCH_AUTO_ALEPH_FILES;
'''
        # Append to existing env file
        env_file = File('POR_TP/TGLH81/EnvironmentFile.env')
        existing_content = env_file.read()
        env_file.touch(existing_content + env_append)

        # Create TestProgram object
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()

        # Add AHMT module to tpobj manually
        with MockVar(tpobj.mtpl, 'get_mod2fname', Mock(return_value={
            'CLK_ISCLK_PXS': 'Modules/CLK/CLK_ISCLKAHMT_PXS/CLK_ISCLK_PXS.mtpl'
        })):
            # Run the checker
            obj = AHMTCheck(tpobj)
            obj.main()

            missing_porroot = ['I:/hdmxpats/nvl_nps/MPclkMISSING/RevTPC4A0.1/p99/plb']
            missing_porroot.extend(
                [f'I:/hdmxpats/nvl_nps/MPclkMISSING/RevTPC4A0.1/p{i}/pat' for i in range(99, -1, -1)]
            )
            missing_porroot_str = ', '.join(missing_porroot)

            expect = f'''
290 CLK_ISCLKAHMT_PXS AHMT bins missing in non-AHMT SubBindef: 90440199, 90440299, 90440399
291 CLK_ISCLKAHMT_PXS PORRoot paths missing in TORCH_AUTO_PLIST_PATH: {missing_porroot_str}
292 CLK_ISCLKAHMT_PXS AlephFile "InputFiles/missing.aleph.file.json" not found in env file
'''
            self.assertTextEqual(obj.ut_result(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True, delete=True)
    def test_no_ahmt_modules_in_tp(self):
        # Test when TP has no AHMT modules - checker should run without errors
        # SimpleNVL by default has no AHMT modules, just use it as-is

        # Initialize test program
        tpobj = TestProgram('POR_TP/TGLH81/EnvironmentFile.env').init()

        # Create checker and run
        checker = AHMTCheck(tpobj)

        with CaptureStdoutLog() as output:
            checker.run()

        # Verify no errors were added (no AHMT modules to check)
        self.assertEqual(len(checker.result), 0, f'Expected no errors but got: {checker.result}')

        # Verify no passes were added (no AHMT modules to pass)
        self.assertEqual(len(checker.passed), 0, f'Expected no passes but got: {checker.passed}')

        # Verify the checker ran successfully without exceptions
        self.assertIn('Success! no errors', output.getvalue())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
