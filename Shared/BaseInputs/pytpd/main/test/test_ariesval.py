#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for ariesval
"""
from setenv_unittest import UT_DIR, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir, File
from tp.testprogram import Env
from main.ariesval import *


class TestAV(TestCase):

    def test_basic(self):
        with MockVar(sys, 'argv', 'ariesval.py'.split()), \
                TempDir(name=True, chdir=True) as tdir:
            File('bot.itf').touch()
            with CaptureStdoutLog() as p:
                with self.assertRaises(SystemExit):
                    main('echo')
            expect = f'''
CMD: echo --ituff {tdir}/bot.itf --email junk.junk@intel.com
===== Stdout:
--ituff {tdir}/bot.itf --email junk.junk@intel.com
===end of stdout or stderr===
ARIES_ITUFF result: 0
'''
            expect2 = '\n'.join(x for x in expect.split('\n') if not x.startswith('Elapsed:'))
            actual = '\n'.join(x for x in p.getvalue().split('\n') if not x.startswith('Elapsed:'))
            self.assertTextEqual(actual, Env.xpath(expect2))

    def test_nobot(self):
        with MockVar(sys, 'argv', 'ariesval.py'.split()), \
                TempDir(name=True, chdir=True) as tdir:
            with CaptureStdoutLog() as p:
                main('echo')
            expect = f'''
-w- Not exist: {tdir}/bot.itf
'''
            expect2 = '\n'.join(x for x in expect.split('\n') if not x.startswith('Elapsed:'))
            actual = '\n'.join(x for x in p.getvalue().split('\n') if not x.startswith('Elapsed:'))
            self.assertTextEqual(actual, expect2)

    def test_witharg(self):
        with MockVar(sys, 'argv', 'ariesval.py -prq 1'.split()), \
                TempDir(name=True, chdir=True) as tdir:
            File('bot.itf').touch()
            with CaptureStdoutLog() as p:
                with self.assertRaises(SystemExit):
                    main('echo')
            expect = f'''
CMD: echo --ituff {tdir}/bot.itf --email junk.junk@intel.com -prq 1
===== Stdout:
--ituff {tdir}/bot.itf --email junk.junk@intel.com -prq 1
===end of stdout or stderr===
ARIES_ITUFF result: 0
'''
            expect2 = '\n'.join(x for x in expect.split('\n') if not x.startswith('Elapsed:'))
            actual = '\n'.join(x for x in p.getvalue().split('\n') if not x.startswith('Elapsed:'))
            self.assertTextEqual(actual, Env.xpath(expect2))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
