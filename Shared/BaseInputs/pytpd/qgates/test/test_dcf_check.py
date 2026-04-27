#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Run unittest for dcf_check.py
Checking simple pass and fail cases.

"""
import sys
try:
    from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.dcf_check import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock, patch, mock_open
from gadget.strmore import sha1
import glob
import os


class DCFCheckTest(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic_pass(self):
        # Test when all BOM groups match and SHA1 matches
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # Mock binmatrix_boms to return test data
        binmatrix_data = {
            'BOM_GROUP_A': ['A0', 'B0'],
            'BOM_GROUP_B': ['A0', 'C0']
        }

        # Mock dcf_registry_boms to return matching data
        dcf_registry_data = {
            'BOM_GROUP_A': ['A0', 'B0'],
            'BOM_GROUP_B': ['A0', 'C0']
        }
        dcf_registry_sha = {
            'BOM_GROUP_A': 'abc123def456',
            'BOM_GROUP_B': 'abc123def456'
        }

        # Mock dcf_file to return matching SHA
        dcf_file_data = {
            'file': '/path/to/DieIDBinning.xml',
            'sha1': 'abc123def456'
        }

        with MockVar(dcf_check, 'binmatrix_boms', Mock(return_value=binmatrix_data)), \
                MockVar(dcf_check, 'dcf_registry_boms', Mock(return_value=(dcf_registry_data, dcf_registry_sha))), \
                MockVar(dcf_check, 'dcf_file', Mock(return_value=dcf_file_data)):
            obj.main()
            self.assertEqual(obj.passed, {(276, 'BASE'): 1})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_missing_bom_group(self):
        # Test when BOM group exists in BinMatrix but not in DCF Registry
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # Mock binmatrix_boms to return test data
        binmatrix_data = {
            'BOM_GROUP_A': ['A0', 'B0'],
            'BOM_GROUP_C': ['A0']  # This one is missing from DCF Registry
        }

        # Mock dcf_registry_boms with missing BOM_GROUP_C
        dcf_registry_data = {
            'BOM_GROUP_A': ['A0', 'B0']
        }
        dcf_registry_sha = {
            'BOM_GROUP_A': 'abc123def456'
        }

        # Mock dcf_file
        dcf_file_data = {
            'file': '/path/to/DieIDBinning.xml',
            'sha1': 'abc123def456'
        }

        with MockVar(dcf_check, 'binmatrix_boms', Mock(return_value=binmatrix_data)), \
                MockVar(dcf_check, 'dcf_registry_boms', Mock(return_value=(dcf_registry_data, dcf_registry_sha))), \
                MockVar(dcf_check, 'dcf_file', Mock(return_value=dcf_file_data)):
            obj.main()
            error_message = [
                {'message': 'BOM Group "BOM_GROUP_C" found in BinMatrix but missing in DCF Registry', 'id': 276, 'module': 'BASE'}
            ]
            self.assertEqual(obj.result, error_message)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_missing_devrevstep(self):
        # Test when devrevstep exists in BinMatrix but not in DCF Registry
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # Mock binmatrix_boms to return test data
        binmatrix_data = {
            'BOM_GROUP_A': ['A0', 'B0', 'C0']  # C0 is missing from DCF Registry
        }

        # Mock dcf_registry_boms with missing devrevstep C0
        dcf_registry_data = {
            'BOM_GROUP_A': ['A0', 'B0']
        }
        dcf_registry_sha = {
            'BOM_GROUP_A': 'abc123def456'
        }

        # Mock dcf_file
        dcf_file_data = {
            'file': '/path/to/DieIDBinning.xml',
            'sha1': 'abc123def456'
        }

        with MockVar(dcf_check, 'binmatrix_boms', Mock(return_value=binmatrix_data)), \
                MockVar(dcf_check, 'dcf_registry_boms', Mock(return_value=(dcf_registry_data, dcf_registry_sha))), \
                MockVar(dcf_check, 'dcf_file', Mock(return_value=dcf_file_data)):
            obj.main()
            error_message = [
                {'message': 'Devrevstep "C0" found in BinMatrix but missing in DCF Registry', 'id': 276, 'module': 'BASE'}
            ]
            self.assertEqual(obj.result, error_message)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_sha_mismatch(self):
        # Test when SHA1 values don't match
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # Mock binmatrix_boms to return test data
        binmatrix_data = {
            'BOM_GROUP_A': ['A0', 'B0']
        }

        # Mock dcf_registry_boms with different SHA
        dcf_registry_data = {
            'BOM_GROUP_A': ['A0', 'B0']
        }
        dcf_registry_sha = {
            'BOM_GROUP_A': 'expected_sha_value'
        }

        # Mock dcf_file with different SHA
        dcf_file_data = {
            'file': '/path/to/DieIDBinning.xml',
            'sha1': 'different_sha_value'
        }

        with MockVar(dcf_check, 'binmatrix_boms', Mock(return_value=binmatrix_data)), \
                MockVar(dcf_check, 'dcf_registry_boms', Mock(return_value=(dcf_registry_data, dcf_registry_sha))), \
                MockVar(dcf_check, 'dcf_file', Mock(return_value=dcf_file_data)):
            obj.main()
            error_message = [
                {'message': 'SHA1 mismatch for BOM Group "BOM_GROUP_A". Expected: expected_sha_value, Found: different_sha_value', 'id': 276, 'module': 'BASE'}
            ]
            self.assertEqual(obj.result, error_message)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_missing_sha_in_registry(self):
        # Test when SHA is not found in DCF Registry for a BOM group
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # Mock binmatrix_boms to return test data
        binmatrix_data = {
            'BOM_GROUP_A': ['A0', 'B0']
        }

        # Mock dcf_registry_boms with empty SHA dict
        dcf_registry_data = {
            'BOM_GROUP_A': ['A0', 'B0']
        }
        dcf_registry_sha = {}  # No SHA for BOM_GROUP_A

        # Mock dcf_file
        dcf_file_data = {
            'file': '/path/to/DieIDBinning.xml',
            'sha1': 'some_sha_value'
        }

        with MockVar(dcf_check, 'binmatrix_boms', Mock(return_value=binmatrix_data)), \
                MockVar(dcf_check, 'dcf_registry_boms', Mock(return_value=(dcf_registry_data, dcf_registry_sha))), \
                MockVar(dcf_check, 'dcf_file', Mock(return_value=dcf_file_data)):
            obj.main()
            error_message = [
                {'message': 'No SHA found in DCF Registry for BOM Group "BOM_GROUP_A"', 'id': 276, 'module': 'BASE'}
            ]
            self.assertEqual(obj.result, error_message)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_empty_dcf_registry(self):
        # Test when DCF Registry file returns empty data
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # Mock binmatrix_boms to return test data
        binmatrix_data = {
            'BOM_GROUP_A': ['A0', 'B0']
        }

        # Mock dcf_registry_boms to return empty data
        dcf_registry_data = {}
        dcf_registry_sha = {}

        # Mock dcf_file
        dcf_file_data = {
            'file': '/path/to/DieIDBinning.xml',
            'sha1': 'some_sha_value'
        }

        with MockVar(dcf_check, 'binmatrix_boms', Mock(return_value=binmatrix_data)), \
                MockVar(dcf_check, 'dcf_registry_boms', Mock(return_value=(dcf_registry_data, dcf_registry_sha))), \
                MockVar(dcf_check, 'dcf_file', Mock(return_value=dcf_file_data)):
            obj.main()
            error_message = [
                {'message': 'Failed to retrieve BOM data from DCF Registry file', 'id': 276, 'module': 'BASE'}
            ]
            self.assertEqual(obj.result, error_message)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_multiple_errors(self):
        # Test when multiple errors occur (missing BOM group and SHA mismatch)
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # Mock binmatrix_boms to return test data
        binmatrix_data = {
            'BOM_GROUP_A': ['A0', 'B0'],
            'BOM_GROUP_B': ['A0']  # Missing from DCF Registry
        }

        # Mock dcf_registry_boms
        dcf_registry_data = {
            'BOM_GROUP_A': ['A0', 'B0']
        }
        dcf_registry_sha = {
            'BOM_GROUP_A': 'expected_sha'
        }

        # Mock dcf_file with different SHA
        dcf_file_data = {
            'file': '/path/to/DieIDBinning.xml',
            'sha1': 'actual_sha'
        }

        with MockVar(dcf_check, 'binmatrix_boms', Mock(return_value=binmatrix_data)), \
                MockVar(dcf_check, 'dcf_registry_boms', Mock(return_value=(dcf_registry_data, dcf_registry_sha))), \
                MockVar(dcf_check, 'dcf_file', Mock(return_value=dcf_file_data)):
            obj.main()
            # Should have 2 errors: missing BOM group and SHA mismatch
            self.assertEqual(len(obj.result), 2)
            self.assertTrue(any('BOM_GROUP_B' in err['message'] for err in obj.result))
            self.assertTrue(any('SHA1 mismatch' in err['message'] for err in obj.result))

    # Tests for binmatrix_boms() method
    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_binmatrix_boms_valid_xml(self):
        # Test binmatrix_boms with valid USRV file
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # Create mock USRV content
        usrv_content_a = '''SelectorRule BomGroupRule(BOM_GROUP_A)
{
    BOM_GROUP_A => TorchRulesVars.bom == "A0" || TorchRulesVars.bom == "B0";
}'''
        usrv_content_b = '''SelectorRule BomGroupRule(BOM_GROUP_B)
{
    BOM_GROUP_B => TorchRulesVars.bom == "A0" || TorchRulesVars.bom == "C0";
}'''

        with TempDir() as tmpdir:
            # Create the directory structure for two BOM groups
            common_dir_a = os.path.join(tmpdir.name(), 'BaseInputs', 'Common', 'Common_Class_BOM_GROUP_A')
            common_dir_b = os.path.join(tmpdir.name(), 'BaseInputs', 'Common', 'Common_Class_BOM_GROUP_B')
            os.makedirs(common_dir_a, exist_ok=True)
            os.makedirs(common_dir_b, exist_ok=True)

            # Write the USRV files
            usrv_file_a = os.path.join(common_dir_a, 'BinMatrix.flm.usrv')
            usrv_file_b = os.path.join(common_dir_b, 'BinMatrix.flm.usrv')
            with open(usrv_file_a, 'w') as f:
                f.write(usrv_content_a)
            with open(usrv_file_b, 'w') as f:
                f.write(usrv_content_b)

            # Mock the shareddir to point to temp directory
            with patch.object(obj.tpobj, 'shareddir', tmpdir.name()):
                result = obj.binmatrix_boms()

                # Verify the result
                self.assertIn('BOM_GROUP_A', result)
                self.assertIn('BOM_GROUP_B', result)
                self.assertIn('A0', result['BOM_GROUP_A'])
                self.assertIn('B0', result['BOM_GROUP_A'])
                self.assertIn('C0', result['BOM_GROUP_B'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_binmatrix_boms_missing_file(self):
        # Test binmatrix_boms when BinMatrix file is missing
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        with TempDir() as tmpdir:
            # Mock the shareddir to point to temp directory (no files created)
            with patch.object(obj.tpobj, 'shareddir', tmpdir.name()):
                result = obj.binmatrix_boms()

                # Should return empty dict and add error
                self.assertEqual(result, {})
                self.assertTrue(len(obj.result) > 0)
                self.assertTrue(any('BinMatrix file not found' in err['message'] for err in obj.result))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_binmatrix_boms_duplicate_devrevsteps(self):
        # Test binmatrix_boms with duplicate devrevstep entries (should allow duplicates in USRV)
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # Create mock USRV content with duplicates (A0 appears twice)
        usrv_content = '''SelectorRule BomGroupRule(BOM_GROUP_A)
{
    BOM_GROUP_A => TorchRulesVars.bom == "A0" || TorchRulesVars.bom == "A0" || TorchRulesVars.bom == "B0";
}'''

        with TempDir() as tmpdir:
            common_dir = os.path.join(tmpdir.name(), 'BaseInputs', 'Common', 'Common_Class_BOM_GROUP_A')
            os.makedirs(common_dir, exist_ok=True)

            usrv_file = os.path.join(common_dir, 'BinMatrix.flm.usrv')
            with open(usrv_file, 'w') as f:
                f.write(usrv_content)

            with patch.object(obj.tpobj, 'shareddir', tmpdir.name()):
                result = obj.binmatrix_boms()

                # A0 will appear twice in the list from regex, but code allows duplicates now
                self.assertIn('BOM_GROUP_A', result)
                self.assertEqual(len(result['BOM_GROUP_A']), 3)  # A0, A0, B0
                self.assertEqual(result['BOM_GROUP_A'].count('A0'), 2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_binmatrix_boms_empty_bom_elements(self):
        # Test binmatrix_boms with valid USRV content
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # Create USRV content for two BOM groups
        usrv_content_a = '''SelectorRule BomGroupRule(BOM_GROUP_A)
{
    BOM_GROUP_A => TorchRulesVars.bom == "A0" || TorchRulesVars.bom == "B0";
}'''
        usrv_content_b = '''SelectorRule BomGroupRule(BOM_GROUP_B)
{
    BOM_GROUP_B => TorchRulesVars.bom == "C0";
}'''

        with TempDir() as tmpdir:
            common_dir_a = os.path.join(tmpdir.name(), 'BaseInputs', 'Common', 'Common_Class_BOM_GROUP_A')
            common_dir_b = os.path.join(tmpdir.name(), 'BaseInputs', 'Common', 'Common_Class_BOM_GROUP_B')
            os.makedirs(common_dir_a, exist_ok=True)
            os.makedirs(common_dir_b, exist_ok=True)

            usrv_file_a = os.path.join(common_dir_a, 'BinMatrix.flm.usrv')
            usrv_file_b = os.path.join(common_dir_b, 'BinMatrix.flm.usrv')
            with open(usrv_file_a, 'w') as f:
                f.write(usrv_content_a)
            with open(usrv_file_b, 'w') as f:
                f.write(usrv_content_b)

            with patch.object(obj.tpobj, 'shareddir', tmpdir.name()):
                result = obj.binmatrix_boms()

                # Verify both BOM groups are parsed correctly
                self.assertIn('BOM_GROUP_A', result)
                self.assertIn('BOM_GROUP_B', result)
                self.assertEqual(result['BOM_GROUP_A'], ['A0', 'B0'])
                self.assertEqual(result['BOM_GROUP_B'], ['C0'])

    # Tests for dcf_file() method
    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_dcf_file_crlf_normalization(self):
        # Test that CRLF line endings are normalized to LF before hashing
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        lf_content = '<?xml version="1.0"?>\n<Root>\n  <Test>Sample</Test>\n</Root>'
        crlf_content = lf_content.replace('\n', '\r\n')

        with TempDir() as tmpdir:
            common_dir = os.path.join(tmpdir.name(), 'BaseInputs', 'Common', 'Common_Class_Test')
            os.makedirs(common_dir, exist_ok=True)

            dcf_file = os.path.join(common_dir, 'DieIDBinning.xml')
            # Write file with CRLF line endings explicitly
            with open(dcf_file, 'wb') as f:
                f.write(crlf_content.encode())

            with patch.object(obj.tpobj, 'shareddir', tmpdir.name()):
                result = obj.dcf_file('CLASS_Test')

                # SHA should match LF-normalized content, not the raw CRLF bytes
                expected_sha = sha1(lf_content)
                self.assertEqual(result['sha1'], expected_sha)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_dcf_file_valid(self):
        # Test dcf_file with valid DieIDBinning.xml file
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        test_content = '<?xml version="1.0"?><Root><Test>Sample</Test></Root>'

        with TempDir() as tmpdir:
            common_dir = os.path.join(tmpdir.name(), 'BaseInputs', 'Common', 'Common_Class_Test')
            os.makedirs(common_dir, exist_ok=True)

            dcf_file = os.path.join(common_dir, 'DieIDBinning.xml')
            with open(dcf_file, 'w') as f:
                f.write(test_content)

            with patch.object(obj.tpobj, 'shareddir', tmpdir.name()):
                result = obj.dcf_file('CLASS_Test')

                # Verify result has file and sha1
                self.assertIn('file', result)
                self.assertIn('sha1', result)
                self.assertTrue(result['file'].endswith('DieIDBinning.xml'))
                # Verify SHA1 is correct for test content
                expected_sha = sha1(test_content)
                self.assertEqual(result['sha1'], expected_sha)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_dcf_file_missing(self):
        # Test dcf_file when DieIDBinning.xml is missing
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        with TempDir() as tmpdir:
            with patch.object(obj.tpobj, 'shareddir', tmpdir.name()):
                result = obj.dcf_file('MISSING_GROUP')

                # Should return empty dict and add error
                self.assertEqual(result, {})
                self.assertTrue(len(obj.result) > 0)
                self.assertTrue(any('DieIDBinning' in err['message'] for err in obj.result))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_dcf_file_read_error(self):
        # Test dcf_file when reading the file raises an exception
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        with TempDir() as tmpdir:
            common_dir = os.path.join(tmpdir.name(), 'BaseInputs', 'Common', 'Common_Class_Test')
            os.makedirs(common_dir, exist_ok=True)

            dcf_file = os.path.join(common_dir, 'DieIDBinning.xml')
            with open(dcf_file, 'w') as f:
                f.write('test')

            with patch.object(obj.tpobj, 'shareddir', tmpdir.name()):
                # Mock open() to raise IOError when reading the DCF file
                original_open = open

                def mock_open_fn(path, *args, **kwargs):
                    if 'DieIDBinning.xml' in str(path):
                        raise IOError('Permission denied')
                    return original_open(path, *args, **kwargs)

                with patch('builtins.open', side_effect=mock_open_fn):
                    # Since there's no error handling, the exception should propagate
                    with self.assertRaises(IOError):
                        obj.dcf_file('CLASS_Test')

    # Tests for dcf_registry_boms() method
    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_dcf_registry_boms_valid(self):
        # Test dcf_registry_boms with valid DCF_Registry.txt file
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # chomp() returns lines with comments and empty lines already filtered
        registry_lines = [
            'BOM_GROUP_A,A0,sha123abc,PKG001',
            'BOM_GROUP_A,B0,sha123abc,PKG001',
            'BOM_GROUP_B,A0,sha456def,PKG002',
            'BOM_GROUP_B,C0,sha456def,PKG002'
        ]

        registry_file = f'{obj.tpobj.tpldir}/Shared/BaseInputs/Common/Common_Files/DCF_Registry.txt'

        with patch.object(File, 'chomp', return_value=registry_lines):
            result_dict, result_sha = obj.dcf_registry_boms()

            # Verify BOM groups
            self.assertIn('BOM_GROUP_A', result_dict)
            self.assertIn('BOM_GROUP_B', result_dict)
            self.assertIn('A0', result_dict['BOM_GROUP_A'])
            self.assertIn('B0', result_dict['BOM_GROUP_A'])
            self.assertIn('C0', result_dict['BOM_GROUP_B'])

            # Verify SHA mappings
            self.assertEqual(result_sha['BOM_GROUP_A'], 'sha123abc')
            self.assertEqual(result_sha['BOM_GROUP_B'], 'sha456def')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_dcf_registry_boms_invalid_columns(self):
        # Test dcf_registry_boms with lines having incorrect number of columns
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # chomp() returns already filtered lines (no comments/empty lines)
        registry_lines = [
            'BOM_GROUP_A,A0,sha123abc,PKG001',
            'BOM_GROUP_B,A0,sha456def',  # Invalid: only 3 fields
            'BOM_GROUP_C,C0,sha789ghi,PKG003,EXTRA'  # Invalid: 5 fields
        ]

        with patch.object(File, 'chomp', return_value=registry_lines):
            result_dict, result_sha = obj.dcf_registry_boms()

            # Only BOM_GROUP_A should be parsed successfully
            self.assertIn('BOM_GROUP_A', result_dict)
            self.assertNotIn('BOM_GROUP_B', result_dict)
            self.assertNotIn('BOM_GROUP_C', result_dict)

            # Should have error messages
            self.assertTrue(len(obj.result) >= 2)
            self.assertTrue(any('does not have complete data' in err['message'] for err in obj.result))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_dcf_registry_boms_comments_and_empty_lines(self):
        # Test dcf_registry_boms correctly skips comments and empty lines (chomp handles this)
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        # chomp() already filters comments and empty lines, so return only valid lines
        registry_lines = [
            'BOM_GROUP_A,A0,sha123abc,PKG001',
            'BOM_GROUP_A,B0,sha123abc,PKG001'
        ]

        with patch.object(File, 'chomp', return_value=registry_lines):
            result_dict, result_sha = obj.dcf_registry_boms()

            # Should parse only the two valid lines
            self.assertEqual(len(result_dict['BOM_GROUP_A']), 2)
            self.assertIn('A0', result_dict['BOM_GROUP_A'])
            self.assertIn('B0', result_dict['BOM_GROUP_A'])
            # No errors should be generated
            self.assertEqual(len(obj.result), 0)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_dcf_registry_boms_duplicate_entries(self):
        # Test dcf_registry_boms does not duplicate devrevsteps
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        registry_lines = [
            'BOM_GROUP_A,A0,sha123abc,PKG001',
            'BOM_GROUP_A,A0,sha123abc,PKG001',
            'BOM_GROUP_A,B0,sha123abc,PKG001'
        ]

        with patch.object(File, 'chomp', return_value=registry_lines):
            result_dict, result_sha = obj.dcf_registry_boms()

            # A0 should appear only once
            self.assertEqual(result_dict['BOM_GROUP_A'].count('A0'), 1)
            self.assertEqual(len(result_dict['BOM_GROUP_A']), 2)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_dcf_registry_boms_empty_sha(self):
        # Test dcf_registry_boms with empty SHA field
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        registry_lines = [
            'BOM_GROUP_A,A0,,PKG001',
            'BOM_GROUP_B,B0,sha456def,PKG002'
        ]

        with patch.object(File, 'chomp', return_value=registry_lines):
            result_dict, result_sha = obj.dcf_registry_boms()

            # BOM_GROUP_A should be in dict but not in SHA mapping (empty SHA)
            self.assertIn('BOM_GROUP_A', result_dict)
            self.assertNotIn('BOM_GROUP_A', result_sha)

            # BOM_GROUP_B should have SHA
            self.assertIn('BOM_GROUP_B', result_sha)
            self.assertEqual(result_sha['BOM_GROUP_B'], 'sha456def')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_main_dcf_file_not_found_per_bom(self):
        # Test when dcf_file() returns empty dict for a BOM group inside the main() loop
        tpobj = TestProgram(f'{UT_DIR}/Qgate_base_specs_chk/ARL_60B_test_passed/POR_TP/Class_ARL_H68/EnvironmentFile.env')
        obj = dcf_check(tpobj)

        binmatrix_data = {
            'BOM_GROUP_A': ['A0']
        }
        dcf_registry_data = {
            'BOM_GROUP_A': ['A0']
        }
        dcf_registry_sha = {
            'BOM_GROUP_A': 'sha123abc'
        }
        # dcf_file returns empty dict - simulates DieIDBinning.xml not found
        dcf_file_data = {}

        with MockVar(dcf_check, 'binmatrix_boms', Mock(return_value=binmatrix_data)), \
                MockVar(dcf_check, 'dcf_registry_boms', Mock(return_value=(dcf_registry_data, dcf_registry_sha))), \
                MockVar(dcf_check, 'dcf_file', Mock(return_value=dcf_file_data)):
            obj.main()
            error_message = [
                {'message': 'Failed to retrieve SHA1 information from DCF file for BOM Group "BOM_GROUP_A"', 'id': 276, 'module': 'BASE'}
            ]
            self.assertEqual(obj.result, error_message)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
