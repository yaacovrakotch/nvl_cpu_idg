#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unittest for cov.py
"""

from setenv_unittest import ROOT_ENV    # must be first import for unittests
import os
from gadget.ut import unittest
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from main.cov import MyCov


class MyCovTests(unittest.TestCase):

    def test_do_text(self):
        args = [os.path.join(ROOT_ENV, "gadget", "test", "test_strmore.py"), "-v", "-b"]
        expect = ['Missing: 0',
                  'BrMiss:  0']

        with CaptureStdoutLog() as p:
            MyCov(args).do_text()
        self.assertRegexpInList(p.getvalue().split('\n'), expect)

    def test_do_cov(self):
        args = [os.path.join(ROOT_ENV, "gadget", "test", "test_strmore.py"), "-v", "-b", "StrTests.test_to_str"]
        myCov = MyCov(args)

        with TempDir(name=True) as tdir:
            myCov.webloc = tdir
            target_htmlcov = os.path.join(myCov.webloc, myCov.webfile)
            myCov.dirweb = target_htmlcov
            with CaptureStdoutLog() as p:
                myCov.do_cov()
            self.assertIn("Coverage report is in:", p.getvalue())
            self.assertTrue(os.path.exists(target_htmlcov), "htmlcov should exist")

    def test_missing_line(self):
        testing_py_code = f'''
def add(a, b):
    return a + b

def sign_text(x):
    if x > 0:
        return "positive"
    return "non-positive"
        '''

        test_testing_py_code = f'''
import unittest
import testing

class TestTesting(unittest.TestCase):
    def test_add(self):
        self.assertEqual(testing.add(1, 2), 3)

    def test_sign_text_positive(self):
        self.assertEqual(testing.sign_text(5), "positive")

if __name__ == "__main__":
    unittest.main()
        '''

        args = ["test_testing.py", "-v", "-b"]
        expect = ['Missing: 1',
                  'BrMiss:  1']
        with TempDir(chdir=True) as tdir:
            with File("testing.py") as tp, \
                    File("test_testing.py") as ttp:
                tp.touch(testing_py_code)
                ttp.touch(test_testing_py_code)

                with CaptureStdoutLog() as p:
                    MyCov(args).do_text()
                self.assertRegexpInList(p.getvalue().split('\n'), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
