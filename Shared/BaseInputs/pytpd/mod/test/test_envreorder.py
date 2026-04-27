#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for envreorder
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE, ROOT_ENV    # must be first import for unittests
from gadget.ut import TestCase, unittest, MockVar
from gadget.helperclass import CaptureStdoutLog
from gadget.gizmo import with_
from gadget.files import TempDir
from gadget.tputil import SDiff
from mod.envreorder import *
from pprint import pprint
from tp.testprogram import TestProgram
from os.path import join
from mod.setting import cfg


def remove_1274():
    """Hack win2unix dictionary to remove 1274 because of tgl disk removed and being restored"""
    return {k: v for k, v in cfg.win2unix.items() if '1274' not in k}


class TestIntegration(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @with_(MockVar, cfg, 'win2unix', remove_1274())
    def test_integration(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        result, winp, finaltext = er.main(disp=True)
        pprint(winp)

        # below for brute-force
        # expct = ['I:\\hdmxpats\\tgl\\MarrMbist\\RevTTR0.3\\p2\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MarrPbist\\RevTTR0.0\\p10\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\Mclk\\RevTTR0.1\\p2\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\Mdrv\\RevTTR0.0\\p6\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MfunIa\\RevTTR0.2\\p13\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MfunSa\\RevTTR1.0\\p1\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\Mfus\\RevTTR0.0\\p0\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MGarr\\RevTTR0.0\\p5\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MGfunDE\\RevTTR0.2\\p0\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MGfunGT\\RevTTR2.1\\p0\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MGscnDE\\RevTTR0.1\\p4\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MGscnGT\\RevTTR0.2\\p2\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MGscnIPU\\RevTTR0.0\\p2\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\Mmio\\RevTTR0.0\\p10\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MpthDTS\\RevTTR0.0\\p2\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MpthFIVR\\RevTTR0.0\\p9\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MpthPwr\\RevTTR0.0\\p6\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MscnCCF\\RevTTR0.5\\p3\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MscnCORE\\RevTTR0.1\\p2\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MscnSOC\\RevTTR0.1\\p21\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\Msio\\RevTTR0.0\\p0\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MsioPCIE\\RevTTR0.0\\p5\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\MsioTC\\RevTTR0.2\\p1\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\Mtpi\\RevTTR0.0\\p0\\pat\\common_files',
        #          'I:\\hdmxpats\\tgl\\Mwio\\RevTTR0.0\\p8\\pat\\common_files']

        expct = ['I:\\hdmxpats\\tgl\\MfunSa\\RevTTR1.0\\p1\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MfunIa\\RevTTR0.2\\p13\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\Mtpi\\RevTTR0.0\\p0\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MGscnGT\\RevTTR0.2\\p2\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MGfunGT\\RevTTR2.1\\p0\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MGscnIPU\\RevTTR0.0\\p2\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MGscnDE\\RevTTR0.1\\p4\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MGfunDE\\RevTTR0.2\\p0\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MGarr\\RevTTR0.0\\p5\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\Mwio\\RevTTR0.0\\p8\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MsioTC\\RevTTR0.2\\p1\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MsioPCIE\\RevTTR0.0\\p5\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\Msio\\RevTTR0.0\\p0\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MscnSOC\\RevTTR0.1\\p21\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MscnCORE\\RevTTR0.1\\p2\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MscnCCF\\RevTTR0.5\\p3\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\Mmio\\RevTTR0.0\\p10\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MpthPwr\\RevTTR0.0\\p6\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MpthFIVR\\RevTTR0.0\\p9\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MpthDTS\\RevTTR0.0\\p2\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\Mfus\\RevTTR0.0\\p0\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\Mclk\\RevTTR0.1\\p2\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\Mdrv\\RevTTR0.0\\p6\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MarrPbist\\RevTTR0.0\\p10\\pat\\common_files',
                 'I:\\hdmxpats\\tgl\\MarrMbist\\RevTTR0.3\\p2\\pat\\common_files']
        expct = [x.replace('I:', 'I:\\tpvalidation\\engtools\\tptools\\mtl\\unittests\\env_reorder') for x in expct]
        self.assertEqual(winp, expct)
        self.assertEqual(len(result), 25)
        self.assertEqual(len(finaltext.split('\n')), 541)

        # Update check - Make sure there are no other changes
        with TempDir(name=True, delete=True) as tdir:
            orig = tp.envfile
            tp.envfile = f'{tdir}/a.env'
            File(orig).copy(tp.envfile)
            er.main(update=True)

            print("Start=========================================================")
            arr_old = sorted(File(orig).chomp(strip=True))
            arr_new = sorted(list(File(tp.envfile).chomp(strip=True)) + [''])
            res = SDiff().simple([x.replace(' ', '') for x in arr_old],
                                 [x.replace(' ', '') for x in arr_new],
                                 disp=True)   # Set to True to debug
            counts = {x: res.count(x) for x in set(res) if x.strip()}
            self.assertEqual(counts, {'<': len(expct)})

    def test_enverrchk(self):
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        obj = EnvReorder(tp)
        with TempDir(name=True, chdir=True, delete=True) as tdir:
            envold = join(tdir, 'EnvironmentFile_CLASS_TGLU42.env.envreorder')
            File(envold).touch('', mkdir=True, newfile=True)
            envold = join(tdir, 'Reports/EnvironmentFile_CLASS_TGLU42.env.envreorder')
            File(envold).touch('', mkdir=True, newfile=True)
            env = join(tdir, 'EnvironmentFile_CLASS_TGLU42.env')
            File(env).touch('', mkdir=True, newfile=True)

            tp.envfile = 'EnvironmentFile_CLASS_TGLU42.env'
            tp.tpldir = tdir
            obj.enverrchk()  # basic pass

        with TempDir(name=True, chdir=True, delete=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_TGLU42.env')
            File(env).touch('', mkdir=True, newfile=True)

            tp.envfile = 'EnvironmentFile_CLASS_TGLU42.env'
            tp.tpldir = tdir
            with self.assertRaisesRegex(ErrorCheck, 'env.envreorder backup file is missing'):
                obj.enverrchk()  # env.envreorder is missing

        with TempDir(name=True, chdir=True, delete=True) as tdir:
            env = join(tdir, 'EnvironmentFile_CLASS_TGLU42.env.envreorder')
            File(env).touch('', mkdir=True, newfile=True)

            tp.envfile = 'EnvironmentFile_CLASS_TGLU42.env'
            tp.tpldir = tdir
            with self.assertRaisesRegex(ErrorCheck, '.env updated file is missing'):
                obj.enverrchk()  # env is missing


class TestReorder(TestCase):

    def short(self, lst):
        """Returns short string based on input lst"""
        return ''.join([x[9] for x in lst])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_combination(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {'/path/RevCCC/common_files/AA.pinObj': 15,    # latest
                  '/path/RevCCC/common_files/BB.pinObj': 16,    # latest
                  '/path/RevBBB/common_files/AA.pinObj': 14,
                  '/path/RevBBB/common_files/CC.pinObj': 17,    # latest
                  '/path/RevAAA/common_files/CC.pinObj': 12,
                  '/path/RevAAA/common_files/AA.pinObj': 11,
                  '/path/RevAAA/common_files/DD.pinObj': 11,    # latest
                  '/path/RevDDD/common_files/DD.pinObj': 10,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'CBAD')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'CBAD')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_one(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {'/path/RevCCC/common_files/CC.pinObj': 15,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'C')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'C')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_jan6(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {"/path/RevAAA/common_files/AA.pinObj": 25,   # latest
                  "/path/RevAAA/common_files/CC.pinObj": 12,   # latest
                  "/path/RevAAA/common_files/DD.pinObj": 9,    # latest

                  "/path/RevBBB/common_files/BB.pinObj": 29,   # latest
                  "/path/RevBBB/common_files/DD.pinObj": 4,
                  "/path/RevBBB/common_files/CC.pinObj": 12,   # latest

                  "/path/RevCCC/common_files/CC.pinObj": 11,
                  "/path/RevCCC/common_files/DD.pinObj": 2}
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'ABC')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))  # still good
        self.assertEqual(self.short(result), 'ABC')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_may2(self):
        # MTL specific case where it older unused rev is inserted on top causing issue later
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {"/path/RevCCC/common_files/oh.pinObj": 46142,
                  "/path/RevCCC/common_files/oy.pinObj": 46120,

                  "/path/RevBBB/common_files/oi.pinObj": 69651,   # latest
                  "/path/RevBBB/common_files/oz.pinObj": 58447,

                  "/path/RevAAA/common_files/oi.pinObj": 63808,
                  "/path/RevAAA/common_files/oz.pinObj": 58447,

                  "/path/RevDDD/common_files/oh.pinObj": 58665,   # latest
                  "/path/RevDDD/common_files/oi.pinObj": 63808,
                  "/path/RevDDD/common_files/oy.pinObj": 58317}   # latest
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BADC')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BADC')

        pinobj = {"/path/RevCCC/common_files/oh.pinObj": 46142,
                  "/path/RevCCC/common_files/oy.pinObj": 58317,   # latest

                  "/path/RevBBB/common_files/oi.pinObj": 69651,   # latest
                  "/path/RevBBB/common_files/oz.pinObj": 58447,

                  "/path/RevAAA/common_files/oi.pinObj": 63808,
                  "/path/RevAAA/common_files/oz.pinObj": 58447,

                  "/path/RevDDD/common_files/oh.pinObj": 58665,   # latest
                  "/path/RevDDD/common_files/oi.pinObj": 63808}
        with self.assertRaisesRegex(ErrorInput, 'oi.pinObj will load incorrectly'):
            result = er.reorder(pinobj, er.get_subr_2nn(pinobj))   # can't process
            # self.assertEqual(self.short(result), 'BADC')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BADC')
        result = er.reorder_main(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BADC')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_sorted(self):
        # case-insensitive sorting
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {"/path/RevSSS/common_files/0l3.pinObj": 79029,  # latest
                  "/path/RevPPP/common_files/0oz.pinObj": 49636,

                  "/path/RevBBB/common_files/aaa.pinObj": 77800,
                  "/path/Revaaa/common_files/0k0.pinObj": 77807,
                  "/path/Revaaa/common_files/0l3.pinObj": 77910,
                  "/path/Revaaa/common_files/0oz.pinObj": 58447,  # latest
                  }

        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'SBaP')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'SaBP')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_two(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {'/path/RevAAA/common_files/AA.pinObj': 12,
                  '/path/RevBBB/common_files/AA.pinObj': 15,
                  '/path/RevBBB/common_files/BB.pinObj': 15,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BA')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BA')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_bbb_is_old(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {'/path/RevCCC/common_files/CC.pinObj': 15,    # latest
                  '/path/RevBBB/common_files/AA.pinObj': 12,
                  '/path/RevBBB/common_files/CC.pinObj': 11,
                  '/path/RevAAA/common_files/AA.pinObj': 14,    # latest
                  '/path/RevDDD/common_files/CC.pinObj': 14,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'CDAB')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'ACBD')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_simple(self):
        # everything is unique
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {'/path/RevCCC/common_files/XX.pinObj': 15,
                  '/path/RevBBB/common_files/YY.pinObj': 12,
                  '/path/RevAAA/common_files/ZZ.pinObj': 14,
                  '/path/RevDDD/common_files/WW.pinObj': 17,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'DCAB')    # order does not matter
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'ABCD')    # order does not matter

        # everything is the same
        pinobj = {'/path/RevCCC/common_files/AA.pinObj': 15,
                  '/path/RevBBB/common_files/AA.pinObj': 15,
                  '/path/RevAAA/common_files/AA.pinObj': 15,
                  '/path/RevDDD/common_files/AA.pinObj': 15,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'DCBA')    # order does not matter
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'ABCD')    # order does not matter

        # One is newer
        pinobj = {'/path/RevCCC/common_files/AA.pinObj': 15,
                  '/path/RevBBB/common_files/AA.pinObj': 15,
                  '/path/RevAAA/common_files/AA.pinObj': 15,
                  '/path/RevDDD/common_files/AA.pinObj': 16,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'DCBA')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'DABC')

        # One is older
        pinobj = {'/path/RevCCC/common_files/AA.pinObj': 15,
                  '/path/RevBBB/common_files/AA.pinObj': 15,
                  '/path/RevAAA/common_files/AA.pinObj': 14,
                  '/path/RevDDD/common_files/AA.pinObj': 15,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'DCBA')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BACD')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_corner(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {'/path/RevAAA/common_files/AA.pinObj': 3,
                  '/path/RevBBB/common_files/AA.pinObj': 4,
                  '/path/RevCCC/common_files/AA.pinObj': 2,
                  '/path/RevCCC/common_files/BB.pinObj': 1,
                  '/path/RevDDD/common_files/BB.pinObj': 2,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BADC')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BADC')

        # swap the rev
        pinobj = {'/path/RevAAA/common_files/AA.pinObj': 3,
                  '/path/RevBBB/common_files/AA.pinObj': 4,
                  '/path/RevDDD/common_files/AA.pinObj': 2,
                  '/path/RevDDD/common_files/BB.pinObj': 1,
                  '/path/RevCCC/common_files/BB.pinObj': 2,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BACD')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'BACD')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_from_ryan(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)

        # case1
        pinobj = {'/path/RevAAA/common_files/AA.pinObj': 20483,
                  '/path/RevBBB/common_files/AA.pinObj': 20483,
                  '/path/RevCCC/common_files/AA.pinObj': 20483,
                  '/path/RevDDD/common_files/AA.pinObj': 14967
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'CBAD')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'ABCD')

        # case2
        pinobj = {'/path/RevAAA/common_files/AA.pinObj': 20,
                  '/path/RevAAA/common_files/BB.pinObj': 19,
                  '/path/RevAAA/common_files/CC.pinObj': 15,
                  '/path/RevBBB/common_files/AA.pinObj': 17,
                  '/path/RevBBB/common_files/BB.pinObj': 12,
                  '/path/RevBBB/common_files/CC.pinObj': 11,
                  '/path/RevBBB/common_files/DD.pinObj': 11,
                  '/path/RevBBB/common_files/EE.pinObj': 10,
                  }
        result = er.reorder(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'AB')
        result = er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'AB')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_failure(self):
        # one subroutine is latest in Rev1 and another subroutine is latest in rev2
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {'/path/Rev1/common_files/AA.pinObj': 15,   # newer
                  '/path/Rev1/common_files/BB.pinObj': 16,
                  '/path/Rev2/common_files/AA.pinObj': 14,
                  '/path/Rev2/common_files/BB.pinObj': 17,   # newer
                  }
        with self.assertRaisesRegex(ErrorInput, 'BB.pinObj will load incorrectly from /path/Rev1/common_files'):
            er.reorder(pinobj, er.get_subr_2nn(pinobj))
        with self.assertRaisesRegex(ErrorInput, 'Cannot insert /path/Rev2/common_files because it has new and old subroutine'):
            er.reorder2(pinobj, er.get_subr_2nn(pinobj))
        with self.assertRaisesRegex(ErrorInput, 'Cannot insert /path/Rev2/common_files because it has new and old subroutine'):
            er.reorder_main(pinobj, er.get_subr_2nn(pinobj))

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_new_jun7(self):
        # USE MAIN
        # brute force algo does not work but sorting works.
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {"/path/RevSSS/common_files/0l3.pinObj": 79029,  # latest
                  "/path/RevPPP/common_files/0oz.pinObj": 49636,

                  "/path/RevAAA/common_files/aaa.pinObj": 77800,
                  "/path/RevZZZ/common_files/0k0.pinObj": 77807,
                  "/path/RevZZZ/common_files/0l3.pinObj": 77910,
                  "/path/RevZZZ/common_files/0oz.pinObj": 58447,  # latest
                  }

        result = er.reorder_main(pinobj, er.get_subr_2nn(pinobj))
        self.assertEqual(self.short(result), 'SAZP')


