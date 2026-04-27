#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unitest for helpers
"""
import json
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock, MagicMock
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog, OPT
from gadget.files import TempDir
from pymtpl.helpers import *
from gadget.errors import ErrorUser, ErrorInput
from pymtpl.core import Initialize, PyMtpl, MConfig
import pymtpl.core as core
from pprint import pformat
import sys
from unittest.mock import patch, MagicMock
from functools import partial
from pymtpl.test.methods import VminTC


class TestCompact(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic(self):
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'
        File('a.mtpl').touch('''
Test blah
{
   param = 1;
}

DUTFlow START_SubFlow
{
    DUTFlowItem TPI_FLWFLGS_XXX_START TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_START
    {
        Result -2
        {
            Property PassFail = "Fail";
            Return -2;
        }
        Result 1 {
            Property PassFail = "Pass";
            GoTo TPI_BASE_XXX_START;
        }
        Result 2 {
            Property PassFail = "Pass";
            Return 1;
        }
    }
}
''')
        expect = '''
Test blah {
 param = 1;
}
DUTFlow START_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_START TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_BASE_XXX_START; }
  Result 2 { Property PassFail = "Pass"; Return 1; }
 }
}
'''
        self.assertTextEqual(str(Compact('a.mtpl')), expect)


class TestValidBomconfig(TestCase):
    @with_(TempDir, chdir=True)
    def test_basic_valid_boms(self):
        # 1. Create your test JSON file
        os.makedirs('Shared/BaseInputs/Inputs', exist_ok=True)
        with open('Shared/BaseInputs/Inputs/bom_to_category.json', 'w') as f:
            f.write('{"Desktop": ["CLASS_NVL_S8C", "CLASS_NVL_S16C"]}')

        # 2. Patch TestProgram to set tpldir to the current directory
        with patch('pymtpl.helpers.TestProgram') as MockTestProgram:
            mock_tp = MagicMock()
            mock_tp.tpldir = os.getcwd()  # or wherever your test file is
            MockTestProgram.return_value = mock_tp

            # 3. Set OPT.env to anything (it will be passed to TestProgram)
            OPT.env = 'dummy_env'

            # 4. Now call getvalidboms, which will use your test file
            result = getvalidboms('Desktop')
            self.assertEqual(result, ["CLASS_NVL_S8C", "CLASS_NVL_S16C"])

    @with_(TempDir, chdir=True)
    def test_missing_env_file(self):
        # 1. Create your test JSON file
        os.makedirs('Shared/BaseInputs/Inputs', exist_ok=True)
        with open('Shared/BaseInputs/Inputs/bom_to_category.json', 'w') as f:
            f.write('{"Desktop": ["CLASS_NVL_S8C", "CLASS_NVL_S16C"]}')

        # 2. Patch TestProgram to set tpldir to the current directory
        with patch('pymtpl.helpers.TestProgram') as MockTestProgram, self.assertRaisesRegex(ErrorUser, 'Env file not found when running Pymtpl'):
            mock_tp = MagicMock()
            mock_tp.tpldir = os.getcwd()  # or wherever your test file is
            MockTestProgram.return_value = mock_tp
            OPT.env = None

            # 4. Now call getvalidboms, which will use your test file
            result = getvalidboms('Desktop')

    @with_(TempDir, chdir=True)
    def test_eval_valid_bom_class(self):
        # 1. Create your test JSON file
        os.makedirs('Shared/BaseInputs/Inputs', exist_ok=True)
        with open('Shared/BaseInputs/Inputs/bom_to_category.json', 'w') as f:
            f.write('{"Desktop":["CLASS_NVL_S8C", "CLASS_NVL_S16C"],"Mobile":["CLASS_NVL_UL6C", "CLASS_NVL_U8C", "CLASS_NVL_H16C"]}')

        # 2. Patch TestProgram to set tpldir to the current directory
        with patch('pymtpl.helpers.TestProgram') as MockTestProgram:
            mock_tp = MagicMock()
            mock_tp.tpldir = os.getcwd()  # or wherever your test file is
            MockTestProgram.return_value = mock_tp

            # 3. Set OPT.env to anything (it will be passed to TestProgram)
            OPT.env = 'dummy_env'

            class PyObj:
                # Start of the "python mtpl code" ====================
                output = Initialize('out', 'FUN')
                mconfig = MConfig()
                mconfig.ipname("IP_CPU")
                mconfig.pattern(path="Test", rev="Some", patch="0.1",
                                plistinfo={"sample.plist": getvalidboms('Desktop'), 'sample2.plist': getvalidboms('Mobile')})
                out = '\n'.join(mconfig.write_lines())
                expect = '''<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="Test" Rev="Some" Patch="0.1">
            <PlistFiles>
                <PlistFile BomGroup="CLASS_NVL_S8C">sample.plist</PlistFile>
                <PlistFile BomGroup="CLASS_NVL_S16C">sample.plist</PlistFile>
                <PlistFile BomGroup="CLASS_NVL_UL6C">sample2.plist</PlistFile>
                <PlistFile BomGroup="CLASS_NVL_U8C">sample2.plist</PlistFile>
                <PlistFile BomGroup="CLASS_NVL_H16C">sample2.plist</PlistFile>
            </PlistFiles>
        </PORRoot>
    </Patterns>
    <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
                self.assertTextEqual(out, expect)

    @with_(TempDir, chdir=True)
    def test_invalid_bommaping_file_format(self):
        # 1. Create your test JSON file
        os.makedirs('Shared/BaseInputs/Inputs', exist_ok=True)
        with open('Shared/BaseInputs/Inputs/bom_to_category.json', 'w') as f:
            f.write('{"Desktop":["CLASS_NVL_S8C", "CLASS_NVL_S16C"],"Mobile":["CLASS_NVL_UL6C", "CLASS_NVL_U8C", "CLASS_NVL_H16C"],}')

        # 2. Patch TestProgram to set tpldir to the current directory
        with patch('pymtpl.helpers.TestProgram') as MockTestProgram, self.assertRaisesRegex(ErrorInput, 'Pls contact the TPI team to fix the BOMMapping json file'):
            mock_tp = MagicMock()
            mock_tp.tpldir = os.getcwd()  # or wherever your test file is
            MockTestProgram.return_value = mock_tp

            # 3. Set OPT.env to anything (it will be passed to TestProgram)
            OPT.env = 'dummy_env'
            getvalidboms('Desktop')

    @with_(TempDir, chdir=True)
    def test_invalid_bommaping_key(self):
        # 1. Create your test JSON file
        os.makedirs('Shared/BaseInputs/Inputs', exist_ok=True)
        with open('Shared/BaseInputs/Inputs/bom_to_category.json', 'w') as f:
            f.write('{"Desktop":["CLASS_NVL_S8C", "CLASS_NVL_S16C"],"Mobile":["CLASS_NVL_UL6C", "CLASS_NVL_U8C", "CLASS_NVL_H16C"]}')

        # 2. Patch TestProgram to set tpldir to the current directory
        with patch('pymtpl.helpers.TestProgram') as MockTestProgram, self.assertRaisesRegex(ErrorUser, 'EvalValidBoms name Desktp not found'):
            mock_tp = MagicMock()
            mock_tp.tpldir = os.getcwd()  # or wherever your test file is
            MockTestProgram.return_value = mock_tp

            # 3. Set OPT.env to anything (it will be passed to TestProgram)
            OPT.env = 'dummy_env'
            getvalidboms('Desktp')

    @with_(TempDir, chdir=True)
    def test_missing_bommaping_file(self):

        # 1. Patch TestProgram to set tpldir to the current directory
        with patch('pymtpl.helpers.TestProgram') as MockTestProgram, self.assertRaisesRegex(ErrorUser, 'BOMMapping file not found so EvalValidBoms cannot be used'):
            mock_tp = MagicMock()
            mock_tp.tpldir = os.getcwd()  # or wherever your test file is
            MockTestProgram.return_value = mock_tp

            # 2. Set OPT.env to anything (it will be passed to TestProgram)
            OPT.env = 'dummy_env'
            getvalidboms('Desktp')


class TestProgFlows(TestCase):

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_basic(self):
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
START_SubFlow               TPI_FLWFLGS_XXX           r2p  r3f r4f1
START_SubFlow               TPI_BASE_XXX              r3f6 rm4pm7

SHAREDRAILSNOM_SubFlow      TPI_FLWFLGS_XXX           r2p2

# The order follows MAIN definition
MAIN                        SHAREDRAILSNOM_SubFlow
MAIN                        START_SubFlow
'''
            ProgramFlows().main(text, 'MAIN')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow START_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_START TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_BASE_XXX_START; }
  Result 2 { Property PassFail = "Pass"; Return 1; }
  Result 3 { Property PassFail = "Fail"; Return 0; }
  Result 4 { Property PassFail = "Fail"; Return 1; }
 }
 DUTFlowItem TPI_BASE_XXX_START TPI_BASE_XXX::TPI_BASE_XXX_START {
  Result -4 { Property PassFail = "Pass"; Return -7; }
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 3 { Property PassFail = "Fail"; Return 6; }
 }
}
DUTFlow SHAREDRAILSNOM_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_SHAREDRAILSNOM TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_SHAREDRAILSNOM {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Pass"; Return 2; }
 }
}
DUTFlow MAIN {
 DUTFlowItem SHAREDRAILSNOM_SubFlow SHAREDRAILSNOM_SubFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo START_SubFlow; }
  Result 2 { Property PassFail = "Pass"; Return 1; }
 }
 DUTFlowItem START_SubFlow START_SubFlow {
  Result -7 { Property PassFail = "Pass"; Return 1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 6 { Property PassFail = "Fail"; Return 0; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_deleteport(self):
        # This tests r0x0. It will remove default port for this line. Jonathan request.
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
START_SubFlow               TPI_FLWFLGS_XXX           r2p  r3f r4f1 r0x0 r5x0
START_SubFlow               TPI_BASE_XXX              r3f6 rm4pm7

SHAREDRAILSNOM_SubFlow      TPI_FLWFLGS_XXX           r2p2

# The order follows MAIN definition
MAIN                        SHAREDRAILSNOM_SubFlow
MAIN                        START_SubFlow
'''
            ProgramFlows().main(text, 'MAIN')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow START_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_START TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_BASE_XXX_START; }
  Result 2 { Property PassFail = "Pass"; Return 1; }
  Result 3 { Property PassFail = "Fail"; Return 0; }
  Result 4 { Property PassFail = "Fail"; Return 1; }
 }
 DUTFlowItem TPI_BASE_XXX_START TPI_BASE_XXX::TPI_BASE_XXX_START {
  Result -4 { Property PassFail = "Pass"; Return -7; }
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 3 { Property PassFail = "Fail"; Return 6; }
 }
}
DUTFlow SHAREDRAILSNOM_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_SHAREDRAILSNOM TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_SHAREDRAILSNOM {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Pass"; Return 2; }
 }
}
DUTFlow MAIN {
 DUTFlowItem SHAREDRAILSNOM_SubFlow SHAREDRAILSNOM_SubFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo START_SubFlow; }
  Result 2 { Property PassFail = "Pass"; Return 1; }
 }
 DUTFlowItem START_SubFlow START_SubFlow {
  Result -7 { Property PassFail = "Pass"; Return 1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 6 { Property PassFail = "Fail"; Return 0; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_next(self):
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
START_SubFlow       TPI_FLWFLGS_XXX           r2pn  r3fn
START_SubFlow       TPI_BASE_XXX              r2p:TPI_FLWFLGS_XXX r3pn

MAIN                START_SubFlow             r2f2
'''
            ProgramFlows().main(text, 'MAIN')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow START_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_START TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_BASE_XXX_START; }
  Result 2 { Property PassFail = "Pass"; GoTo TPI_BASE_XXX_START; }
  Result 3 { Property PassFail = "Fail"; GoTo TPI_BASE_XXX_START; }
 }
 DUTFlowItem TPI_BASE_XXX_START TPI_BASE_XXX::TPI_BASE_XXX_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Pass"; GoTo TPI_FLWFLGS_XXX_START; }
  Result 3 { Property PassFail = "Pass"; Return 1; }
 }
}
DUTFlow MAIN {
 DUTFlowItem START_SubFlow START_SubFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Fail"; Return 2; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_default(self):
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
# override port0, no other ports
START_SubFlow       DEFAULTS                  r0f1
START_SubFlow       TPI_FLWFLGS_XXX           r2pn
START_SubFlow       TPI_BASE_XXX

# new port override, port0 must show up
BEGIN_SubFlow       DEFAULTS                  rm3fm3
BEGIN_SubFlow       TPI_BASE_XXX

# below is standard defaults
END_SubFlow         TPI_FLWFLGS_XXX

MAIN                DEFAULTS                          rm1f:ALARM_SubFlow
MAIN                START_SubFlow                     r0pn r2p:END_SubFlow
MAIN                END_SubFlow                       r1p
MAIN                ALARM_SubFlow                     rm1f
'''
            ProgramFlows().main(text, 'MAIN')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow START_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_START TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_START {
  Result 0 { Property PassFail = "Fail"; Return 1; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_BASE_XXX_START; }
  Result 2 { Property PassFail = "Pass"; GoTo TPI_BASE_XXX_START; }
 }
 DUTFlowItem TPI_BASE_XXX_START TPI_BASE_XXX::TPI_BASE_XXX_START {
  Result 0 { Property PassFail = "Fail"; Return 1; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
DUTFlow BEGIN_SubFlow {
 DUTFlowItem TPI_BASE_XXX_BEGIN TPI_BASE_XXX::TPI_BASE_XXX_BEGIN {
  Result -3 { Property PassFail = "Fail"; Return -3; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
DUTFlow END_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_END TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_END {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
DUTFlow MAIN {
 DUTFlowItem START_SubFlow START_SubFlow {
  Result -1 { Property PassFail = "Fail"; GoTo ALARM_SubFlow; }
  Result 0 { Property PassFail = "Pass"; GoTo END_SubFlow; }
  Result 1 { Property PassFail = "Pass"; GoTo END_SubFlow; }
  Result 2 { Property PassFail = "Pass"; GoTo END_SubFlow; }
 }
 DUTFlowItem END_SubFlow END_SubFlow {
  Result -1 { Property PassFail = "Fail"; GoTo ALARM_SubFlow; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
 DUTFlowItem ALARM_SubFlow ALARM_SubFlow {
  Result -1 { Property PassFail = "Fail"; Return 0; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_autoip(self):
        # auto IP
        # MAIN port override
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
START_SubFlow               ARR           r2f3
START_SubFlow               SCN           r2p4

MAIN     START_SubFlow          r4f3
'''
            ProgramFlows().main(text, 'MAIN')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow START_SubFlow {
 DUTFlowItem ARR_START IP_CPU::ARR::ARR_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo SCN_START; }
  Result 2 { Property PassFail = "Fail"; Return 3; }
 }
 DUTFlowItem SCN_START SCN::SCN_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Pass"; Return 4; }
 }
}
DUTFlow MAIN {
 DUTFlowItem START_SubFlow START_SubFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 3 { Property PassFail = "Fail"; Return 0; }
  Result 4 { Property PassFail = "Fail"; Return 3; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_autoipx(self):
        # auto IP
        # MAIN port override
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
START_SubFlow               ARR           r2f3
START_SubFlow               SCN           r2p4

MAIN START_SubFlow          r4f3
'''
            ProgramFlows().main(text, 'MAIN', ip=True)
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow START_SubFlow {
 DUTFlowItem ARR_START ARR::ARR_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo SCN_START; }
  Result 2 { Property PassFail = "Fail"; Return 3; }
 }
 DUTFlowItem SCN_START SCN::SCN_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Pass"; Return 4; }
 }
}
DUTFlow MAIN {
 DUTFlowItem START_SubFlow START_SubFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 3 { Property PassFail = "Fail"; Return 0; }
  Result 4 { Property PassFail = "Fail"; Return 3; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_noclear(self):
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
START_SubFlow               ARR           rm3p r2p
START_SubFlow               SCN           r2f

MAIN START_SubFlow
'''
            ProgramFlows().main(text, 'MAIN')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow START_SubFlow {
 DUTFlowItem ARR_START IP_CPU::ARR::ARR_START {
  Result -3 { Property PassFail = "Pass"; Return 1; }
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo SCN_START; }
  Result 2 { Property PassFail = "Pass"; Return 1; }
 }
 DUTFlowItem SCN_START SCN::SCN_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Fail"; Return 0; }
 }
}
DUTFlow MAIN {
 DUTFlowItem START_SubFlow START_SubFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_mainflow(self):
        # PRLCPU case  - print asis, this is not defined within normal subflows
        # TPI_XXX case - direct module call
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
START_SubFlow       TPI_FLWFLGS_XXX           r2p3 r3f2

MAIN                START_SubFlow                     r2f:TPI_XXX_MAIN r3f:PRLCPU
MAIN                TPI_XXX::TPI_XXX_MAIN
MAIN                $PRLCPU
'''
            ProgramFlows().main(text, 'MAIN')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow START_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_START TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Pass"; Return 3; }
  Result 3 { Property PassFail = "Fail"; Return 2; }
 }
}
DUTFlow MAIN {
 DUTFlowItem START_SubFlow START_SubFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_XXX_MAIN; }
  Result 2 { Property PassFail = "Fail"; GoTo TPI_XXX_MAIN; }
  Result 3 { Property PassFail = "Fail"; GoTo PRLCPU; }
 }
 DUTFlowItem TPI_XXX_MAIN TPI_XXX::TPI_XXX_MAIN {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo PRLCPU; }
 }
 DUTFlowItem PRLCPU PRLCPU {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_nvl_style(self):
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
A_SubFlow           TPI_FLWFLGS_XXX
A_SubFlow           TPI_FLWFLGS_XXY

START_TopFlow       A_SubFlow
START_TopFlow       TPI_FLWFLGS_XXZ::TPI_FLWFLGS_XXZ_START
START_TopFlow       $PRL0

MAIN                START_TopFlow
'''
            ProgramFlows().main(text, 'MAIN')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow A_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_A TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_A {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_FLWFLGS_XXY_A; }
 }
 DUTFlowItem TPI_FLWFLGS_XXY_A TPI_FLWFLGS_XXY::TPI_FLWFLGS_XXY_A {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
DUTFlow START_TopFlow {
 DUTFlowItem A_SubFlow_START A_SubFlow {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_FLWFLGS_XXZ_START_START; }
 }
 DUTFlowItem TPI_FLWFLGS_XXZ_START_START TPI_FLWFLGS_XXZ::TPI_FLWFLGS_XXZ_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo PRL0_START; }
 }
 DUTFlowItem PRL0_START PRL0 {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
DUTFlow MAIN {
 DUTFlowItem START_TopFlow START_TopFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_directcall(self):
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
PRL1                ABC_SubFlow
PRL1                TPI_XXX_XXX::XYZ
PRL1                TPI_XXX_XXX
PRL1                $PRL0

START_TopFlow       HAT_SubFlow
START_TopFlow       TPI_XXX_XXX::XYZ
START_TopFlow       PRL2

MAIN                TPI_XXX_XXX::XYZ            r2f:TPI_XXX_MAIN r3f:PRLCPU
MAIN                PRL1
MAIN                TPI_XXX_MAIN
MAIN                PRLCPU
'''
            ProgramFlows().main(text, 'MAIN')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''DUTFlow PRL1 {
 DUTFlowItem ABC_SubFlow_PRL1 ABC_SubFlow {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo XYZ_PRL1; }
 }
 DUTFlowItem XYZ_PRL1 TPI_XXX_XXX::XYZ {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_XXX_XXX_PRL1; }
 }
 DUTFlowItem TPI_XXX_XXX_PRL1 TPI_XXX_XXX::TPI_XXX_XXX_PRL1 {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo PRL0_PRL1; }
 }
 DUTFlowItem PRL0_PRL1 PRL0 {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
DUTFlow START_TopFlow {
 DUTFlowItem HAT_SubFlow_START HAT_SubFlow {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo XYZ_START; }
 }
 DUTFlowItem XYZ_START TPI_XXX_XXX::XYZ {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo PRL2_START; }
 }
 DUTFlowItem PRL2_START PRL2 {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
DUTFlow MAIN {
 DUTFlowItem XYZ TPI_XXX_XXX::XYZ {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo PRL1; }
  Result 2 { Property PassFail = "Fail"; GoTo TPI_XXX_MAIN; }
  Result 3 { Property PassFail = "Fail"; GoTo PRLCPU; }
 }
 DUTFlowItem PRL1 PRL1 {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_XXX_MAIN; }
 }
 DUTFlowItem TPI_XXX_MAIN TPI_XXX_MAIN {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo PRLCPU; }
 }
 DUTFlowItem PRLCPU PRLCPU {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_ip_programflows(self):
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
PRL0     TPI_FLWFLGS_XXX
PRL0     ABC::DEF
PRL0     HAT_SubFlow
PRL0     $PRL1
'''
            ProgramFlows().main(text, 'IP_PCH')     # Define something non-existent and it will not be printed
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow PRL0 {
 DUTFlowItem TPI_FLWFLGS_XXX_PRL0 TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_PRL0 {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo DEF_PRL0; }
 }
 DUTFlowItem DEF_PRL0 ABC::DEF {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo HAT_SubFlow_PRL0; }
 }
 DUTFlowItem HAT_SubFlow_PRL0 HAT_SubFlow {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo PRL1_PRL0; }
 }
 DUTFlowItem PRL1_PRL0 PRL1 {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)

    @with_(TempDir, chdir=True)
    @with_(MockVar, PyMtpl, '_headers', MagicMock())
    def test_custom_suffix(self):
        # Test custom suffix override using :SUFFIX notation
        OPT.env = f'{UT_DIR_REPO}/Simple7c/POR_TP/TGLH81/EnvironmentFile.env'

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = Initialize('out', 'FUN')
            text = '''
START_SubFlow               TPI_FLWFLGS_XXX:BEGIN     r2p
START_SubFlow               TPI_BASE_XXX              r2p

MAIN                        START_SubFlow
'''
            ProgramFlows().main(text, 'MAIN')
            # End of "python mtpl code"

        PyMtpl().main_one(PyObj)
        expect = '''
DUTFlow START_SubFlow {
 DUTFlowItem TPI_FLWFLGS_XXX_BEGIN TPI_FLWFLGS_XXX::TPI_FLWFLGS_XXX_BEGIN {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; GoTo TPI_BASE_XXX_START; }
  Result 2 { Property PassFail = "Pass"; Return 1; }
 }
 DUTFlowItem TPI_BASE_XXX_START TPI_BASE_XXX::TPI_BASE_XXX_START {
  Result -2 { Property PassFail = "Fail"; Return -2; }
  Result -1 { Property PassFail = "Fail"; Return -1; }
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
  Result 2 { Property PassFail = "Pass"; Return 1; }
 }
}
DUTFlow MAIN {
 DUTFlowItem START_SubFlow START_SubFlow {
  Result 0 { Property PassFail = "Fail"; Return 0; }
  Result 1 { Property PassFail = "Pass"; Return 1; }
 }
}
'''
        self.assertTextEqual(str(Compact('out.mtpl')), expect)


class TestNVL(TestCase):

    def test_4die(self):
        NVLProgramFlows.PORT_DEF = {'CPU': '[-2:-1],  IPC',
                                    'HUB': '[-2:-1],  IPH',
                                    'GCD': '[-2:-1],  IPG',
                                    'PCD': '[-2:-1],  IPP'}

        expect = '''
{'IPC': 'IPC_FLOWS::ENDCPU',
 'IPG': 'IPG_FLOWS::ENDGCD',
 'IPH': 'IPH_FLOWS::ENDHUB',
 'IPP': 'IPP_FLOWS::ENDPCD',
 'result': ['IPC, IPG, IPH, IPP, EffectiveIPResult',
            '[-2:-1], *, *, *,  IPC',
            '*, [-2:-1], *, *,  IPG',
            '*, *, [-2:-1], *,  IPH',
            '*, *, *, [-2:-1],  IPP',
            '0, *, *, *,  IPC',
            '*, 0, *, *,  IPG',
            '*, *, 0, *,  IPH',
            '*, *, *, 0,  IPP',
            '20, *, *, *,  IPC',
            '*, 30, *, *,  IPG',
            '*, *, 40, *,  IPH',
            '*, *, *, 50,  IPP',
            '1, 1, 1, 1,  IPC']}
'''
        self.assertTextEqual(pformat(NVLProgramFlows.get_flow_params(['CPU', 'GCD', 'HUB', 'PCD'], 'END%s')),
                             expect)

    def test_3die(self):
        NVLProgramFlows.PORT_DEF = {'GCD': '[-2:-1], IPG',
                                    'HUB': '[-2:-1], IPH',
                                    'PCD': '[-2:-1], IPP'}

        expect = '''
{'IPG': 'IPG_FLOWS::ENDGCD',
 'IPH': 'IPH_FLOWS::ENDHUB',
 'IPP': 'IPP_FLOWS::ENDPCD',
 'result': ['IPG, IPH, IPP, EffectiveIPResult',
            '[-2:-1], *, *,  IPG',
            '*, [-2:-1], *,  IPH',
            '*, *, [-2:-1],  IPP',
            '0, *, *,  IPG',
            '*, 0, *,  IPH',
            '*, *, 0,  IPP',
            '30, *, *,  IPG',
            '*, 40, *,  IPH',
            '*, *, 50,  IPP',
            '1, 1, 1,  IPH']}
'''
        self.assertTextEqual(pformat(NVLProgramFlows.get_flow_params(['GCD', 'HUB', 'PCD'], 'END%s'), width=60),
                             expect)

    def test_2die(self):
        NVLProgramFlows.PORT_DEF = {'HUB': '[-2:-1], IPH',
                                    'PCD': '[-2:-1], IPP'}

        expect = '''
{'IPH': 'IPH_FLOWS::ENDHUB',
 'IPP': 'IPP_FLOWS::ENDPCD',
 'result': ['IPH, IPP, EffectiveIPResult',
            '[-2:-1], *,  IPH',
            '*, [-2:-1],  IPP',
            '0, *,  IPH',
            '*, 0,  IPP',
            '40, *,  IPH',
            '*, 50,  IPP',
            '1, 1,  IPH']}
'''
        self.assertTextEqual(pformat(NVLProgramFlows.get_flow_params(['HUB', 'PCD'], 'END%s'), width=60),
                             expect)

    def test_1die(self):
        NVLProgramFlows.PORT_DEF = {'HUB': '[-2:-1], IPH'}

        expect = '''
{'IPH': 'IPH_FLOWS::ENDHUB',
 'result': ['IPH, EffectiveIPResult',
            '[-2:-1],  IPH',
            '0,  IPH',
            '40,  IPH',
            '1,  IPH']}
'''
        self.assertTextEqual(pformat(NVLProgramFlows.get_flow_params(['HUB'], 'END%s'), width=60),
                             expect)

    def test_get_subflow_name(self):
        self.assertEqual(NVLProgramFlows.get_subflow_name(['CPU'], 'blah%s'), 'blahCPU')
        with self.assertRaisesRegex(ErrorUser, 'Expecting IP scope'):
            NVLProgramFlows.get_subflow_name(['RZL'], 'blah%s')

    def test_get_module_flow_name(self):
        self.assertEqual(NVLProgramFlows.get_module_flow_name(['CPU'], 'blah%s'), 'IPC::IPC_FLOWS::blahCPU')
        with self.assertRaisesRegex(ErrorUser, 'get_module_flow_name'):
            NVLProgramFlows.get_module_flow_name(['RZL'], 'blah%s')

    def test_strip_dielets_fbist(self):
        # without the marker
        code = '''
SPEEDPREPRL0_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0

STARTCPUPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2
STARTCPUPATMODSPKG     DRV_FBIST_XXX        rm2fm2

STARTGCDPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2

STARTHUBPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2

STARTPCDPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2

SPEEDPREPRL1_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0

HUBIPFF_SubFlow        TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1

HUBIPFF_SubFlow        DRV_RESET_HXX        rm2fm2 rm1fm1 r0f0

'''
        expect = '''
SPEEDPREPRL0_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0

STARTCPUPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2
STARTCPUPATMODSPKG     DRV_FBIST_XXX        rm2fm2

STARTGCDPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2



SPEEDPREPRL1_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0



'''
        self.assertTextEqual(NVLProgramFlows.strip_dielets(code, 'CPU GCD'.split()), expect)

        # with marker
        code = '''
# FULLTPONLY: DRV_FBIST_XXX
# FULLTPONLY: DRV_FBIST_YYY
SPEEDPREPRL0_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0

STARTCPUPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2
STARTCPUPATMODSPKG     DRV_FBIST_XXX        rm2fm2

STARTGCDPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2
STARTGCDPATMODSPKG     DRV_FBIST_YYY        rm2fm2

STARTHUBPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2

STARTPCDPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2

SPEEDPREPRL1_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0

HUBIPFF_SubFlow        TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1

HUBIPFF_SubFlow        DRV_RESET_HXX        rm2fm2 rm1fm1 r0f0
'''
        expect = '''
# FULLTPONLY: DRV_FBIST_XXX
# FULLTPONLY: DRV_FBIST_YYY
SPEEDPREPRL0_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0

STARTCPUPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2

STARTGCDPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2



SPEEDPREPRL1_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0


'''
        self.assertTextEqual(NVLProgramFlows.strip_dielets(code, 'CPU GCD'.split()), expect)

    def test_strip_dielets(self):
        code = '''
SPEEDPREPRL0_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0

STARTCPUPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2

STARTGCDPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2

STARTHUBPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2

STARTPCDPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2

SPEEDPREPRL1_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0

HUBIPFF_SubFlow        TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1

HUBIPFF_SubFlow        DRV_RESET_HXX        rm2fm2 rm1fm1 r0f0

MAIN             START_TopFlow               r20f:CPUIPFF_SubFlow r30f:GCDIPFF_SubFlow r40f:HUBIPFF_SubFlow
MAIN             HVBI_TopFlow                r20f:CPUIPFF_SubFlow r30f:GCDIPFF_SubFlow r40f:HUBIPFF_SubFlow
MAIN             HUBIPFF_SubFlow                rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:PKGFF_SubFlow r1f:HUBPKGFF_SubFlow
MAIN             PCDIPFF_SubFlow                rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:PKGFF_SubFlow r1f:PCDPKGFF_SubFlow
'''
        self.assertTextEqual(NVLProgramFlows.strip_dielets(code, 'CPU GCD HUB PCD'.split()), code)

        expect = '''
SPEEDPREPRL0_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0



STARTHUBPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2


SPEEDPREPRL1_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0

HUBIPFF_SubFlow        TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0 r2p1

HUBIPFF_SubFlow        DRV_RESET_HXX        rm2fm2 rm1fm1 r0f0

MAIN             START_TopFlow               r20f:CPUIPFF_SubFlow r30f:GCDIPFF_SubFlow r40f:HUBIPFF_SubFlow
MAIN             HVBI_TopFlow                r20f:CPUIPFF_SubFlow r30f:GCDIPFF_SubFlow r40f:HUBIPFF_SubFlow
MAIN             HUBIPFF_SubFlow                rm2f:ALARM_SubFlow rm1f:ALARM_SubFlow r0f:PKGFF_SubFlow r1f:HUBPKGFF_SubFlow
'''
        self.assertTextEqual(NVLProgramFlows.strip_dielets(code, 'HUB'.split()), expect)

        expect = '''
SPEEDPREPRL0_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0

STARTCPUPATMODSPKG     TPI_FLWFLGS_XXX      rm2fm2




SPEEDPREPRL1_SubFlow   TPI_FLWFLGS_XXX      rm2fm2 rm1fm1 r0f0



MAIN             START_TopFlow               r20f:CPUIPFF_SubFlow r30f:GCDIPFF_SubFlow r40f:FINAL_SubFlow
MAIN             HVBI_TopFlow                r20f:CPUIPFF_SubFlow r30f:GCDIPFF_SubFlow r40f:FINAL_SubFlow

'''
        self.assertTextEqual(NVLProgramFlows.strip_dielets(code, 'CPU'.split()), expect)

        # Test for regex, need a "string" before the diename and should be less than 8 chars
        code2 = '''
ACPUBLAH      TPI_FLWFLGS_XXX

STARTPATMODSPKGVERYLONGBLAHCPU   TPI_FLWFLGS_XXX


CPUBLAH      TPI_FLWFLGS_XXX

Some_TopFlow  STARTCPU_SubFlow
Some_TopFlow  STARTGCD_SubFlow
'''
        expect = '''

STARTPATMODSPKGVERYLONGBLAHCPU   TPI_FLWFLGS_XXX


CPUBLAH      TPI_FLWFLGS_XXX

Some_TopFlow  STARTGCD_SubFlow
'''
        self.assertTextEqual(NVLProgramFlows.strip_dielets(code2, 'GCD'.split()), expect)

    def test_ignore_emptycomp(self):
        # One die with ###
        die_combo1 = ['GCD']
        comp_name1 = '''
INIT_SubFlow               TPI_BASE_XXX::TPI_BASE_XXX_INIT              rm2fm2 rm1fm1 r0f0
INIT_SubFlow               TPI_XIU_XXX::TPI_XIU_XXX_INIT                rm2fm2 rm1fm1 r0f0

###INITGCDPKG_SubFlow   Your_Module_Name::Your_Module_Name_INIT        rm2fm2 rm1fm1 r0f0

INITGCD_SubFlow          IPG::TPI_GFXAGG_GXX::TPI_GFXAGG_GXX_INIT       rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_FUSECFG_GXX::FUS_FUSECFG_GXX_INIT     rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_UNITINFO_GXX::FUS_UNITINFO_GXX_INIT   rm2fm2 rm1fm1 r0f0

INITLAST_SubFlow           TPI_END_XXX::TPI_END_XXX_INIT                rm2fm2 rm1fm1 r0f0

INIT         INIT_SubFlow          rm2fm2 rm1fm1 r0f0
INIT         INITGCDPKG_SubFlow    rm2fm2 rm1fm1 r0f0
INIT         INITGCD_SubFlow       rm2fm2 rm1fm1 r0f0
INIT         INITLAST_SubFlow      rm2fm2 rm1fm1 r0f0
'''
        expect = '''
INIT_SubFlow               TPI_BASE_XXX::TPI_BASE_XXX_INIT              rm2fm2 rm1fm1 r0f0
INIT_SubFlow               TPI_XIU_XXX::TPI_XIU_XXX_INIT                rm2fm2 rm1fm1 r0f0

###INITGCDPKG_SubFlow   Your_Module_Name::Your_Module_Name_INIT        rm2fm2 rm1fm1 r0f0

INITGCD_SubFlow          IPG::TPI_GFXAGG_GXX::TPI_GFXAGG_GXX_INIT       rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_FUSECFG_GXX::FUS_FUSECFG_GXX_INIT     rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_UNITINFO_GXX::FUS_UNITINFO_GXX_INIT   rm2fm2 rm1fm1 r0f0

INITLAST_SubFlow           TPI_END_XXX::TPI_END_XXX_INIT                rm2fm2 rm1fm1 r0f0

INIT         INIT_SubFlow          rm2fm2 rm1fm1 r0f0
INIT         INITGCD_SubFlow       rm2fm2 rm1fm1 r0f0
INIT         INITLAST_SubFlow      rm2fm2 rm1fm1 r0f0
'''
        self.assertTextEqual(NVLProgramFlows.ignore_emptycomp(comp_name1, die_combo1), expect)

        # Two dielets with ###
        die_combo2 = ['GCD', 'HUB']
        comp_name2 = '''
INIT_SubFlow               TPI_BASE_XXX::TPI_BASE_XXX_INIT              rm2fm2 rm1fm1 r0f0
INIT_SubFlow               TPI_XIU_XXX::TPI_XIU_XXX_INIT                rm2fm2 rm1fm1 r0f0

###INITGCDPKG_SubFlow   Your_Module_Name::Your_Module_Name_INIT        rm2fm2 rm1fm1 r0f0
###INITHUBPKG_SubFlow   Your_Module_Name::Your_Module_Name_INIT        rm2fm2 rm1fm1 r0f0

INITGCD_SubFlow          IPG::TPI_GFXAGG_GXX::TPI_GFXAGG_GXX_INIT       rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_FUSECFG_GXX::FUS_FUSECFG_GXX_INIT     rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_UNITINFO_GXX::FUS_UNITINFO_GXX_INIT   rm2fm2 rm1fm1 r0f0

INITLAST_SubFlow           TPI_END_XXX::TPI_END_XXX_INIT                rm2fm2 rm1fm1 r0f0

INIT         INIT_SubFlow          rm2fm2 rm1fm1 r0f0
INIT         INITGCDPKG_SubFlow    rm2fm2 rm1fm1 r0f0
INIT         INITHUBPKG_SubFlow    rm2fm2 rm1fm1 r0f0
INIT         INITGCD_SubFlow       rm2fm2 rm1fm1 r0f0
INIT         INITLAST_SubFlow      rm2fm2 rm1fm1 r0f0
'''
        expect = '''
INIT_SubFlow               TPI_BASE_XXX::TPI_BASE_XXX_INIT              rm2fm2 rm1fm1 r0f0
INIT_SubFlow               TPI_XIU_XXX::TPI_XIU_XXX_INIT                rm2fm2 rm1fm1 r0f0

###INITGCDPKG_SubFlow   Your_Module_Name::Your_Module_Name_INIT        rm2fm2 rm1fm1 r0f0
###INITHUBPKG_SubFlow   Your_Module_Name::Your_Module_Name_INIT        rm2fm2 rm1fm1 r0f0

INITGCD_SubFlow          IPG::TPI_GFXAGG_GXX::TPI_GFXAGG_GXX_INIT       rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_FUSECFG_GXX::FUS_FUSECFG_GXX_INIT     rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_UNITINFO_GXX::FUS_UNITINFO_GXX_INIT   rm2fm2 rm1fm1 r0f0

INITLAST_SubFlow           TPI_END_XXX::TPI_END_XXX_INIT                rm2fm2 rm1fm1 r0f0

INIT         INIT_SubFlow          rm2fm2 rm1fm1 r0f0
INIT         INITGCD_SubFlow       rm2fm2 rm1fm1 r0f0
INIT         INITLAST_SubFlow      rm2fm2 rm1fm1 r0f0
'''

        self.assertTextEqual(NVLProgramFlows.ignore_emptycomp(comp_name2, die_combo2), expect)

        # Two dielets without ###
        die_combo3 = ['GCD', 'HUB']
        comp_name3 = '''
INIT_SubFlow               TPI_BASE_XXX::TPI_BASE_XXX_INIT              rm2fm2 rm1fm1 r0f0
INIT_SubFlow               TPI_XIU_XXX::TPI_XIU_XXX_INIT                rm2fm2 rm1fm1 r0f0

INITGCDPKG_SubFlow   Your_Module_Name::Your_Module_Name_INIT        rm2fm2 rm1fm1 r0f0
INITHUBPKG_SubFlow   Your_Module_Name::Your_Module_Name_INIT        rm2fm2 rm1fm1 r0f0

INITGCD_SubFlow          IPG::TPI_GFXAGG_GXX::TPI_GFXAGG_GXX_INIT       rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_FUSECFG_GXX::FUS_FUSECFG_GXX_INIT     rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_UNITINFO_GXX::FUS_UNITINFO_GXX_INIT   rm2fm2 rm1fm1 r0f0

INITLAST_SubFlow           TPI_END_XXX::TPI_END_XXX_INIT                rm2fm2 rm1fm1 r0f0

INIT         INIT_SubFlow          rm2fm2 rm1fm1 r0f0
INIT         INITGCDPKG_SubFlow    rm2fm2 rm1fm1 r0f0
INIT         INITHUBPKG_SubFlow    rm2fm2 rm1fm1 r0f0
INIT         INITGCD_SubFlow       rm2fm2 rm1fm1 r0f0
INIT         INITLAST_SubFlow      rm2fm2 rm1fm1 r0f0
'''
        expect = '''
INIT_SubFlow               TPI_BASE_XXX::TPI_BASE_XXX_INIT              rm2fm2 rm1fm1 r0f0
INIT_SubFlow               TPI_XIU_XXX::TPI_XIU_XXX_INIT                rm2fm2 rm1fm1 r0f0

INITGCDPKG_SubFlow   Your_Module_Name::Your_Module_Name_INIT        rm2fm2 rm1fm1 r0f0
INITHUBPKG_SubFlow   Your_Module_Name::Your_Module_Name_INIT        rm2fm2 rm1fm1 r0f0

INITGCD_SubFlow          IPG::TPI_GFXAGG_GXX::TPI_GFXAGG_GXX_INIT       rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_FUSECFG_GXX::FUS_FUSECFG_GXX_INIT     rm2fm2 rm1fm1 r0f0
INITGCD_SubFlow          IPG::FUS_UNITINFO_GXX::FUS_UNITINFO_GXX_INIT   rm2fm2 rm1fm1 r0f0

INITLAST_SubFlow           TPI_END_XXX::TPI_END_XXX_INIT                rm2fm2 rm1fm1 r0f0

INIT         INIT_SubFlow          rm2fm2 rm1fm1 r0f0
INIT         INITGCDPKG_SubFlow    rm2fm2 rm1fm1 r0f0
INIT         INITHUBPKG_SubFlow    rm2fm2 rm1fm1 r0f0
INIT         INITGCD_SubFlow       rm2fm2 rm1fm1 r0f0
INIT         INITLAST_SubFlow      rm2fm2 rm1fm1 r0f0
'''

        self.assertTextEqual(NVLProgramFlows.ignore_emptycomp(comp_name3, die_combo3), expect)


class TestGetBinLimitsFromJson(TestCase):

    @with_(TempDir, chdir=True)
    def test_missing_json_file(self):
        # folder and files don't exist
        # expect error
        with self.assertRaisesRegex(ErrorUser, 'Bin Limits file not found'):
            # don't get a valid one
            result = get_bin_limits_from_json('MIO_DDR')

    @with_(TempDir, chdir=True)
    def test_basic_limits(self):
        # Create test JSON file
        File('MIO_DDR.BinLimits.json').touch(
            '{"BinLimits": [[900, 999],[6800, 6899]]}'
        )

        # call
        result = get_bin_limits_from_json('MIO_DDR')
        self.assertEqual(result, [(900, 999), (6800, 6899)])

    @with_(TempDir, chdir=True)
    def test_missing_binlimits_error(self):
        # Create test JSON file
        File('MIO_DDR.BinLimits.json').touch(
            '{"Incorrect": [[900, 999],[6800, 6899]]}'
        )

        # call
        with self.assertRaisesRegex(ErrorUser, 'BinLimits key not found'):
            result = get_bin_limits_from_json('MIO_DDR')

    @with_(TempDir, chdir=True)
    def test_invalid_json_format(self):
        # Create a test JSON file with invalid JSON format
        File('MIO_DDR.BinLimits.json').touch(
            '{"BinLimits": [[900, 999],[6800, 6899]'  # Missing closing brackets
        )

        # call
        with self.assertRaisesRegex(json.decoder.JSONDecodeError, "Expecting ',' delimiter") \
                and self.assertRaisesRegex(ErrorInput, 'json read exception'):

            result = get_bin_limits_from_json('MIO_DDR')

    @with_(TempDir, chdir=True)
    def test_invalid_bin_limit_pair_length(self):
        # Create a test JSON file where a bin limit doesn't have exactly 2 elements
        File('MIO_DDR.BinLimits.json').touch(
            '{"BinLimits": [[900, 999, 1000], [6800, 6899]]}'
        )

        # call
        with self.assertRaisesRegex(ErrorUser, 'exactly two elements'):
            result = get_bin_limits_from_json('MIO_DDR')

    @with_(TempDir, chdir=True)
    def test_invalid_bin_limit_non_numeric(self):
        # Create a test JSON file where bin limit values are not numeric
        File('MIO_DDR.BinLimits.json').touch(
            '{"BinLimits": [["abc", 999], [6800, 6899]]}'
        )

        # call
        with self.assertRaisesRegex(ErrorUser, 'should be integers'):
            result = get_bin_limits_from_json('MIO_DDR')

    @with_(TempDir, chdir=True)
    def test_invalid_bin_limit_range(self):
        # Create a test JSON file where the first value is greater than the second
        File('MIO_DDR.BinLimits.json').touch(
            '{"BinLimits": [[999, 900], [6800, 6899]]}'
        )

        # call
        with self.assertRaisesRegex(ErrorUser, 'must be less than'):
            result = get_bin_limits_from_json('MIO_DDR')

    @with_(TempDir, chdir=True)
    def test_invalid_negative(self):
        # Create a test JSON file where the first value is greater than the second
        File('MIO_DDR.BinLimits.json').touch(
            '{"BinLimits": [[-900, 999], [6800, 6899]]}'
        )

        # call
        with self.assertRaisesRegex(ErrorUser, 'non-negative'):
            result = get_bin_limits_from_json('MIO_DDR')

    @with_(TempDir, chdir=True)
    def test_alternate_path_when_main_missing(self):
        # Test that alternate path (.BinLimits.json) is used when main path doesn't exist
        # Create only alternate JSON file (without module name prefix)
        File('.BinLimits.json').touch(
            '{"BinLimits": [[900, 999],[6800, 6899]]}'
        )

        # call with module name that doesn't have a matching file
        result = get_bin_limits_from_json('MIO_DDR')
        # Should successfully use alternate path
        self.assertEqual(result, [(900, 999), (6800, 6899)])

    @with_(TempDir, chdir=True)
    def test_neither_path_exists(self):
        # Test error when neither main nor alternate path exists
        # Don't create any files

        # call
        with self.assertRaisesRegex(ErrorUser, 'Bin Limits file not found'):
            result = get_bin_limits_from_json('MIO_DDR')


class TestCreateTestInstanceWithDefaults(TestCase):

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_just_kwargs(self):
        """ Test creating a test instance with just keyword arguments, not using defaults """
        class PyObj1:
            output = Initialize('out', 'FUN')
            subflow = Flow('SubFlow1', [
                create_test_instance_with_defaults(VminTC, name="Instance1", EndVoltageLimits="0.9",
                                                   _fitem=Fitem(r0=pFail()))])

        PyMtpl().main_one(PyObj1)

        # We expect the counters to prevent the same bins from being used
        expect = '''
Test VminTC Instance1
{
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_nonoverlap_defaults_and_kwargs(self):
        """ Test creating a test instance with non-overlapping defaults and keyword arguments """
        class PyObj1:
            output = Initialize('out', 'FUN')
            subflow = Flow('SubFlow1', [
                create_test_instance_with_defaults(VminTC, defaults={"Patlist": "plist1"}, name="Instance1", EndVoltageLimits="0.9",
                                                   _fitem=Fitem(r0=pFail()))])

        PyMtpl().main_one(PyObj1)

        # We expect the counters to prevent the same bins from being used
        expect = '''
Test VminTC Instance1
{
    Patlist = "plist1";
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

DUTFlow SubFlow1
{
    DUTFlowItem Instance1 Instance1
    {
        Result 0
        {
            Property PassFail = "Fail";
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}

        '''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_overlap_defaults_and_kwargs(self):
        """ Test creating a test instance with overlapping defaults and keyword arguments """
        class PyObj1:
            output = Initialize('out', 'FUN')
            subflow = Flow('SubFlow1', [
                create_test_instance_with_defaults(VminTC, defaults={"Patlist": "plist1"}, name="Instance1", EndVoltageLimits="0.9", Patlist="plist2",
                                                   _fitem=Fitem(r0=pFail()))])

        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertIn('Patlist = "plist2"', readout)
        self.assertIn('EndVoltageLimits = "0.9"', readout)
        self.assertIn('FailCaptureCount = 999', readout)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.binctr.CtrHBSB.get_portctrstring', Mock(return_value=''))
    @patch('pymtpl.core.PyMtpl._headers', MagicMock())
    def test_partial_simple(self):
        """ Creating the test instance with partial, the intended use case """
        MyVminTC = partial(create_test_instance_with_defaults, VminTC, defaults={"Patlist": "plist1", "EndVoltageLimits": "0.9"})

        class PyObj1:
            output = Initialize('out', 'FUN')
            subflow = Flow('SubFlow1', [
                MyVminTC(name="Instance1", Patlist="plist2",
                         _fitem=Fitem(r0=pFail()))])

        PyMtpl().main_one(PyObj1)
        readout = File('out.mtpl').read()
        self.assertIn('Patlist = "plist2"', readout)
        self.assertIn('EndVoltageLimits = "0.9"', readout)

    def test_missing_required_param(self):
        """ Test that an error is raised if a required parameter is not provided """
        from pymtpl.por_methods_default import VminTC  # this version has more required parameters
        MyVminTC = partial(create_test_instance_with_defaults, VminTC, defaults={"Patlist": "plist1"})
        with self.assertRaisesRegex(ErrorUser, 'Missing required parameter'):
            class PyObj1:
                output = Initialize('out', 'FUN')
                subflow = Flow('SubFlow1', [
                    MyVminTC(name="Instance1", _fitem=Fitem(r0=pFail()))])
            PyMtpl().main_one(PyObj1)

    def test_testmethod_none(self):
        """ Test that an error is raised if user forgets to specify the testmethod """
        MyVminTC = partial(create_test_instance_with_defaults)
        with self.assertRaisesRegex(ErrorUser, 'Error, testmethod is None on line'):
            class PyObj1:
                output = Initialize('out', 'FUN')
                subflow = Flow('SubFlow1', [
                    MyVminTC(name="Instance1",
                             _fitem=Fitem(r0=pFail()))])
            PyMtpl().main_one(PyObj1)

    def test_not_callable(self):
        """ Test that an error is raised if user doesn't pass the class properly """
        MyVminTC = partial(create_test_instance_with_defaults, "VminTC")
        with self.assertRaisesRegex(ErrorUser, 'testmethod must be a class'):
            class PyObj1:
                output = Initialize('out', 'FUN')
                subflow = Flow('SubFlow1', [
                    MyVminTC(name="Instance1",
                             _fitem=Fitem(r0=pFail()))])
            PyMtpl().main_one(PyObj1)

    def test_defaults_not_dict(self):
        """ test raising an error when defaults is not a dict."""
        MyVminTC = partial(create_test_instance_with_defaults, VminTC, defaults=['not', 'a', 'dict'])
        with self.assertRaisesRegex(ErrorUser, 'defaults must be a dict'):
            class PyObj1:
                output = Initialize('out', 'FUN')
                subflow = Flow('SubFlow1', [
                    MyVminTC(name="Instance1",
                             _fitem=Fitem(r0=pFail()))])
            PyMtpl().main_one(PyObj1)


