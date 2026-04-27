#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for checks
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest
from gadget.printmore import Dumper
from mod.checks import *
from os.path import basename
import os


class TestChecks(TestCase):

    def test_basic(self):
        assert 'LC_ALL' not in os.environ, 'Pls execute "unsetenv LC_ALL" first. Unittest will not work if this is set.'
        tpldir = f'{UT_DIR_REPO}/check_special_char'
        scc = SpecialCharCheck(tpldir).main()
        self.assertEqual(len(scc._read), len(os.listdir(tpldir)) - 1)
        self.maxDiff = None

        result = [f'{basename(k)}: {v}' for k, v in sorted(scc.result.items())]
        print('\n'.join(result))
        self.assertRegexpEachList(result, ['bad_text.txt: .*line#121',
                                           'bad_xml.xml: .*XML Line with special char.*LimitLoUserVar',
                                           'bad_xml_read.xml: .*Cannot read xml file: mismatched tag: line 94, column 6'])

    def test_is_readable(self):
        scc = SpecialCharCheck(f'{UT_DIR_REPO}/check_special_char')
        scc.is_readable('/notfound/file1')
        self.assertEqual(dict(scc.result),
                         {'/notfound/file1':
                          ["Cannot open/read: [Errno 2] No such file or directory: '/notfound/file1'"]})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
