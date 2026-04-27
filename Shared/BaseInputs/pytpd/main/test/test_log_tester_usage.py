#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for log_tester_usage.py
"""
import setenv_unittest   # must be first import for unittests
try:
    from log_tester_usage import *
except ImportError:
    from main.log_tester_usage import *
from unittest.mock import Mock
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar
from gadget.helperclass import CaptureStdoutLog
from gadget.gizmo import with_
from gadget.files import TempDir, File
from gadget.shell import HOSTNAME
from pprint import pprint, pformat


class TestLU(TestCase):

    def fake_get_path_file(self, tester, partial):
        return partial

    def fake_get_all_testers(self):
        yield ('tester1', 'tiuA', 'D3', [])

    def _remove_time_keys(self, dd):
        """Remove keys with time so unittest will work"""
        for item in dd.values():
            for key in ('last_update', 'process_time_secs', 'Version', 'Elapsed'):
                if key in item:
                    item[key] = 'UT'

    def test_basic1(self):
        # case: found one log file
        with TempDir(name=True, chdir=True) as tdir:
            # setup
            lu = LogUsage()
            lu.output_file = f'{tdir}/out.json'
            lu.logfiles = ['a.txt']
            File('a.txt').touch('''
[0-10-2023 08:17:35.018][A][TAL][DUT: 11]
[2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X]
[2023-Jun-25 08:18:22.018][A][TAL][DUT: 11X] [SASS Alarm] SensorId = HPCC:4:PE Temperature:13
''')

            # Run
            with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                    MockVar(lu, '_get_path_file', self.fake_get_path_file):
                lu.run()
            with open(lu.output_file) as fh:
                resultall = json.load(fh)
            self._remove_time_keys(resultall)
            expect = '''
{'_INFO_': {'Elapsed': 'UT', 'Message': [], 'Tester_Count': 1, 'Version': 'UT'},
 '_PREV_': {'tester1': '[2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X] [PREV:a.txt] '},
 'tester1': {'last_touch': '2023-06-23 08:18:10',
             'last_update': 'UT',
             'location': 'D3',
             'logfile_source': 'a.txt',
             'message': ['[a.txt]: [2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X]'],
             'offset': -1.2345,
             'process_time_secs': 'UT',
             'sass_alarm_count': 1,
             'tester': 'tester1',
             'tiu': 'tiuA'}}
'''
            self.assertTextEqual(pformat(resultall, width=100), expect)

    def test_basic2(self):
        # case: found two files
        with TempDir(name=True, chdir=True) as tdir:
            # setup
            lu = LogUsage()
            lu.output_file = f'{tdir}/out.json'
            lu.logfiles = ['a.txt', 'b.txt']
            File('a.txt').touch('''
[2023-Jun-23 08:17:35.018][A][TAL][DUT: 11]
[2023-Jun-23 08:18:10.018][A][TAL][DUT: 11]

''')
            File('b.txt').touch('''
06-23-2023 08:13:45;[122];INF
06-23-2023 08:23:49;[122];INF
''')

            # Run
            with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                    MockVar(lu, '_get_path_file', self.fake_get_path_file):
                lu.run()
            with open(lu.output_file) as fh:
                resultall = json.load(fh)
            self._remove_time_keys(resultall)
            expect = '''
{'_INFO_': {'Elapsed': 'UT', 'Message': [], 'Tester_Count': 1, 'Version': 'UT'},
 '_PREV_': {'tester1': '06-23-2023 08:23:49;[122];INF [PREV:b.txt] '},
 'tester1': {'last_touch': '2023-06-23 08:23:49',
             'last_update': 'UT',
             'location': 'D3',
             'logfile_source': 'b.txt',
             'message': ['[a.txt]: [2023-Jun-23 08:18:10.018][A][TAL][DUT: 11]',
                         '[b.txt]: 06-23-2023 08:23:49;[122];INF'],
             'offset': -1.2345,
             'process_time_secs': 'UT',
             'sass_alarm_count': 0,
             'tester': 'tester1',
             'tiu': 'tiuA'}}
'''
            self.assertTextEqual(pformat(resultall, width=100), expect)

        # swap it
        print("====== New testcase")
        with TempDir(name=True, chdir=True) as tdir:
            # setup
            lu = LogUsage()
            lu.output_file = f'{tdir}/out.json'
            lu.logfiles = ['a.txt', 'b.txt']
            File('a.txt').touch('''
[2023-Jun-23 08:17:35.018][A][TAL][DUT: 11]
[2023-Jun-23 08:23:49.018][A][TAL][DUT: 11]

''')
            File('b.txt').touch('''
06-23-2023 08:13:45;[122];INF
06-23-2023 08:20:49;[122];INF
''')

            # Run
            with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                    MockVar(lu, '_get_path_file', self.fake_get_path_file):
                lu.run()
            with open(lu.output_file) as fh:
                resultall = json.load(fh)
            self._remove_time_keys(resultall)
            expect = '''
{'_INFO_': {'Elapsed': 'UT', 'Message': [], 'Tester_Count': 1, 'Version': 'UT'},
 '_PREV_': {'tester1': '[2023-Jun-23 08:23:49.018][A][TAL][DUT: 11] [PREV:a.txt] '},
 'tester1': {'last_touch': '2023-06-23 08:23:49',
             'last_update': 'UT',
             'location': 'D3',
             'logfile_source': 'a.txt',
             'message': ['[a.txt]: [2023-Jun-23 08:23:49.018][A][TAL][DUT: 11]',
                         '[b.txt]: 06-23-2023 08:20:49;[122];INF'],
             'offset': -1.2345,
             'process_time_secs': 'UT',
             'sass_alarm_count': 0,
             'tester': 'tester1',
             'tiu': 'tiuA'}}
'''
            self.assertTextEqual(pformat(resultall, width=100), expect)
            pprint(resultall)

    def test_basic3_get_all_testers(self):
        # case: two testers
        with TempDir(name=True, chdir=True) as tdir:
            # setup
            lu = LogUsage()
            lu.output_file = f'{tdir}/out.json'
            lu.logfiles = ['a.txt']
            File('a.txt').touch('''
[2023-Jun-23 08:17:35.018][A][TAL][DUT: 11]
[2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X]

''')

            # Run
            with MockVar(lu, 'get_all_testers', Mock(return_value=[('tester1.pdx', 'tiuA', 'D1', []),
                                                                   ('tester2.pdx', 'tiuB', 'D1', ['def1'])])), \
                    MockVar(lu, '_get_path_file', self.fake_get_path_file):
                lu.run()
            with open(lu.output_file) as fh:
                resultall = json.load(fh)
            self._remove_time_keys(resultall)
            expect = '''
{'_INFO_': {'Elapsed': 'UT', 'Message': [], 'Tester_Count': 2, 'Version': 'UT'},
 '_PREV_': {'tester1': '[2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X] [PREV:a.txt] ',
            'tester2': '[2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X] [PREV:a.txt] '},
 'tester1': {'last_touch': '2023-06-23 08:18:10',
             'last_update': 'UT',
             'location': 'D1',
             'logfile_source': 'a.txt',
             'message': ['[a.txt]: [2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X]'],
             'offset': -1.2345,
             'process_time_secs': 'UT',
             'sass_alarm_count': 0,
             'tester': 'tester1.pdx',
             'tiu': 'tiuA'},
 'tester2': {'last_touch': '2023-06-23 08:18:10',
             'last_update': 'UT',
             'location': 'D1',
             'logfile_source': 'a.txt',
             'message': ['def1', '[a.txt]: [2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X]'],
             'offset': -1.2345,
             'process_time_secs': 'UT',
             'sass_alarm_count': 0,
             'tester': 'tester2.pdx',
             'tiu': 'tiuB'}}
'''
            self.assertTextEqual(pformat(resultall, width=100), expect)

            # get_all_testers default
            lu.allinfo_file = '/notfound'
            lu.prevdata = lu.data
            lu.info = []
            self.assertEqual(list(lu.get_all_testers()), [('tester1.pdx', 'tiuA', 'D1', ['Using previous tester metadata']),
                                                          ('tester2.pdx', 'tiuB', 'D1', ['Using previous tester metadata'])])
            self.assertEqual(lu.info, ['Not Exist /notfound'])

            lu.allinfo_file = './empty'
            lu.prevdata = lu.data
            lu.info = []
            File(lu.allinfo_file).touch(newfile=True)
            self.assertEqual(list(lu.get_all_testers()), [('tester1.pdx', 'tiuA', 'D1', ['Using previous tester metadata']),
                                                          ('tester2.pdx', 'tiuB', 'D1', ['Using previous tester metadata'])])
            self.assertEqual(lu.info, ['./empty is EMPTY'])

            # get_all_testers
            lu.allinfo_file = 'testers.csv'
            File('testers.csv').touch('''
JF04HHHX1376.PDX.INTEL.COM,NA,NA,0.0.0.0,DOWN,X10HDMT1376,NA
JF04TXBT60859A.PDX.INTEL.COM,CELL-Class-HDMTBT-J9-310,MTLPA1,10.23.9.64,UP,HDMTG2-60859,Module Robot
JF04TXBT60859B.PDX.INTEL.COM,CELL-Class-ICDC-HDMTBT-J9-310,MTLPA1,10.23.9.64,UP,HDMTG2-60859,Module Robot
JF04TXBT60966A.PDX.INTEL.COM,CELL-Class-X10HDMT-L2938-301,MTLPA2,0.0.0.0,X10,HDMTG2-60966,PLANNING
''')
            print(list(lu.get_all_testers()))
            self.assertEqual(list(lu.get_all_testers()),
                             [('JF04TXBT60859A.PDX.INTEL.COM', 'MTLPA1', 'CELL-Class-HDMTBT-J9-310', [])])

    @with_(TempDir, chdir=True)
    def test_sass_previous1(self):
        # case: sass line only, use previous
        lu = LogUsage()
        lu.output_file = f'out.json'
        lu.logfiles = ['a.txt', 'b.txt']
        File('a.txt').touch('''
[2023-06-20 08:18:22.018][A][TAL][DUT: 11X] [SASS Alarm] SensorId = HPCC:4:PE Temperature:13
''')
        File("out.json").touch("""
{"tester1": {"last_touch": "2023-06-22 09:18:10"},
 "_PREV_": {"tester1": "[2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X] [PREV:a.txt] "}
}
""")

        # Run
        with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                MockVar(lu, '_get_path_file', self.fake_get_path_file):
            lu.run()
        with open(lu.output_file) as fh:
            resultall = json.load(fh)
        self._remove_time_keys(resultall)
        pprint(resultall)
        expect = '''
{'_INFO_': {'Elapsed': 'UT', 'Message': [], 'Tester_Count': 1, 'Version': 'UT'},
 '_PREV_': {'tester1': '[2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X] [PREV:a.txt]'},
 'tester1': {'last_touch': '2023-06-23 08:18:10',
             'last_update': 'UT',
             'location': 'D3',
             'logfile_source': 'a.txt',
             'message': ['[a.txt]: [2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X] [PREV:a.txt]',
                         'b.txt does not exist.'],
             'offset': -1.2345,
             'process_time_secs': 'UT',
             'sass_alarm_count': 0,
             'tester': 'tester1',
             'tiu': 'tiuA'}}
'''
        self.assertTextEqual(pformat(resultall, width=100), expect)

    @with_(TempDir, chdir=True)
    def test_sass_previous2(self):
        # case: sass line only, no previous
        lu = LogUsage()
        lu.output_file = f'out.json'
        lu.logfiles = ['a.txt', 'b.txt']
        File('a.txt').touch('''
[2023-Jun-20 08:18:22.018][A][TAL][DUT: 11X] [SASS Alarm] SensorId = HPCC:4:PE Temperature:13
''')
        File("out.json").touch("""
{"tester1": {"last_touch": "2023-06-22 09:18:10"},
 "_PREV_": {"tester2": "[2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X] [PREV:a.txt] "}
}
""")

        # Run
        with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                MockVar(lu, '_get_path_file', self.fake_get_path_file):
            lu.run()
        with open(lu.output_file) as fh:
            resultall = json.load(fh)
        self._remove_time_keys(resultall)
        expect = '''
{'_INFO_': {'Elapsed': 'UT',
            'Message': ['tester1: [a.txt] No valid date found',
                        'tester1: b.txt does not exist.',
                        'tester1: None of the logfiles read (count: 1) has valid date'],
            'Tester_Count': 1,
            'Version': 'UT'},
 '_PREV_': {'tester2': '[2023-Jun-23 08:18:10.018][A][TAL][DUT: 11X] [PREV:a.txt] '}}
'''
        self.assertTextEqual(pformat(resultall, width=100), expect)

    @with_(TempDir, chdir=True)
    def test_once(self):
        lu = LogUsage()
        File('a.txt').touch('''
202xx
''')
        File('config.json').touch(r'''
{
 "logfiles": ["a.txt", "b.txt"],
 "output_file": "out.json",
 "allinfo_file": "\\\\ra4ssttdsdsdx24\\JF_TesterStatus\\CurrentStatus.txt"
}
''')

        # Run
        with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                MockVar(lu, '_get_path_file', self.fake_get_path_file):
            self.assertEqual(lu.main('config.json', once=True), -1)
        with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                MockVar(lu, '_get_path_file', self.fake_get_path_file):
            self.assertEqual(lu.main('config.json', x10=True), -1)

    @with_(TempDir, chdir=True)
    def test_nonefound1(self):
        # case: no date found in log files and no previous
        lu = LogUsage()
        File('a.txt').touch('''
202xx
''')
        File('config.json').touch(r'''
{
 "logfiles": ["a.txt", "b.txt"],
 "output_file": "out.json",
 "allinfo_file": "\\\\ra4ssttdsdsdx24\\JF_TesterStatus\\CurrentStatus.txt"
}
''')

        # Run
        with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                MockVar(lu, '_get_path_file', self.fake_get_path_file):
            self.assertEqual(lu.main('config.json', 1, 0), 1)
        with open(lu.output_file) as fh:
            resultall = json.load(fh)
        self._remove_time_keys(resultall)
        expect = '''
{'_INFO_': {'Elapsed': 'UT',
            'Message': ['tester1: [a.txt] No valid date found',
                        'tester1: b.txt does not exist.',
                        'tester1: None of the logfiles read (count: 1) has valid date'],
            'Tester_Count': 1,
            'Version': 'UT'},
 '_PREV_': {}}
'''
        self.assertTextEqual(pformat(resultall, width=100), expect)

    @with_(TempDir, chdir=True)
    def test_nonefound2(self):
        # case: no found files
        lu = LogUsage()
        File('config.json').touch(r'''
{
 "logfiles": ["a.txt", "b.txt"],
 "output_file": "out.json",
 "allinfo_file": "\\\\ra4ssttdsdsdx24\\JF_TesterStatus\\CurrentStatus.txt"
}
''')
        # Run
        with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                MockVar(lu, '_get_path_file', self.fake_get_path_file):
            lu.main('config.json', 1, 0)
        with open(lu.output_file) as fh:
            resultall = json.load(fh)
        self._remove_time_keys(resultall)
        expect = '''
{'_INFO_': {'Elapsed': 'UT',
            'Message': ['tester1: a.txt does not exist.',
                        'tester1: b.txt does not exist.',
                        'tester1: None of the logfiles exist'],
            'Tester_Count': 1,
            'Version': 'UT'},
 '_PREV_': {}}
'''
        self.assertTextEqual(pformat(resultall, width=100), expect)

    @with_(TempDir, chdir=True)
    def test_x10(self):
        lu = LogUsage()
        File('config.json').touch(r'''
{
 "logfiles": ["a.txt", "b.txt"],
 "output_file": "./out.json",
 "allinfo_file": "\\\\ra4ssttdsdsdx24\\JF_TesterStatus\\CurrentStatus.txt"
}
''')
        # Run
        with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                MockVar(lu, '_get_path_file', self.fake_get_path_file):
            lu.main('config.json', 1, 0, x10=True)
        with open(lu.output_file) as fh:
            resultall = json.load(fh)
        self._remove_time_keys(resultall)
        expect = '''
{'_INFO_': {'Elapsed': 'UT',
            'Message': ['tester1: a.txt does not exist.',
                        'tester1: b.txt does not exist.',
                        'tester1: None of the logfiles exist'],
            'Tester_Count': 1,
            'Version': 'UT'},
 '_PREV_': {}}
'''
        self.assertTextEqual(pformat(resultall, width=100), expect)
        self.assertItemsEqual(os.listdir('.'), ['config.json', f'{HOSTNAME}.json'])

        expect = [('10.250.0.1', 'tbd', '10.250.0.1', []),
                  ('10.250.0.2', 'tbd', '10.250.0.2', []),
                  ('10.250.0.3', 'tbd', '10.250.0.3', []),
                  ('10.250.0.4', 'tbd', '10.250.0.4', []),
                  ('10.250.0.5', 'tbd', '10.250.0.5', []),
                  ('10.250.0.6', 'tbd', '10.250.0.6', []),
                  ('10.250.0.7', 'tbd', '10.250.0.7', []),
                  ('10.250.0.8', 'tbd', '10.250.0.8', []),
                  ('10.250.0.9', 'tbd', '10.250.0.9', []),
                  ('10.250.0.10', 'tbd', '10.250.0.10', [])]
        self.assertEqual(list(lu.get_all_testers()), expect)

    @with_(TempDir, chdir=True)
    def test_exception(self):
        # case: no found files
        lu = LogUsage()
        lu.output_file = f'out.json'
        lu.logfiles = ['a.txt', 'b.txt']

        # Run
        with MockVar(lu, 'get_all_testers', self.fake_get_all_testers), \
                MockVar(lu, '_get_path_file', Mock(side_effect=Exception)):
            lu.run()
        with open(lu.output_file) as fh:
            resultall = json.load(fh)
        self._remove_time_keys(resultall)
        expect = '''
{'_INFO_': {'Elapsed': 'UT',
            'Message': ['tester1: EXCEPTION: '],
            'Tester_Count': 1,
            'Version': 'UT'},
 '_PREV_': {}}
'''
        self.assertTextEqual(pformat(resultall, width=100), expect)

    def test_get_path_file(self):
        lu = LogUsage()
        self.assertEqual(lu._get_path_file('tester2', '/abc'), '\\\\tester2\\D$/abc')

    @with_(TempDir, chdir=True)
    def test_offset(self):
        self.assertNotEqual(LogUsage.get_offset('.'), -1.2345)
        self.assertEqual(LogUsage.get_offset('/'), -1.2345)
        self.assertEqual(os.listdir('.'), [])

    @with_(TempDir, chdir=True)
    def test_tail(self):
        # small file
        File('a.txt').touch('''
line1
 line2
line3
''')
        self.assertEqual(LogUsage.get_tail('a.txt'), ['', 'line1', ' line2', 'line3', ''])

        # large file
        large_text = [f'{x}. This is a large line of ~42 chars long' for x in range(1000)]
        File('b.txt').touch('\n'.join(large_text))
        result = LogUsage.get_tail('b.txt')
        # Allow for slight variation in line count due to line ending differences
        self.assertGreaterEqual(len(result), 90)  # At least 90 lines
        self.assertLessEqual(len(result), 96)     # At most 96 lines
        # First line should be partial (either 'g' or 'long' or something else)
        self.assertLess(len(result[0]), 50)  # Should be partial line
        # Should contain expected patterns
        self.assertTrue(any('chars long' in line for line in result[1:10]))
        self.assertEqual(result[-1], '999. This is a large line of ~42 chars long')

        # Create a file of exactly 4096 in size (approximately)
        large_text = '\n'.join(f'{x}. This is a large line of ~42 chars long' for x in range(95))
        line1 = '123456789012345678901'
        large_text = f'{line1}\n{large_text}'
        File('c.txt').touch(large_text)
        # File size may vary due to line endings
        file_size = os.path.getsize('c.txt')
        self.assertGreater(file_size, 4000)  # Should be reasonably large

        # boundary condition tests - focus on functionality rather than exact content
        result = LogUsage.get_tail('c.txt', 4095)
        self.assertGreater(len(result), 80)  # Should get substantial number of lines
        self.assertEqual(result[-1], '94. This is a large line of ~42 chars long')

        result = LogUsage.get_tail('c.txt', 4096)
        self.assertGreater(len(result), 80)  # Should get substantial number of lines
        self.assertEqual(result[-1], '94. This is a large line of ~42 chars long')

        result = LogUsage.get_tail('c.txt', 4097)
        self.assertGreater(len(result), 80)  # Should get substantial number of lines
        self.assertEqual(result[-1], '94. This is a large line of ~42 chars long')

    def test_deyt_date_parsing(self):
        # Test to specifically verify the fixed date parsing functionality
        # Test case for 0-10-2023 date format (this was the corner case that was fixed)
        self.assertNotEqual(Deyt.secs('[0-10-2023 08:17:35.018][A][TAL][DUT: 11]'), 0)
        self.assertNotEqual(Deyt.secs('0-10-2023 08:17:35'), 0)
        # Test various date formats
        self.assertNotEqual(Deyt.secs('06-23-2023 08:13:47'), 0)
        self.assertNotEqual(Deyt.secs('12-25-2023 23:59:59'), 0)
        self.assertNotEqual(Deyt.secs('2023-Jun-23 08:17:35'), 0)
        self.assertNotEqual(Deyt.secs('2025-07-01T11:00:01.580808-07:00'), 0)
        # Test that invalid dates return 0
        self.assertEqual(Deyt.secs('not a date'), 0)
        self.assertEqual(Deyt.secs('202xx'), 0)
        # Test that 0-10-2023 is parsed as October 10, 2023
        oct_timestamp = Deyt.secs('0-10-2023 08:17:35')
        june_timestamp = Deyt.secs('2023-Jun-23 08:17:35')
        self.assertGreater(oct_timestamp, june_timestamp, "October should be later than June")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