class TestInputFile(TestCase):
    """
    Testing inputfile and InputFilePathOptions
    """

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_basic(self):
        # basic filename
        self.assertTextEqual(inputfile('myctv.json'), Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/myctv.json"'))
        # multiple extension filename
        self.assertTextEqual(inputfile('myctv.smartctv.json'), Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/myctv.smartctv.json"'))
        # with folder
        self.assertTextEqual(inputfile(r"folder\myctv.json"), Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/folder/myctv.json"'))
        # folder using forward slash instead of backslash
        self.assertTextEqual(inputfile('folder/myctv.json'), Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/folder/myctv.json"'))
        # double forwardslash
        self.assertTextEqual(inputfile('folder//myctv.json'), Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/folder/myctv.json"'))
        # double backslash
        self.assertTextEqual(inputfile('folder\\myctv.json'), Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/folder/myctv.json"'))

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_use_spec_false(self):
        original_use_spec = InputFilePathOptions.USE_SPEC
        InputFilePathOptions.USE_SPEC = False
        try:
            # basic filename
            self.assertTextEqual(inputfile('myctv.json'), rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/myctv.json"')
        finally:
            InputFilePathOptions.USE_SPEC = original_use_spec

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='overridden'))
    def test_override_path(self):
        orig_path = InputFilePathOptions.OVERRIDE_INPUTFILE_PATH
        orig_use_spec = InputFilePathOptions.USE_SPEC
        try:
            InputFilePathOptions.USE_SPEC = False
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = './Shared/Modules/MIO/MIO_DDR/InputFiles'
            # basic filename
            self.assertTextEqual(inputfile('myctv.json'), "./Shared/Modules/MIO/MIO_DDR/InputFiles/myctv.json")
            # backslashes in path
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = r'.\\Shared\\Modules\\MIO\\MIO_DDR\\InputFiles'
            self.assertTextEqual(inputfile('myctv.json'), r".\\Shared\\Modules\\MIO\\MIO_DDR\\InputFiles/myctv.json")
        finally:
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = orig_path
            InputFilePathOptions.USE_SPEC = orig_use_spec

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='overridden'))
    def test_override_path_env(self):
        orig_path = InputFilePathOptions.OVERRIDE_INPUTFILE_PATH
        orig_use_spec = InputFilePathOptions.USE_SPEC
        try:
            # make sure we get the right number of "
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Shared/Modules/PTH/PTH_DTS/InputFiles'
            self.assertTextEqual(inputfile('myctv.json'), r'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Shared/Modules/PTH/PTH_DTS/InputFiles/myctv.json"')
            self.assertTextEqual(inputfile(), r'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Shared/Modules/PTH/PTH_DTS/InputFiles"')
        finally:
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = orig_path
            InputFilePathOptions.USE_SPEC = orig_use_spec

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='overridden'))
    def test_override_path_usrv(self):
        orig_path = InputFilePathOptions.OVERRIDE_INPUTFILE_PATH
        orig_join = InputFilePathOptions.JOINING_OPERATOR
        try:
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = 'PTH_DTS.InputFilePath'
            InputFilePathOptions.JOINING_OPERATOR = ' + "'
            # make sure we get the right number of " and +
            self.assertTextEqual(inputfile('myctv.json'), r'PTH_DTS.InputFilePath + "myctv.json"')
            self.assertTextEqual(inputfile(), r'PTH_DTS.InputFilePath')
        finally:
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = orig_path
            InputFilePathOptions.JOINING_OPERATOR = orig_join

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_errors(self):
        # int, float, negative int, arr
        for input in [1, 1.0, -1, ["1", "2"]]:
            with self.subTest(input=input):  # if this test fails, this shows each fail individually so it's easier to debug
                with self.assertRaisesRegex(ErrorUser, 'string or None'):
                    result = inputfile(input)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_get_path(self):
        # get path
        for (input) in ['', None]:
            with self.subTest(input=input):
                self.assertTextEqual(inputfile(input), Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/"'))
        self.assertTextEqual(inputfile(), Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/"'))

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_get_path_override(self):
        orig_path = InputFilePathOptions.OVERRIDE_INPUTFILE_PATH
        orig_use_spec = InputFilePathOptions.USE_SPEC
        try:
            InputFilePathOptions.USE_SPEC = False
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = './Shared/Modules/MIO/MIO_DDR/InputFiles'
            # get path
            for (input) in ['', None]:
                with self.subTest(input=input):
                    self.assertTextEqual(inputfile(input), "./Shared/Modules/MIO/MIO_DDR/InputFiles")
            self.assertTextEqual(inputfile(), "./Shared/Modules/MIO/MIO_DDR/InputFiles")
        finally:
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = orig_path
            InputFilePathOptions.USE_SPEC = orig_use_spec


class TestInputFilePathFromUserVar(TestCase):
    # Testing InputFilePathOptions.InputFilePathFromUserVar classmethod

    def setUp(self):
        # Save current state and reset to defaults
        self.saved_use_spec = InputFilePathOptions.USE_SPEC
        self.saved_override_path = InputFilePathOptions.OVERRIDE_INPUTFILE_PATH
        self.saved_joining_operator = InputFilePathOptions.JOINING_OPERATOR
        InputFilePathOptions.reset()

    def tearDown(self):
        # Restore original state
        InputFilePathOptions.USE_SPEC = self.saved_use_spec
        InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = self.saved_override_path
        InputFilePathOptions.JOINING_OPERATOR = self.saved_joining_operator

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='PTH_DTS'))
    def test_basic_with_spec(self):
        # Test with a Spec object (simulating usrv.InputFilePath)
        from pymtpl.core import Spec
        uservar_ref = Spec('PTH_DTS.InputFilePath')
        InputFilePathOptions.InputFilePathFromUserVar(uservar_ref)

        # Verify settings were applied correctly
        self.assertEqual(InputFilePathOptions.OVERRIDE_INPUTFILE_PATH, 'PTH_DTS.InputFilePath')
        self.assertEqual(InputFilePathOptions.JOINING_OPERATOR, ' + "')

        # Test that inputfile() works correctly with these settings
        self.assertTextEqual(inputfile('myctv.json'), r'PTH_DTS.InputFilePath + "myctv.json"')
        self.assertTextEqual(inputfile(), r'PTH_DTS.InputFilePath')

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='PTH_DTS'))
    def test_basic_with_string(self):
        # Test with a plain string
        InputFilePathOptions.InputFilePathFromUserVar('PTH_DTS.InputFilePath')

        # Verify settings were applied correctly
        self.assertEqual(InputFilePathOptions.OVERRIDE_INPUTFILE_PATH, 'PTH_DTS.InputFilePath')
        self.assertEqual(InputFilePathOptions.JOINING_OPERATOR, ' + "')

        # Test that inputfile() works correctly with these settings
        self.assertTextEqual(inputfile('config.csv'), r'PTH_DTS.InputFilePath + "config.csv"')
        self.assertTextEqual(inputfile('folder/file.txt'), r'PTH_DTS.InputFilePath + "folder/file.txt"')

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_with_different_module(self):
        # Test with a different module name
        InputFilePathOptions.InputFilePathFromUserVar('MIO_DDR.InputFilePath')

        self.assertEqual(InputFilePathOptions.OVERRIDE_INPUTFILE_PATH, 'MIO_DDR.InputFilePath')
        self.assertEqual(InputFilePathOptions.JOINING_OPERATOR, ' + "')

        self.assertTextEqual(inputfile('test.dat'), r'MIO_DDR.InputFilePath + "test.dat"')

    @with_(TempDir, chdir=True)
    def test_errors(self):
        # Test error handling for invalid inputs
        # None should raise error
        with self.assertRaisesRegex(ErrorUser, 'non-empty string'):
            InputFilePathOptions.InputFilePathFromUserVar(None)

        # Empty string should raise error
        with self.assertRaisesRegex(ErrorUser, 'non-empty string'):
            InputFilePathOptions.InputFilePathFromUserVar('')

        # Whitespace-only string should raise error
        with self.assertRaisesRegex(ErrorUser, 'whitespace-only strings are not allowed'):
            InputFilePathOptions.InputFilePathFromUserVar('   ')

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='PTH_DTS'))
    def test_whitespace_handling(self):
        # Test that leading/trailing whitespace is stripped
        from pymtpl.core import Spec
        # String with leading/trailing whitespace
        InputFilePathOptions.InputFilePathFromUserVar('  PTH_DTS.InputFilePath  ')

        # Verify whitespace was stripped
        self.assertEqual(InputFilePathOptions.OVERRIDE_INPUTFILE_PATH, 'PTH_DTS.InputFilePath')
        self.assertEqual(InputFilePathOptions.JOINING_OPERATOR, ' + "')

        # Test that it works correctly with inputfile
        self.assertTextEqual(inputfile('test.csv'), r'PTH_DTS.InputFilePath + "test.csv"')

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='PTH_DTS'))
    def test_integration_with_uservars(self):
        # Test integration with actual UserVars usage
        from pymtpl.uservars import UserVars
        from pymtpl.core import Spec

        # Clear any existing UserVars
        UserVars.clear_registry()

        try:
            # Create a UserVars instance
            usrv = UserVars('PTH_DTS')
            usrv.InputFilePath = ('GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/PTH_DTS/InputFiles/"', str)

            # When accessing usrv.InputFilePath, it returns a Spec('PTH_DTS.InputFilePath')
            uservar_ref = usrv.InputFilePath

            # Verify it's a Spec object
            self.assertIsInstance(uservar_ref, Spec)
            self.assertEqual(str(uservar_ref), 'PTH_DTS.InputFilePath')

            # Use the new method
            InputFilePathOptions.InputFilePathFromUserVar(uservar_ref)

            # Verify settings
            self.assertEqual(InputFilePathOptions.OVERRIDE_INPUTFILE_PATH, 'PTH_DTS.InputFilePath')
            self.assertEqual(InputFilePathOptions.JOINING_OPERATOR, ' + "')

            # Test inputfile works correctly
            self.assertTextEqual(inputfile('config.csv'), r'PTH_DTS.InputFilePath + "config.csv"')
        finally:
            UserVars.clear_registry()