class TestHelpers(TestCase):

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, 'JF only test due to time zone dependence')
    def test_get_nn_timestamp(self):

        # ls -ltr /p/pde/tvpv/mtl/hdmt2/central/cfx/2bb/mtl_comK_cf2bb_sub11_J_0_200731.pinObj
        # -rwxr-x--- 1 p6vector gdlusers 25793 Jul 13 14:44 /p/pde/tvpv/mtl/hdmt2/central/cfx/2bb/mtl_comK_cf2bb_sub11_J_0_200731.pinObj
        #                                      ^^^^^^^^^^^^
        f1 = f'{UT_DIR_REPO}/misc_files/mtl_comK_cf2bb_sub11_J_0_200731.pinObj'
        secs = EnvReorder.get_nn_timestamp(f1)
        self.assertEqual(datetime.fromtimestamp(secs).strftime("%Y-%m-%d %H:%M:%S"), '2023-07-13 14:44:16')

        # ls -ltr /p/pde/tvpv/mtl/hdmt2/central/cfx/2bb/mtl_comK_cf2bb_sub11_J_0_183882.pinObj
        # -rwxr-x--- 1 p6vector gdlusers 20865 May 19 16:05 /p/pde/tvpv/mtl/hdmt2/central/cfx/2bb/mtl_comK_cf2bb_sub11_J_0_183882.pinObj
        #                                      ^^^^^^^^^^^^
        f1 = f'{UT_DIR_REPO}/misc_files/mtl_comK_cf2bb_sub11_J_0_183882.pinObj'
        secs = EnvReorder.get_nn_timestamp(f1)
        self.assertEqual(datetime.fromtimestamp(secs).strftime("%Y-%m-%d %H:%M:%S"), '2023-05-19 16:05:54')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_success(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {'/path/RevAAA/common_files/LL.pinObj': 1,
                  '/path/RevAAA/common_files/MM.pinObj': 2,
                  '/path/RevBBB/common_files/MM.pinObj': 3,
                  '/path/RevBBB/common_files/NN.pinObj': 4,
                  '/path/RevCCC/common_files/NN.pinObj': 5,
                  '/path/RevCCC/common_files/OO.pinObj': 6,
                  '/path/RevDDD/common_files/OO.pinObj': 7,
                  '/path/RevDDD/common_files/LL.pinObj': 8,
                  }
        s2n = er.get_subr_2nn(pinobj)

        def create(seq):
            return [f'/path/Rev{x}{x}{x}/common_files' for x in seq]

        self.assertEqual(er.success(pinobj, s2n, create('A')), True)
        self.assertEqual(er.success(pinobj, s2n, create('B')), True)
        self.assertEqual(er.success(pinobj, s2n, create('C')), True)
        self.assertEqual(er.success(pinobj, s2n, create('D')), True)
        self.assertEqual(er.success(pinobj, s2n, create('E')), True)    # path not found

        self.assertEqual(er.success(pinobj, s2n, create('BA')), True)
        self.assertEqual(er.success(pinobj, s2n, create('AB')), False)
        self.assertEqual(er.success(pinobj, s2n, create('CB')), True)
        self.assertEqual(er.success(pinobj, s2n, create('BC')), False)
        self.assertEqual(er.success(pinobj, s2n, create('DC')), True)
        self.assertEqual(er.success(pinobj, s2n, create('CD')), False)
        self.assertEqual(er.success(pinobj, s2n, create('DB')), True)
        self.assertEqual(er.success(pinobj, s2n, create('BD')), True)
        self.assertEqual(er.success(pinobj, s2n, create('DA')), True)
        self.assertEqual(er.success(pinobj, s2n, create('AD')), False)
        self.assertEqual(er.success(pinobj, s2n, create('CA')), True)
        self.assertEqual(er.success(pinobj, s2n, create('AC')), True)

        self.assertEqual(er.success(pinobj, s2n, create('CBA')), True)
        self.assertEqual(er.success(pinobj, s2n, create('CAB')), False)
        self.assertEqual(er.success(pinobj, s2n, create('BCA')), False)
        self.assertEqual(er.success(pinobj, s2n, create('BAC')), False)
        self.assertEqual(er.success(pinobj, s2n, create('ACB')), False)
        self.assertEqual(er.success(pinobj, s2n, create('ABC')), False)

        self.assertEqual(er.success(pinobj, s2n, create('DCAB')), False)
        self.assertEqual(er.success(pinobj, s2n, create('DBCA')), False)
        self.assertEqual(er.success(pinobj, s2n, create('DBAC')), False)
        self.assertEqual(er.success(pinobj, s2n, create('DACB')), False)
        self.assertEqual(er.success(pinobj, s2n, create('DABC')), False)
        self.assertEqual(er.success(pinobj, s2n, create('DCBA')), True)

        self.assertEqual(er.success(pinobj, s2n, create('CDBA')), False)
        self.assertEqual(er.success(pinobj, s2n, create('CDAB')), False)
        self.assertEqual(er.success(pinobj, s2n, create('CBDA')), False)
        self.assertEqual(er.success(pinobj, s2n, create('CBAD')), False)
        self.assertEqual(er.success(pinobj, s2n, create('CADB')), False)
        self.assertEqual(er.success(pinobj, s2n, create('CABD')), False)

        self.assertEqual(er.success(pinobj, s2n, create('BDCA')), False)
        self.assertEqual(er.success(pinobj, s2n, create('BDAC')), False)
        self.assertEqual(er.success(pinobj, s2n, create('BCDA')), False)
        self.assertEqual(er.success(pinobj, s2n, create('BCAD')), False)
        self.assertEqual(er.success(pinobj, s2n, create('BADC')), False)
        self.assertEqual(er.success(pinobj, s2n, create('BACD')), False)

        self.assertEqual(er.success(pinobj, s2n, create('ADCB')), False)
        self.assertEqual(er.success(pinobj, s2n, create('ADBC')), False)
        self.assertEqual(er.success(pinobj, s2n, create('ACDB')), False)
        self.assertEqual(er.success(pinobj, s2n, create('ACBD')), False)
        self.assertEqual(er.success(pinobj, s2n, create('ABDC')), False)
        self.assertEqual(er.success(pinobj, s2n, create('ABCD')), False)

        self.assertEqual(create('ABDC'), ['/path/RevAAA/common_files',
                                          '/path/RevBBB/common_files',
                                          '/path/RevDDD/common_files',
                                          '/path/RevCCC/common_files'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_build_final_list(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)

        # POR case
        main = 'D:/a L:/b ~HDMT_supercede I:/a I:/b'.split()
        com = 'com1 com2'.split()
        self.assertEqual(er.build_final_list(main, com),
                         ['D:/a', 'L:/b', '~HDMT_supercede',
                          'com1', 'com2',
                          'I:/a', 'I:/b'])

        # single case
        main = '~HDMT_supercede I:/a I:/b'.split()
        com = 'com1 com2'.split()
        self.assertEqual(er.build_final_list(main, com),
                         ['~HDMT_supercede',
                          'com1', 'com2',
                          'I:/a', 'I:/b'])

        # no supercede case
        main = 'I:/a I:/b'.split()
        com = 'com1 com2'.split()
        self.assertEqual(er.build_final_list(main, com),
                         ['com1', 'com2',
                          'I:/a', 'I:/b'])

        # no I:\ drive case (not realistic - but a good test anyway)
        main = '~HDMT_supercede J:/a J:/b'.split()
        com = 'com1 com2'.split()
        self.assertEqual(er.build_final_list(main, com),
                         ['com1', 'com2',
                          '~HDMT_supercede', 'J:/a', 'J:/b'])

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_unreachable_code(self):
        # caught with windows test case
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {'/path/RevAAA/common_files//LL.pinObj': 8}
        s2n = er.get_subr_2nn(pinobj)
        with self.assertRaisesRegex(ErrorCockpit, 'Unreachable code'):
            er.success(pinobj, s2n, ['/path/RevAAA/common_files'])

    def test_readlink_subr(self):
        # simple case - middle
        with TempDir(name=True) as tdir:
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0.pinObj').touch('abc')
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0_019986.pinObj').touch('abc1')
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0_019987.pinObj').touch('abc')
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0_019988.pinObj').touch('abc2')
            arr = []
            result = EnvReorder.readlink_subr(f'{tdir}/mtl_comA_cf077_sub11_J_0.pinObj', arr)
            self.assertEqual(result, 'mtl_comA_cf077_sub11_J_0_019987.pinObj')
            self.assertEqual(len(arr), 2)

        # simple case - top
        with TempDir(name=True) as tdir:
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0.pinObj').touch('abc')
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0_019986.pinObj').touch('abc1')
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0_019987.pinObj').touch('abc2')
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0_019988.pinObj').touch('abc')
            arr = []
            result = EnvReorder.readlink_subr(f'{tdir}/mtl_comA_cf077_sub11_J_0.pinObj', arr)
            self.assertEqual(result, 'mtl_comA_cf077_sub11_J_0_019988.pinObj')
            self.assertEqual(len(arr), 1)

        # not found
        with TempDir(name=True) as tdir:
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0.pinObj').touch('abc')
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0_019986.pinObj').touch('abc1')
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0_019987.pinObj').touch('abc2')
            File(f'{tdir}/mtl_comA_cf077_sub11_J_0_019988.pinObj').touch('abc3')
            arr = []

            # with self.assertRaisesRegex(ErrorInput, 'Cannot find subroutine softlink equivalent'):
            #     EnvReorder.readlink_subr(f'{tdir}/mtl_comA_cf077_sub11_J_0.pinObj', arr)

            result = EnvReorder.readlink_subr(f'{tdir}/mtl_comA_cf077_sub11_J_0.pinObj', arr)
            self.assertEqual(result, 'mtl_comA_cf077_sub11_J_0.pinObj')
            self.assertEqual(len(arr), 3)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_info(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env')
        er = EnvReorder(tp)
        pinobj = {'/path/Rev1/common_files/AA.pinObj': 15,
                  '/path/Rev1/common_files/BB.pinObj': 16,
                  '/path/Rev2/common_files/AA.pinObj': 14,
                  '/path/Rev2/common_files/BB.pinObj': 17,
                  '/path/Rev3/common_files/CC.pinObj': 18,
                  }
        subr_2nn = er.get_subr_2nn(pinobj)
        result = ['/path/Rev1/common_files',
                  '/path/Rev2/common_files',
                  '/path/Rev3/common_files']
        with CaptureStdoutLog() as p:
            er.info(pinobj, subr_2nn, result)
        expect = """/path/Rev1/common_files:
   AA.pinObj: 15
   BB.pinObj: 16 << NOT LATEST (vs 17)
/path/Rev2/common_files:
   AA.pinObj: 14 << NOT LATEST (vs 15)
   BB.pinObj: 17
/path/Rev3/common_files:
   CC.pinObj: 18
"""
        self.assertTextEqual(p.getvalue(), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
