#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Unit test for indicators
"""
from setenv_unittest import UT_DIR_REPO, ROOT_ENV, EXIST_PDX_I_DRIVE    # must be first import for unittests
from gadget.ut import TestCase, unittest, Mock
from gadget.files import TempName, TempDir
from gadget.gizmo import MockVar
from mod.indicators import *
from main.nvl_buildtp import NVLBuildTP
from gadget.errors import ErrorUser
from pprint import pprint
from mod.test.test_cci_list import TestSharedCCI
import mod.indicators as indicators
import glob


class TestLit(TestCase):

    def onetime(self):
        # Execute this one time to generate all the data:
        # cd /nfs/site/home/jqdelosr/pytpd_rel/logs/checkers
        # test_indicataors.py -v TestLit.onetime

        for fname in glob.glob('2023*/buildtp*JF04*.log.gz'):    # 1684532815.log.gz'):
            try:
                logtext = File(fname).read()
            except ErrorUser:
                print(f"Error Reading: {fname}")
                continue

            # get prno
            res = re.findall(r"^number:\s(\d+)", logtext, re.MULTILINE)
            if not res:
                continue
            prno = res[0]

            # get date
            res = re.findall(r"EXECUTE INFO:.*(202\w.\d\d.\d\d)", logtext, re.MULTILINE)
            assert res
            date = res[0]

            # get robot
            res = re.findall(r"FULL CMD:.*\s(tprobo\w+)\s", logtext, re.MULTILINE)
            if not res:
                continue
            robot = res[0]

            # get code
            res = re.findall(r"buildtp.py complete.*exit (\S+)", logtext, re.MULTILINE)
            if not res:
                continue
            code = int(res[0])

            print(f'{fname}: PR={prno} D={date} R={robot}')
            with MockVar(indicators, 'curtime', Mock(return_value=date)):
                with TempDir(name=True) as tdir:
                    print("Is there a replace feature in NVL?")
                    # bt = Bot(TPBuild('P68_ARR', f'{tdir}/DEST'), robot=robot, batfile='', repljson='')
                    # bt.prno = prno
                    # bt.copy_logs(logtext, tdir, code)

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_basic(self):
        with TempDir(name=True, chdir=True) as tdir:
            f1 = File('ituff_TestUnitLog_2023-05-19-14.txt').touch('3_ttime_510.1\n')
            f2 = File('initLog_2023-05-19-14-55-36.txt').touch('[2023-May-19 15:19:04][Tos]Ini\n[2023-May-19 15:20:04][Tos]Ini\n')
            f3 = File('loadLog_2023-05-19-.txt').touch('[2023-May-19 15:19:04][Tos]Ini\n[2023-May-19 15:21:04][Tos]Ini\n')
            f4 = File('TestUnitLog_2023-05-19-14-55-36.txt').touch('[2023-May-19 15:19:04][Tos]Ini\n[2023-May-19 15:10:06][Tos]Ini\n')
            lit = Lit(tdir, 'tprobot_blah', '1')
            self.assertEqual(lit.write(0), 1)
            lit.one_log(f1.get_name())
            lit.one_log(f2.get_name())
            lit.one_log(f3.get_name())
            self.assertEqual(lit.one_log(f4.get_name()), 3)
            self.assertEqual(lit.one_log('CLASSCOLD_initLog_2023-06-09-13-20.txt'), 2)   # ignore
            self.assertEqual(lit.data, {'tt': 510.1,
                                        'ituffsize': 14,
                                        'init': 60.0,
                                        'load': 120.0})
            Lit.set_buildtime_end()
            with MockVar(indicators, 'curtime', Mock(return_value='2022-05-23')):
                lit.write(0)
                expect = '''{
   "ituffsize": 14,
   "tt": 510.1,
   "init": 60.0,
   "load": 120.0,
   "buildtime": 99
}'''
                result = File(f'{tdir}/tprobot_blah/2022-05-23/1.json').read()
                result = re.sub(r'buildtime": \d+', 'buildtime": 99', result)
                self.assertTextEqual(result, expect)

            # write again on a different day, it should delete
            with MockVar(indicators, 'curtime', Mock(return_value='2022-05-24')):
                self.assertTrue(exists(f'{tdir}/tprobot_blah/2022-05-23/1.json'))
                lit.write(0)
                self.assertFalse(exists(f'{tdir}/tprobot_blah/2022-05-23/1.json'))
                self.assertTrue(exists(f'{tdir}/tprobot_blah/2022-05-24/1.json'))

            # fail case code
            self.assertEqual(lit.write(1), 2)

            # no prno
            lit = Lit(tdir, 'tprobot_blah', None)
            lit.one_log(f1.get_name())
            self.assertEqual(lit.data, {})

            # invalid category
            lit = Lit(tdir, 'tprobot_blah', '1')
            with self.assertRaisesRegex(ErrorCockpit, 'File unknown_name is unknown category'):
                lit.one_log('unknown_name')

    def test_get_time_toslog(self):
        # test: age_tos_time() as well
        self.assertEqual(Lit.get_time_toslog(f'{UT_DIR_REPO}/misc_files/initLog1.txt'), 1906)
        self.assertEqual(Lit.get_time_toslog(f'{UT_DIR_REPO}/misc_files/empty_auto_aleph.env'), 0)

        self.assertEqual(Lit.age_tos_time('2024-11-14T16:01:29', '2024-11-14T16:02:29'), 60)

    def test_get_ttime_ituff(self):
        with TempName(name=True) as tname:
            File(tname).touch('''
2_tname_PCS_VMU_VB
2_mrslt_44702515200
2_lend
3_dvtsteddt_20230519155925
3_ttime_507.256
3_ttime_509.256
3_ttime_508.256
3_tpass_{99602453,99600250,99600253,99600304,99600304,99600543,99210273,99630279,99630293,99610171,99610341,99610343,15060001,15060001,15060001,15060002,15060002,15060002,15060002,15060002,15060002,1
3_tfail_{90760762,90191595,90190705,90190705,90190805,90314906,90314916,90315480,90610002,90610005,90610008,90191595,90760403,90160140,90165095,90165119,90515005,90515017,90760403,90471884,90760122,9
3_subflstpid_CLASSHOT
3_binn_10010000
3_curfbin_100
3_curibin_1
3_sscurfbin_U1_9069
3_sscurfbin_U1.U1_9069
3_sscurfbin_U1.U5_9069
''')
            self.assertEqual(Lit.get_ttime_ituff(tname), 509.256)
            self.assertEqual(Lit.get_ttime_ituff(f'{UT_DIR_REPO}/misc_files/initLog1.txt'), 0)


class TestBotFail(TestCase):

    def test_onelog(self):
        with TempDir(name=True) as tdir:
            tbf = TPBotFail()

            # root dir not found
            tbf.root = '/sure_not_found'
            self.assertEqual(tbf.one_log([], [], 1, 'bot1', '1'), 2)

            # passing case
            tbf.root = tdir
            self.assertEqual(tbf.one_log([], [], 0, 'bot1', '1'), 1)

            # no valid name found
            self.assertEqual(tbf.one_log([], [], 1, 'bot1', '1'), 3)

            # mrobot do not log
            self.assertEqual(tbf.one_log([], [], 1, 'mrobot_arl', '1'), 4)

            # draft
            with MockVar(GitHub, "get_pr_info", Mock(return_value='DRAFT')):
                self.assertEqual(tbf.one_log([], [], 1, 'bot1', '1'), 5)

            # one tpbot fail valid log
            all_type = [('Load log', '/path/path2/a_2.txt')]
            prio = ['INIT log', 'Load log']
            self.assertEqual(tbf.one_log(all_type, prio, 1, 'bot1', '1'), 4)
            self.assertEqual(os.listdir(f'{tdir}/bot1'), ['1_a_2.open.json'])

    def test_get_list(self):
        with TempDir(name=True) as tdir:
            # setup
            File(f'{tdir}/robot1/25_blah.open.json').touch('{"prno": 25, "logpath": "/blah", "time": 25000}', mkdir=True)
            File(f'{tdir}/robot1/24_blah.json').touch('{"prno": 24, "logpath": "/blah", "time": 25001}', mkdir=True)
            File(f'{tdir}/robot1/23_blah.json').touch('{}', mkdir=True)
            File(f'{tdir}/robot1/mtl.product').touch()
            File(f'{tdir}/robot2/23_blah.open.json').touch('{"prno": 23, "logpath": "/blah", "time": 25000}', mkdir=True)
            File(f'{tdir}/robot2/22_blah.json').touch('{"prno": 22, "logpath": "/blah", "time": 25000}', mkdir=True)
            File(f'{tdir}/robot3').touch()   # This is not a folder, so it should be ignored
            # note: robot2 does not have any .product, so it will match anything

            # testcase
            tbf = TPBotFail()
            tbf.root = tdir
            self.assertEqual(tbf.get_list('mtl'), [{'filename': 'robot1/25_blah.open.json',
                                                    'logpath': '/blah',
                                                    'prno': 25,
                                                    'time': 25000}])

            self.assertEqual(tbf.get_list('arl'), [])

            result = list(tbf.get_all_list(['robot1']))
            pprint(result)
            self.assertEqual(result, [{'robot': 'robot1', 'logpath': '/blah', 'prno': 24, 'time': 25001},
                                      {'robot': 'robot1', 'logpath': '/blah', 'prno': 25, 'time': 25000}])


GitHub.pr_view_output = 'No info'     # to make it fast

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
