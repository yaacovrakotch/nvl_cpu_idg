#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for setting.py
"""
import setenv_unittest     # must be first import for unittests
from mod.setting import cfg
from gadget.ut import TestCase, unittest


class SettingTest(TestCase):

    def test_basic(self):
        value = cfg.unittest_sample     # Get a configuration
        self.assertEqual(value, ['FlowControl', 'SetFlowInfo'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
