#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for qgate.py
"""
import os
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from main.qgate import *
from unittest.mock import Mock
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdoutLog
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.tputil import trimut
from gadget.disk import Chdir
from gadget.shell import IS_UNIX
from tp.testprogram import Env
from pprint import pprint
import main.qgate as qgate
import shutil
import sys


class QTest(TestCase):

    def test_missing_cfg(self):
        env = f'{UT_DIR_REPO}/Simple3a/POR_TP/TGLH81/EnvironmentFile.env'
        tpobj = TestProgram(env).init()
        tpobj.envfile = './env.env'
        with CaptureStdoutLog() as p:
            with self.assertRaisesRegex(ErrorUser, 'Missing'):
                QGateExecute(tpobj).main()

    def test_invalid_cfg(self):
        # invalid cfg plus give your own cfg
        with TempDir(name=True) as tdir:
            File(f'{tdir}/qgate_config.json').touch('''
{ "missing_ports.py":  {"211": "Gate",    "212": "wraning"}
}
''')
            env = f'{UT_DIR_REPO}/Simple3_missingports/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(env).init()
            with self.assertRaisesRegex(ErrorInput, 'is invalid'):
                QGateExecute(tpobj, cfg=f'{tdir}/qgate_config.json').main()

    def test_duplicate_id(self):
        # cfg with duplicate number
        with TempDir(name=True) as tdir, \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            File(f'{tdir}/qgate_config.json').touch('''
{ "missing_ports.py":  {"211": "Gate",
                        "211 ": "warning"}
}
''')
            env = f'{UT_DIR_REPO}/Simple4a/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(env).init()
            with self.assertRaisesRegex(ErrorInput, 'is defined twice by'):
                QGateExecute(tpobj, cfg=f'{tdir}/qgate_config.json').main()

    def test_next(self):
        with TempDir(name=True) as tdir:
            with MockVar(sys, "argv", ['qgate.py', '-next']),\
                    MockVar(qgate, "ROOT_ENV", tdir):

                # no files found
                qg = QGateArgs()
                with CaptureStdoutLog() as p:
                    qg.main()
                self.assertIn('Next available free: 200', p.getvalue())

                # normal case
                File(f'{tdir}/qgates/sample.py').touch('''
self.add_error(200, 'blah')
self.add_pass(201, 'blah')
self.random(202, 'blah')
''', mkdir=True)
                with CaptureStdoutLog() as p:
                    qg.main()
                self.assertIn('Next available free: 202', p.getvalue())

                # maximum reached
                with CaptureStdoutLog() as p:
                    qg.do_next(201)
                self.assertIn('No available free id from 200 to 201', p.getvalue())

                # check
                File(f'{tdir}/qgates/sample.py').touch('''
self.add_error(200, 'blah')
self.add_pass(201, 'blah')
self.check(bool(), 202, mod1, 203)
''', mkdir=True, newfile=True)
                with CaptureStdoutLog() as p:
                    qg.main()
                self.assertIn('Next available free: 203', p.getvalue())

    @with_(Chdir, f'{UT_DIR_REPO}/Simple3_missingports')
    @with_(MockVar, QGateExecute, '_write_file', Mock())
    def test_toc(self):
        QGateExecute.set_repo_dir()
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with MockVar(sys, "argv", ['qgate.py', env, '-toc']), \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            qg = QGateArgs()
            with CaptureStdoutLog() as p:
                print()
                with self.assertRaises(SystemExit):
                    qg.main()

        expect = '''
QGate213: Warning qgates/missing_ports.py
QGate211: Gate    qgates/missing_ports.py
QGate212: warning qgates/missing_ports.py
QGate301: Gate    ARRX/InputFiles/module_check.py
'''
        self.assertTextEqual(Env.xpath(trimut(p.getvalue(), istext=True)), expect)

        # -runner
        with MockVar(sys, "argv", ['qgate.py', env, '-toc', '-runner']), \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            qg = QGateArgs()
            with CaptureStdoutLog() as p:
                print()
                with self.assertRaises(SystemExit):
                    qg.main()
        self.assertTextEqual(Env.xpath(trimut(p.getvalue(), istext=True)), expect)

    @with_(Chdir, f'{UT_DIR_REPO}/Simple3_missingports')
    @with_(MockVar, QGateExecute, '_write_file', Mock())
    def test_fullrun(self):
        # This is a run start to finish without Mock. No Warning.
        QGateExecute.set_repo_dir()
        env = f'POR_TP/TGLH81/EnvironmentFile.env'

        with MockVar(sys, "argv", ['qgate.py', env]),\
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            qg = QGateArgs()
            with CaptureStdoutLog() as p:
                print()
                with self.assertRaisesRegex(ErrorUser, 'Gating Testprogram'):
                    qg.main()
        expect = '''
WARNING:
None

ERRORS:
===========================
 Module | QG_211 | QG_301
===========================
    ARR |      1 |      1
===========================


Below are list of errors (2):
ARR -QGate211- Input json file vs mtpl file mismatch: Port3 defined in json file but Not defined in mtpl file. TestName: ARR/CCA, ConfigFile: CLASS_P28G1_dlvrcalc_dac_chk.json ConfigSet: DAC_CHK_15C
ARR -QGate301- module specific error

'''
        self.assertTextEqual('\n'.join(trimut(p.getvalue(), empty=True)), expect)

    def test_exceptionfail(self):
        # exception fail
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports2', chdir=True, name=True) as tdir, \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            py = '''
from qgates.qgate_base import QGateBase
class QUT2(QGateBase):
    def main(self):
        raise TypeError('oopsie')
'''
            File(f'{tdir}/qut2.py').touch(py)
            File('POR_TP/TGLH81/InputFiles/qgate_config.json').touch('''
{ "%s":  {"199": "NewOnly"}
}
''' % './qut2.py', newfile=True)
            tpobj = TestProgram(env).init()

            qg = QGateExecute(tpobj)
            with self.assertRaisesRegex(ErrorUser, 'Gating Testprogram'):
                qg.main()
            self.assertEqual(qg.error, [('BASE', 199, 'oopsie')])

    def test_exitfail(self):         # good template2
        # system exit
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports2', chdir=True, name=True) as tdir, \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            py = '''
from qgates.qgate_base import QGateBase
class QUT1(QGateBase):
    def main(self):
        exit(1)
'''
            File(f'{tdir}/qut1.py').touch(py)
            File('POR_TP/TGLH81/InputFiles/qgate_config.json').touch('''
{ "%s":  {}
}
''' % './qut1.py', newfile=True)
            tpobj = TestProgram(env).init()

            qg = QGateExecute(tpobj)
            with self.assertRaisesRegex(ErrorUser, 'Gating Testprogram'):
                qg.main()
            self.assertEqual(qg.error, [('BASE', 101, 'SystemExit 1')])

    def test_250case(self):
        # warning case
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports2', chdir=True), \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/InputFiles/qgate_config.json').touch('''
{ "missing_ports.py":  {"250": "warning"}
}
''', newfile=True)
            tpobj = TestProgram(env).init()
            qg = QGateExecute(tpobj)
            with self.assertRaisesRegex(ErrorUser, 'Qgate 250 .torch_build error check. is not a gate.'):
                qg.main()

        # missing 250
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports2', chdir=True), \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/InputFiles/qgate_config.json').touch('''
{ "missing_ports.py":  {"211": "warning"}
}
''', newfile=True)
            File('POR_TP/TGLH81/InputFiles/250_qgate_required.txt').touch()
            tpobj = TestProgram(env).init()
            qg = QGateExecute(tpobj)
            with self.assertRaisesRegex(ErrorInput, 'Qgate 250 is missing in qgate config'):
                qg.main()

            # missing 250 - no txt file
            File('POR_TP/TGLH81/InputFiles/250_qgate_required.txt').unlink()
            qg = QGateExecute(tpobj)
            qg.main()     # pass case

    def test_newonly_caseA(self):     # good template
        # caseA - individual executable
        # No modified files, with Error
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports2', chdir=True), \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/InputFiles/qgate_config.json').touch('''
{ "missing_ports.py":  {"211": "NewOnly"}
}
''', newfile=True)
            tpobj = TestProgram(env).init()
            qg = QGateExecute(tpobj)
            with self.assertRaisesRegex(ErrorUser, 'Gating Testprogram'):
                qg.main()
            self.assertEqual(len(qg.error), 1)

    def test_qgate_fulltp(self):
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports2', chdir=True), \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/InputFiles/qgate_config.json').touch('''
{ "missing_ports.py":  {"211": "Warning"}
}
''', newfile=True)
            tpobj = TestProgram(env).init()
            QGateBase.fulltp_tempdir = TempDir()
            tname = QGateBase.fulltp_tempdir.get_name()
            self.assertTrue(os.path.isdir(tname))
            qg = QGateExecute(tpobj)
            qg.main()
            self.assertFalse(os.path.isdir(tname))

    @with_(MockVar, qgate, 'CALLERBIN', '/blah/buildtp.py')
    def test_newonly_caseB(self):
        # caseB - buildtp.py
        # No modified files, no error
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports2', chdir=True), \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/InputFiles/qgate_config.json').touch('''
{ "missing_ports.py":  {"211": "NewOnly"}
}
''', newfile=True)
            tpobj = TestProgram(env).init()

            print('START0 ========')
            qg = QGateExecute(tpobj)
            qg.main()
            self.assertEqual(len(qg.error), 0)

            # with modified files - Module-Folder != Module-Plan-Name
            with MockVar(QGateExecute, '_modfiles', ['Modules/PTH/pth.mtpl']):
                print('START1 ========')
                qg = QGateExecute(tpobj)
                qg.main()
                self.assertEqual(len(qg.error), 0)
                self.assertEqual(len(qg.warning), 1)

                print('START2 ========')
                QGateExecute.set_modfiles(['Modules/XA/array.mtpl'])
                qg = QGateExecute(tpobj)
                with self.assertRaisesRegex(ErrorUser, 'Gating Testprogram'):
                    qg.main()
                self.assertEqual(len(qg.error), 1)

                print('START3 ========')
                QGateExecute.set_modfiles(['Modules/ARR/array.mtpl'])
                qg = QGateExecute(tpobj)
                with self.assertRaisesRegex(ErrorUser, 'Gating Testprogram'):
                    qg.main()
                self.assertEqual(len(qg.error), 1)

    @with_(MockVar, qgate, 'CALLERBIN', '/blah/buildtp.py')
    def test_newonly_non_module(self):
        # Module name appears in SkipModule folder
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports2', chdir=True), \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/InputFiles/qgate_config.json').touch('''
{ "missing_ports.py":  {"211": "NewOnly"}
}
''', newfile=True)
            tpobj = TestProgram(env).init()

            print('START0 ========')
            qg = QGateExecute(tpobj)
            qg.main()
            self.assertEqual(len(qg.error), 0)

            # with modified files - Module-Folder != Module-Plan-Name
            with MockVar(QGateExecute, '_modfiles', ['POR_TP/SkipModules/ARR.permanent']):
                print('START1 ========')
                qg = QGateExecute(tpobj)
                qg.main()
                self.assertEqual(len(qg.error), 0)
                self.assertEqual(len(qg.warning), 1)

    def test_ut_is_modified(self):
        env = f'{UT_DIR_REPO}/Simple3_missingports2/POR_TP/TGLH81/EnvironmentFile.env'
        tpobj = TestProgram(env).init()
        qg = QGateExecute(tpobj)

        with MockVar(qgate, 'CALLERBIN', '/blah/buildtp.py'):
            # case1 - empty / default
            with MockVar(QGateExecute, '_modfiles', []):
                self.assertEqual(qg._is_modified('BASE'), False)

            # case2 - no match - BASE
            with MockVar(QGateExecute, '_modfiles', ['Modules/PTH/pth.mtpl']):
                self.assertEqual(qg._is_modified('BASE'), False)

            # case3 - base match
            with MockVar(QGateExecute, '_modfiles', ['POR_TP/blah']):
                self.assertEqual(qg._is_modified('BASE'), True)

            # case4 - direct match
            with MockVar(QGateExecute, '_modfiles', ['Modules/ARR/abc.mtpl']):
                self.assertEqual(qg._is_modified('ARR'), True)

            # case5 - indirect match
            with MockVar(QGateExecute, '_modfiles', ['Modules/XA/abc.mtpl']):
                self.assertEqual(qg._is_modified('ARR'), True)

            # case6 - no match - nonbase
            with MockVar(QGateExecute, '_modfiles', ['Modules/PTH/pth.mtpl']):
                self.assertEqual(qg._is_modified('ARR'), False)

        # case7 - empty but qgate run
        with MockVar(QGateExecute, '_modfiles', []):
            self.assertEqual(qg._is_modified('BASE'), True)

    def test_waivers1(self):
        # Full run, no mocking, all pass
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports', chdir=True), \
                MockVar(sys, "argv", ['qgate.py', env]),\
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/InputFiles/qgate_waivers.txt').touch('''
ARR -QGate211- Input json file vs mtpl file mismatch: Port3 defined in json file but Not defined in mtpl file. TestName: ARR/CCA, ConfigFile: CLASS_P28G1_dlvrcalc_dac_chk.json ConfigSet: DAC_CHK_15C
ARR -QGate301- module specific error
''')
            qg = QGateArgs()
            with CaptureStdoutLog() as p:
                qg.main()
            expect = '''
PASSING:

WARNING:
===========================
 Module | WA_211 | WA_301
===========================
    ARR |      1 |      1
===========================


ERROR:
None
Below are list of errors (0):
No Errors

Below are list of warnings (2):
ARR -Warning211- Input json file vs mtpl file mismatch: Port3 defined in json file but Not defined in mtpl file. TestName: ARR/CCA, ConfigFile: CLASS_P28G1_dlvrcalc_dac_chk.json ConfigSet: DAC_CHK_15C (Waived)
ARR -Warning301- module specific error (Waived)
'''
            self.assertTextEqual(File('POR_TP/TGLH81/Reports/QGate_report.txt').read(), expect)
            # shared
            File('Shared/POR_TP/TGLH81/InputFiles/qgate_waivers.txt').touch('''
ARR -QGate211- Input json file vs mtpl file mismatch: Port3 defined in json file but Not defined in mtpl file. TestName: ARR/CCA, ConfigFile: CLASS_P28G1_dlvrcalc_dac_chk.json ConfigSet: DAC_CHK_15C
ARR -QGate301- module specific error
''', mkdir=True)
            qg = QGateArgs()
            with CaptureStdoutLog() as p:
                qg.main()
            expect = '''
PASSING:

WARNING:
===========================
 Module | WA_211 | WA_301
===========================
    ARR |      1 |      1
===========================


ERROR:
None
Below are list of errors (0):
No Errors

Below are list of warnings (2):
ARR -Warning211- Input json file vs mtpl file mismatch: Port3 defined in json file but Not defined in mtpl file. TestName: ARR/CCA, ConfigFile: CLASS_P28G1_dlvrcalc_dac_chk.json ConfigSet: DAC_CHK_15C (Waived)
ARR -Warning301- module specific error (Waived)
'''
            self.assertTextEqual(File('POR_TP/TGLH81/Reports/QGate_report.txt').read(), expect)

    def test_waivers2(self):
        # Full run, no mocking, 1 waived 1 fail
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports', chdir=True), \
                MockVar(sys, "argv", ['qgate.py', env]),\
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/InputFiles/qgate_waivers.txt').touch('''
ARR -QGate211- Input json file vs mtpl file mismatch: Port3 defined in json file but Not defined in mtpl file. TestName: ARR/CCA, ConfigFile: CLASS_P28G1_dlvrcalc_dac_chk.json ConfigSet: DAC_CHK_15C
''')
            qg = QGateArgs()
            with CaptureStdoutLog() as p:
                with self.assertRaisesRegex(ErrorUser, 'Gating Testprogram'):
                    qg.main()
            expect = '''
PASSING:

WARNING:
==================
 Module | WA_211
==================
    ARR |      1
==================


ERROR:
==================
 Module | QG_301
==================
    ARR |      1
==================

Below are list of errors (1):
ARR -QGate301- module specific error

Below are list of warnings (1):
ARR -Warning211- Input json file vs mtpl file mismatch: Port3 defined in json file but Not defined in mtpl file. TestName: ARR/CCA, ConfigFile: CLASS_P28G1_dlvrcalc_dac_chk.json ConfigSet: DAC_CHK_15C (Waived)

'''
            self.assertTextEqual(File('POR_TP/TGLH81/Reports/QGate_report.txt').read(), expect)

    def test_waivers3(self):
        def fake(slf, number, mod, text):
            slf.result.append({'message': f'{text} ',
                               'id': number,
                               'module': mod})

        # Mocked error, there is space in the error message
        env = f'POR_TP/TGLH81/EnvironmentFile.env'
        with TempDir(startcopy=f'{UT_DIR_REPO}/Simple3_missingports', chdir=True), \
                MockVar(sys, "argv", ['qgate.py', env]),\
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            File('POR_TP/TGLH81/InputFiles/qgate_waivers.txt').touch('''
 ARR -QGate211- Input json file vs mtpl file mismatch: Port3 defined in json file but Not defined in mtpl file. TestName: ARR/CCA, ConfigFile: CLASS_P28G1_dlvrcalc_dac_chk.json ConfigSet: DAC_CHK_15C
''')
            qg = QGateArgs()
            with CaptureStdoutLog() as p, \
                    MockVar(QGateBase, 'add_error', fake):
                with self.assertRaisesRegex(ErrorUser, 'Gating Testprogram'):
                    qg.main()
            expect = '''
PASSING:

WARNING:
==================
 Module | WA_211
==================
    ARR |      1
==================


ERROR:
==================
 Module | QG_301
==================
    ARR |      1
==================

Below are list of errors (1):
ARR -QGate301- module specific error

Below are list of warnings (1):
ARR -Warning211- Input json file vs mtpl file mismatch: Port3 defined in json file but Not defined in mtpl file. TestName: ARR/CCA, ConfigFile: CLASS_P28G1_dlvrcalc_dac_chk.json ConfigSet: DAC_CHK_15C  (Waived)

'''
            self.assertTextEqual(File('POR_TP/TGLH81/Reports/QGate_report.txt').read(), expect)

    @with_(MockVar, QGateExecute, 'standalone_calls', Mock())     # This is tested separately
    def test_basic(self):
        # This is 2 warning and 2 errors
        tpref = f'{UT_DIR_REPO}/Simple3_missingports'
        with TempDir(name=True, delete=True) as tdir:
            shutil.copytree(tpref, f'{tdir}/TPL')
            env = f'{tdir}/TPL/POR_TP/TGLH81/EnvironmentFile.env'

            class Q1(QGateBase):
                def main(self):
                    self.add_error(100, "MOD1", 'message1 not defined in config')
                    self.add_error(212, "MOD1", 'must be warning1')
                    self.add_error(213, "MOD1", 'must be warning2')
                    self.add_error(214, "MOD1", 'must be off')
                    self.add_pass(100, "MOD1")

            class Q2(QGateBase):
                def main(self):
                    self.add_error(211, "MOD2", 'message2 defined in config')
                    self.add_error(212, "MOD2", 'must be warning')
                    self.add_pass(211, "MOD1")
                    self.add_pass(100, "MOD1")

            def fake_read_module(slf):
                slf.qcls = [Q1, Q2]

            with MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
                tpobj = TestProgram(env).init()
                qg = QGateExecute(tpobj)
                with CaptureStdoutLog() as p,\
                        MockVar(QGateExecute, '_read_modules', fake_read_module):
                    print()
                    with self.assertRaisesRegex(ErrorUser, 'Gating'):
                        qg.main()
            expect = '''
WARNING:
===========================
 Module | WA_212 | WA_213
===========================
   MOD1 |      1 |      1
   MOD2 |      1 |
===========================


ERRORS:
===========================
 Module | QG_100 | QG_211
===========================
   MOD1 |      1 |
   MOD2 |        |      1
===========================


There are total of 3 warnings. Refer to Reports/QGate_report.txt

Below are list of errors (2):
MOD1 -QGate100- message1 not defined in config
MOD2 -QGate211- message2 defined in config


'''
            self.assertTextEqual('\n'.join(trimut(p.getvalue(), empty=True)), expect)

            expect = '''PASSING:
Qgate#100: pass count=2
Qgate#211: pass count=1

WARNING:
===========================
 Module | WA_212 | WA_213
===========================
   MOD1 |      1 |      1
   MOD2 |      1 |
===========================


ERROR:
===========================
 Module | QG_100 | QG_211
===========================
   MOD1 |      1 |
   MOD2 |        |      1
===========================

Below are list of errors (2):
MOD1 -QGate100- message1 not defined in config
MOD2 -QGate211- message2 defined in config

Below are list of warnings (3):
MOD1 -Warning212- must be warning1
MOD1 -Warning213- must be warning2
MOD2 -Warning212- must be warning
'''
            self.assertTextEqual(File(f'{tdir}/TPL/POR_TP/TGLH81/Reports/QGate_report.txt').read(),
                                 expect)

    @with_(MockVar, QGateExecute, '_write_file', Mock())
    def test_warningonly(self):
        # This is 1 warning, no errors
        env = f'{UT_DIR_REPO}/Simple3_missingports/POR_TP/TGLH81/EnvironmentFile.env'

        class Q1(QGateBase):
            def main(self):
                pass

        class Q2(QGateBase):
            def main(self):
                self.add_error(212, "MOD2", 'must be warning')

        def fake_read_module(slf):
            slf.qcls = [Q1, Q2]

        with MockVar(sys, "argv", ['qgate.py', env]), \
                MockVar(QGateExecute, 'standalone_calls', Mock()), \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            qg = QGateArgs()
            with CaptureStdoutLog() as p,\
                    MockVar(QGateExecute, '_read_modules', fake_read_module):
                print()
                qg.main()
        expect = '''
WARNING:
==================
 Module | WA_212
==================
   MOD2 |      1
==================


ERRORS:
None

There are total of 1 warnings. Refer to Reports/QGate_report.txt

Below are list of errors (0):
No Errors
'''
        self.assertTextEqual('\n'.join(trimut(p.getvalue(), empty=True)), expect)

    @with_(MockVar, QGateExecute, '_write_file', Mock())
    def test_warning_bi(self):
        # This is 1 warning, no errors
        env = f'{UT_DIR_REPO}/Simple3_missingports/POR_TP/TGLH81/EnvironmentFile.env'

        class Q1(QGateBase):
            def main(self):
                pass

        class Q2(QGateBase):
            def main(self):
                self.add_error(212, "MOD2", 'must be warning')

        def fake_read_module(slf):
            slf.qcls = [Q1, Q2]

        with MockVar(sys, "argv", ['qgate.py', env, '-verbose']), \
                MockVar(QGateExecute, 'standalone_calls', Mock()), \
                MockVar(qgate, "ROOT_ENV", dirname(ROOT_ENV)):
            qg = QGateArgs()
            with CaptureStdoutLog() as p,\
                    MockVar(QGateExecute, '_read_modules', fake_read_module):
                print()
                qg.main()
        expect = '''
PASSING:

WARNING:
==================
 Module | WA_212
==================
   MOD2 |      1
==================


ERRORS:
None

There are total of 1 warnings. Refer to Reports/QGate_report.txt

Below are list of errors (0):
No Errors

Below are list of warnings (1):
MOD2 -Warning212- must be warning
'''
        self.assertTextEqual('\n'.join(trimut(p.getvalue(), empty=True)), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple3a', chdir=True)
    def test_get_config(self):
        qe = QGateExecute(tpobj=TestProgram('POR_TP/TGLH81/EnvironmentFile.env'))

        # own config
        self.assertEqual(qe._get_config('blah'), 'blah')

        # default
        self.assertEqual(Env.xpath(qe._get_config(None)), f'{Env.xpath(os.getcwd())}/POR_TP/TGLH81/InputFiles/qgate_config.json')

        # shared
        File('Shared/POR_TP/TGLH81/InputFiles/qgate_config.json').touch(mkdir=True)
        self.assertEqual(Env.xpath(qe._get_config(None)), f'{Env.xpath(os.getcwd())}/Shared/POR_TP/TGLH81/InputFiles/qgate_config.json')

    @with_(MockVar, QGateExecute, 'repodir', '.')
    @with_(MockVar, QGateExecute, '_modfiles', [])
    def test_standalone(self):
        # Run from a non-repo
        ut_root = f'{UT_DIR_REPO}/Simple3a'
        with Chdir(ut_root):
            QGateExecute(tpobj=TestProgram('POR_TP/TGLH81/EnvironmentFile.env')).main()
        self.assertEqual(QGateExecute.repodir, '.')
        self.assertEqual(QGateExecute._modfiles, [])

        # From a repo, no https
        with TempDir(startcopy=ut_root, chdir=True, name=True) as tdir, \
                MockVar(os.environ, 'https_proxy', MockVar.delete):
            File('.git/something').touch(mkdir=True)
            QGateExecute(tpobj=TestProgram('POR_TP/TGLH81/EnvironmentFile.env')).main()
        self.assertEqual(QGateExecute.repodir, tdir)
        self.assertEqual(QGateExecute._modfiles, [])

        # From a repo, with
        with TempDir(startcopy=ut_root, chdir=True, name=True) as tdir, \
                MockVar(os.environ, 'https_proxy', 'http://proxy-chain.intel.com:912'):
            File('.git/something').touch(mkdir=True)
            QGateExecute.set_repo_dir()
            QGateExecute(tpobj=TestProgram('POR_TP/TGLH81/EnvironmentFile.env')).main()
        self.assertEqual(QGateExecute.repodir, tdir)
        self.assertEqual(QGateExecute._modfiles, [])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
