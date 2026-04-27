#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unitest for methods
UT_DIR_REPO var is - /intel/tpvalidation/engtools/tptools/mtl/unittests/
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option, Mock
from gadget.gizmo import MockVar, with_
from gadget.files import TempDir, File
from pymtpl.autobinctrupdate import UpdateAutobinAndAutoCtrJson
import pymtpl.autobinctrupdate as autobinctrupdate
import os
import json
from pymtpl.core import *
from pymtpl.binctr import BaseBin, BinSSB, BaseCounter, CtrHBSB, Sort8dig, CtrSort8dig
import pymtpl.core as core
import pymtpl.binctr as binctr
from main.pymtpl import PyMtplArgs
from pymtpl.test.methods import VminTC
# Import the module to test


class TestUpdateAutobinAndAutoCtrJson(TestCase):

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_bin(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99449901_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98449801_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44270000_fail_FUN_MTTtname_0;
            IncrementCounters FUN::n44270000_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)

        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440000",
                "r0": "44000000",
                "r2": "44000001"
            }
        }
        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)
        file_path = os.path.join("./Modules/ARR/PymtplInputFiles", "array_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''{
    "MTTtname": {
        "bin": "4427",
        "rm2": "99449901",
        "rm1": "98449801",
        "r0": "44270000"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_ctr(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99449901_fail_FAIL_DPS_ALARM;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98449801_fail_FAIL_SYSTEM_SOFTWARE;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44270003_fail_FUN_MTTtname_0;
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
    }

}
''', newfile=True)
        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440000",
                "r0": "44000000",
                "r2": "44000001"
            }
        }
        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)
        file_path = os.path.join("./Modules/ARR/PymtplInputFiles", "array_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''
{
    "MTTtname": {
        "r0": "44270003"
    }
}
'''
        # self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autocounter.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_edc_bin(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

Import VminTC.xml;

MultiTrialTest MTTtname
{
    TrialVariable IP_CPU_BASE::FlowDomain.Default;
    TrialVariableExitAction Continue;
    TrialTest VminTC Instance1
    {
        TrialParam EndVoltageLimits = FlowMatrix.End_Voltage;
        FailCaptureCount = 999;
        Patlist = "scn_cdie_ccrf2_core2_atspeed_mio200_edt_classhvm_list";
        TrialResult -2
        {
            PassFail Fail;
            TrialAction Exit;
            Return -2;
        }
        TrialResult -1
        {
            PassFail Fail;
            TrialAction Exit;
            Return -1;
        }
        TrialResult 0
        {
            PassFail Fail;
            TrialAction Exit;
            IncrementCounters "FUN::n" + FlowMatrix.bin + "0001_fail_Instance1_0";
            Return 0;
        }
        TrialResult 1
        {
            PassFail Pass;
            TrialAction Exit;
            Return 1;
        }
    }
}

DUTFlow SubFlow1
{
    DUTFlowItem MTTtname MTTtname
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b99449901_fail_FAIL_DPS_ALARM_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b98449801_fail_FAIL_SYSTEM_SOFTWARE_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44270003_fail_FUN_MTTtname_0;
            IncrementCounters FUN::n44270003_fail_MTTtname_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin SoftBins.b44270002_fail_FUN_MTTtname_2;
            IncrementCounters FUN::n44270002_fail_MTTtname_2;
        }
        Result 3
        {
            Property PassFail = "Fail";
            ##EDC## SetBin SoftBins.b44270001_fail_FUN_MTTtname_3;
            IncrementCounters FUN::n44270001_fail_MTTtname_3;
        }
    }

}
''', newfile=True)

        bindict = {
            "Instance1": {
                "bin": "4400",
                "rm2": "99440162",
                "rm1": "98440162",
                "r0": "44000000",
                "r2": "44000001"
            }
        }
        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)
        file_path = os.path.join("./Modules/ARR/PymtplInputFiles", "array_AutoBinner.json")
        with open(file_path, 'w') as json_file:
            json.dump(bindict, json_file, indent=4)

        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''{
    "MTTtname": {
        "bin": "4427",
        "rm2": "99449901",
        "rm1": "98449801",
        "r0": "44270003",
        "r2": "44270002",
        "r3": "44270001"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_bin_tos4(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44000000_fail_FUN_Instance1_1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_RESET_PORT5_SHARED_BIN;
            IncrementCounters FUN::n44190000_fail_Instance1_5;
        }
    }

}

''', newfile=True)

        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)

        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''{
    "Instance1": {
        "bin": "4400",
        "rm2": "99440101",
        "rm1": "98440101",
        "r0": "44000000",
        "r2": "44000001",
        "r4": "97440000",
        "r5": "44190000"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_incorrect_bin_tos4(self):
        """Port 0 has incorrect bin format so it will be skipped"""

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b4400000_fail_FUN_Instance1_1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_RESET_PORT5_SHARED_BIN;
            IncrementCounters FUN::n44190000_fail_Instance1_5;
        }
    }

}

