#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for querytid.py
"""
from setenv_unittest import UT_DIR_REPO    # must be first import for unittests
from mod.querytid import *
from tp.testprogram import TestProgram
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.files import File, TempDir
from gadget.printmore import Dumper
from unittest.mock import Mock


class TestQ(TestCase):

    def test_basic(self):
        qbox.__init__()    # clear stuff for unittests
        qbox.root = f'{UT_DIR_REPO}/qbox'

        # basic test block: vault, linus query and finder
        SetProdStep('ut05', 'a0')
        obj1 = QueryTid(intent='avenger')
        obj2 = QueryTid(linus_name='fury')
        obj3 = QueryTid(finder_tag='LI_green')
        qbox.process()
        self.assertEqual(obj1.result(), ['0153425', '0153426'])
        self.assertEqual(obj2.result(), ['0156316'])
        self.assertEqual(obj3.result(), ['0648957', '0648958'])

        # per-item run
        obja = QueryTid(intent='avengers', debugexpect='0153427')
        with self.assertRaisesRegex(ErrorInput, 'is not yet processed'):
            obja.result()
        qbox.process(obja)     # specific object
        self.assertEqual(obja.result(), ['0153427'])

        objb = QueryTid(linus_name='li_ut05', debugexpect='0317279')
        qbox.process(objb)     # specific object
        self.assertEqual(objb.result(), ['0317279'])

        # operations
        self.assertEqual(AND(obj1, obj2).result(),
                         [])
        self.assertEqual(OR(obj1, obj2).result(),
                         ['0153425', '0153426', '0156316'])
        self.assertEqual(AND(obj1, obj1).result(),
                         ['0153425', '0153426'])
        self.assertEqual(CONCAT(obj1, obj1).result(),
                         ['0153425', '0153426', '0153425', '0153426'])
        self.assertEqual(SUBTRACT(obj1, obj2).result(),
                         ['0153425', '0153426'])
        self.assertEqual(SUBTRACT(obj1, obj1).result(),
                         [])
        self.assertEqual(AND(obj1, obj1, obj2).result(),
                         [])
        self.assertEqual(OR(obj1, obj2, obj2).result(),
                         ['0153425', '0153426', '0156316'])
        self.assertEqual(CONCAT(obj2, obj2, obj2).result(),
                         ['0156316', '0156316', '0156316'])

    def test_aa1_setprodstep(self):
        qbox.__init__()    # clear stuff for unittests
        qbox.root = f'{UT_DIR_REPO}/qbox'

        self.assertEqual(qbox.process(), 1)     # Do nothing check, since there are no objects
        with self.assertRaisesRegex(ErrorUser, 'Valid product/step combinations: prod=ut05 step=a0'):
            qbox.set_prod_step()

        # This should be success
        SetProdStep('ut05', 'a0')

        with self.assertRaisesRegex(ErrorUser, 'is already Set'):
            SetProdStep('ut05', 'a01')
        with self.assertRaisesRegex(ErrorUser, 'is already Set'):
            SetProdStep('ut05a', 'a0')

        # same value, this should be success
        SetProdStep('ut05', 'a0')

    def test_ordering(self):
        qbox.__init__()    # clear stuff for unittests
        qbox.root = f'{UT_DIR_REPO}/qbox'

        # ordering test
        SetProdStep('ut05', 'a0')
        obj1 = QueryTid(intent='avenger', ordertop='intent=fea.*ring')
        obj2 = QueryTid(intent='avenger', ordertop='intent=!bin1')
        obj3 = QueryTid(intent='avenger')
        qbox.process()
        self.assertEqual(obj1.result(), ['0153426', '0153425'])
        self.assertEqual(obj2.result(), ['0153426', '0153425'])
        self.assertEqual(obj3.result(), ['0153425', '0153426'])

    def test_aa2_setcommon(self):
        qbox.__init__()    # clear stuff for unittests
        SetProdStep._clear()
        qbox.root = f'{UT_DIR_REPO}/qbox'

        # set common
        SetProdStep('ut05', 'a0')
        QueryTid.set_common(intent='avenger')
        obj1 = QueryTid(attributes='west')
        obj2 = QueryTid(attributes='north')
        qbox.process()
        self.assertEqual(obj1.result(), ['0153425', '0153426'])
        self.assertEqual(obj2.result(), ['0153426'])


class Test_ZFuncs(TestCase):

    def test_check_regex_str(self):
        self.assertEqual(Funcs.check_regex_str('a', None, pseudo=True), None)
        self.assertEqual(Funcs.check_regex_str('a', 'str1', pseudo=True), 'str1')
        self.assertEqual(Funcs.check_regex_str('a', 'str.*1', pseudo=True), 'str.*1')
        self.assertEqual(Funcs.check_regex_str('a', '*str', pseudo=True), '*str')
        with self.assertRaisesRegex(ErrorInput, 'value is an invalid regex'):
            Funcs.check_regex_str('a', '*str')
        with self.assertRaisesRegex(ErrorInput, 'expecting a string'):
            Funcs.check_regex_str('a', 1, pseudo=True)

    def test_check_string(self):
        self.assertEqual(Funcs.check_string('a', None), None)
        self.assertEqual(Funcs.check_string('a', 'ab'), 'ab')
        self.assertEqual(Funcs.check_string('a', 'ab', valid='^(ab|ac)$'), 'ab')
        with self.assertRaisesRegex(ErrorInput, 'expecting a string'):
            Funcs.check_string('a', 1)
        with self.assertRaisesRegex(ErrorInput, 'is invalid'):
            Funcs.check_string('a', 'ad', valid='^(ab|ac)$')

    def test_check_bool(self):
        self.assertEqual(Funcs.check_bool('a', "TRUE"), True)
        self.assertEqual(Funcs.check_bool('a', "FALSE"), False)
        self.assertEqual(Funcs.check_bool('a', True), True)
        self.assertEqual(Funcs.check_bool('a', False), False)
        self.assertEqual(Funcs.check_bool('a', None), None)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
