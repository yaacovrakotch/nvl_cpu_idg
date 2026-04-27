#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for dynamic_BOM_chk.py
"""
import sys
import os
from unittest.mock import MagicMock, Mock

try:
    from setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests

from qgates.dynamic_BOM_chk import *
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from unittest.mock import MagicMock

import sys
import json
import tempfile
import shutil
import unittest
from xml.etree import ElementTree as ET

from qgates.dynamic_BOM_chk import *


class DummyTPObj:
    def __init__(self, tpldir):
        self.tpldir = tpldir


class TestMtprojConfigChk(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.tpobj = DummyTPObj(self.test_dir)
        self.chk = MtprojConfigChk(self.tpobj)
        self.chk.add_error = MagicMock()
        self.chk.add_pass = MagicMock()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def write_mtproj(self, filename, xml_content):
        path = os.path.join(self.test_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        return path

    def test_all_pass(self):
        # Valid mtproj: has ProjectConfigurations and no duplicate ProjectReference
        xml = '''<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Class_NVL_S28C|AnyCPU">
      <Configuration>Class_NVL_S28C</Configuration>
      <Platform>AnyCPU</Platform>
    </ProjectConfiguration>
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="foo.ipctproj" />
    <ProjectReference Include="bar.ipctproj" />
  </ItemGroup>
</Project>
'''
        self.write_mtproj("good.mtproj", xml)
        self.chk.main()
        # Should call add_pass twice (once for config, once for no dup)
        self.assertEqual(self.chk.add_pass.call_count, 2)
        self.chk.add_error.assert_not_called()

    def test_missing_project_configurations(self):
        # No <ItemGroup Label="ProjectConfigurations">
        xml = '''<?xml version="1.0" encoding="utf-8"?>
<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <ProjectReference Include="foo.ipctproj" />
  </ItemGroup>
</Project>
'''
        self.write_mtproj("missing_config.mtproj", xml)
        self.chk.main()
        self.chk.add_error.assert_any_call(272, "missing_config", "missing_config.mtproj is not dynamic BOM compatible. Please copy from an existing one")
        self.chk.add_pass.assert_called_with(272, "missing_config")

    def test_duplicate_project_reference(self):
        # Duplicate ProjectReference Include
        xml = '''<?xml version="1.0" encoding="utf-8"?>
<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Class_NVL_S28C|AnyCPU">
      <Configuration>Class_NVL_S28C</Configuration>
      <Platform>AnyCPU</Platform>
    </ProjectConfiguration>
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="foo.ipctproj" />
    <ProjectReference Include="foo.ipctproj" />
  </ItemGroup>
</Project>
'''
        self.write_mtproj("dup.mtproj", xml)
        self.chk.main()
        self.chk.add_pass.assert_any_call(272, "dup")
        self.chk.add_error.assert_any_call(272, "dup", "dup.mtproj is not dynamic BOM compatible. Please copy from an existing one")

    def test_xml_parse_error(self):
        # Invalid XML
        xml = "<Project><ItemGroup></Project"
        self.write_mtproj("badxml.mtproj", xml)
        self.chk.main()
        # Should call add_error with 'Error parsing'
        found = False
        for call in self.chk.add_error.call_args_list:
            if "Error parsing" in call[0][2]:
                found = True
        self.assertTrue(found)

    def test_no_namespace(self):
        # No xmlns, no ProjectConfigurations, no ProjectReference
        xml = '''<Project>
  <ItemGroup>
    <ProjectReference Include="foo.ipctproj" />
  </ItemGroup>
</Project>
'''
        self.write_mtproj("nonamespace.mtproj", xml)
        self.chk.main()
        self.chk.add_error.assert_any_call(272, "nonamespace", "nonamespace.mtproj is not dynamic BOM compatible. Please copy from an existing one")
        self.chk.add_pass.assert_called_with(272, "nonamespace")


if __name__ == "__main__":
    unittest.main()
