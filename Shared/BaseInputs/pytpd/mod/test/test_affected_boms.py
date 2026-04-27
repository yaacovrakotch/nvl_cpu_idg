#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for affected_boms
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, Mock, is_ut_option
from gadget.files import TempDir
from gadget.disk import mkdirs
from gadget.gizmo import MockVar, with_
from gadget.errors import ErrorInput
from mod.affected_boms import *
import shutil
import json


class TestAB(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL2', chdir=True)
    def test_tpproj_read(self):
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=[])):
            result = AffectedBom()._read_stpl('TGLH81')
        self.assertEqual(len(result), 62)

    @with_(TempDir, chdir=True)
    @with_(MockVar, GitHub, 'get_modfiles', Mock(return_value=[]))
    def test_tpproj_or_stpl(self):
        # common
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
    "../../Modules/TPI/ARR_CORE/blah.mtpl";
''', mkdir=True)

        File('POR_TP/TGLR20/subtestplan.stpl').touch('''
    "../../Modules/TPI/ARR_CORE/blah.mtpl";
''', mkdir=True)

        result = AffectedBom()._read_stpl('TGLR20')
        self.assertEqual(len(result), 1)

        # dielet
        mkdirs('Shared')
        result = AffectedBom()._read_stpl('TGLR20')
        self.assertEqual(len(result), 2)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_1bom(self):

        # module that is dont care
        mfiles_no = ['Modules/PTHXX/pth.mtpl', 'Modules/ARRXX/arr.mtpl']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_no)):
            self.assertEqual(AffectedBom().main(), [])

        # modified Module
        mfiles_yes = ['Modules/PTH/pth.mtpl', 'Modules/ARRXX/arr.mtpl']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_no + mfiles_yes)):
            self.assertEqual(AffectedBom().main(), ['TGLH81'])
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_yes)):
            self.assertEqual(AffectedBom().main(), ['TGLH81'])

        # modified common
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=['BaseInputs/CPU/CPU_TGLH81/blah'])):
            self.assertEqual(AffectedBom().main(), ['TGLH81'])

        # special files
        mfiles = ['Modules/PTHXX/pth.mtpl', '.github/workflows', 'TPConfig/MV_Templates', 'Shared']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            self.assertEqual(AffectedBom().main(), [])

        # catch all
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles + ['something/blah.txt'])):
            self.assertEqual(AffectedBom().main(), ['TGLH81'])

        # empty modified files
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=[])):
            self.assertEqual(AffectedBom().main(), ['TGLH81'])

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_2bom(self):
        shutil.copytree('POR_TP/TGLH81', 'POR_TP/TGLR20')
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
Version 1.0;

SubTestPlans
{
        "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
        "../../Modules/TPI/ARR_CORE/blah.mtpl";
        "../../Modules/TPI/SCN_CORE/blah.mtpl";
}
''', newfile=True)

        # module that is dont care
        mfiles_no = ['Modules/PTHXX/pth.mtpl', 'Modules/ARRXX/arr.mtpl']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_no)):
            self.assertEqual(AffectedBom().main(), [])

        # modified Module both BOM
        mfiles_yes = ['Modules/PTH/pth.mtpl', 'Modules/TPI/ARR_CORE/blah.mtpl']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_no + mfiles_yes)):
            self.assertEqual(AffectedBom().main(), ['TGLH81', 'TGLR20'])

        # modified one bom only
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_no + ['Modules/TPI/ARR_CORE/blah.mtpl'])):
            self.assertEqual(AffectedBom().main(), ['TGLR20'])

        # Empty
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=[])):
            self.assertEqual(AffectedBom().main(), ['TGLH81', 'TGLR20'])

        # SubModule
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=['Modules/TPI'])):
            self.assertEqual(AffectedBom().main(), ['TGLR20'])

        # .github plus POR_TP
        mfiles = ['.github/workflows/TPBot_Schedule.yml', 'POR_TP/TGLH81/something.bat', 'BaseInputs/Common/Common_TGLH81/blah.txt']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            self.assertEqual(AffectedBom().main(), ['TGLH81'])

        # .github plus POR_TP
        mfiles = ['.github/workflows/TPBot_Schedule.yml', 'BaseInputs/Common/Common_Torch/blah.txt']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            self.assertEqual(AffectedBom().main(), ['TGLH81', 'TGLR20'])

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_common(self):
        shutil.rmtree('Shared')
        shutil.copytree('POR_TP/TGLH81', 'POR_TP/TGLR20')
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
Version 1.0;

