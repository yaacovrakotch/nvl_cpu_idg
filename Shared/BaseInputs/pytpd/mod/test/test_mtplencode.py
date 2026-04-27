#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for mtplencode
"""
from pickle import FALSE

from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, Mock
from gadget.gizmo import with_
from gadget.errors import ErrorUser
from gadget.files import TempDir, check_and_del
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdoutLog
from gadget.disk import Allfiles
from mod.mtplencode import *
from pprint import pprint
import sys
import tarfile
import shutil
import os


class TestME(TestCase):

    def test_add_all_tn(self):
        tproot = f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81'
        tpobj = TestProgram(f'{tproot}/EnvironmentFile.env')
        me = MtplEncode(tpobj)
        me._add_alltn('m1', ['XTest Vmin test0', 'Test Vmin test1', 'TrialTest Vmin abc'])
        self.assertEqual(me.alltn, {('m1', 'abc'), ('m1', 'test1')})

        # no meta
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        me = MtplEncode(tp).read_meta()
        self.assertEqual(me.data, {})

    def test_get_ulat_mv_path(self):
        # Test the dynamic ULAT_MV path generation
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        me = MtplEncode(tp)

        # Test NVL product
        with MockVar(me.tpobj, 'get_family_name', Mock(return_value='NVLS756A0H01P0FS538')):  # Changed from get_name to get_family_name
            result_nvl = me._get_ulat_mv_path()
            # Check that the path ends with the expected product-specific part
            self.assertTrue(result_nvl.endswith('/hdmxprogs/nvl/ulat_mv'))

        # Test DNL product
        with MockVar(me.tpobj, 'get_family_name', Mock(return_value='DNLS763B0H49A00S610')):  # Changed from get_name to get_family_name
            result_dnl = me._get_ulat_mv_path()
            self.assertTrue(result_dnl.endswith('/hdmxprogs/dnl/ulat_mv'))

    def test_error_expand(self):
        # default meta_info
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81/EnvironmentFile.env')

            def fake(*args):
                raise ErrorInput('error', 'happened')

            with MockVar(BM, 'expand', fake):
                with self.assertRaisesRegex(ErrorUser, 'Failed to expand'):
                    MtplEncode(tp).read_meta()   # read original

    def test_basic_generate(self):
        tproot = f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81'
        tpobj = TestProgram(f'{tproot}/EnvironmentFile.env')

        with TempDir(name=True) as tdir:
            me = MtplEncode(tpobj)
            me.metapath = f'{tdir}/{me.ROOTNAME}'

            # generate
            me.generate_meta()
            self.assertEqual(me.ctr, 2)    # number of TrialTests

            self.assertGoldEqual(me.metapath, f'{tproot}/meta_info.do_not_commit.log')   # File in utdir must represent correct one

    def test_basic_read(self):
        # no missing
        tproot = f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81'
        tpobj = TestProgram(f'{tproot}/EnvironmentFile.env')
        me = MtplEncode(tpobj)
        with CaptureStdoutLog() as p:
            me.read_meta()
        print(p.getvalue())
        self.assertTrue('Missing' not in p.getvalue())
        self.assertEqual(me.data, {'ARR CCA': ['# FSM: COLD: IP_CPU'],
                                   'ARR CCB1101_1': ['# PPR: IP: *: Config1'],
                                   'ARR CCB1102_2': ['# PPR: IP: *: Config1'],
                                   'ARR CCB1103_3': ['# PPR: IP: *: Config1']})

        # some missing
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81/EnvironmentFile.env')

            tp.envdir = tdir
            File(f'{tp.envdir}/meta_info.do_not_commit.log').touch('''{
"SCN T1": ["# FSM: COLD: IP_CPU"],
"ARR CCA": ["# FSM: HOT: IP_CPU", "# FSM: COLD: IP_CPU"]
}''')
            with CaptureStdoutLog() as p:
                me = MtplEncode(tp).read_meta()
            print(p.getvalue())
            self.assertTrue('Missing' in p.getvalue())

    def test_do_fsm1(self):
        # default meta_info
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81/EnvironmentFile.env')
            me = MtplEncode(tp).read_meta()   # read original

            tp.envdir = tdir

            # Nothing to process since FSM_Config.csv does not exist
            self.assertEqual(me.do_fsm(), 1)

            File('InputFiles/FSM_Config.csv').touch('''ProcessStep,LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode
COLD,*,HDMX,X7,4AAA*,*,B,6248,5Q,CC
HOT,*,HDMX,X7,4AAA*,*,B,6167,6T,CH
''', mkdir=True)

            me.do_fsm()

            expect = '''LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode,ModuleName,InstanceName,IPName
*,HDMX,X7,4AAA*,*,B,6248,5Q,CC,ARR,CCA,IP_CPU
'''
            self.assertTextEqual(File('FullSkipModelInput.csv').read(), expect)

    def test_do_fsm2(self):
        # meta_info is specified in unittest
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81/EnvironmentFile.env')

            tp.envdir = tdir
            File(f'{tp.envdir}/meta_info.do_not_commit.log').touch('''{
"SCN T1": ["# FSM: COLD: IP_CPU"],
"ARR CCA": ["# FSM: HOT: IP_CPU", "# FSM: COLD: IP_CPU"]
}''')
            me = MtplEncode(tp).read_meta()

            # Nothing to process
            self.assertEqual(me.do_fsm(), 1)

            File('InputFiles/FSM_Config.csv').touch('''ProcessStep,LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode
COLD,*,HDMX,X7,4AAA*,*,B,6248,5Q,CC
HOT,*,HDMX,X7,4AAA*,*,B,6167,6T,CH
''', mkdir=True)

            me.do_fsm()

            expect = '''LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode,ModuleName,InstanceName,IPName
*,HDMX,X7,4AAA*,*,B,6248,5Q,CC,ARR,CCA,IP_CPU
*,HDMX,X7,4AAA*,*,B,6167,6T,CH,ARR,CCA,IP_CPU
'''
            # SCN T1 is skipped since this module "does not exist" since all instances are not existing
            self.assertTextEqual(File('FullSkipModelInput.csv').read(), expect)

    def test_do_fsm3(self):
        # cfg file and meta_info; meta_info is specified in unittest - empty and with comma
        with TempDir(chdir=True, name=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple4'
            shutil.copytree(tpref, f'{tdir}/TPL')
            tp = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')

            File(f'{tp.envdir}/meta_info.do_not_commit.log').touch('''{
"SCN T1": ["# FSM: COLD: IP_CPU"],
"ARR CCA": ["# FSM: HOT,COLD:"]
}''', newfile=True)
            me = MtplEncode(tp).read_meta()

            # Nothing to process
            self.assertEqual(me.do_fsm(), 1)

            File('TPL/POR_TP/TGLH81/InputFiles/FSM_Config.csv').touch('''ProcessStep,LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode
COLD,*,HDMX,X7,4AAA*,*,B,6248,5Q,CC
HOT,*,HDMX,X7,4AAA*,*,B,6167,6T,CH
''', mkdir=True)
            File('TPL/POR_TP/TGLH81/InputFiles/digital.fsm.json').touch('''
[{"process": "HOT",
 "ip": "IP_CPU",
 "module": "SCN",
 "regex": "CC*"
}]''', mkdir=True)

            me.do_fsm()

            expect = '''LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode,ModuleName,InstanceName,IPName
*,HDMX,X7,4AAA*,*,B,6248,5Q,CC,ARR,CCA,
*,HDMX,X7,4AAA*,*,B,6167,6T,CH,ARR,CCA,
*,HDMX,X7,4AAA*,*,B,6167,6T,CH,SCN,CC.*,IP_CPU
'''
            # SCN T1 is skipped since this module "does not exist" since all instances are not existing
            self.assertTextEqual(File('TPL/POR_TP/TGLH81/FullSkipModelInput.csv').read(), expect)

            expect = '''count,pstep,module,testname
1,COLD,ARR,CCA
1,HOT,ARR,CCA
1,HOT,SCN,CCA
1,HOT,SCN,CCB
0,HOT,SCN,TPIE_PgmRules
count,pstep,module_regex,testname_regex
2,HOT,SCN,CC*'''
            self.assertTextEqual(File('TPL/POR_TP/TGLH81/Reports/FSM.csv').read(), expect)

    def test_do_fsm4_multi(self):
        # cfg file and meta_info; meta_info is specified in unittest - multiple process steps
        with TempDir(chdir=True, name=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple4'
            shutil.copytree(tpref, f'{tdir}/TPL')
            tp = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')

            File(f'{tp.envdir}/meta_info.do_not_commit.log').touch('''{
"SCN T1": ["# FSM: COLD: IP_CPU"],
"ARR CCA": ["# FSM: HOT,COLD-AY:"],
"PTH CCA_1200_blah_1502": ["# FSM: COLD-AY,COLD-5Q:"]
}''', newfile=True)
            me = MtplEncode(tp).read_meta()

            # Nothing to process
            self.assertEqual(me.do_fsm(), 1)

            File('TPL/POR_TP/TGLH81/InputFiles/FSM_Config.csv').touch('''ProcessStep,LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode
COLD,*,HDMX,X7,4AAA*,*,B,6248,5Q,CC
HOT,*,HDMX,X7,4AAA*,*,B,6167,6T,CH
COLD,*,HDMX,X7,4AAA*,*,B,6222,AY,CC
''', mkdir=True)
            File('TPL/POR_TP/TGLH81/InputFiles/digital.fsm.json').touch('''
[{"process": "COLD-AY",
 "ip": "IP_CPU",
 "module": "SCN",
 "regex": "CC*"
}]''', mkdir=True)

            me.do_fsm()

            expect = '''LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode,ModuleName,InstanceName,IPName
*,HDMX,X7,4AAA*,*,B,6248,5Q,CC,PTH,CCA_1200_blah_1502,
*,HDMX,X7,4AAA*,*,B,6222,AY,CC,ARR,CCA,
*,HDMX,X7,4AAA*,*,B,6222,AY,CC,PTH,CCA_1200_blah_1502,
*,HDMX,X7,4AAA*,*,B,6222,AY,CC,SCN,CC.*,IP_CPU
*,HDMX,X7,4AAA*,*,B,6167,6T,CH,ARR,CCA,
'''
            # SCN T1 is skipped since this module "does not exist" since all instances are not existing
            self.assertTextEqual(File('TPL/POR_TP/TGLH81/FullSkipModelInput.csv').read(), expect)

            expect = '''count,pstep,module,testname
1,COLD-5Q,PTH,CCA_1200_blah_1502
1,COLD-AY,ARR,CCA
1,COLD-AY,PTH,CCA_1200_blah_1502
1,COLD-AY,SCN,CCA
1,COLD-AY,SCN,CCB
0,COLD-AY,SCN,TPIE_PgmRules
1,HOT,ARR,CCA
count,pstep,module_regex,testname_regex
2,COLD-AY,SCN,CC*'''
            self.assertTextEqual(File('TPL/POR_TP/TGLH81/Reports/FSM.csv').read(), expect)

    def test_do_fsm5_multi(self):
        # cfg file and meta_info; meta_info is specified in unittest - multiple process steps
        with TempDir(chdir=True, name=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple4'
            shutil.copytree(tpref, f'{tdir}/TPL')
            tp = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')

            File(f'{tp.envdir}/meta_info.do_not_commit.log').touch('''{
"ARR CCA": ["# FSM: HOT,COLD:"]
}''', newfile=True)
            me = MtplEncode(tp).read_meta()

            # Nothing to process
            self.assertEqual(me.do_fsm(), 1)

            File('TPL/POR_TP/TGLH81/InputFiles/FSM_Config.csv').touch('''ProcessStep,LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode
COLD,*,HDMX,X7,4AAA*,*,B,6248,5Q,CC
HOT,*,HDMX,X7,4AAA*,*,B,6167,6T,CH
COLD,*,HDMX,X7,4AAA*,*,B,6222,AY,CC
''', mkdir=True)
            File('TPL/POR_TP/TGLH81/InputFiles/digital.fsm.json').touch('''
[{"process": "COLD",
 "ip": "IP_CPU",
 "module": "SCN,SCNNOTFOUND1",
 "regex": "CC*"
},
{"process": "COLD",
 "ip": "IP_CPU",
 "module": "SCNNOTFOUND2",
 "regex": "CC*"
}
]''', mkdir=True)

            me.do_fsm()

            expect = '''LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode,ModuleName,InstanceName,IPName
*,HDMX,X7,4AAA*,*,B,6248,5Q,CC,ARR,CCA,
*,HDMX,X7,4AAA*,*,B,6222,AY,CC,ARR,CCA,
*,HDMX,X7,4AAA*,*,B,6248,5Q,CC,SCN,CC.*,IP_CPU
*,HDMX,X7,4AAA*,*,B,6222,AY,CC,SCN,CC.*,IP_CPU
*,HDMX,X7,4AAA*,*,B,6167,6T,CH,ARR,CCA,
'''
            # SCN T1 is skipped since this module "does not exist" since all instances are not existing
            self.assertTextEqual(File('TPL/POR_TP/TGLH81/FullSkipModelInput.csv').read(), expect)

            expect = '''count,pstep,module,testname
1,COLD,ARR,CCA
1,COLD,SCN,CCA
1,COLD,SCN,CCB
0,COLD,SCN,TPIE_PgmRules
1,HOT,ARR,CCA
count,pstep,module_regex,testname_regex
2,COLD,SCN,CC*
'''
            self.assertTextEqual(File('TPL/POR_TP/TGLH81/Reports/FSM.csv').read(), expect)

    def test_do_fsm6_overlap(self):
        # mtpltag and regex are overlapping / duplicate
        with TempDir(chdir=True, name=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple4'
            shutil.copytree(tpref, f'{tdir}/TPL')
            tp = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')

            File(f'{tp.envdir}/meta_info.do_not_commit.log').touch('''{
"ARR CCA": ["# FSM: HOT,COLD:"]
}''', newfile=True)
            me = MtplEncode(tp).read_meta()

            # Nothing to process
            self.assertEqual(me.do_fsm(), 1)

            File('TPL/POR_TP/TGLH81/InputFiles/FSM_Config.csv').touch('''ProcessStep,LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode
COLD,*,HDMX,X7,4AAA*,*,B,6248,5Q,CC
HOT,*,HDMX,X7,4AAA*,*,B,6167,6T,CH
''', mkdir=True)
            File('TPL/POR_TP/TGLH81/InputFiles/digital.fsm.json').touch('''
[{"process": "COLD",
 "ip": "",
 "module": "ARR",
 "regex": "*"
}
]''', mkdir=True)

            me.do_fsm()

            expect = '''LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode,ModuleName,InstanceName,IPName
*,HDMX,X7,4AAA*,*,B,6248,5Q,CC,ARR,.*,
*,HDMX,X7,4AAA*,*,B,6248,5Q,CC,ARR,CCA,
*,HDMX,X7,4AAA*,*,B,6167,6T,CH,ARR,CCA,
'''
            # SCN T1 is skipped since this module "does not exist" since all instances are not existing
            self.assertTextEqual(File('TPL/POR_TP/TGLH81/FullSkipModelInput.csv').read(), expect)

            expect = '''count,pstep,module,testname
2,COLD,ARR,CCA
1,COLD,ARR,CCB1101_1
1,COLD,ARR,CCB1102_2
1,COLD,ARR,CCB1103_3
1,COLD,ARR,CCD1101
1,COLD,ARR,CCD1102
1,COLD,ARR,CCD1103
1,COLD,ARR,TPIE_PgmRules
1,HOT,ARR,CCA
count,pstep,module_regex,testname_regex
8,COLD,ARR,*
'''
            self.assertTextEqual(File('TPL/POR_TP/TGLH81/Reports/FSM.csv').read(), expect)

    def test_do_fsm7_bom(self):
        # Unit test FSM file only in Common_BOM folder.
        # default meta_info
        with TempDir(chdir=True, name=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple4'
            shutil.copytree(tpref, f'{tdir}/TPL')
            tp = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')
            me = MtplEncode(tp).read_meta()  # read original

            File('TPL/Shared/BaseInputs/Common/Common_TGLH81/FSM_Config.csv').touch('''ProcessStep,LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode
COLD,*,HDMX,X7,4AAA*,*,B,6248,5Q,CC
HOT,*,HDMX,X7,4AAA*,*,B,6167,6T,CH
''', mkdir=True)

            me.do_fsm('TGLH81')

            expect = '''LotType,Platform,Pkg,Device,Revision,Stepping,LocationCode,EngId,Encode,ModuleName,InstanceName,IPName
*,HDMX,X7,4AAA*,*,B,6248,5Q,CC,ARR,CCA,IP_CPU
'''
            self.assertTextEqual(File('TPL/POR_TP/TGLH81/FullSkipModelInput.csv').read(), expect)

    def test_fsm_re_bug(self):

        # bug due to empty ip becoming regex
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81/EnvironmentFile.env')
            me = MtplEncode(tp).read_meta()   # read original
            tp.tpldir = tdir
            tp.envdir = f'{tdir}/POR_TP'
            File('POR_TP/InputFiles/FSM_input.fsm.json').touch('''
[{"process": "PHMHOT, PHMCOLD",
 "ip": "IP_CPU",
 "module": "ARR",
 "regex": ".*"
},
{"process": "PHMHOT",
 "ip": "",
 "module": "SCN",
 "regex": ".*"
}]''', mkdir=True)
            result, totals = me._fsm_re_cfg([])
            pprint(result)
            self.assertEqual(result, [('PHMCOLD', 'ARR', '.*', 'IP_CPU'),
                                      ('PHMHOT', 'ARR', '.*', 'IP_CPU'),
                                      ('PHMHOT', 'SCN', '.*', '')])

    def test_fsm_re_cfg(self):

        # global file - everything
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81/EnvironmentFile.env')
            me = MtplEncode(tp).read_meta()   # read original
            tp.tpldir = tdir
            tp.envdir = f'{tdir}/POR_TP'
            File('POR_TP/InputFiles/FSM_input.fsm.json').touch('''
[{"process": "PHMHOT, PHMCOLD",
 "ip": "IP_CPU",
 "module": "ARR",
 "regex": ".*"
}]''', mkdir=True)
            result, totals = me._fsm_re_cfg([])
            # pprint(result)
            self.assertEqual(len(result), 2)
            # pprint(totals)
            self.assertEqual(len(totals), 20)

        # global file - one process, module regex, tn regex
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81/EnvironmentFile.env')
            me = MtplEncode(tp).read_meta()   # read original
            tp.tpldir = tdir
            tp.envdir = f'{tdir}/POR_TP'
            File('POR_TP/InputFiles/FSM_input.fsm.json').touch('''
[{"process": "PHMHOT",
 "ip": "IP_CPX",
 "module": "ARR",
 "regex": "CCA"
}]''', mkdir=True)
            result, totals = me._fsm_re_cfg([])
            self.assertEqual(result, [('PHMHOT', 'ARR', 'CCA', 'IP_CPX')])
            expect = '''
[['count', 'pstep', 'module', 'testname'],
 [1, 'PHMHOT', 'ARR', 'CCA'],
 [0, 'PHMHOT', 'ARR', 'CCB1101_1'],
 [0, 'PHMHOT', 'ARR', 'CCB1102_2'],
 [0, 'PHMHOT', 'ARR', 'CCB1103_3'],
 [0, 'PHMHOT', 'ARR', 'CCD1101'],
 [0, 'PHMHOT', 'ARR', 'CCD1102'],
 [0, 'PHMHOT', 'ARR', 'CCD1103'],
 [0, 'PHMHOT', 'ARR', 'TPIE_PgmRules'],
 ['count', 'pstep', 'module_regex', 'testname_regex'],
 [1, 'PHMHOT', 'ARR', 'CCA']]'''
            self.assertTextEqual('\n' + Dumper(totals, p=False).string(), expect)

    def test_fsm_cfg_basic(self):
        # Good template
        with TempDir(chdir=True, name=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple4'
            shutil.copytree(tpref, f'{tdir}/TPL')
            tp = TestProgram(f'TPL/POR_TP/TGLH81/EnvironmentFile.env')
            me = MtplEncode(tp).read_meta()   # read original

            # specific module
            File('TPL/Modules/ARRX/InputFiles/input.fsm.json').touch('''
[{"process": "PHMHOT",
 "module": "ARR",
 "ip": "IP_CPU",
 "regex": "CCB"
}]''', mkdir=True)

            result, _ = me._fsm_re_cfg([])
            expect = '''
[['PHMHOT',
  'ARR',
  'CCB',
  'IP_CPU']]'''
            self.assertTextEqual('\n' + Dumper(result, p=False).string(), expect)

            # module and global combined, make it uniq
            File('TPL/POR_TP/TGLH81/InputFiles/digital.fsm.json').touch('''
[{"process": "PHMHOT",
 "ip": "IP_CPU",
 "module": "ARR",
 "regex": "*CC*"
}]''', mkdir=True, newfile=True)
            result, _ = me._fsm_re_cfg([])
            expect = '''
[['PHMHOT', 'ARR', '.*CC.*', 'IP_CPU'],
 ['PHMHOT', 'ARR', 'CCB', 'IP_CPU']]'''
            self.assertTextEqual('\n' + Dumper(result, p=False).string(), expect)

            # error case - different ip on the same module process, mod, tn
            File('TPL/POR_TP/TGLH81/InputFiles/digital.fsm.json').touch('''
[{"process": "PHMHOT",
 "ip": "IP_CPX",
 "module": "ARR",
 "regex": "CCB"
}]''', mkdir=True, newfile=True)
            with self.assertRaisesRegex(ErrorUser, 'Error on ip .IP_CPU vs IP_CPX. for'):
                me._fsm_re_cfg([])

            # no duplicate
            File('TPL/POR_TP/TGLH81/InputFiles/digital.fsm.json').touch('''
[{"process": "PHMHOT",
 "ip": "IP_CPU",
 "module": "ARR",
 "regex": "CCB"
}]''', mkdir=True, newfile=True)
            result, _ = me._fsm_re_cfg([])
            self.assertEqual(len(result), 1)

            # multiple process step
            File('TPL/POR_TP/TGLH81/InputFiles/digital.fsm.json').unlink()
            File('TPL/Modules/ARRX/InputFiles/input.fsm.json').touch('''
[{"process": "PHMHOT, COLD",
 "module": "ARR",
 "ip": "IP_CPU",
 "regex": "CCB1101"
}]''', mkdir=True, newfile=True)

            result, _ = me._fsm_re_cfg([])
            expect = '''
[['COLD', 'ARR', 'CCB1101', 'IP_CPU'],
 ['PHMHOT', 'ARR', 'CCB1101', 'IP_CPU']]'''
            self.assertTextEqual('\n' + Dumper(result, p=False).string(), expect)

    def test_get_all_duplicate_dutflow(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3e/POR_TP/TGLH81/EnvironmentFile.env')
        me = MtplEncode(tp)
        self.assertEqual(me.get_all_duplicate_dutflow(), {('ARR', 'CCC')})

    def test_do_ppr_global(self):
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81/EnvironmentFile.env')
            me = MtplEncode(tp).read_meta()   # read original

            tp.tpldir = tdir

            File('Modules/PPR/InputFiles/PPR_Config.json').touch('''{
  "PPR_general_fields": {
    "DtsUpperThreshold": 151,
    "DtsLowerThreshold": 1
  },
  "DEFAULT": [{
    "UpperTjTolerancePreEmphasis": 0,
    "UpperTjTolerancePowerScaling": 10
  }],
  "Config1": [{
    "Key1": "Val1"
  }],
  "Config2": [{
    "Key1": "Val2"
  }]
}
''', mkdir=True)

            File('Modules/PPR/InputFiles/GlobalPPRconfiguration.json').touch('''
{"PPRTargetTests": {
   "IP::ARR::CCB.+": "Config1"
}}
''')
            me.do_ppr()

            expect = '''{
   "DtsUpperThreshold": 151,
   "DtsLowerThreshold": 1,
   "TestInstance2Tolerances": {
      "IP::ARR::CCB1101_1": [
         {
            "UpperTjTolerancePreEmphasis": 0,
            "UpperTjTolerancePowerScaling": 10,
            "Key1": "Val1"
         }
      ],
      "IP::ARR::CCB1102_2": [
         {
            "UpperTjTolerancePreEmphasis": 0,
            "UpperTjTolerancePowerScaling": 10,
            "Key1": "Val1"
         }
      ],
      "IP::ARR::CCB1103_3": [
         {
            "UpperTjTolerancePreEmphasis": 0,
            "UpperTjTolerancePowerScaling": 10,
            "Key1": "Val1"
         }
      ]
   }
}'''
            self.assertTextEqual(File('Modules/PPR/InputFiles/PprConfiguration.json').read(), expect)

            # skipmodule
            me.skip_mod = {'ARR'}
            me.do_ppr()
            expect = '''
{
   "DtsUpperThreshold": 151,
   "DtsLowerThreshold": 1,
   "TestInstance2Tolerances": {}
}
'''
            self.assertTextEqual(File('Modules/PPR/InputFiles/PprConfiguration.json').read(), expect)

    def test_do_ppr(self):
        # default meta_info
        with TempDir(chdir=True, name=True) as tdir:
            tp = TestProgram(f'{UT_DIR_REPO}/Simple4/POR_TP/TGLH81/EnvironmentFile.env')
            me = MtplEncode(tp).read_meta()   # read original

            tp.tpldir = tdir

            # Nothing to process since PPR_Config.json does not exist
            self.assertEqual(me.do_ppr(), 1)

            File('Modules/PPR/InputFiles/PPR_Config.json').touch('''{
  "PPR_general_fields": {
    "DtsUpperThreshold": 151,
    "DtsLowerThreshold": 1
  },
  "DEFAULT": [{
    "UpperTjTolerancePreEmphasis": 0,
    "UpperTjTolerancePowerScaling": 10
  }],
  "Config1": [{
    "Key1": "Val1"
  }],
  "Config2": [{
    "Key1": "Val2"
  }]
}
''', mkdir=True)

            me.do_ppr()

            expect = '''{
   "DtsUpperThreshold": 151,
   "DtsLowerThreshold": 1,
   "TestInstance2Tolerances": {
      "IP::ARR::CCB1101_1": [
         {
            "UpperTjTolerancePreEmphasis": 0,
            "UpperTjTolerancePowerScaling": 10,
            "Key1": "Val1"
         }
      ],
      "IP::ARR::CCB1102_2": [
         {
            "UpperTjTolerancePreEmphasis": 0,
            "UpperTjTolerancePowerScaling": 10,
            "Key1": "Val1"
         }
      ],
      "IP::ARR::CCB1103_3": [
         {
            "UpperTjTolerancePreEmphasis": 0,
            "UpperTjTolerancePowerScaling": 10,
            "Key1": "Val1"
         }
      ]
   }
}'''
            self.assertTextEqual(File('Modules/PPR/InputFiles/PprConfiguration.json').read(), expect)

            # case2 =======================================================
            me.data = {'ARR CCA': ['# PPR: IP1: .*: Config1'],
                       'ARR CCB1101_1': ['# PPR: IP: *: Config1'],
                       'ARR CCB1102_2': ['# PPR: IP: *: Config1', '# PPR: IP: _2: Config2'],
                       'ARR CCB1103_3': ['# PPR: IP: nomatch: Config1']}
            me.do_ppr()
            expect = '''{
   "DtsUpperThreshold": 151,
   "DtsLowerThreshold": 1,
   "TestInstance2Tolerances": {
      "IP1::ARR::CCA": [
         {
            "UpperTjTolerancePreEmphasis": 0,
            "UpperTjTolerancePowerScaling": 10,
            "Key1": "Val1"
         }
      ],
      "IP::ARR::CCB1101_1": [
         {
            "UpperTjTolerancePreEmphasis": 0,
            "UpperTjTolerancePowerScaling": 10,
            "Key1": "Val1"
         }
      ],
      "IP::ARR::CCB1102_2": [
         {
            "UpperTjTolerancePreEmphasis": 0,
            "UpperTjTolerancePowerScaling": 10,
            "Key1": "Val2"
         }
      ]
   }
}'''
            self.assertTextEqual(File('Modules/PPR/InputFiles/PprConfiguration.json').read(), expect)

            # Skip mod case
            me.skip_mod = ['ARR']
            me.do_ppr()
            expect = '''{
   "DtsUpperThreshold": 151,
   "DtsLowerThreshold": 1,
   "TestInstance2Tolerances": {
      "DEFAULT::DEFAULT": [
         {
            "UpperTjTolerancePreEmphasis": 0,
            "UpperTjTolerancePowerScaling": 10
         }
      ]
   }
}'''
            self.assertTextEqual(File('Modules/PPR/InputFiles/PprConfiguration.json').read(), expect)

    @with_(TempDir, startcopy=f'{UT_DIR_REPO}/Simple5', chdir=True)
    def test_do_ppr2(self):
        tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
        obj = MtplEncode(tp)

        # ppr config does not exist ==============================================
        self.assertEqual(obj.do_ppr_2nd(), 1)

        # basic pass case ========================================================
        text = '''
{
   "DtsUpperThreshold": 151,
   "IgnoreUnitsWithCurfbins": [
      "9901",
      "9742"
   ],
   "TestInstance2Tolerances": {
      "IP_CPU::ARR_ATOM_L2CXX::SSA_ATOM_VMIN_K_CATF6_X_VCCIA_F6_3800_L2DATAPMUXON_1006": [
         {
            "PprExitTempRangeUpperTolerance": 0,
            "PprExitTempRangeLowerTolerance": 60,
            "DefaultTemperatureOffset": 2,
            "DefaultPowerScalingFactor": 1,
            "TtrMode": [
               "SHORT"
            ]
         }
      ],
      "IP_CPU::ARR_ATOM_L2CXX::SSA_ATOM_VMIN_K_CATF6_X_VCCIA_F6_3800_L2DATAPMUXON_1005": [
         {
            "PprExitTempRangeUpperTolerance": 0,
            "PprExitTempRangeLowerTolerance": 60,
            "DefaultTemperatureOffset": 2,
            "DefaultPowerScalingFactor": 1,
            "TtrMode": [
               "SHORT"
            ]
         }
      ]
   }
}
'''
        pprfile = 'Modules/PPR/InputFiles/PprConfiguration.json'
        File(pprfile).touch(text, mkdir=True)

        text = '''
{
"DefaultPowerScalingFactor": {
   "IP_CPU::ARR_ATOM_L2CXX::SSA_ATOM_VMIN_K_CATF6_X_VCCIA_F6_3800_L2DATAPMUXON_1006": 2.3
   }
}
'''
        File('Modules/PPR/InputFiles/SafeDefaults.json').touch(text, mkdir=True)

        obj.do_ppr_2nd()

        expect = '''
{
   "DtsUpperThreshold": 151,
   "IgnoreUnitsWithCurfbins": [
      "9901",
      "9742"
   ],
   "TestInstance2Tolerances": {
      "IP_CPU::ARR_ATOM_L2CXX::SSA_ATOM_VMIN_K_CATF6_X_VCCIA_F6_3800_L2DATAPMUXON_1006": [
         {
            "PprExitTempRangeUpperTolerance": 0,
            "PprExitTempRangeLowerTolerance": 60,
            "DefaultTemperatureOffset": 2,
            "DefaultPowerScalingFactor": 2.3,
            "TtrMode": [
               "SHORT"
            ]
         }
      ],
      "IP_CPU::ARR_ATOM_L2CXX::SSA_ATOM_VMIN_K_CATF6_X_VCCIA_F6_3800_L2DATAPMUXON_1005": [
         {
            "PprExitTempRangeUpperTolerance": 0,
            "PprExitTempRangeLowerTolerance": 60,
            "DefaultTemperatureOffset": 2,
            "DefaultPowerScalingFactor": 1,
            "TtrMode": [
               "SHORT"
            ]
         }
      ]
   }
}
'''
        self.assertTextEqual(File(pprfile).read(), expect)

        # check report
        expect = '''IP_CPU::ARR_ATOM_L2CXX::SSA_ATOM_VMIN_K_CATF6_X_VCCIA_F6_3800_L2DATAPMUXON_1005
'''
        self.assertTextEqual(File('POR_TP/TGLH81/Reports/ppr_instancenames_no_safe_value.txt').read(), expect)

        # Fail case: instance name not match ============================================
        text = '''
{
"DefaultPowerScalingFactor": {
   "IP_CPU::ARR_ATOM_L2CXX::SSA_ATOM_VMIN_K_CATF6_X_VCCIA_F6_3800_L2DATAPMUXON_1001": 2.3
   }
}
'''
        File('Modules/PPR/InputFiles/SafeDefaults.json').touch(text, newfile=True)
        with self.assertRaisesRegex(ErrorInput, 'instance name not found'):
            obj.do_ppr_2nd()

        # use engtp, should be no error
        File('POR_TP').rename('ENG_TP')
        tp = TestProgram('ENG_TP/TGLH81/EnvironmentFile.env')
        obj = MtplEncode(tp)
        obj.do_ppr_2nd()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_do_fsm_env_copy(self):
        with TempDir(startcopy=f'{UT_DIR}/Simple3', chdir=True, name=True) as tdir:
            tp = TestProgram(f'POR_TP/TGLH81/EnvironmentFile.env')
            obj = MtplEncode(tp)
            bom = 'TGLH81'

            # case1: I drive production ulat, env has no FSM_FILE_PATH
            self.assertEqual(obj.do_fsm_env_copy('I:/ulat/fsm/blah', bom), -1)

            # Add the FSM_FILE_PATH in env
            tp.env.set_item('FSM_FILE_PATH', 'I:/something')
            File(tp.envfile).rewrite(''.join(tp.env.rebuild()), 'unittest')

            # case2: I drive production ulat
            self.assertEqual(obj.do_fsm_env_copy('I:/ulat/fsm/blah', bom), 1)
            res = re.findall('(FSM_FILE_PATH.*)', File('POR_TP/TGLH81/EnvironmentFile.env').read(), re.MULTILINE)
            self.assertEqual(res, ['FSM_FILE_PATH = "I:/ulat/fsm/blah";'])

            # case3: mv ulat test case
            called = []

            def fake(slf, *args, **kwargs):
                called.append(args)

            timesec = time.time()
            File(f'POR_TP/TGLH81/FullSkipModelInput.csv').touch('fsm,csv,blah')

            # Mock the _get_ulat_mv_path method to return our test directory
            with MockVar(obj, '_get_ulat_mv_path', Mock(return_value=f'{tdir}/ulat_mv')):
                fsmfile = f'{tdir}/ulat_mv/fsm/{timesec}/FullSkipModelInput.csv'
                with MockVar(File, "copy", Mock()), \
                        MockVar(DataHost, 'central', fake):  # Mock the Data host copy output, already manual validated
                    self.assertEqual(obj.do_fsm_env_copy(fsmfile, bom), 2)
                res = re.findall('(FSM_FILE_PATH.*)', File('POR_TP/TGLH81/EnvironmentFile.env').read(), re.MULTILINE)
                self.assertEqual(res, [f'FSM_FILE_PATH = "{fsmfile}";'])
                print(called)
                actual_call = called[0]
                actual_path = actual_call[1][0]
                convert_suffix = actual_path.replace('\\', '/').split('ulat_mv/')[-1]
                actual_suffix = f'ulat_mv/{convert_suffix}'
                self.assertEqual(actual_call[0], 'ulatmv_copy')
                self.assertEqual(actual_call[1][1], 'fsm,csv,blah')
                self.assertEqual(actual_suffix, f'ulat_mv/fsm/{timesec}/FullSkipModelInput.csv')

            # case4: V drive engg ulat but x-site info file not existing
            with MockVar(MtplEncode, 'ULAT_ENGG', f'{tdir}/ulat_engg'):
                File(f'{UT_DIR}/ulat_ut/FullSkipModelInput.csv').copy(f'{tdir}/ulat_engg')
                File(f'POR_TP/TGLH81/FullSkipModelInput.csv').touch('fsm,csv,blah')
                fsmfile = f'{tdir}/ulat_engg'
                with MockVar(File, "copy", Mock()), \
                        MockVar(DataHost, 'central', Mock()):  # Mock the Data host copy output, already manual validated
                    self.assertEqual(obj.do_fsm_env_copy(fsmfile, bom), -2)
                res = re.findall('(FSM_FILE_PATH.*)', File('POR_TP/TGLH81/EnvironmentFile.env').read(), re.MULTILINE)
                self.assertEqual(res, [f'FSM_FILE_PATH = "{fsmfile}";'])

            # case5: V drive engg ulat
            with MockVar(MtplEncode, 'ULAT_ENGG', f'{tdir}/ulat_engg'):
                File(f'POR_TP/TGLH81/FullSkipModelInput.csv').touch('fsm,csv,blah')
                File(f'Shared/BaseInputs/Common/Common_TGLH81/FSM_Site_Config.JF.PG.txt').touch('blah, blah, blah', mkdir=True)
                fsmfile = f'{tdir}/ulat_engg'
                with MockVar(File, "copy", Mock()), \
                        MockVar(DataHost, 'central', Mock()):    # Mock the Data host copy output, already manual validated
                    self.assertEqual(obj.do_fsm_env_copy(fsmfile, bom), 103)
                res = re.findall('(FSM_FILE_PATH.*)', File('POR_TP/TGLH81/EnvironmentFile.env').read(), re.MULTILINE)
                self.assertEqual(res, [f'FSM_FILE_PATH = "{fsmfile}";'])

            # case6: engg ulat and duplicate config files
            with MockVar(MtplEncode, 'ULAT_ENGG', f'{tdir}/ulat_engg'):
                File(f'POR_TP/TGLH81/FullSkipModelInput.csv').touch('fsm,csv,blah')
                File(f'Shared/BaseInputs/Common/Common_TGLH81/FSM_Site_Config.JF.PG.txt').touch('blah, blah, blah', mkdir=True)
                File(f'Shared/BaseInputs/Common/Common_TGLH81/FSM_Site_Config.JF.FM.PG.txt').touch('blah', mkdir=True)
                fsmfile = f'{tdir}/ulat_engg'
                # Mock DataHost.central to prevent real network calls
                with MockVar(File, "copy", Mock()), \
                        MockVar(DataHost, 'central', Mock()):
                    with self.assertRaisesRegex(ErrorUser, 'Only 1 FSM_Site_Config file allowed per BOM'):
                        obj.do_fsm_env_copy(fsmfile, bom)
                res = re.findall('(FSM_FILE_PATH.*)', File('POR_TP/TGLH81/EnvironmentFile.env').read(), re.MULTILINE)
                self.assertEqual(res, [f'FSM_FILE_PATH = "{fsmfile}";'])

    def test_do_fsmpath_assembl(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple3/POR_TP/TGLH81/EnvironmentFile.env')
        obj = MtplEncode(tp)

        # Test NVL product paths
        tpname_nvl = 'NVLS756A0H01P0FS538'
        bom = 'Class_NVL_S28C'
        isval1 = True
        ispart1 = False

        # None Case, return MV FSM path for NVL
        with MockVar(tp, 'get_family_name', Mock(return_value='NVLS756A0H01P0FS538')):  # Changed from get_name to get_family_name
            result_none = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/ulat_mv/fsm/1.1/FullSkipModelInput.csv'
            with MockVar(time, "time", Mock(return_value=1.1)):
                self.assertEqual(obj.do_fsmpath_assembl(None, bom, isval1, ispart1), result_none)

        # Test Case 1, return V: drive FSM path for NVL
        result1 = obj.do_fsmpath_assembl(tpname_nvl, bom, isval1, ispart1)
        expect1 = 'I:/engineering/dev/sctp/tptorrent/ulat/fsm/hdmx/nvl/Class_NVL_S28C/01P00/FullSkipModelInput.csv'
        self.assertTextEqual(result1, expect1)

        # Test Case 2, return V: drive partial TP FSM path for NVL
        tpname2 = 'NVLS756A0H01P0FGX38'
        isval2 = False
        ispart2 = True
        result2 = obj.do_fsmpath_assembl(tpname2, bom, isval2, ispart2)
        expect2 = 'I:/engineering/dev/sctp/tptorrent/ulat/fsm/hdmx/nvl/Class_NVL_S28C/01P00GX/FullSkipModelInput.csv'
        self.assertTextEqual(result2, expect2)

        # Test Case 3, return I: drive FSM path for NVL
        tpname3 = 'NVLS756A0H01P00S538'
        isval3 = False
        ispart3 = False
        result3 = obj.do_fsmpath_assembl(tpname3, bom, isval3, ispart3)
        expect3 = 'I:/ulat/fsm/hdmx/nvl/Class_NVL_S28C/01P00/FullSkipModelInput.csv'
        self.assertTextEqual(result3, expect3)

        # Test DNL product paths
        tpname_dnl = 'DNLS763B0H49A00S610'
        bom_dnl = 'Class_DNL_S28C'

        # DNL Test Case 1, return I: drive FSM path
        result_dnl1 = obj.do_fsmpath_assembl(tpname_dnl, bom_dnl, False, False)
        expect_dnl1 = 'I:/ulat/fsm/hdmx/dnl/Class_DNL_S28C/49A00/FullSkipModelInput.csv'
        self.assertTextEqual(result_dnl1, expect_dnl1)

        # DNL Test Case 2, return V: drive partial TP FSM path
        tpname_dnl2 = 'DNLS763B0H49A0ACX09'
        result_dnl2 = obj.do_fsmpath_assembl(tpname_dnl2, bom_dnl, False, True)
        expect_dnl2 = 'I:/engineering/dev/sctp/tptorrent/ulat/fsm/hdmx/dnl/Class_DNL_S28C/49A00CX/FullSkipModelInput.csv'
        self.assertTextEqual(result_dnl2, expect_dnl2)

        # DNL None Case, return MV FSM path
        with MockVar(tp, 'get_family_name', Mock(return_value='DNLS763B0H49A00S610')):  # Changed from get_name to get_family_name
            result_dnl_none = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/dnl/ulat_mv/fsm/1.1/FullSkipModelInput.csv'
            with MockVar(time, "time", Mock(return_value=1.1)):
                self.assertEqual(obj.do_fsmpath_assembl(None, bom_dnl, False, False), result_dnl_none)


class TestNPRTrigger(TestCase):

    def _make_csv(self, path):
        # Create a sample CSV file for testing
        content = (
            'TLA,TP_naming,PUPONOFF,Hermes\n'
            'NVL,A0H01,ON,FALSE\n'
            'NVL,B0H02,ON,FALSE\n'
            'NVL,A0H05,OFF,FALSE\n'
        )
        File(path).touch(content)

    def test_npr_csv_parser_type1(self):
        # Type 1: find line number by column header name and value
        with TempDir(name=True, chdir=True) as tdir:
            tp = TestProgram(f'{UT_DIR}/torch_mvtp_pass/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env')
            self._make_csv('test.csv')

            # Case 1: Column name exact match
            found, lineno = NPRTrigger(tp).npr_csv_parser('test.csv', 'TP_naming', value='A0H01')
            self.assertTrue(found)
            self.assertEqual(lineno, 1)

            # Case 2: column name lookup is case-insensitive
            found, lineno = NPRTrigger(tp).npr_csv_parser('test.csv', 'tp_naming', value='A0H05')
            self.assertTrue(found)
            self.assertEqual(lineno, 3)

            # Case 3: value not found returns (False, -1)
            found, lineno = NPRTrigger(tp).npr_csv_parser('test.csv', 'tp_naming', value='NONEXISTENT')
            self.assertFalse(found)
            self.assertEqual(lineno, -1)

    def test_npr_csv_parser_type2(self):
        # Type 2: get value by line number and column name
        with TempDir(name=True, chdir=True) as tdir:
            tp = TestProgram(f'{UT_DIR}/torch_mvtp_pass/ENG_TP/Class_MTL_P68_DEBUG/EnvironmentFile.env')
            self._make_csv('test.csv')

            # Case 1: Column name is case-insensitive with line number
            result1 = NPRTrigger(tp).npr_csv_parser('test.csv', 'PUPONOFF', line_number=3)
            self.assertEqual(result1, 'OFF')

            # Case 2: line_number out of range raises ErrorInput
            with self.assertRaisesRegex(ErrorInput, 'npr_csv_parser:'):
                NPRTrigger(tp).npr_csv_parser('test.csv', 'Hermes', value='B0H02', line_number=99)

    def test_outdir_tpname_decode(self):
        with TempDir(startcopy=f'{UT_DIR}/Simple3', chdir=True, name=True) as tdir:
            File(f'{UT_DIR}/NPR_usrv/UservarDefinitions.usrv').copy('Shared/BaseInputs/UservarDefinitions.usrv')
            tp = TestProgram('POR_TP/TGLH81/EnvironmentFile.env')
            obj = NPRTrigger(tp)

            # Case 1: user outdir is valid for prod so decode from it
            outdir1 = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/NVLS763B0H02S03S609'
            expect1 = True, 'NVLS763B0H02S03S609'
            self.assertEqual(obj.outdir_tpname_decode(outdir1), expect1)

            # Case 2: user outdir is invalid for prod so decode from alt name
            outdir2 = 'I:/engineering/dev/PQV/dtv/xGFx/wwei8/Hermes_PUP_with_bom'
            expect2 = False, 'NVLS763B0H02A03S600'
            self.assertEqual(obj.outdir_tpname_decode(outdir2), expect2)

            # Case 3: user outdir is None
            outdir3 = None
            expect3 = False, 'NVLS763B0H02A03S600'
            self.assertEqual(obj.outdir_tpname_decode(outdir3), expect3)

    def test_do_puppath_assembl(self):
        with TempDir(startcopy=f'{UT_DIR}/SimpleNVL6', chdir=True, name=True) as tdir:
            File(f'{UT_DIR}/NPR_usrv/UservarDefinitions.usrv').copy('Shared/BaseInputs/UservarDefinitions.usrv')
            tp = TestProgram(f'POR_TP/Class_NVL_H81/EnvironmentFile.env')
            obj = NPRTrigger(tp)

            # Case None, tp path is None, return MV ulat pup path with timestamp
            tppath_none = None
            expect_none = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/ulat_mv/pup/1772066770.895639'
            with MockVar(time, "time", Mock(return_value=1772066770.895639)):
                self.assertEqual(obj.do_puppath_assembl(tppath_none), expect_none)

            # Case 1, I drive prod build
            tppath1 = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/NVLS763B0H02S03S609'
            result1 = obj.do_puppath_assembl(tppath1)
            expect1 = 'I:/ulat/pup/release/nvl/NVLXXB0H02S03'
            self.assertTextEqual(result1, expect1)

            # Case 2, V drive prod build
            tppath2 = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/NVLS763B0H02S0BS609'
            result2 = obj.do_puppath_assembl(tppath2)
            expect2 = 'I:/engineering/dev/sctp/tptorrent/ulat/pup/staging/nvl/NVLXXB0H02S0B'
            self.assertTextEqual(result2, expect2)

            # Case 3, MV build
            tppath3 = 'I:/engineering/dev/PQV/dtv/xGFx/wwei8/Hermes_PUP_with_bom'
            expect3 = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/ulat_mv/pup/1772066770.895739'
            with MockVar(time, "time", Mock(return_value=1772066770.895739)):
                self.assertEqual(obj.do_puppath_assembl(tppath3), expect3)

            # Case 4, V drive engineering build
            tppath4 = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/NVLS763B0H02SPTH609'
            expect4 = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/ulat_mv/pup/1772066770.895839'
            with MockVar(time, "time", Mock(return_value=1772066770.895839)):
                self.assertEqual(obj.do_puppath_assembl(tppath4), expect4)

    def test_modify_env(self):
        with TempDir(startcopy=f'{UT_DIR}/SimpleNVL6', chdir=True, name=True) as tdir:
            File(f'{UT_DIR}/NPR_usrv/UservarDefinitions.usrv').copy('Shared/BaseInputs/UservarDefinitions.usrv')
            tp = TestProgram(f'POR_TP/Class_NVL_H81/EnvironmentFile.env')
            obj = NPRTrigger(tp)

            # Case 1: Normal case, modify env for I drive TP, return True.
            outdir1 = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/NVLS763B0H02S03S609'
            expect1 = 'I:/ulat/pup/release/nvl/NVLXXB0H02S03'
            self.assertEqual(obj.modify_env(outdir1), 10)
            self.assertEqual(tp.env.get_env_dict().get('PUP_PATTERNS_DIR'), expect1)

            # Case 2: Normal case, modify env for V drive TP, return True.
            outdir2 = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/NVLS763B0H02S0BS609'
            expect2 = 'I:/engineering/dev/sctp/tptorrent/ulat/pup/staging/nvl/NVLXXB0H02S0B'
            self.assertEqual(obj.modify_env(outdir2), 10)
            self.assertEqual(tp.env.get_env_dict().get('NPR_FOLDER_PATH'), expect2)

            # Case 3: Normal case, modify env for MV TP, return True
            outdir3 = 'I:/engineering/dev/PQV/dtv/xGFx/wwei8/Hermes_PUP_with_bom'
            expect3 = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/ulat_mv/pup/1772066770.895739'
            with MockVar(time, "time", Mock(return_value=1772066770.895739)):
                self.assertEqual(obj.modify_env(outdir3), 10)
                self.assertEqual(tp.env.get_env_dict().get('PUP_SHORT_PLISTS_PATH'), expect3)

            # Case 4: modify env with None path, should set to MV ulat pup path with timestamp
            expect4 = 'I:/engineering/dev/sctp/tptorrent/hdmxprogs/nvl/ulat_mv/pup/1772066770.895839'
            with MockVar(time, "time", Mock(return_value=1772066770.895839)):
                self.assertEqual(obj.modify_env(None), 10)
                self.assertEqual(tp.env.get_env_dict().get('PUP_PATTERNS_DIR'), expect4)

    def test_mod_inst_update(self):
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True) as tdir:
            shutil.copytree(src, f'{tdir}/TPL')
            with Chdir(f'{tdir}/TPL'):
                npr = NPRTrigger(TestProgram(Env.get_envfile()))

                # Mock up a PUP module
                text = r'''
                Test PrimePUPTestMethod CTRL_X_PUP_K_TESTPLANENDFLOW_X_X_X_X_PRINTITUFF
                {
                      LogLevel = "Disabled";
                      Mode = "Disabled";
                }
                Test PrimeCallbacksRegistrarTestMethod CTRL_X_CALLBACKS_K_INIT_X_X_X_X_PUP
                {
                      LogLevel = "Disabled";
                }
                '''
                File(f'Shared/Modules/TPI/TPI_PUP_XXX/TPI_PUP_XXX.mtpl').touch(text, newfile=True, mkdir=True)

                # Case 1: updates is None.
                mod_path1 = 'Shared/Modules/TPI/TPI_PUP_XXX/TPI_PUP_XXX.mtpl'
                self.assertEqual(npr.mod_inst_update(mod_path1), 1)

                # Case 2: mod_path is not exist.
                mod_path2 = 'Shared/Modules/TPI/TPI_PUP_BLAH/TPI_PUP_XXX.mtpl'
                updates2 = [
                    {
                        'test_instance': 'PrimePUPTestMethod CTRL_X_PUP_K_TESTPLANENDFLOW_X_X_X_X_PRINTITUFF',
                        'param': 'Mode = ',
                        'replace_val': 'Enabled',
                    },
                    {
                        'test_instance': 'PrimeCallbacksRegistrarTestMethod CTRL_X_CALLBACKS_K_INIT_X_X_X_X_PUP',
                        'param': 'LogLevel =',
                        'replace_val': 'Enabled',
                    },
                ]
                self.assertEqual(npr.mod_inst_update(mod_path2, updates2), 2)

                # Case 3: mod_path exist and modification successful.
                mod_path3 = 'Shared/Modules/TPI/TPI_PUP_XXX/TPI_PUP_XXX.mtpl'
                updates3 = [
                    {
                        'test_instance': 'PrimePUPTestMethod CTRL_X_PUP_K_TESTPLANENDFLOW_X_X_X_X_PRINTITUFF',
                        'param': 'Mode = ',
                        'replace_val': 'Chicken',
                    },
                    {
                        'test_instance': 'PrimeCallbacksRegistrarTestMethod CTRL_X_CALLBACKS_K_INIT_X_X_X_X_PUP',
                        'param': 'LogLevel =',
                        'replace_val': 'Wing',
                    },
                ]
                self.assertEqual(npr.mod_inst_update(mod_path3, updates3), 3)

                # Case 4: mod_path exist but no modification. Raise ErrorInput in this case since it is unexpected.
                mod_path4 = 'Shared/Modules/TPI/TPI_PUP_XXX/TPI_PUP_XXX.mtpl'
                updates4 = [
                    {
                        'test_instance': 'PrimeCallbacksRegistrarTestMethod CTRL_X_CALLBACKS_K_INIT_X_X_X_X_PUP',
                        'param': 'MonitorLoopNum =',
                        'replace_val': '3',
                    }
                ]
                with self.assertRaisesRegex(ErrorInput, 'NPRTrigger mod_instance_update: no modification made.'):
                    npr.mod_inst_update(mod_path4, updates4)

    def test_modify_mod_pupoff(self):
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True) as tdir:
            shutil.copytree(src, f'{tdir}/TPL')
            with Chdir(f'{tdir}/TPL'):
                npr = NPRTrigger(TestProgram(Env.get_envfile()))

                # Mock up a Base module
                text = r'''
                Test VminForwardingBase CTRL_X_PRIMEVMINFORWARDING_K_INIT_X_X_X_X_VMIN
                {
                      LogLevel = "Disabled";
                      EnableHermesMode = "Blahblah";
                      Mode = "Disabled";
                }
                '''
                File(f'Shared/Modules/TPI/TPI_BASE_XXX/TPI_BASE_XXX.mtpl').touch(text, newfile=True, mkdir=True)

                # Case: updates the TPI_base module.
                self.assertEqual(npr.modify_mod_pupoff(), 12)

    def test_modify_mod_pupon(self):
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True) as tdir:
            shutil.copytree(src, f'{tdir}/TPL')
            with Chdir(f'{tdir}/TPL'):
                npr = NPRTrigger(TestProgram(Env.get_envfile()))

                # Mock up a Base module
                text = r'''
                Test VminForwardingBase CTRL_X_PRIMEVMINFORWARDING_K_INIT_X_X_X_X_VMIN
                {
                      LogLevel = "Disabled";
                      EnableHermesMode = "Blahblah";
                      Mode = "Disabled";
                }
                '''
                File(f'Shared/Modules/TPI/TPI_BASE_XXX/TPI_BASE_XXX.mtpl').touch(text, newfile=True, mkdir=True)

                # Mock up a PUP module
                text = r'''
                Test PlistConfigTC CTRLX_PLISTCONFIG_E_INIT_X_X_X_X_SKIPSHORT
                {
                      LogLevel = "Disabled";
                      EnableHermesMode = "Blahblah";
                      BypassPort = "Blahblah";
                }
                CSharpTest PrimePUPTestMethod CTRL_X_PUP_K_TESTPLANENDFLOW_X_X_X_X_PRINTITUFF
                {
                    LogLevel = "Disabled";
                    Mode = "Disabled";
                    MonitorLoopNum = 3;
                    PatternsFilePath = "$PUP_PATTERNS_DIR\\@LATEST_REV@\\PAS_PTD.pup.json";
                    PupDebugMode = "Disabled";
                    PupMatchMode = "VidAndEfuseBoth";
                }
                '''
                File(f'Shared/Modules/TPI/TPI_PUP_XXX/TPI_PUP_XXX.mtpl').touch(text, newfile=True, mkdir=True)

                # Case: updates the above 2 modules.
                self.assertEqual(npr.modify_mod_pupon(), 13)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_allowed(self):
        tp = TestProgram(f'{UT_DIR}/torch_p6828_fixer/POR_TP/Class_MTL_P28/EnvironmentFile.env')
        self.assertEqual(NPRTrigger(tp).allowed_modules(), True)  # This include dig modules

        # unittest - no ARR
        data = ['/path/TPI_VCC/a.mtpl',
                '/path/CLK_VCC/a.mtpl']
        with MockVar(tp, 'get_all_mtpl_from_stpl', Mock(return_value=data)):
            self.assertEqual(NPRTrigger(tp).allowed_modules(), False)

        # unittest - SARR
        data = ['/path/TPI_VCC/a.mtpl',
                '/path/SARR_blah/a.mtpl',
                '/path/CLK_VCC/a.mtpl']
        with MockVar(tp, 'get_all_mtpl_from_stpl', Mock(return_value=data)):
            self.assertEqual(NPRTrigger(tp).allowed_modules(), True)

        # unittest - ARR
        data = ['/path/TPI_VCC/a.mtpl',
                '/path/ARR_blah/a.mtpl',
                '/path/CLK_VCC/a.mtpl']
        with MockVar(tp, 'get_all_mtpl_from_stpl', Mock(return_value=data)):
            self.assertEqual(NPRTrigger(tp).allowed_modules(), True)

    def test_trigger(self):
        # Test NPRTrigger.trigger() - creates tar.gz, copies to trigpath, creates .trigger file with TP_PATH content
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True) as tdir:
            shutil.copytree(src, f'{tdir}/TPL')
            with Chdir(f'{tdir}/TPL'):
                npr = NPRTrigger(TestProgram(Env.get_envfile()))

                # Case 1: fname not set, outdir provided - fname auto-generated, tar.gz and .trigger created
                with TempDir(name=True) as trigdir, TempDir(name=True) as outdir:
                    # Create a fake InputFiles folder in CWD so input_files_dirs is non-empty
                    fake_input = 'Modules/ARR_CORE/C0/InputFiles'
                    mkdirs(fake_input)

                    captured = {}

                    def fake_taradd(tarfname, folder, exclude=None):
                        # Capture exclude_list and create a real dummy tar.gz
                        captured['exclude'] = exclude
                        captured['tarfname'] = tarfname
                        with tarfile.open(tarfname, 'w:gz'):
                            pass

                    npr.trigpath = trigdir
                    npr.fname = None  # ensure fname is not set so auto-generation is tested

                    with MockVar(sys.modules['mod.mtplencode'], 'TarAdd', fake_taradd):
                        npr.trigger(outdir)

                    # Verify fname was auto-generated
                    self.assertIsNotNone(npr.fname)

                    # Verify the tar.gz was created and copied to trigpath
                    tar_file = f'{trigdir}/{npr.fname}.tar.gz'
                    self.assertTrue(exists(tar_file), f'tar.gz not created: {tar_file}')

                    # Verify the .trigger file was created with TP_PATH content
                    trigger_file = f'{trigdir}/{npr.fname}.trigger'
                    self.assertTrue(exists(trigger_file), f'.trigger file not created: {trigger_file}')
                    trigger_content = File(trigger_file).read()
                    self.assertIn(f'TP_PATH: {outdir}', trigger_content)

                    # Verify local tar.gz was cleaned up
                    local_tar = f'{captured["tarfname"]}'
                    self.assertFalse(exists(local_tar), f'Local tar.gz should be cleaned up: {local_tar}')

                    # Verify trigflag was set
                    self.assertTrue(npr.trigflag)

                    # Verify exclude_list contains all expected entries
                    self.assertIn('exclude', captured)
                    self.assertIn('.github', captured['exclude'])
                    self.assertIn('astra', captured['exclude'])
                    self.assertIn('complete_tp.tar.gz', captured['exclude'],
                                  'complete_tp.tar.gz must be excluded')
                    self.assertIn('Modules/ARR_CORE/C0/InputFiles', captured['exclude'],
                                  'input_files_dirs must be included in exclude_list')
                    self.assertIn(f'{npr.fname}.tar.gz', captured['exclude'],
                                  'Current tar.gz filename must be in exclude_list')

                # Case 2: fname already set, outdir=None - fname preserved, .trigger with MV message
                with TempDir(name=True) as trigdir:
                    captured = {}

                    def fake_taradd(tarfname, folder, exclude=None):
                        captured['exclude'] = exclude
                        with tarfile.open(tarfname, 'w:gz'):
                            pass

                    npr.trigpath = trigdir
                    npr.fname = 'preset_fname'
                    npr.trigflag = False  # reset

                    with MockVar(sys.modules['mod.mtplencode'], 'TarAdd', fake_taradd):
                        npr.trigger(outdir=None)

                    # Verify fname was not overwritten
                    self.assertEqual(npr.fname, 'preset_fname')

                    # Verify the tar.gz was copied to trigpath
                    tar_file = f'{trigdir}/preset_fname.tar.gz'
                    self.assertTrue(exists(tar_file), f'tar.gz not created: {tar_file}')

                    # Verify the .trigger file was created with MV message
                    trigger_file = f'{trigdir}/preset_fname.trigger'
                    self.assertTrue(exists(trigger_file), f'.trigger file not created: {trigger_file}')
                    trigger_content = File(trigger_file).read()
                    self.assertIn('User defined TP build destination is none, treat as MV', trigger_content)

                    # Verify exclude_list contains static entries including complete_tp.tar.gz
                    self.assertIn('exclude', captured)
                    self.assertIn('.github', captured['exclude'])
                    self.assertIn('temp', captured['exclude'])
                    self.assertIn('complete_tp.tar.gz', captured['exclude'])

    def test_wait(self):
        # Test NPRTrigger.wait() covering all branches: skip when no trigger, success, error, and timeout
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True) as tdir:
            shutil.copytree(src, f'{tdir}/TPL')
            with Chdir(f'{tdir}/TPL'):
                npr = NPRTrigger(TestProgram(Env.get_envfile()))

                with TempDir(name=True) as trigdir:
                    npr.trigpath = trigdir
                    npr.fname = 'test_wait_file'
                    npr.timeout = 2  # reduce timeout for test speed
                    npr.sleep_sec = 1

                    # Case 0: trigflag=False (trigger never fired), skip and return 0
                    npr.trigflag = False
                    self.assertEqual(npr.wait(), 0)

                    # Set trigflag=True for all remaining cases (trigger did fire)
                    npr.trigflag = True

                    # Case 1: success file exists, return 18
                    File(f'{trigdir}/test_wait_file.success').touch('success')
                    self.assertEqual(npr.wait(), 18)

                    # Case 2: error file exists, raises ErrorInput
                    check_and_del(f'{trigdir}/test_wait_file.success')
                    File(f'{trigdir}/test_wait_file.ERROR').touch('error')
                    with self.assertRaisesRegex(ErrorInput, 'NPRTrigger error:'), \
                            MockVar(npr, 'trigpath', trigdir):
                        npr.wait()

                    # Case 3: no success/error files, timeout reached, raises ErrorInput
                    check_and_del(f'{trigdir}/test_wait_file.ERROR')
                    npr.timeout = 2
                    npr.sleep_sec = 1
                    with self.assertRaisesRegex(ErrorInput, 'NPRTrigger wait: timeout of'), \
                            MockVar(npr, 'trigpath', trigdir):
                        npr.wait()

    def test_is_invalid(self):
        # Test is_invalid with various cases
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True) as tdir:
            shutil.copytree(src, f'{tdir}/TPL')
            with Chdir(f'{tdir}/TPL'):
                npr = NPRTrigger(TestProgram(Env.get_envfile()))

                # Case 1: PCD dielet indicator, return 3
                with MockVar(npr.tpobj, 'usrv', Mock(get_var=Mock(return_value='PCD'))):
                    self.assertEqual(npr.is_invalid(), 3)

                # Case 2: no digital modules (allowed_modules returns False), return 4
                with MockVar(npr.tpobj, 'usrv', Mock(get_var=Mock(return_value='CPU, PCD'))):
                    with MockVar(npr, 'allowed_modules', Mock(return_value=False)):
                        self.assertEqual(npr.is_invalid(), 4)

                # Case 3: trigpath does not exist, return 5
                with MockVar(npr.tpobj, 'usrv', Mock(get_var=Mock(return_value='not_PCD'))):
                    with MockVar(npr, 'allowed_modules', Mock(return_value=True)):
                        with MockVar(npr, 'trigpath', '/nonexistent/path/that/does/not/exist'):
                            self.assertEqual(npr.is_invalid(), 5)

                # Case 4: all conditions pass, return 0
                with TempDir(name=True) as trigdir:
                    with MockVar(npr.tpobj, 'usrv', Mock(get_var=Mock(return_value='not_PCD'))):
                        with MockVar(npr, 'allowed_modules', Mock(return_value=True)):
                            with MockVar(npr, 'trigpath', trigdir):
                                self.assertEqual(npr.is_invalid(), 0)

    def test_npr_trigger_main(self):
        # Integration test for NPRTrigger.main() with nprtrigger=True
        src = f'{UT_DIR_REPO}/Simple3'
        with TempDir(name=True) as tdir:
            shutil.copytree(src, f'{tdir}/TPL')
            with Chdir(f'{tdir}/TPL'):
                npr = NPRTrigger(TestProgram(Env.get_envfile()))

                # Case 1: nprtrigger=False, return immediately
                result = npr.main(nprtrigger=False, outdir='/some/outdir')
                self.assertEqual(result, 1)

                # Case 2: nprtrigger=True but outdir=None, return 2
                result = npr.main(nprtrigger=True, outdir=None)
                self.assertEqual(result, 2)

                # Case 3: is_invalid returns non-zero, return that error code
                with MockVar(npr, 'is_invalid', lambda: 3):
                    result = npr.main(nprtrigger=True, outdir='/some/outdir')
                    self.assertEqual(result, 3)

                # Case 4: TP name not found in CSV, return 6
                with MockVar(npr, 'is_invalid', lambda: 0), \
                        MockVar(npr, 'outdir_tpname_decode', lambda outdir: ('prod', 'NVLTEST01')), \
                        MockVar(npr, 'npr_csv_parser', lambda *a, **kw: (False, None)):
                    result = npr.main(nprtrigger=True, outdir='/some/outdir')
                    self.assertEqual(result, 6)

                # Case 5: NPR mode is OFF, modify_mod_pupoff called, return 7
                call_log = []
                with MockVar(npr, 'is_invalid', lambda: 0), \
                        MockVar(npr, 'outdir_tpname_decode', lambda outdir: ('prod', 'NVLTEST01')), \
                        MockVar(npr, 'npr_csv_parser', lambda *a, **kw: (True, 1) if kw.get('value') else 'off'), \
                        MockVar(npr, 'modify_mod_pupoff', lambda: call_log.append('pupoff') or 12):
                    result = npr.main(nprtrigger=True, outdir='/some/outdir')
                    self.assertEqual(result, 7)
                    self.assertIn('pupoff', call_log)

                # Case 6: NPR mode is ON, modify_mod_pupon/modify_env/trigger called
                call_log = []
                with TempDir(name=True) as trigdir:
                    with TempDir(name=True) as outdir:
                        npr.trigpath = trigdir
                        npr.fname = 'test_main_trigger'

                        def fake_taradd(tarfname, *args, **kwargs):
                            # Create a real dummy tar.gz so File.copy has a valid source
                            with tarfile.open(tarfname, 'w:gz'):
                                pass

                        with MockVar(npr, 'is_invalid', lambda: 0), \
                                MockVar(npr, 'outdir_tpname_decode', lambda o: ('prod', 'NVLTEST01')), \
                                MockVar(npr, 'npr_csv_parser', lambda *a, **kw: (True, 1) if kw.get('value') else 'on'), \
                                MockVar(npr, 'modify_mod_pupon', lambda: call_log.append('pupon') or 13), \
                                MockVar(npr, 'modify_env', lambda o: call_log.append('modify_env') or 10), \
                                MockVar(sys.modules['mod.mtplencode'], 'TarAdd', fake_taradd):
                            npr.main(nprtrigger=True, outdir=outdir)

                        self.assertIn('pupon', call_log)
                        self.assertIn('modify_env', call_log)

                        # Verify tar.gz was copied to trigpath
                        tar_file = f'{trigdir}/test_main_trigger.tar.gz'
                        self.assertTrue(exists(tar_file), f'tar.gz not created: {tar_file}')

                        # Verify .trigger file was created with TP_PATH content
                        trigger_file = f'{trigdir}/test_main_trigger.trigger'
                        self.assertTrue(exists(trigger_file), f'Trigger file not created: {trigger_file}')
                        trigger_content = File(trigger_file).read()
                        self.assertIn(f'TP_PATH: {outdir}', trigger_content)

                        # Verify trigflag was set
                        self.assertTrue(npr.trigflag)

    def test_ignore_func(self):
        with TempDir(name=True, delete=True) as tdir:
            File(f'{tdir}/SRC/a.txt').touch(mkdir=True)
            File(f'{tdir}/SRC/Modules/A/InputFiles/a.txt').touch(mkdir=True)
            File(f'{tdir}/SRC/Modules/A/a.mtpl').touch(mkdir=True)
            File(f'{tdir}/SRC/UserCode/a.dll').touch(mkdir=True)
            File(f'{tdir}/SRC/astra/a.xml').touch(mkdir=True)
            File(f'{tdir}/SRC/Shared/ok.mtpl').touch(mkdir=True)
            shutil.copytree(f'{tdir}/SRC', f'{tdir}/DST', ignore=NPRTrigger.ignore_func)
            self.assertItemsEqual(list(Allfiles(f'{tdir}/DST')), [f'{tdir}/DST/Modules/A/a.mtpl',
                                                                  f'{tdir}/DST/Shared/ok.mtpl',
                                                                  f'{tdir}/DST/a.txt',
                                                                  f'{tdir}/DST/Modules/A/InputFiles/a.txt'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