class TestInputFileSelectorRule(TestCase):
    """
    Testing inputfile_selector_rule
    """

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_basic(self):
        # direct writing every field
        self.assertTextEqual(inputfile_selector_rule('hot.csv', 'cold.csv', selectorrule='TPKNOBS.TEMP', argcount=2),
                             Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/" + TPKNOBS.TEMP("hot.csv", "cold.csv")')
                             )

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_errors(self):
        with self.assertRaisesRegex(ErrorUser, 'non-empty string'):
            inputfile_selector_rule('hot.csv', 'cold.csv')
        with self.assertRaisesRegex(ErrorUser, 'non-empty string'):
            inputfile_selector_rule('hot.csv', 'cold.csv', selectorrule=2)
        with self.assertRaisesRegex(ErrorUser, 'no argcount'):
            inputfile_selector_rule('hot.csv', 'cold.csv', selectorrule='TPKNOBS.TEMP')
        with self.assertRaisesRegex(ErrorUser, 'arguments, got'):
            inputfile_selector_rule('hot.csv', 'cold.csv', selectorrule='TPKNOBS.TEMP', argcount=3)
        with self.assertRaisesRegex(ErrorUser, 'arguments, got'):
            inputfile_selector_rule('hot.csv', 'cold.csv', selectorrule='TPKNOBS.TEMP', argcount=1)
        with self.assertRaisesRegex(ErrorUser, 'arguments, got'):
            inputfile_selector_rule(selectorrule='TPKNOBS.TEMP', argcount=3)

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_partial(self):
        # partial function with some defaults
        MyInputFileSelectorRule = partial(inputfile_selector_rule, selectorrule='TPKNOBS.TEMP', argcount=2)
        self.assertTextEqual(MyInputFileSelectorRule('hot.csv', 'cold.csv'),
                             Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Modules/MIO_DDR/InputFiles/" + TPKNOBS.TEMP("hot.csv", "cold.csv")')
                             )

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_partial_env(self):
        # partial function with some defaults, a uservar, intended usage
        orig_path = InputFilePathOptions.OVERRIDE_INPUTFILE_PATH
        try:
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = 'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Shared/Modules/PTH/PTH_DTS/InputFiles'
            MyInputFileSelectorRule = partial(inputfile_selector_rule, selectorrule='TPKNOBS.TEMP', argcount=2)
            self.assertTextEqual(MyInputFileSelectorRule('hot.csv', 'cold.csv'),
                                 Spec(rf'GetEnvironmentVariable("~HDMT_TP_BASE_DIR") + "/Shared/Modules/PTH/PTH_DTS/InputFiles" + TPKNOBS.TEMP("hot.csv", "cold.csv")')
                                 )
        finally:
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = orig_path

    @with_(TempDir, chdir=True)
    @patch('pymtpl.core.Initialize.get_modulename', Mock(return_value='MIO_DDR'))
    def test_partial_usrv(self):
        # partial function with some defaults, a uservar, intended usage
        orig_path = InputFilePathOptions.OVERRIDE_INPUTFILE_PATH
        orig_join = InputFilePathOptions.JOINING_OPERATOR
        try:
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = 'MIO_DDR.InputFilePath'
            InputFilePathOptions.JOINING_OPERATOR = ' + "'
            MyInputFileSelectorRule = partial(inputfile_selector_rule, selectorrule='TPKNOBS.CHOP', argcount=3)
            self.assertTextEqual(MyInputFileSelectorRule('xcc.csv', 'lcc.csv', 'ucc.csv'),
                                 Spec(rf'MIO_DDR.InputFilePath + TPKNOBS.CHOP("xcc.csv", "lcc.csv", "ucc.csv")')
                                 )
        finally:
            InputFilePathOptions.OVERRIDE_INPUTFILE_PATH = orig_path
            InputFilePathOptions.JOINING_OPERATOR = orig_join


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
