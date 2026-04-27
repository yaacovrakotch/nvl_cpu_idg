#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Qgate that checks the module mtproj file are dynamic BOM compliant
"""
import os

import setenv      # must be first in the imports
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from os.path import basename
import sys
import json
import glob
from xml.etree import cElementTree as ElementTree
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from os.path import basename


class MtprojConfigChk(QGateBase):
    def main(self):
        """
        Checks all .mtproj files for:
        - Existence of <ItemGroup Label="ProjectConfigurations">
        - Duplicate <ProjectReference Include="...">
        Fails with error code 272 if missing ProjectConfigurations or duplicate ProjectReference.
        """
        # Find all .mtproj files in the test program directory tree
        root_dir = self.tpobj.tpldir
        print(root_dir)
        for file_path in glob.glob(os.path.join(root_dir, '**', '*.mtproj'), recursive=True):
            self._check_mtproj_file(file_path)

    def _check_mtproj_file(self, file_path):
        try:
            tree = ElementTree.parse(file_path)
            root = tree.getroot()
            ns = {'msbuild': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}

            mod = basename(file_path).split('.')[0]
            # Check for <ItemGroup Label="ProjectConfigurations">
            found_config = False
            for item_group in root.findall('.//msbuild:ItemGroup', ns) if ns else root.findall('.//ItemGroup'):
                if item_group.get('Label') == 'ProjectConfigurations':
                    found_config = True
                    break
            if not found_config:
                self.add_error(272, mod, f'{mod}.mtproj is not dynamic BOM compatible. Please copy from an existing one')
            else:
                self.add_pass(272, mod)

            # Check for duplicate <ProjectReference Include="...">
            seen_refs = set()
            duplicates = set()
            for pr in root.findall('.//msbuild:ProjectReference', ns) if ns else root.findall('.//ProjectReference'):
                include = pr.get('Include')
                if include in seen_refs:
                    duplicates.add(include)
                else:
                    seen_refs.add(include)
            if duplicates:
                for dup in duplicates:
                    self.add_error(272, mod, f'{mod}.mtproj is not dynamic BOM compatible. Please copy from an existing one')
            else:
                self.add_pass(272, mod)
        except Exception as e:
            self.add_error(272, 'BASE', f'Error parsing {file_path}: {e}')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    MtprojConfigChk(TestProgram(sys.argv[1]).pickle_init()).run()
