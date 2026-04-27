#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for patterns_site_check.
"""
from setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.test.setenv_unittest import UT_DIR, ROOT_ENV, EXIST_PDX_I_DRIVE     # must be first import for unittests
from qgates.patterns_site_check import *
from gadget.ut import TestCase, unittest, MockVar
from pprint import pprint


class TestPatternSiteCheck(TestCase):

    def fake_data_host(slf, cmd='path_exists', arg='abcd.plb', check=True, site='JF'):
        result = {'I:/hdmxpats/nvl_cpu/MCAscn/RevTCI8GA0.0/p0/plb': True,
                  'I:/hdmxpats/nvl_cpu/MCAscn/RevTCI8GB0.0/p1/plb': True}
        return result

    def fake_data_host_fail(slf, cmd='path_exists', arg='abcd.plb', check=True, site='JF'):
        result = {'I:/hdmxpats/nvl_cpu/MCAscn/RevTCI8GA0.0/p0/plb': False,
                  'I:/hdmxpats/nvl_cpu/MCAscn/RevTCI8GB0.0/p1/plb': True}
        return result

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        tpobj = TestProgram(f'{UT_DIR}/nvl_testprogram_release/NVLXXXXAXH01A0BSXXX/POR_TP/Class_NVL_S28C/EnvironmentFile.env')
        obj = CheckPatterns_AllSites(tpobj)

        # case: not from a PR
        self.assertEqual(obj.main(), 1)

        # pass case
        with MockVar(os.environ, 'FROM_PR', 'True'), \
                MockVar(DataHost, 'central', self.fake_data_host):
            obj.main()
        self.assertEqual(obj.result, [])
        self.assertEqual(obj.passed, {(258, 'BASE'): 6})

        # fail case
        with MockVar(os.environ, 'FROM_PR', 'True'), \
                MockVar(DataHost, 'central', self.fake_data_host_fail):
            obj.main()

        fake_result = [{'message': 'I:/hdmxpats/nvl_cpu/MCAscn/RevTCI8GA0.0/p0/plb does NOT exist in JF', 'id': 258, 'module': 'BASE'},
                       {'message': 'I:/hdmxpats/nvl_cpu/MCAscn/RevTCI8GA0.0/p0/plb does NOT exist in PG', 'id': 258, 'module': 'BASE'},
                       {'message': 'I:/hdmxpats/nvl_cpu/MCAscn/RevTCI8GA0.0/p0/plb does NOT exist in FM', 'id': 258, 'module': 'BASE'}]
        self.assertEqual(obj.result, fake_result)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