SubTestPlans
{
        "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
        "../../Modules/TPI/ARR_CORE/blah.mtpl";
        "../../Modules/TPI/SCN_CORE/blah.mtpl";
}
''', newfile=True)

        # module that is dont care
        mfiles_no = ['Modules/PTHXX/pth.mtpl', 'Modules/ARRXX/arr.mtpl']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_no)):
            self.assertEqual(AffectedBom().main(), ['TGLH81', 'TGLR20'])
            mkdirs('Shared')
            self.assertEqual(AffectedBom().main(), [])


class TestAffectedBomsJson(TestCase):

    @with_(TempDir, chdir=True)
    @with_(MockVar, GitHub, 'get_modfiles', Mock(return_value=[]))
    def test_json_file_loading(self):
        # Test loading of JSON file
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        File('POR_TP/TGLR20/subtestplan.stpl').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        # Create a valid JSON file
        json_content = {
            "InputFiles/.*\\.csv": "TGLR20",
            "patterns/.*": "TGL.*"
        }
        File('Modules/TPI/ARR_COMMON_CKX/affected_boms.json').touch(
            json.dumps(json_content), mkdir=True)

        ab = AffectedBom()
        mappings = ab._load_json_mappings('Modules/TPI/ARR_COMMON_CKX/')
        self.assertEqual(mappings, json_content)

    @with_(TempDir, chdir=True)
    @with_(MockVar, GitHub, 'get_modfiles', Mock(return_value=[]))
    def test_json_file_missing(self):
        # Test that missing JSON file doesn't cause error
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        ab = AffectedBom()
        mappings = ab._load_json_mappings('Modules/TPI/ARR_COMMON_CKX/')
        self.assertEqual(mappings, {})

    @with_(TempDir, chdir=True)
    @with_(MockVar, GitHub, 'get_modfiles', Mock(return_value=[]))
    def test_json_file_invalid_format(self):
        # Test invalid JSON format
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        # Create an invalid JSON (list instead of dict)
        File('Modules/TPI/ARR_COMMON_CKX/affected_boms.json').touch(
            '["not", "a", "dict"]', mkdir=True)

        ab = AffectedBom()
        mappings = ab._load_json_mappings('Modules/TPI/ARR_COMMON_CKX/')
        self.assertEqual(mappings, {})

    @with_(TempDir, chdir=True)
    @with_(MockVar, GitHub, 'get_modfiles', Mock(return_value=[]))
    def test_json_file_malformed(self):
        # Test malformed JSON - should raise error
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        # Create malformed JSON
        File('Modules/TPI/ARR_COMMON_CKX/affected_boms.json').touch(
            '{invalid json}', mkdir=True)

        ab = AffectedBom()
        # Should raise ErrorInput exception due to malformed JSON
        with self.assertRaises(ErrorInput):
            ab._load_json_mappings('Modules/TPI/ARR_COMMON_CKX/')

    @with_(TempDir, chdir=True)
    @with_(MockVar, GitHub, 'get_modfiles', Mock(return_value=[]))
    def test_json_file_empty(self):
        # Test empty JSON file
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        File('Modules/TPI/ARR_COMMON_CKX/affected_boms.json').touch(
            '{}', mkdir=True)

        ab = AffectedBom()
        mappings = ab._load_json_mappings('Modules/TPI/ARR_COMMON_CKX/')
        self.assertEqual(mappings, {})

    @with_(TempDir, chdir=True)
    @with_(MockVar, GitHub, 'get_modfiles', Mock(return_value=[]))
    def test_json_caching(self):
        # Test that JSON files are cached
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        json_content = {"pattern": "bom"}
        File('Modules/TPI/ARR_COMMON_CKX/affected_boms.json').touch(
            json.dumps(json_content), mkdir=True)

        ab = AffectedBom()
        mappings1 = ab._load_json_mappings('Modules/TPI/ARR_COMMON_CKX/')
        mappings2 = ab._load_json_mappings('Modules/TPI/ARR_COMMON_CKX/')

        # Should get same object from cache
        self.assertEqual(mappings1, mappings2)
        self.assertTrue('Modules/TPI/ARR_COMMON_CKX/' in ab.json_mappings_cache)

    @with_(TempDir, chdir=True)
    @with_(MockVar, GitHub, 'get_modfiles', Mock(return_value=[]))
    def test_check_json_mapping_exact_match(self):
        # Test exact string matching for paths and BOMs
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        json_content = {
            "InputFiles/data.csv": "TGLR20"
        }
        File('Modules/TPI/ARR_COMMON_CKX/affected_boms.json').touch(
            json.dumps(json_content), mkdir=True)

        # Should match: file in subfolder with exact BOM match
        mfiles = ['Modules/TPI/ARR_COMMON_CKX/InputFiles/data.csv']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            ab = AffectedBom()
            self.assertTrue(ab._check_json_mapping('TGLR20'))

        # Should not match: different BOM
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            ab = AffectedBom()
            self.assertFalse(ab._check_json_mapping('TGLH81'))

        # Should not match: file in immediate folder (not subfolder)
        mfiles_immediate = ['Modules/TPI/ARR_COMMON_CKX/file.txt']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_immediate)):
            ab = AffectedBom()
            self.assertFalse(ab._check_json_mapping('TGLR20'))

    @with_(TempDir, chdir=True)
    @with_(MockVar, GitHub, 'get_modfiles', Mock(return_value=[]))
    def test_check_json_mapping_regex_match(self):
        # Test regex matching for paths and BOMs
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        json_content = {
            "InputFiles/.*\\.csv": "TGL.*"
        }
        File('Modules/TPI/ARR_COMMON_CKX/affected_boms.json').touch(
            json.dumps(json_content), mkdir=True)

        # Should match: regex pattern for both path and BOM
        mfiles = ['Modules/TPI/ARR_COMMON_CKX/InputFiles/test.csv']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            ab = AffectedBom()
            self.assertTrue(ab._check_json_mapping('TGLR20'))

        mfiles2 = ['Modules/TPI/ARR_COMMON_CKX/InputFiles/another.csv']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles2)):
            ab = AffectedBom()
            self.assertTrue(ab._check_json_mapping('TGLH81'))

        # Should not match: path doesn't match pattern
        mfiles_no_match = ['Modules/TPI/ARR_COMMON_CKX/InputFiles/test.txt']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_no_match)):
            ab = AffectedBom()
            self.assertFalse(ab._check_json_mapping('TGLR20'))

    @with_(TempDir, chdir=True)
    @with_(MockVar, GitHub, 'get_modfiles', Mock(return_value=[]))
    def test_check_json_mapping_subfolder_restriction(self):
        # Test that JSON only affects subfolders, not immediate folder
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        json_content = {
            ".*\\.csv": "TGLR20"
        }
        File('Modules/TPI/ARR_COMMON_CKX/affected_boms.json').touch(
            json.dumps(json_content), mkdir=True)

        # Should match: file in subfolder
        mfiles = ['Modules/TPI/ARR_COMMON_CKX/subfolder/file.csv']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            ab = AffectedBom()
            self.assertTrue(ab._check_json_mapping('TGLR20'))

        # Should not match: file in immediate folder
        mfiles_immediate = ['Modules/TPI/ARR_COMMON_CKX/file.csv']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_immediate)):
            ab = AffectedBom()
            self.assertFalse(ab._check_json_mapping('TGLR20'))

        # Should not match: file outside module folder
        mfiles_outside = ['Modules/OTHER/file.csv']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles_outside)):
            ab = AffectedBom()
            self.assertFalse(ab._check_json_mapping('TGLR20'))

    @with_(TempDir, chdir=True)
    def test_integration_with_json(self):
        # Integration test with JSON mapping
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
Version 1.0;

SubTestPlans
{
        "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
}
''', mkdir=True)

        File('POR_TP/TGLR20/subtestplan.stpl').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        # Create JSON file with mapping
        json_content = {
            "InputFiles/.*\\.csv": "TGLR20"
        }
        File('Modules/TPI/ARR_COMMON_CKX/affected_boms.json').touch(
            json.dumps(json_content), mkdir=True)

        # Test with modified file matching JSON pattern
        mfiles = ['Modules/TPI/ARR_COMMON_CKX/InputFiles/data.csv']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            result = AffectedBom().main()
            self.assertEqual(result, ['TGLR20'])

    @with_(TempDir, chdir=True)
    def test_integration_without_json_match(self):
        # Integration test where modified file matches path_pattern but not bom_pattern
        # File should be handled exclusively by JSON - should NOT affect TGLR20
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
Version 1.0;

