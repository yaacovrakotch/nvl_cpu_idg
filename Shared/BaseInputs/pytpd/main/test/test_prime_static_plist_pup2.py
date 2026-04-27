#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for test_prime_static_plist_pup2
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File
from gadget.disk import Chdir
from gadget.gizmo import MockVar, with_
from gadget.ut import Mock
from gadget.helperclass import CaptureStdoutLog
from tp.testprogram import Env
from main.prime_static_plist_pup2 import *
from os.path import join, dirname, abspath
import os


class TestSPP(TestCase):

    def test_integ(self):
        # unittest integration start to finish
        # case: fuse.plist is not part of pup_short_plists.plist because it is untouched
        # tests pup_short_plists.plist is written

        with TempDir(name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup') as tdir:
            mkdirs('outdir')
            spp = StaticPlistPup('prime_static/PAS_PTD.pup.json', 'POR_TP/TGLH81/EnvironmentFile.env', 'outdir')
            spp.main()
            outfile = 'outdir/pup_short_plists.plist'
            File(outfile).touch(File(outfile).read().replace(Env.xpath(tdir), ''), newfile=True)    # remove the tdir path in expect
            self.assertGoldEqual('outdir/pup_short_plists.plist',
                                 f'{UT_DIR_REPO}/misc_files/pup_short_plists.plist.gold2')

    @with_(TempDir, name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup')
    def test_ignore(self):
        # No static prime
        File('POR_TP/TGLH81/InputFiles/No_Static_Prime_Pup2').touch(mkdir=True)
        with MockVar(TestProgram, 'init', lambda x: x):
            spp = StaticPlistPup('bom1/PAS_PTD.pup.json', 'POR_TP/TGLH81/EnvironmentFile.env', 'outdir')
            self.assertEqual(spp.main(), 2)

        # ENG_TP
        File('POR_TP').rename('ENG_TP')
        with MockVar(TestProgram, 'init', lambda x: x):
            spp = StaticPlistPup('bom1/PAS_PTD.pup.json', 'ENG_TP/TGLH81/EnvironmentFile.env', 'outdir')
            self.assertEqual(spp.main(), 1)

    @with_(TempDir, name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup')
    def test_process_plist1(self):
        # ====== unittest process_plist: Fixed PTD file and Fixed plist file
        # case1: basic pattern removed in a plb
        # case2: keep one pattern in empty plb
        # case3: Do not remove pats with #KEEP#
        # case4: top level plist with no disabled pat are not printed: main4
        # case5: sub plist untouched (main3a)
        # case5a: default occurence '1'

        File('PAS_PTD.json').touch('''
{
    "Version": "1000",
    "ProcessTypes": [
        {
            "Name": "PROCNAME",
            "StepName": "STEPNAME",
            "PerPatlistPatternsToDisable": [
                {
                    "Patlist": "IP_PCH::main1",
                    "Functionality": "FUNCT",
                    "PatternsToDisable": [
                        {
                            "Pattern": "r1"
                        },
                        {
                            "Pattern": "r2"
                        }
                    ]
                },
                {
                    "Patlist": "IP_PCH::main3",
                    "PatternsToDisable": [
                        {
                            "Pattern": "r3"
                        },
                        {
                            "Pattern": "r4"
                        }
                    ]
                }
            ]
        }
    ]
}
''')
        File('targ.plist').touch('''
Version 5.0;
GlobalPList main2
{
    GlobalPList main1 {
       Pat r1;
       Pat r2;
       Pat r2;  #KEEP#
       Pat ab;
    }
    # this tests empty
    GlobalPList main3 {
       Pat r3;
       Pat r4;
    }
    GlobalPList main3a {
       Pat r3;
       Pat r4;
    }
}

# comment1
GlobalPList main4       # not part of PTD
{
   GlobalPList main4a       # not part of PTD
   {
      Pat r1;
      Pat r2;
   }
}
# comment2
''')

        mkdirs('outdir')
        spp = StaticPlistPup('PAS_PTD.json', 'POR_TP/TGLH81/EnvironmentFile.env', 'outdir')
        spp.read_ptdfile()
        spp.process_plist('targ.plist', 'IP_PCH')
        expect = '''
# Source: targ.plist

GlobalPList main2_FUNCT_STEPNAME_PROCNAME
{
 GlobalPList main1_FUNCT_STEPNAME_PROCNAME
 {
  Pat r2;    #KEEP#
  Pat ab;
 }
 # this tests empty
 GlobalPList main3a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r3;
  Pat r4;
 }
}

# comment1
# comment2
'''
        self.assertTextEqual(''.join(spp.short['IP_PCH']).replace('\t', ' '), expect)

        # case6: untouched plist file. PTD has no match in the .plist
        spp = StaticPlistPup(f'{UT_DIR_REPO}/Simple4b_staticpup/prime_static/PAS_PTD.pup.json',
                             'POR_TP/TGLH81/EnvironmentFile.env', 'outdir')
        spp.read_ptdfile()
        spp.process_plist('targ.plist', 'IP_PCH')
        self.assertEqual(spp.short, {})    # empty

    @with_(TempDir, name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup')
    def test_process_plist2(self):
        # ====== unittest process_plist: Fixed PTD file and Fixed plist file
        # case7: ptd has top level plist and disable in subplist

        File('PAS_PTD.json').touch('''
{
    "Version": "1000",
    "ProcessTypes": [
        {
            "Name": "PROCNAME",
            "StepName": "STEPNAME",
            "PerPatlistPatternsToDisable": [
                {
                    "Patlist": "IP_PCH::main1",
                    "Functionality": "FUNCT",
                    "PatternsToDisable": [
                        {
                            "Pattern": "r1"
                        },
                        {
                            "Pattern": "r2"
                        }
                    ]
                }
            ]
        }
    ]
}
''')
        File('targ.plist').touch('''
Version 5.0;
GlobalPList main1
{
    GlobalPList main1a {
       Pat r1;
       Pat r2;
       Pat r2;  #KEEP#
       Pat ab;
    }
    # this tests empty
    GlobalPList main2a {
       Pat r1;
       Pat r2;    # 2nd occurrence
    }
    GlobalPList main3a {
       Pat r3;
       Pat r4;
    }
}
''')

        mkdirs('outdir')
        spp = StaticPlistPup('PAS_PTD.json', 'POR_TP/TGLH81/EnvironmentFile.env', 'outdir')
        spp.read_ptdfile()
        spp.process_plist('targ.plist', 'IP_PCH')
        expect = '''
# Source: targ.plist

GlobalPList main1_FUNCT_STEPNAME_PROCNAME
{
 GlobalPList main1a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r2;    #KEEP#
  Pat ab;
 }
 # this tests empty
 GlobalPList main2a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r1;
  Pat r2;    # 2nd occurrence
 }
 GlobalPList main3a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r3;
  Pat r4;
 }
}
'''
        self.assertTextEqual(''.join(spp.short['IP_PCH']).replace('\t', ' '), expect)

    @with_(TempDir, name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup')
    def test_process_plist2_occur(self):
        # ====== unittest process_plist: Fixed PTD file and Fixed plist file
        # case7a: case7 but with occurrence

        File('PAS_PTD.json').touch('''
{
    "Version": "1000",
    "ProcessTypes": [
        {
            "Name": "PROCNAME",
            "StepName": "STEPNAME",
            "PerPatlistPatternsToDisable": [
                {
                    "Patlist": "IP_PCH::main1",
                    "Functionality": "FUNCT",
                    "PatternsToDisable": [
                        {
                            "Pattern": "r1"
                        },
                        {
                            "Pattern": "r2",
                            "Occurrence": "1-3"
                        }
                    ]
                }
            ]
        }
    ]
}
''')
        File('targ.plist').touch('''
Version 5.0;
GlobalPList main1
{
    GlobalPList main1a {
       Pat r1;
       Pat r2;
       Pat r2;  #KEEP#
       Pat ab;
    }
    # this tests empty
    GlobalPList main2a {
       Pat r1;
       Pat r2;
    }
    GlobalPList main3a {
       Pat r3;
       Pat r4;
    }
}
''')

        mkdirs('outdir')
        spp = StaticPlistPup('PAS_PTD.json', 'POR_TP/TGLH81/EnvironmentFile.env', 'outdir')
        spp.read_ptdfile()
        spp.process_plist('targ.plist', 'IP_PCH')
        expect = '''
# Source: targ.plist

GlobalPList main1_FUNCT_STEPNAME_PROCNAME
{
 GlobalPList main1a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r2;    #KEEP#
  Pat ab;
 }
 # this tests empty
 GlobalPList main2a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r1;
 }
 GlobalPList main3a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r3;
  Pat r4;
 }
}
'''
        self.assertTextEqual(''.join(spp.short['IP_PCH']).replace('\t', ' '), expect)

    @with_(TempDir, name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup')
    def test_process_plist3(self):
        # ====== unittest process_plist: Fixed PTD file and Fixed plist file
        # process_plist3 with default occurrence - first only

        File('PAS_PTD.json').touch('''
{
    "Version": "1000",
    "ProcessTypes": [
        {
            "Name": "PROCNAME",
            "StepName": "STEPNAME",
            "PerPatlistPatternsToDisable": [
                {
                    "Patlist": "main1",
                    "Functionality": "FUNCT",
                    "PatternsToDisable": [
                        {
                            "Pattern": "r1"
                        },
                        {
                            "Pattern": "r2"
                        },
                        {
                            "Pattern": "ab"
                        }
                    ]
                }
            ]
        }
    ]
}
''')
        File('targ.plist').touch('''
Version 5.0;
GlobalPList main1
{
    GlobalPList main1a {
       Pat r1;
       Pat r2;  #KEEP#
       Pat ab;
    }
    # this tests empty
    GlobalPList main2a {
       Pat r1;
       PList xx;

       # some comment
    }
    GlobalPList main3a {
       Pat r2;
       PList xx;
       PList xy;
    }
}
''')

        mkdirs('outdir')
        spp = StaticPlistPup('PAS_PTD.json', 'POR_TP/TGLH81/EnvironmentFile.env', 'outdir')
        spp.read_ptdfile()
        spp.process_plist('targ.plist', 'IP_PCH')
        expect = '''
# Source: targ.plist

GlobalPList main1_FUNCT_STEPNAME_PROCNAME
{
 GlobalPList main1a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r2;    #KEEP#
 }
 # this tests empty
 GlobalPList main2a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r1;
  PList xx;

  # some comment
 }
 GlobalPList main3a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r2;
  PList xx;
  PList xy;
 }
}
'''
        self.assertTextEqual(''.join(spp.short['IP_PCH']).replace('\t', ' '), expect)

    @with_(TempDir, name=True, chdir=True, startcopy=f'{UT_DIR_REPO}/Simple4b_staticpup')
    def test_process_plist3_occur(self):
        # ====== unittest process_plist: Fixed PTD file and Fixed plist file
        # case8: all patterns disabled
        # case9: remove duplicate consecutive plist

        File('PAS_PTD.json').touch('''
{
    "Version": "1000",
    "ProcessTypes": [
        {
            "Name": "PROCNAME",
            "StepName": "STEPNAME",
            "PerPatlistPatternsToDisable": [
                {
                    "Patlist": "main1",
                    "Functionality": "FUNCT",
                    "PatternsToDisable": [
                        {
                            "Pattern": "r1"
                        },
                        {
                            "Pattern": "r2",
                            "Occurrence": "1-10"
                        },
                        {
                            "Pattern": "ab",
                            "Occurrence": "1-10"
                        }
                    ]
                }
            ]
        }
    ]
}
''')
        File('targ.plist').touch('''
Version 5.0;
GlobalPList main1
{
    GlobalPList main1a {
       Pat r1;
       Pat r2;  #KEEP#
       Pat ab;
    }
    # this tests empty
    GlobalPList main2a {
       Pat r1;
       PList xx;
       Pat r2;

       # some comment
       PList xx;
    }
    GlobalPList main3a {
       Pat r2;
       PList xx;
       Pat ab;
       PList xy;
    }
}
''')

        mkdirs('outdir')
        spp = StaticPlistPup('PAS_PTD.json', 'POR_TP/TGLH81/EnvironmentFile.env', 'outdir')
        spp.read_ptdfile()
        spp.process_plist('targ.plist', 'IP_PCH')
        expect = '''
# Source: targ.plist

GlobalPList main1_FUNCT_STEPNAME_PROCNAME
{
 GlobalPList main1a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r2;    #KEEP#
 }
 # this tests empty
 GlobalPList main2a_FUNCT_STEPNAME_PROCNAME
 {
  Pat r1;
  PList xx;

  # some comment
  PList xx;
 }
 GlobalPList main3a_FUNCT_STEPNAME_PROCNAME
 {
  PList xx;
  PList xy;
 }
}
'''
        self.assertTextEqual(''.join(spp.short['IP_PCH']).replace('\t', ' '), expect)

    def test_remove_empty(self):
        # case1 - basic, with comment and empty
        lines = '''
GlobalPList main1
{
 # comment

 GlobalPList main2
 {
 # empty
 }
 GlobalPList main3
 {
     PList abc;
 }
}
'''.split('\n')
        expect = '''
GlobalPList main1
{
 # comment

 GlobalPList main3
 {
     PList abc;
 }
}

        '''
        self.assertTextEqual('\n'.join(StaticPlistPup.remove_empty(lines)), expect)

        # case2 - simple
        lines = '''
GlobalPList main0
{
   Pat1;
}
GlobalPList main1
{
}
'''.split('\n')
        expect = '''
GlobalPList main0
{
   Pat1;
}
        '''
        self.assertTextEqual('\n'.join(StaticPlistPup.remove_empty(lines)), expect)

        # case3 - multi
        lines = '''
# hi
GlobalPList main0
{
 GlobalPList main1
 {
 # comment

  GlobalPList main2
  {
   # empty
  }
  GlobalPList main3
  {
  }
 }
} # end main0

GlobalPList main0a
{
 GlobalPList main1a
 {
 # comment

  GlobalPList main2a
  {
   # empty
  }
  GlobalPList main3a
  {
     Pat a;
  }
 }
} # end main0
'''.split('\n')
        expect = '''
# hi

GlobalPList main0a
{
 GlobalPList main1a
 {
 # comment

  GlobalPList main3a
  {
     Pat a;
  }
 }
} # end main0
        '''
        self.assertTextEqual('\n'.join(StaticPlistPup.remove_empty(lines)), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
