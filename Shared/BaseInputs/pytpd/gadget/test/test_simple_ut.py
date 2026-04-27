#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unittest for simple_ut.py
"""
from setenv_unittest import ROOT_ENV     # must be first import for unittests
from gadget.simple_ut import *
from gadget.ut import TestCase, unittest


class UTTest(TestCase):

    def test_basic(self):
        self.assertEqual(foo1(), 1)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