SubTestPlans
{
        "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
}
''', mkdir=True)

        File('POR_TP/TGLR20/subtestplan.stpl').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        # Create JSON file that targets TGLH81 specifically
        # Files matching this path_pattern should ONLY affect TGLH81, not TGLR20
        json_content = {
            "InputFiles/.*\\.csv": "TGLH81"
        }
        File('Modules/TPI/ARR_COMMON_CKX/affected_boms.json').touch(
            json.dumps(json_content), mkdir=True)

        # Test with modified file matching JSON pattern but different BOM
        # Should NOT affect TGLR20 because file is handled exclusively by JSON
        mfiles = ['Modules/TPI/ARR_COMMON_CKX/InputFiles/data.csv']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            result = AffectedBom().main()
            # Should be empty - file matches path_pattern but not the bom_pattern for TGLR20
            self.assertEqual(result, [])

    @with_(TempDir, chdir=True)
    def test_backward_compatibility(self):
        # Test that existing behavior is preserved when no JSON exists
        File('POR_TP/TGLR20/TGLH81.tpproj').touch('''
Version 1.0;

SubTestPlans
{
        "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
}
''', mkdir=True)

        File('POR_TP/TGLR20/subtestplan.stpl').touch('''
    "../../Modules/TPI/ARR_COMMON_CKX/ARR_COMMON_CKX.mtpl";