''', newfile=True)

        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)
        obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''{
    "Instance1": {
        "bin": "NA",
        "rm2": "99440101",
        "rm1": "98440101",
        "r2": "44000001",
        "r4": "97440000",
        "r5": "44190000"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_incorrect_ctr_tos4(self):
        """Port 0 has incorrect bin format so it will be skipped"""

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b4400000_fail_FUN_Instance1_1;
            IncrementCounters FUN::n4400000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44000001_fail_FUN_Instance1;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97440000_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_RESET_PORT5_SHARED_BIN;
            IncrementCounters FUN::n44190000_fail_Instance1_5;
        }
    }

}

''', newfile=True)

        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)

        obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
        obj1.main()
        expect = '''{
    "Instance1": {
        "r2": "44000001",
        "r4": "97440162",
        "r5": "44190000"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autocounter.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_bin_ignore_ports(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_RESET_PORT5_SHARED_BIN;
            IncrementCounters FUN::n44190000_fail_Instance1_5;
        }
    }

}

''', newfile=True)

        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)

        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''{
    "Instance1": {
        "bin": "NA",
        "rm2": "99440101",
        "rm1": "98440101",
        "r5": "44190000"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_bin_ignore_ports_edcport0(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000000_fail_FUN_RESET_PORT5_SHARED_BIN_0;
            IncrementCounters FUN::n44000000_fail_Instance1_5;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44190000_fail_FUN_RESET_PORT5_SHARED_BIN;
            IncrementCounters FUN::n44190000_fail_Instance1_5;
        }
    }

}

