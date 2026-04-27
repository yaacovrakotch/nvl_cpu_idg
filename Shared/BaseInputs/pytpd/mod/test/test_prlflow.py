#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for prlflow
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, Mock, MockVar
from gadget.helperclass import CaptureStdoutLog
from gadget.printmore import Dumper
from gadget.shell import IS_UNIX, SystemCall
from gadget.files import TempDir
from gadget.disk import Allfiles
from pprint import pprint
from mod.prlflow import *
from tp.testprogram import TestProgram, Mtpl
import shutil
import os


class TestPrlFlow(TestCase):

    def trytp(self):
        pf = PrlFlow('EnvironmentFile_CLASS_P68G2.env')
        pf.main()

    def test_integration(self):
        src = f'{UT_DIR_REPO}/prlflow2'
        with TempDir(name=True, delete=True) as tdir:
            shutil.copytree(src, f'{tdir}/TPL')
            pf = PrlFlow(f'{tdir}/TPL/EnvironmentFile_CLASS_P68G2.env')
            pf.main()

            target1 = 'Modules/IP_CPU_CONCURRENT_FLOWS/IP_CPU_CONCURRENT_FLOWS_CLASS_P68G2.mtpl'
            expect1 = [line.strip() for line in File(f'{src}/{target1}.gold').chomp()]
            msg1 = (f"Mismatch on {tdir}/TPL/{target1}; To debug, compare with {src}/{target1}.gold; "
                    f"Set delete=False.")
            result = [line.strip() for line in File(f'{tdir}/TPL/{target1}').chomp()]
            self.assertTrue(result == expect1, msg1)

            target2 = 'ProgramFlowsTestPlan/ProgramFlows_CLASS_P68G2.mtpl'
            expect2 = [line.strip() for line in File(f'{src}/{target2}.gold').chomp()]
            msg2 = (f"Mismatch on {tdir}/TPL/{target2}; To debug, compare with {src}/{target2}.gold; "
                    f"Set delete=False.")
            result = [line.strip() for line in File(f'{tdir}/TPL/{target2}').chomp()]
            self.assertTrue(result == expect2, msg2)

            # rerun
            pf.main()
            result = [line.strip() for line in File(f'{tdir}/TPL/{target1}').chomp()]
            self.assertTrue(result == expect1, msg1)
            result = [line.strip() for line in File(f'{tdir}/TPL/{target2}').chomp()]
            self.assertTrue(result == expect2, msg2)

    def test_no_change(self):
        src = f'{UT_DIR_REPO}/prlflow2'
        with TempDir(name=True, delete=True) as tdir:
            shutil.copytree(src, f'{tdir}/TPL')
            File(f'{tdir}/TPL/intradut_flows.json').unlink()
            pf = PrlFlow(f'{tdir}/TPL/EnvironmentFile_CLASS_P68G2.env')
            pf.main()

            target = 'Modules/IP_CPU_CONCURRENT_FLOWS/IP_CPU_CONCURRENT_FLOWS_CLASS_P68G2.mtpl'
            result = [line.strip() for line in File(f'{tdir}/TPL/{target}').chomp()]
            expect = [line.strip() for line in File(f'{src}/{target}').chomp()]
            self.assertTrue(result == expect, f"Something got changed in {target}. Expecting no change")

            target = 'ProgramFlowsTestPlan/ProgramFlows_CLASS_P68G2.mtpl'
            result = [line.strip() for line in File(f'{tdir}/TPL/{target}').chomp()]
            expect = [line.strip() for line in File(f'{src}/{target}').chomp()]
            self.assertTrue(result == expect, f"Something got changed in {target}. Expecting no change")

    def test_check_rerun(self):
        pf = PrlFlow(f'{UT_DIR_REPO}/prlflow2/EnvironmentFile_CLASS_P68G2.env')
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            pf.tpobj.tpldir = tdir
            File('A/B/C/D/E/a.origprl').touch(mkdir=True)
            File('A/B/C/D/E/a').touch(mkdir=True)
            File('A/B/C/D/a.origprl').touch()
            File('A/B/C/D/a').touch()
            File('A/B/C/a.origprl').touch()
            File('A/B/C/a').touch()
            File('A/B/a.origprl').touch()
            File('A/B/a').touch()
            File('A/a.origprl').touch()
            File('A/a').touch()
            File('a.origprl').touch()
            File('aa').touch()
            result = list(Allfiles('.'))
            self.assertEqual(len(result), 12)
            pf.check_rerun()
            pprint(set(Allfiles('.')))
            self.assertEqual(set(Allfiles('.')), {'./A/B/C/D/E/a',
                                                  './A/B/C/D/E/a.origprl',
                                                  './A/B/C/D/a',
                                                  './A/B/C/D/a.origprl',
                                                  './A/B/C/a',
                                                  './A/B/a',
                                                  './A/a',
                                                  './aa',
                                                  './a.origprl'})

    def test_initial_map(self):
        pf = PrlFlow(f'{UT_DIR_REPO}/prlflow2/EnvironmentFile_CLASS_P68G2.env')
        self.assertEqual(pf.mapping, {'PRL0CPUGT_SubFlow': {'ALARM_SubFlow': -1,
                                                            'FFCPU_SubFlow': 0,
                                                            'FFGT_SubFlow': 2,
                                                            'FINAL_SubFlow': 3,
                                                            'POSTPRLCPUGT_SubFlow': 1},
                                      'PRL0CPUIOE_SubFlow': {'ALARM_SubFlow': -1,
                                                             'FFCPU_SubFlow': 0,
                                                             'FFIOE_SubFlow': 2,
                                                             'FINAL_SubFlow': 3,
                                                             'POSTPRLCPUIOE_SubFlow': 1}})

    def test_update_programflow(self):
        src = f'{UT_DIR_REPO}/prlflow2'
        with TempDir(name=True) as tdir:
            text = """Version 1.0;
DUTFlow START_SubFlow
{
        DUTFlowItem TPI_BASE_XXX_START TPI_BASE_XXX::TPI_BASE_XXX_START
        {
                Result -2
        }
        DUTFlowItem PRL0CPUGT_SubFlow PRL0CPUGT_SubFlow
        {
                Result -2
                {
                        Property PassFail = "Fail";
                        GoTo ALARM_SubFlow;
                }
                Result 0
                {
                        Property PassFail = "Fail";
                        GoTo REP;
                }

                Result 1
                {
                        Property PassFail = "Pass";
                        GoTo NEXTFLOW;
                }
                Result 2
                {
                        Property PassFail = "Fail";
                        GoTo WHAT;
                }
        }
}
            """
            fname = f'{tdir}/a.mtpl'
            File(fname).touch(text)
            pf = PrlFlow(f'{src}/EnvironmentFile_CLASS_P68G2.env')
            pf.mapping = {'PRL0CPUGT_SubFlow':
                          {'ALARM_SubFlow': -1,
                           'FFPKG_SubFlow': 0,
                           'POSTPRLCPUGT_SubFlow': 1,
                           'FFGT_SubFlow': 2,
                           'FINAL_SubFlow': 3,
                           }
                          }
            result = list(pf.update_programflow(fname))
            expect = """Version 1.0;
DUTFlow START_SubFlow
{
        DUTFlowItem TPI_BASE_XXX_START TPI_BASE_XXX::TPI_BASE_XXX_START
        {
                Result -2
        }
        DUTFlowItem PRL0CPUGT_SubFlow PRL0CPUGT_SubFlow
        {

            Result -2
            {
                Property PassFail = "Fail";
                GoTo ALARM_SubFlow;
            }
            Result -1
            {
                Property PassFail = "Fail";
                GoTo ALARM_SubFlow;
            }
            Result 0
            {
                Property PassFail = "Fail";
                GoTo FFPKG_SubFlow;
            }
            Result 1
            {
                Property PassFail = "Pass";
                GoTo NEXTFLOW;
            }
            Result 2
            {
                Property PassFail = "Fail";
                GoTo FFGT_SubFlow;
            }
            Result 3
            {
                Property PassFail = "Fail";
                GoTo FINAL_SubFlow;
            }
        }
}
"""
            self.assertTextEqual(''.join(result), expect)

    def test_insert_dutflowitems(self):
        text = """Version 1.0;
DUTFlow PRL0CPUIOE_IP_CPU_FLOW_SubFlow
{
        FlowItem IP_CPU_CONCURRENT_FLOWS_TPI_BASE_IPCPU_PRLFLGCPU TPI_BASE_IPCPU::TPI_BASE_IPCPU_PRLFLGCPU {
                Result 1
                {
                        Property PassFail = "Pass";
                        GoTo IP_CPU_CONCURRENT_FLOWS_TPI_ENDIPCPU_XXX_PRLFLGCPU;
                }
        }
        FlowItem IP_CPU_CONCURRENT_FLOWS_TPI_ENDIPCPU_XXX_PRLFLGCPU TPI_ENDIPCPU_XXX::TPI_ENDIPCPU_XXX_PRLFLGCPU {
                Result 1
                {
                        Property PassFail = "Pass";
                        Return 1;
                }
        }
}  # End of DUTFlow PRL0CPUIOE_IP_CPU_FLOW_SubFlow
DUTFlow PRL0CPUGT_IP_CPU_FLOW_SubFlow
{
        FlowItem IP_CPU_CONCURRENT_FLOWS_TPI_BASE_IPCPU_PRLFLGCPU TPI_BASE_IPCPU::TPI_BASE_IPCPU_PRLFLGCPU {
                Result -2
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }
                Result 1
                {
                        Property PassFail = "Pass";
                        GoTo IP_CPU_CONCURRENT_FLOWS_TPI_ENDIPCPU_XXX_PRLFLGCPU;
                }
        }
        FlowItem IP_CPU_CONCURRENT_FLOWS_TPI_ENDIPCPU_XXX_PRLFLGCPU TPI_ENDIPCPU_XXX::TPI_ENDIPCPU_XXX_PRLFLGCPU {
                Result -2
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }
                Result 1
                {
                        Property PassFail = "Pass";
                        Return 1;
                }
        }
}  # End of DUTFlow PRL0CPUGT_IP_CPU_FLOW_SubFlow
"""
        flines = [f'{x}\n' for x in text.split('\n')]
        subflows = 'S1 S2 S3'.split()

        def fake(subflow, nextflow, mapping):
            yield f'line {subflow}\n'
            yield f'line {nextflow}\n'

        pf = PrlFlow(f'{UT_DIR_REPO}/prlflow2/EnvironmentFile_CLASS_P68G2.env')
        pf.mapping = {'PRL0CPUGT_SubFlow':
                      {'ALARM_SubFlow': -1,
                       'FFPKG_SubFlow': 0,
                       'POSTPRLCPUGT_SubFlow': 1,
                       'FFGT_SubFlow': 2,
                       'FINAL_SubFlow': 3,
                       'IPFFCPU_SubFlow': 4,
                       'FFCPU_SubFlow': 5,
                       'INFFFCPU_SubFlow': 6,
                       'IPFFGT_SubFlow': 7,
                       }
                      }

        with MockVar(pf, 'one_dutflowitem', fake):
            key = 'IP_CPU_CONCURRENT_FLOWS::PRL0CPUGT_IP_CPU_FLOW_SubFlow'
            insertat = 'IP_CPU_CONCURRENT_FLOWS_TPI_BASE_IPCPU_PRLFLGCPU'
            result = pf.insert_dutflowitems(flines, key, subflows, 'a.mtpl', insertat)
        expect = """Version 1.0;
DUTFlow PRL0CPUIOE_IP_CPU_FLOW_SubFlow
{
        FlowItem IP_CPU_CONCURRENT_FLOWS_TPI_BASE_IPCPU_PRLFLGCPU TPI_BASE_IPCPU::TPI_BASE_IPCPU_PRLFLGCPU {
                Result 1
                {
                        Property PassFail = "Pass";
                        GoTo IP_CPU_CONCURRENT_FLOWS_TPI_ENDIPCPU_XXX_PRLFLGCPU;
                }
        }
        FlowItem IP_CPU_CONCURRENT_FLOWS_TPI_ENDIPCPU_XXX_PRLFLGCPU TPI_ENDIPCPU_XXX::TPI_ENDIPCPU_XXX_PRLFLGCPU {
                Result 1
                {
                        Property PassFail = "Pass";
                        Return 1;
                }
        }
}  # End of DUTFlow PRL0CPUIOE_IP_CPU_FLOW_SubFlow
DUTFlow PRL0CPUGT_IP_CPU_FLOW_SubFlow
{
        FlowItem IP_CPU_CONCURRENT_FLOWS_TPI_BASE_IPCPU_PRLFLGCPU TPI_BASE_IPCPU::TPI_BASE_IPCPU_PRLFLGCPU {
                Result -2
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }
                Result 1
                {
                        Property PassFail = "Pass";
         GoTo S1;
                }
        }
line S1
line S2
line S2
line S3
line S3
line IP_CPU_CONCURRENT_FLOWS_TPI_ENDIPCPU_XXX_PRLFLGCPU
        FlowItem IP_CPU_CONCURRENT_FLOWS_TPI_ENDIPCPU_XXX_PRLFLGCPU TPI_ENDIPCPU_XXX::TPI_ENDIPCPU_XXX_PRLFLGCPU {
                Result -2
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }
                Result 1
                {
                        Property PassFail = "Pass";
                        Return 1;
                }
        }
}  # End of DUTFlow PRL0CPUGT_IP_CPU_FLOW_SubFlow

"""
        self.assertTextEqual(''.join(result), expect)

        # do it again, it should fail
        flines = result
        with MockVar(pf, 'one_dutflowitem', fake):
            with self.assertRaisesRegex(AssertionError, 'is already postprocessed'):
                pf.insert_dutflowitems(flines, key, subflows, 'a.mtpl', insertat)

    def test_one_dutflowitem(self):
        pf = PrlFlow(f'{UT_DIR_REPO}/prlflow2/EnvironmentFile_CLASS_P68G2.env')
        pf.dutflows = {'BEGCPU': {-2: {'GoTo': 'ALARM_SubFlow', 'PassFail': 'Fail'},
                                  -1: {'GoTo': 'ALARM_SubFlow', 'PassFail': 'Fail'},
                                  0: {'GoTo': 'FFPKG_SubFlow', 'PassFail': 'Fail'},
                                  1: {'GoTo': 'SCHDCF1_SubFlow', 'PassFail': 'Pass'},
                                  2: {'GoTo': 'IPFFCPU_SubFlow', 'PassFail': 'Fail'},
                                  999: 'BEGCPU_SubFlow'}}

        # Note: IPFFCPU_SubFlow should be added
        mapping = {'ALARM_SubFlow': -1,
                   'SFLOW1': 2,
                   'FFPKG_SubFlow': 3,
                   'SCHDCF1_SubFlow': 4}

        result = list(pf.one_dutflowitem('BEGCPU', 'NEXTFLOW', mapping))
        expect = """    DUTFlowItem BEGCPU BEGCPU
    {
        Result -2
        {
            Property PassFail = "Fail";
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            Return 3;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo NEXTFLOW;
        }
        Result 2
        {
            Property PassFail = "Fail";
            Return 5;
        }
    }
"""
        self.assertTextEqual(''.join(result), expect)

        # confirm that 5 is added automatically
        self.assertEqual(mapping, {'ALARM_SubFlow': -1,
                                   'SFLOW1': 2,
                                   'FFPKG_SubFlow': 3,
                                   'SCHDCF1_SubFlow': 4,
                                   'IPFFCPU_SubFlow': 5})

    def test_one_dutflowitem_ret(self):
        pf = PrlFlow(f'{UT_DIR_REPO}/prlflow2/EnvironmentFile_CLASS_P68G2.env')
        pf.dutflows = {'BEGCPU': {-2: {'GoTo': 'ALARM_SubFlow', 'PassFail': 'Fail'},
                                  -1: {'GoTo': 'ALARM_SubFlow', 'PassFail': 'Fail'},
                                  0: {'Return': 0, 'PassFail': 'Fail'},
                                  1: {'GoTo': 'SCHDCF1_SubFlow', 'PassFail': 'Pass'},
                                  2: {'GoTo': 'IPFFCPU_SubFlow', 'PassFail': 'Fail'},
                                  999: 'BEGCPU_SubFlow'}}

        # Note: IPFFCPU_SubFlow should be added
        mapping = {'ALARM_SubFlow': -1,
                   'SFLOW1': 2,
                   'FFPKG_SubFlow': 3,
                   'SCHDCF1_SubFlow': 4}

        result = list(pf.one_dutflowitem('BEGCPU', 'NEXTFLOW', mapping))
        expect = """    DUTFlowItem BEGCPU BEGCPU
    {
        Result -2
        {
            Property PassFail = "Fail";
            Return -2;
        }
        Result -1
        {
            Property PassFail = "Fail";
            Return -1;
        }
        Result 0
        {
            Property PassFail = "Fail";
            Return 0;
        }
        Result 1
        {
            Property PassFail = "Pass";
            GoTo NEXTFLOW;
        }
        Result 2
        {
            Property PassFail = "Fail";
            Return 5;
        }
    }
"""
        self.assertTextEqual(''.join(result), expect)

        # confirm that 5 is added automatically
        self.assertEqual(mapping, {'ALARM_SubFlow': -1,
                                   'SFLOW1': 2,
                                   'FFPKG_SubFlow': 3,
                                   'SCHDCF1_SubFlow': 4,
                                   'IPFFCPU_SubFlow': 5})

    def test_paste_dutflow(self):
        pf = PrlFlow(f'{UT_DIR_REPO}/prlflow2/EnvironmentFile_CLASS_P68G2.env')
        with TempDir(name=True) as tdir:
            fname = f'{tdir}/a.mtpl'
            text = """
Version 1.0;
TestPlan IP_CPU_CONCURRENT_FLOWS;

DUTFlow PRL0CPUIOE_IP_CPU_FLOW_SubFlow
{
    blah
}
DUTFlow PRL0CPUGT_IP_CPU_FLOW_SubFlow
{
    blah
}
"""
            File(fname).touch(text)
            result = list(pf.paste_dutflow(fname, ['  line1\n', 'line2\n']))
            expect = """
Version 1.0;
TestPlan IP_CPU_CONCURRENT_FLOWS;

  line1
line2
DUTFlow PRL0CPUIOE_IP_CPU_FLOW_SubFlow
{
    blah
}
DUTFlow PRL0CPUGT_IP_CPU_FLOW_SubFlow
{
    blah
}
"""
            self.assertTextEqual(''.join(result), expect)

    def test_get_ip_mtpl(self):
        pf = PrlFlow(f'{UT_DIR_REPO}/prlflow2/EnvironmentFile_CLASS_P68G2.env')
        ip_mtpl = pf.get_ip_mtpl('IP_CPU_CONCURRENT_FLOWS::PRL0CPUGT_IP_CPU_FLOW_SubFlow')
        self.assertTrue(os.path.exists(ip_mtpl))

    def test_get_all_subflows_ports(self):
        pf = PrlFlow(f'{UT_DIR_REPO}/prlflow3/EnvironmentFile_CLASS_P68G2.env')
        result = pf.get_all_subflows(['CCLRF6_SubFlow', 'MAXAT_SubFlow'])
        self.assertEqual(result, ['CCLRF6_SubFlow', 'CCRF6_SubFlow', 'CATF6_SubFlow', 'MAXCLR_SubFlow', 'MAXCR_SubFlow', 'MAXAT_SubFlow'])

    def test_get_all_subflows(self):
        pf = PrlFlow(f'{UT_DIR_REPO}/prlflow2/EnvironmentFile_CLASS_P68G2.env')
        result = pf.get_all_subflows(['BEGCPU_SubFlow', 'SCLRF2_SubFlow'])
        self.assertEqual(result, ['BEGCPU_SubFlow', 'SCHDCF1_SubFlow', 'SCLRF1_SubFlow', 'SCLRF2_SubFlow'])

        # get_new_subflows
        pfile = pf.tpobj.get_final_mtpl()
        result2 = pf.get_new_subflows(pfile, result)
        self.assertEqual(result2, [])

        mfile = f'{UT_DIR_REPO}/prlflow2/Modules/IP_CPU_CONCURRENT_FLOWS/IP_CPU_CONCURRENT_FLOWS_CLASS_P68G2.mtpl'
        result2 = pf.get_new_subflows(mfile, result)
        self.assertEqual(result2, result)

    def test_get_prl2ip(self):
        pf = PrlFlow(f'{UT_DIR_REPO}/prlflow2/EnvironmentFile_CLASS_P68G2.env')
        with TempDir(name=True) as tdir:
            fname = f'{tdir}/a.mtpl'
            text = """Version 1.0;

ProgramStyle = Modular;

TestPlan Flows;

ConcurrentFlow PRL0CPUGT_SubFlow [Parallel]
{
        ConcurrentFlowItem              IP_CPU          IP_CPU_CONCURRENT_FLOWS::PRL0CPUGT_IP_CPU_FLOW_SubFlow;
        ConcurrentFlowItem              IP_PCH          IP_PCH_CONCURRENT_FLOWS::PRL0CPUGT_IP_PCH_FLOW_SubFlow;
        ConcurrentResultTable (IP_CPU, IP_PCH, EffectiveIPResult)
        {
                1,      *,      IP_PCH;
                [*:0],  *,      IP_CPU;
                [2:*],  *,      IP_CPU;
        }
}
ConcurrentFlow PRL0CPUIOE_SubFlow [Parallel]
{
        ConcurrentFlowItem              IP_CPU          IP_CPU_CONCURRENT_FLOWS::PRL0CPUIOE_IP_CPU_FLOW_SubFlow;
        ConcurrentFlowItem              IP_PCH          IP_PCH_CONCURRENT_FLOWS::PRL0CPUIOE_IP_PCH_FLOW_SubFlow;
        ConcurrentResultTable (IP_CPU, IP_PCH, EffectiveIPResult)
        {
                1,      *,      IP_PCH;
                [*:0],  *,      IP_CPU;
                [2:*],  *,      IP_CPU;
        }
}
"""
            File(fname).touch(text)
            expect = {'IP_CPU_CONCURRENT_FLOWS::PRL0CPUGT_IP_CPU_FLOW_SubFlow': 'PRL0CPUGT_SubFlow',
                      'IP_CPU_CONCURRENT_FLOWS::PRL0CPUIOE_IP_CPU_FLOW_SubFlow': 'PRL0CPUIOE_SubFlow',
                      'IP_PCH_CONCURRENT_FLOWS::PRL0CPUGT_IP_PCH_FLOW_SubFlow': 'PRL0CPUGT_SubFlow',
                      'IP_PCH_CONCURRENT_FLOWS::PRL0CPUIOE_IP_PCH_FLOW_SubFlow': 'PRL0CPUIOE_SubFlow'}
            self.assertEqual(pf.get_prl2ip(fname), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