''', mkdir=True)

        # No JSON file created

        # Test with modified file in module
        mfiles = ['Modules/TPI/ARR_COMMON_CKX/file.txt']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            result = AffectedBom().main()
            self.assertEqual(result, ['TGLR20'])

    @with_(TempDir, chdir=True)
    def test_json_exclusive_behavior(self):
        # Test that JSON mapping is exclusive - files matching path_pattern
        # are only handled by JSON logic, not regular logic
        mkdirs('Shared')  # Dielet repo

        # BOM1 and BOM2 both have ARR_TEST module
        File('POR_TP/BOM1/BOM1.tpproj').touch('''
Version 1.0;
SubTestPlans
{
    "../../Modules/TPI/ARR_TEST/ARR_TEST.mtpl";
}
''', mkdir=True)

        File('POR_TP/BOM2/BOM2.tpproj').touch('''
Version 1.0;
SubTestPlans
{
    "../../Modules/TPI/ARR_TEST/ARR_TEST.mtpl";
}
''', mkdir=True)

        # JSON maps InputFiles to BOM2 specifically
        json_content = {
            "InputFiles/.*": "BOM2"
        }
        File('Modules/TPI/ARR_TEST/affected_boms.json').touch(
            json.dumps(json_content), mkdir=True)

        # File in InputFiles should ONLY affect BOM2 (JSON match)
        # BOM1 should NOT be affected even though file is in its module
        # because the file matches a JSON path_pattern (exclusive behavior)
        mfiles = ['Modules/TPI/ARR_TEST/InputFiles/test.csv']
        with MockVar(GitHub, 'get_modfiles', Mock(return_value=mfiles)):
            result = AffectedBom().main()
            self.assertEqual(result, ['BOM2'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