''', newfile=True)

        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)

        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''{
    "Instance1": {
        "bin": "4400",
        "rm2": "99440101",
        "rm1": "98440101",
        "r5": "44190000",
        "r0": "44000000"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_edc_bin_tos4(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b99440101_fail_FAIL_DPS_ALARM_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b97444400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN_4;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44191900_fail_FUN_RESET_PORT5_SHARED_BIN_5;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

}

''', newfile=True)

        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)

        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''{
    "Instance1": {
        "bin": "4400",
        "rm2": "99440101",
        "rm1": "98440101",
        "r0": "44000000",
        "r2": "44000001",
        "r4": "97444400",
        "r5": "44191900"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_edc_comment_dutflow_bin_tos4(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9"; # Comment 3
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail"; # Comment 1
            ##EDC## SetBin b99440101_fail_FAIL_DPS_ALARM_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE_n1; # Comment 2
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97444400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN_4;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44191900_fail_FUN_RESET_PORT5_SHARED_BIN_5;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

}

''', newfile=True)

        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)

        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''{
    "Instance1": {
        "bin": "4400",
        "r4": "97444400",
        "r5": "44191900",
        "rm2": "99440101",
        "rm1": "98440101",
        "r0": "44000000",
        "r2": "44000001"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_edc_comment_repeat_name_dutflow_bin_tos4(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9"; # Comment 3
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail"; # Comment 1
            ##EDC## SetBin b99440101_fail_FAIL_DPS_ALARM_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE_1_n1; # Comment 2
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail"; # Comment 4
            ##EDC## SetBin b44000001_fail_FUN_Instance1_1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b97444400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN_1_4;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b44191900_fail_FUN_RESET_PORT5_SHARED_BIN_2_5;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

}

''', newfile=True)

        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)

        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''{
    "Instance1": {
        "bin": "4400",
        "r4": "97444400",
        "r5": "44191900",
        "rm2": "99440101",
        "rm1": "98440101",
        "r0": "44000000",
        "r2": "44000001"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_edc_bin_tos4_none_port(self):
        """Test case for when the setboni does not have the _portinfo at the end like at class"""

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b99440101_fail_FAIL_DPS_ALARM_n2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b98440101_fail_FAIL_SYSTEM_SOFTWARE_n1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000000_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44000001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b97444400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN_4;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            ##EDC## SetBin b44191900_fail_FUN_RESET_PORT5_SHARED_BIN_5;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

}

''', newfile=True)

        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)

        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''{
    "Instance1": {
        "bin": "NA",
        "rm2": "99440101",
        "rm1": "98440101",
        "r2": "44000001",
        "r4": "97444400",
        "r5": "44191900"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autobinner.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/SimpleNVL', chdir=True)
    def test_basic_ctr_tos4(self):

        File('./Modules/ARR/array.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan array;

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b90990101_fail_FAIL_DPS_ALARM;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b90980101_fail_FAIL_SYSTEM_SOFTWARE;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1;
            IncrementCounters FUN::n44000000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b90440001_fail_FUN_Instance1;
            IncrementCounters FUN::n44000001_fail_Instance1_2;
        }
        Result 4
        {
            Property PassFail = "Fail";
            SetBin b90974400_fail_PTH_DTS_XXX_FUN_THERMAL_PORT4_SHARED_BIN;
            IncrementCounters FUN::n97440162_fail_Instance1_4;
        }
        Result 5
        {
            Property PassFail = "Fail";
            SetBin b90441900_fail_FUN_RESET_PORT5_SHARED_BIN;
            IncrementCounters FUN::n44190162_fail_Instance1_5;
        }
    }

}

''', newfile=True)

        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)
        ctrdict = {
            "Instance1": {
                "r0": "44000000",
                "r2": "44000001"
            }
        }
        os.makedirs("./Modules/ARR/PymtplInputFiles", exist_ok=True)
        file_path = os.path.join("./Modules/ARR/PymtplInputFiles", "array_AutoCounter.json")
        with open(file_path, 'w') as json_file:
            json.dump(ctrdict, json_file, indent=4)
        with MockVar(autobinctrupdate.OPT, 'env', f'{UT_DIR_REPO}/SimpleNVL/POR_TP/TGLH81/EnvironmentFile.env'):
            obj1 = UpdateAutobinAndAutoCtrJson('./Modules/ARR/array.mtpl')
            obj1.main()
        expect = '''{
    "Instance1": {
        "r0": "44000000",
        "r2": "44000001",
        "r4": "97440162",
        "r5": "44190162"
    }
}
'''
        self.assertTextEqual(File('./Modules/ARR/PymtplInputFiles/array_Autocounter.json').read(), expect)

    @with_(TempDir, chdir=True)
    def test_pymtpl_manual_edit_autbinctr_pymtpl(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)
        File('out.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n44005000_fail_Instance1_0,
    n44005001_fail_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44005000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44005000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44005001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44005001_fail_Instance1_2;
        }
    }

}
''', newfile=True)

        obj1 = UpdateAutobinAndAutoCtrJson('out.mtpl')
        obj1.main()

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n44005000_fail_Instance1_0,
    n44005001_fail_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44005000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44005000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44005001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44005001_fail_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)

    @with_(TempDir, chdir=True)
    def test_pymtpl_manual_edit_autbinctr_pymtpl_softbinchange(self):

        class PyObj:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4400), r2=pFail(setbin=4400)))
        PyMtpl().main_one(PyObj)
        File('out.mtpl').touch('''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n44010000_fail_Instance1_0,
    n44010001_fail_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44010000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44010000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44010001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44010001_fail_Instance1_2;
        }
    }

}
''', newfile=True)

        obj1 = UpdateAutobinAndAutoCtrJson('out.mtpl')
        obj1.main()

        class PyObj1:
            # Start of the "python mtpl code" ====================
            output = InitializeNVLSort('out', 'FUN', binrange=(4400, 4450), nonmttbinstrategy=Sort8dig)
            test1 = VminTC(name="Instance1",
                           _comment="VminTC comment",
                           EndVoltageLimits="0.9")
            subflow = Flow('SubFlow1', Fitem('SAME', test1, r0=pFail(setbin=4401), r2=pFail(setbin=4401)))

        PyMtpl().main_one(PyObj1)
        expect = '''
Version 1.0;

ProgramStyle = Modular;

TestPlan FUN;


# Test Counter Definition

Counters
{
    n44010000_fail_Instance1_0,
    n44010001_fail_Instance1_2
} # End of Test Counter Definition

CSharpTest VminTC Instance1
{
    # VminTC comment
    EndVoltageLimits = "0.9";
    FailCaptureCount = 999;
}

Flow SubFlow1
{
    FlowItem Instance1 Instance1
    {
        Result -2
        {
            Property PassFail = "Fail";
            SetBin b99440162_fail_FUN_Instance1_n2;
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            SetBin b98440162_fail_FUN_Instance1_n1;
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            SetBin b44010000_fail_FUN_Instance1_0;
            IncrementCounters FUN::n44010000_fail_Instance1_0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            Return 1;
        }
        Result 2
        {
            Property PassFail = "Fail";
            SetBin b44010001_fail_FUN_Instance1_2;
            IncrementCounters FUN::n44010001_fail_Instance1_2;
        }
    }

}
'''
        self.assertTextEqual(File('out.mtpl').read(), expect)


if __name__ == '__main__':
    unittest.main()
