#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unittest for tputil.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE     # must be first import for unittests
from gadget.tputil import *
from gadget.ut import TestCase, unittest
from gadget.helperclass import CaptureStdoutLog
from gadget.printmore import Dumper
from gadget.files import TempDir, File
from gadget.gizmo import MockVar, with_
from gadget.disk import mkdirs, Chdir, Allfiles
from gadget.dictmore import keys_atlevel
from gadget.shell import IS_UNIX
from unittest.mock import Mock
from mod.setting import cfg
from os.path import join
from tp.testprogram import Env
from pprint import pprint, pformat
import gadget.helperclass as gadget_helperclass
import re


class TestUtil(TestCase):

    def test_delete_por_tp(self):
        with TempDir(name=True) as tdir:
            # none found
            self.assertEqual(delete_por_tp(tdir, 'ABC'), 0)

            # one found
            File(f'{tdir}/POR_TP/ABC/EnvironmentFile.env').touch(mkdir=True)
            self.assertEqual(delete_por_tp(tdir, 'ABC'), 0)

            # two found, delete one
            File(f'{tdir}/POR_TP/DEF/EnvironmentFile.env').touch(mkdir=True)
            File(f'{tdir}/POR_TP/GHI/EnvironmentFile.env').touch(mkdir=True)
            self.assertEqual(delete_por_tp(tdir, 'ABC'), 2)
            self.assertEqual(os.listdir(f'{tdir}/POR_TP'), ['ABC'])

    def test_delete_por_tp_enhance(self):
        with TempDir(name=True) as tdir:
            # check for baseinputs removal
            File(f'{tdir}/POR_TP/H_J_K/EnvironmentFile.env').touch(mkdir=True)
            File(f'{tdir}/POR_TP/L_M_N/EnvironmentFile.env').touch(mkdir=True)
            File(f'{tdir}/Shared/POR_TP/H_J_K/EnvironmentFile.env').touch(mkdir=True)
            File(f'{tdir}/Shared/POR_TP/L_M_N/EnvironmentFile.env').touch(mkdir=True)
            File(f'{tdir}/BaseInputs/Dielet/Dielet_H_J_K/Supersedes').touch(mkdir=True)
            File(f'{tdir}/BaseInputs/Dielet/Dielet_L_M_N/Supersedes').touch(mkdir=True)
            File(f'{tdir}/BaseInputs/Dielet/Dielet_Files/blah.txt').touch(mkdir=True)
            File(f'{tdir}/Shared/BaseInputs/Common/Common_H_J_K/Supersedes').touch(mkdir=True)
            File(f'{tdir}/Shared/BaseInputs/Common/Common_L_M_N/Supersedes').touch(mkdir=True)
            File(f'{tdir}/Shared/BaseInputs/Common/Common_Files/blah.txt').touch(mkdir=True)

            self.assertEqual(delete_por_tp(tdir, 'H_J_K'), 4)
            expected_list = ['BaseInputs/Dielet/Dielet_Files/blah.txt',
                             'BaseInputs/Dielet/Dielet_H_J_K/Supersedes',
                             'POR_TP/H_J_K/EnvironmentFile.env',
                             'Shared/BaseInputs/Common/Common_Files/blah.txt',
                             'Shared/BaseInputs/Common/Common_H_J_K/Supersedes',
                             'Shared/POR_TP/H_J_K/EnvironmentFile.env']
            self.assertEqual(sorted(Env.xpath(os.path.relpath(f, tdir)) for f in Allfiles(tdir)), expected_list)

    def test_tid_testname(self):
        self.assertEqual(tid_from_pat('d0000136W0748667K_'), '0748667_00')
        self.assertEqual(tid_from_pat('d0000136W0748667K_', chunk=False), '0748667')
        with MockVar(cfg, 'testname_pos', 20):
            pat = 'd0000136W0748667K_08_testname'
            #      123456789012345678901
            self.assertEqual(tid_from_pat(pat), '0748667_08')
            pat = 'd0000136W0748667K_08testname'
            self.assertEqual(tid_from_pat(pat), '0748667_00')

        self.assertEqual(tuple_tid('d0000136W0748667K_'), ('0000136', '0748667_00'))
        with MockVar(cfg, 'testname_pos', 50):
            self.assertEqual(testname_from_pat('not_a_pat'), '')
        with MockVar(cfg, 'testname_pos', 10):
            self.assertEqual(testname_from_pat('123456789_a'), '')
        with MockVar(cfg, 'testname_pos', 9):
            self.assertEqual(testname_from_pat('123456789_a'), 'a')
        with MockVar(cfg, 'testname_pos', 8):
            self.assertEqual(testname_from_pat('123456789_aa'), 'aa')
            self.assertEqual(testname_from_pat('123456789_a'), 'a')
            self.assertEqual(testname_from_pat('123456789_'), '')
            self.assertEqual(testname_from_pat('123456789'), '')

        pat = 'g0474168C9061114D_KB_A0S1301_CA5PHCAAC010M'
        self.assertEqual(tid_from_pat(pat, chunk=True, pos=26), '9061114_01')

    def test_tuple_modname(self):
        # tuple_modname
        self.assertEqual(tuple_modname('abc'), ('BASE', 'abc'))
        self.assertEqual(tuple_modname('A::abc'), ('A', 'abc'))
        self.assertEqual(tuple_modname('IP_CPU::A::abc'), ('A', 'abc'))

    def test_is_int(self):
        # numeric
        self.assertEqual(is_int(''), True)
        self.assertEqual(is_int('1'), True)
        self.assertEqual(is_int('-1'), True)
        self.assertEqual(is_int(1), True)
        # not numeric
        self.assertEqual(is_int('1.0'), False)
        self.assertEqual(is_int('a'), False)
        self.assertEqual(is_int('1V'), False)
        # assert cases
        with self.assertRaisesRegex(AssertionError, 'Expecting string'):
            is_int(1.0)

    def test_noquote(self):
        self.assertEqual(noquote('123'), '123')
        self.assertEqual(noquote('"123"'), '123')
        self.assertEqual(noquote('"123'), '"123')
        self.assertEqual(noquote('"123"+"45"'), '"123"+"45"')
        self.assertEqual(noquote("'123'"), "'123'")
        self.assertEqual(noquote('""'), '')

    def test_removeip(self):
        self.assertEqual(remove_ip('IP_a::SCN::abc'), 'IP_a::SCN::abc')
        self.assertEqual(remove_ip('IP_PCH::abc'), 'abc')
        self.assertEqual(remove_ip('IP_CPU::A:abc'), 'A:abc')
        self.assertEqual(remove_ip('IP_CD::A:abc'), 'A:abc')
        self.assertEqual(remove_ip('IPC::A:abc'), 'A:abc')      # NVL
        self.assertEqual(remove_ip('IPa::A:abc'), 'IPa::A:abc')
        self.assertEqual(remove_ip('IP_CPU_BASE::A.abc'), 'A.abc')
        self.assertEqual(remove_ip('IP_CPU_CONCURRENT_FLOWS::PRL0CPUGT_IP_CPU_FLOW_SubFlow'), 'IP_CPU_CONCURRENT_FLOWS::PRL0CPUGT_IP_CPU_FLOW_SubFlow')

    def test_num_disp(self):
        self.assertEqual(volt_disp('1'), '1')

        # special cases
        self.assertEqual(volt_disp(1.1 + 2.2 - 3.3), '  0pV    ')
        self.assertEqual(volt_disp(-1.0), ' -1V     ')
        self.assertEqual(volt_disp(-0.0001), '-100uV   ')
        self.assertEqual(volt_disp(0), '  0V     ')

        # No trailing zero
        self.assertEqual(volt_disp(1 * 0.001), '  1mV    ')
        self.assertEqual(volt_disp(10 * 0.001), ' 10mV    ')
        self.assertEqual(volt_disp(100 * 0.001), '100mV    ')
        self.assertEqual(volt_disp(1.1 * 0.001), '  1.1mV  ')

        # Rounded off
        self.assertEqual(volt_disp(1.1069 * 0.001), '  1.107mV')
        self.assertEqual(time_disp(1.1069 * 0.001), '  1.107mS')
        self.assertEqual(num_disp(1.106 * 0.001), '  1.106m')
        self.assertEqual(num_disp(1.1069 * 0.001, dec=2), '  1.11m')
        self.assertEqual(num_disp(1.1069 * 0.001, dec=5), '  1.1069m ')
        self.assertEqual(volt_disp(1.106 * 0.001, dec=4), '  1.106mV ')
        self.assertEqual(time_disp(1.106 * 0.001, dec=4), '  1.106mS ')
        self.assertEqual(volt_disp(100.1069 * 0.001), '100.107mV')
        self.assertEqual(volt_disp(100.106 * 0.001), '100.106mV')
        self.assertEqual(volt_disp(1000.106 * 0.001), '  1V     ')
        self.assertEqual(volt_disp(100.106), '100.106V ')
        self.assertEqual(num_disp(100, dec=12), '100.00           ')    # since max of 10 iterations, for coverage

        # 3 significant digit
        self.assertEqual(volt_disp(1.01 * 0.0000000000000001), '  0pV    ')
        self.assertEqual(volt_disp(1.01 * 0.000000000000001), '  0.001pV')
        self.assertEqual(volt_disp(1.01 * 0.00000000000001), '  0.01pV ')
        self.assertEqual(volt_disp(1.01 * 0.0000000000001), '  0.101pV')
        self.assertEqual(volt_disp(1.01 * 0.000000000001), '  1.01pV ')
        self.assertEqual(volt_disp(1.01 * 0.00000000001), ' 10.1pV  ')
        self.assertEqual(volt_disp(1.01 * 0.0000000001), '101pV    ')
        self.assertEqual(volt_disp(1.01 * 0.000000001), '  1.01nV ')
        self.assertEqual(volt_disp(1.01 * 0.00000001), ' 10.1nV  ')
        self.assertEqual(volt_disp(1.01 * 0.0000001), '101nV    ')
        self.assertEqual(volt_disp(1.01 * 0.000001), '  1.01uV ')
        self.assertEqual(volt_disp(1.01 * 0.00001), ' 10.1uV  ')
        self.assertEqual(volt_disp(1.01 * 0.0001), '101uV    ')
        self.assertEqual(volt_disp(1.01 * 0.001), '  1.01mV ')
        self.assertEqual(volt_disp(1.01 * 0.01), ' 10.1mV  ')
        self.assertEqual(volt_disp(1.01 * 0.1), '101mV    ')
        self.assertEqual(volt_disp(1.01), '  1.01V  ')
        self.assertEqual(volt_disp(1.01 * 10), ' 10.1V   ')
        self.assertEqual(volt_disp(1.01 * 100), '101V     ')
        self.assertEqual(volt_disp(1.01 * 1000), '1010V    ')
        self.assertEqual(volt_disp(1.01 * 1000000), '1010000V ')

        # time
        self.assertEqual(time_disp(1 * 0.00000000000001), '  0.01pS ')
        self.assertEqual(time_disp(1 * 0.0000000000001), '  0.1pS  ')
        self.assertEqual(time_disp(1 * 0.000000000001), '  1pS    ')
        self.assertEqual(time_disp(1 * 0.00000000001), ' 10pS    ')
        self.assertEqual(time_disp(1 * 0.0000000001), '100pS    ')
        self.assertEqual(time_disp(1 * 0.000000001), '  1nS    ')
        self.assertEqual(time_disp(1 * 0.00000001), ' 10nS    ')
        self.assertEqual(time_disp(1 * 0.0000001), '100nS    ')
        self.assertEqual(time_disp(1 * 0.000001), '  1uS    ')
        self.assertEqual(time_disp(1 * 0.00001), ' 10uS    ')
        self.assertEqual(time_disp(1 * 0.0001), '100uS    ')
        self.assertEqual(time_disp(1 * 0.001), '  1mS    ')
        self.assertEqual(time_disp(1 * 0.01), ' 10mS    ')
        self.assertEqual(time_disp(1 * 0.1), '100mS    ')
        self.assertEqual(time_disp(1), '  1S     ')
        self.assertEqual(time_disp(10), ' 10S     ')
        self.assertEqual(time_disp(1000), '1000S    ')
        self.assertEqual(time_disp(10000), '10000S   ')

    def test_trimut(self):
        text = '''
a
-i- bc
b'''
        self.assertEqual(trimut(text), ['a', 'b'])
        self.assertEqual(trimut(text, True), 'a\nb')
        self.assertEqual(trimut(text, True, True), '\na\nb')

    def test_log_usage(self):
        # unittest
        self.assertEqual(log_usage('blah', None), 1)

        # real one
        with TempDir(name=True) as tdir,\
                MockVar(cfg, 'log_dir', tdir),\
                MockVar(gadget_helperclass, 'IS_UT', False):
            mkdirs(join(tdir, 'tput'))
            log_usage('tput', cfg)
            self.assertIn('test_tputil.py', open(join(tdir, 'tput/usage.log')).read())

    def test_pat_section_diff(self):
        self.assertEqual(pat_section_diff('1_2_3', '1_2_3'),
                         ('', ''))
        self.assertEqual(pat_section_diff('1_2_3', 'a_b_c'),
                         ('1_ _2_ _3', 'a_ _b_ _c'))
        self.assertEqual(pat_section_diff('1_2_3a_4', '1_2_5b_4'),
                         ('_3a_', '_5b_'))
        self.assertEqual(pat_section_diff('1_2_3', '1_2'),
                         ('_3', '_None'))
        self.assertEqual(pat_section_diff('1_2', '1_2_3'),
                         ('_None', '_3'))

    def test_ti_disassemble(self):
        # This is MTL specific convention!

        # dictionary
        expect = {'corner': 'X',
                  'freq': 'X',
                  'kill_edc': 'K',
                  'partition': 'X',
                  'patratio': 'X',
                  'speedflow': '1000',
                  'subflow': 'START',
                  'test_cat': 'CONT',
                  'testtype': 'VCCCONT',
                  'userinput': '',
                  'voltage_domain': 'X'}
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_1000', True), expect)
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_1000', True, isclass=True), expect)

        # without user without speedflow
        expect = ['CONT', 'X', 'VCCCONT', 'K', 'START', 'X', 'X', 'X', 'X', '', '']
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X'), expect)
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X', isclass=True), expect)

        # without user with speedflow
        expect = ['CONT', 'X', 'VCCCONT', 'K', 'START', 'X', 'X', 'X', 'X', '', '1000']
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_1000'), expect)
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_1000', isclass=True), expect)

        # with user without speedflow
        expect = ['CONT', 'X', 'VCCCONT', 'K', 'START', 'X', 'X', 'X', 'X', 'BLAH1000', '']
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_BLAH1000'), expect)
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_BLAH1000', isclass=True), expect)

        # with user with speedflow
        expect = ['CONT', 'X', 'VCCCONT', 'K', 'START', 'X', 'X', 'X', 'X', 'A_A_B', '1000']
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_A_A_B_1000'), expect)
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_A_A_B_1000', isclass=True), expect)

        expect = ['CONT', 'X', 'VCCCONT', 'K', 'START', 'X', 'X', 'X', 'X', 'A_A_B', '*']
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_A_A_B_*'), expect)
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_A_A_B_*', isclass=True), expect)

        # special character issue
        expect = ['ATPG', 'CNVI', 'SCANFI', 'K', 'BEGSOC', '10', 'VAON', 'F2', '0100', 'MIN', '']
        self.assertEqual(ti_disassemble('ATPG_CNVI_SCANFI_K_BEGSOC_10_VAON_F2_0100_MIN'), expect)
        self.assertEqual(ti_disassemble('ATPG_CNVI_SCANFI_K_BEGSOC_10_VAON_F2_0100_MIN', isclass=True), expect)
        expect = ['ATPG', 'CNVI', 'SCANFI', 'K', 'BEGSOC', 'X', 'VAON', 'X', '0100', 'MIN', '0110']
        self.assertEqual(ti_disassemble('ATPG_CNVI_SCANFI_K_BEGSOC_X_VAON_X_0100_MIN_0110'), expect)
        self.assertEqual(ti_disassemble('ATPG_CNVI_SCANFI_K_BEGSOC_X_VAON_X_0100_MIN_0110', isclass=True), expect)

        # invalid
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X'), [])
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X', isclass=True), [])
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X', True), {})
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X', True, isclass=True), {})
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_ VCC1P8_QUIET_1_LC'), [])
        self.assertEqual(ti_disassemble('CONT_X_VCCCONT_K_START_X_X_X_X_ VCC1P8_QUIET_1_LC', isclass=True), [])

        # sort only
        #               1   2  3      4  5    6 7  8   9  10 11
        for given in ('CONT_B_VCCCONT_X_START_B_B_VMIN_LFM_Z_*',
                      'CONT_B_VCCCONT_X_START_B_B_VMIN_300_Z_*'):
            expect = given.split('_')
            self.assertEqual(ti_disassemble(given), expect)
            self.assertEqual(ti_disassemble(given, isclass=True), [])

        given = 'CONT_B_VCCCONT_X_START_B_B_VMIN_300_A_B_c'
        expect = ['CONT', 'B', 'VCCCONT', 'X', 'START', 'B', 'B', 'VMIN', '300', 'A_B_c', '']
        self.assertEqual(ti_disassemble(given), expect)
        self.assertEqual(ti_disassemble(given, isclass=True), [])

    def test_get_param(self):
        self.assertEqual(get_param({'level': 'ghi'}, 'level'), 'ghi')
        self.assertEqual(get_param({'level': 'ghi'}, 'level', 'xx'), 'ghi')
        self.assertEqual(get_param({'oops': 'ghi'}, 'level'), None)
        self.assertEqual(get_param({'oops': 'ghi'}, 'level', 'xx'), 'xx')

        # special
        self.assertEqual(get_param({'level': 'ghi'}, 'level', 'xx'), 'ghi')
        self.assertEqual(get_param({'levels': 'ghi'}, 'level', 'xx'), 'ghi')
        self.assertEqual(get_param({'LevelsTc': 'ghi'}, 'level', 'xx'), 'ghi')
        self.assertEqual(get_param({'tim': 'ghi'}, 'level', 'xx'), 'xx')
        self.assertEqual(get_param({'timings': 'ghi'}, 'timing', 'xx'), 'ghi')

    def test_to_regex(self):
        self.assertEqual(to_regex(''), '^$')
        self.assertEqual(to_regex(None), '')
        self.assertEqual(to_regex('no_chan.*ge'), 'no_chan.*ge')
        self.assertEqual(to_regex('chan*ge'), 'chan.*ge')
        self.assertEqual(to_regex('*chan**ge*'), '.*chan.*.*ge.*')
        self.assertEqual(to_regex('.*chan.*.*ge.*'), '.*chan.*.*ge.*')
        self.assertEqual(to_regex('.*chan.**ge*'), '.*chan.*.*ge.*')
        self.assertEqual(to_regex('^_*max_*$', exact=True), '^_.*max_.*$')
        self.assertEqual(to_regex('nochange$', exact=True, maxlen=2), '^nochange$')   # coverage
        self.assertEqual(to_regex('^nochange', exact=True), '^nochange$')

    def test_instancename_no_speed(self):
        # drv case
        self.assertEqual(instancename_no_speed('test_instance_0123'), ('test_instance_0123', 0))
        # not a speedflow
        self.assertEqual(instancename_no_speed('SBFT_CORE_VMIN_K_SRHCRF6_X_VCORE_F6_4400_MLC'),
                         ('SBFT_CORE_VMIN_K_SRHCRF6_X_VCORE_F6_4400_MLC', 0))
        # speedflow
        self.assertEqual(instancename_no_speed('SBFT_CORE_VMIN_K_SRHCRF6_X_VCORE_F6_4400_MLC_1222'),
                         ('SBFT_CORE_VMIN_K_SRHCRF6_X_VCORE_F6_*_MLC_*', 4400))
        self.assertEqual(instancename_no_speed('SBFT_CORE_VMIN_K_SRHCRF6_X_VCORE_F6_HFM_MLC_1222'),
                         ('SBFT_CORE_VMIN_K_SRHCRF6_X_VCORE_F6_HFM_MLC_*', 0))
        # speedflow regex
        self.assertEqual(instancename_no_speed('TGL_CD651_2000'),
                         ('TGL_CD651_*', 0))
        self.assertEqual(instancename_no_speed('TGL_CD651_FAILFLOW_2000'),
                         ('TGL_CD651_FAILFLOW_*', 0))
        self.assertEqual(instancename_no_speed('TGL_651_SOMETHING_2000'),
                         ('TGL_651_SOMETHING_*', 0))

    def test_float_2_noerr(self):
        self.assertEqual(float_2_noerr('1.211111'), 1.21)
        self.assertEqual(float_2_noerr('1.211111+21'), '1.211111+21')
        self.assertEqual(float_2_noerr(1.211111), 1.21)
        self.assertEqual(float_2_noerr('1.1V'), 1.1)
        self.assertEqual(float_2_noerr('1.1VA'), '1.1VA')
        self.assertEqual(float_2_noerr('1V'), 1.0)

    def test_isvalidip(self):
        self.assertEqual(is_validip('IP_CPU'), True)
        self.assertEqual(is_validip('IP_PCH'), True)
        self.assertEqual(is_validip('IP'), False)

    def test_ip_tuple(self):
        self.assertEqual(ip_tuple('abc'), (None, 'abc'))
        self.assertEqual(ip_tuple('IP_PCH::abc'), ('IP_PCH', 'abc'))
        self.assertEqual(ip_tuple('__main__::IP_CPU::abc'), ('IP_CPU', 'abc'))
        self.assertEqual(ip_tuple('__main__::abc'), (None, 'abc'))

    def test_correct_type(self):
        self.assertEqual(correct_type('a', None), 'a')    # None
        self.assertEqual(correct_type('a', 'b'), 'a')     # correct type str
        self.assertEqual(correct_type(1, 2), 1)           # correct type int
        self.assertEqual(correct_type(1.1, 2.0), 1.1)     # correct type float
        self.assertEqual(correct_type('1', 2), 1)         # to int
        self.assertEqual(correct_type(1, 'ab'), '1')      # to str
        self.assertEqual(correct_type('1.1', 1.0), 1.1)   # to float
        with self.assertRaisesRegex(TypeError, 'Unknown type:'):
            correct_type('1.2', {})

    @with_(TempDir, chdir=True)
    def test_find_files_given_paths(self):
        File('d1/a.plist').touch(mkdir=True)
        File('d1/B.plist').touch(mkdir=True)
        File('d2/a.plist').touch(mkdir=True)
        File('d2/c.plist').touch(mkdir=True)
        File('d3/a.plist').touch(mkdir=True)
        File('d3/D.plist').touch(mkdir=True)
        File('d4').touch()   # file instead of dir
        searchpath = 'd1 d4 d2 d5 d3'.split()

        # returns the real filename case regardless of input list case
        result = find_files_given_paths('a.plist b.plist'.split(), searchpath, 'no msg')
        expected_a = {'d1/a.plist', 'd1/B.plist'}
        self.assertEqual(result, expected_a)

        # lower case list of files to be found
        expected = {'d3/D.plist', 'd1/a.plist', 'd1/B.plist', 'd2/c.plist'}
        result = find_files_given_paths('a.plist b.plist c.plist d.plist'.split(), searchpath, 'no msg')
        self.assertEqual(result, expected)

        # upper case list of files to be found
        result = find_files_given_paths('A.plist B.plist C.plist D.plist'.split(), searchpath, 'no msg')
        self.assertEqual(result, expected)

        # File defined but does not exist. Throws a warning instead of an error
        result = find_files_given_paths('A.plist B.plist C.plist D.plist E.plist'.split(), searchpath, 'no msg', error_out=False)
        self.assertEqual(result, expected)

        # File defined but does not exist. Throws error
        with self.assertRaisesRegex(ErrorEnv, 'Cannot find'):
            find_files_given_paths(['E.plist'], searchpath, 'no msg')

        if IS_UNIX:
            # File defined but does not exist due to case sensitive path. Throws error
            with self.assertRaisesRegex(ErrorEnv, 'Cannot find'):
                find_files_given_paths(['c.plist'], ['D2'], 'no msg')
        else:
            # File defined and should be found on windows
            result = find_files_given_paths(['c.plist'], ['D2'], 'no msg')
            self.assertEqual(result, {'D2/c.plist'})

    def regres_get_modulename(self):
        # Purpose: make sure all files in Module/ are ok with get_modulename
        # Run this from tp folder
        from gadget.disk import Allfiles
        errors = 0
        idx = 0
        for idx, ff in enumerate(Allfiles('Modules', skipsvn=True)):
            if basename(ff) == '.git':
                continue
            try:
                get_modulename(ff)
            except Exception as e:
                errors += 1
                print(e)
        print(f'Total: {idx}, errors: {errors}')
        self.assertEqual(errors, 0)

    def test_get_modulename(self):
        self.assertEqual(get_modulename('blah'), None)
        self.assertEqual(get_modulename('Modules/TPI'), None)
        self.assertEqual(get_modulename('Modules/TPI/.gitignore'), None)
        self.assertEqual(get_modulename('POR_TP/Class_MTL_P28/SkipModules/MIO_DDR5AC_SXM.txt'), None)

        # normal case
        self.assertEqual(get_modulename('Modules/TP_I/a.mtpl'), 'TP_I')
        self.assertEqual(get_modulename('Modules/TP-a/ID_V/a.mtpl'), 'ID_V')
        self.assertEqual(get_modulename(r'Modules\TP_I\a-.mtpl'), 'TP_I')
        self.assertEqual(get_modulename(r'Modules\TP-a\ID_V\a_-.mtpl'), 'ID_V')

        # InputFiles and AlephFiles
        self.assertEqual(get_modulename('Modules/blah/blah/blah/ID_V/InputFiles/a-.mtpl'), 'ID_V')
        self.assertEqual(get_modulename('Modules/blah/blah/blah/ID_V/AlephFiles/a-.mtpl'), 'ID_V')
        self.assertEqual(get_modulename(r'Modules\bla\lah\blah\ID_V\AlephFiles\a-.mtpl'), 'ID_V')
        self.assertEqual(get_modulename('Modules/TP_V/a'), 'TP_V')
        self.assertEqual(get_modulename('UserCodes/blah/IronPython.Modules.dll'), None)
        self.assertEqual(get_modulename('Modules/CLK/.github/CODEOWNERS'), 'CLK')
        self.assertEqual(get_modulename('Modules/CLK/_source/CLK_BASE_CXX/CLK_BASE_CXX.input.flw'), 'CLK_BASE_CXX')
        self.assertEqual(get_modulename('Modules/FUS/FUS_FUSEBURN_CXX/PymtplInputFiles/FUS_FUSEBURN_CXX_AutoCounter.json'), 'FUS_FUSEBURN_CXX')

        # safety check
        with self.assertRaisesRegex(ErrorUser, 'Unknown file in Modules'):
            get_modulename('Modules/ID-V/aa')

    def test_is_number(self):
        self.assertEqual(is_number('-1.23'), True)
        self.assertEqual(is_number('-1.23.2'), False)
        self.assertEqual(is_number('-1.23A'), False)
        self.assertEqual(is_number('.*'), False)
        self.assertEqual(is_number(1.0), True)
        self.assertEqual(is_number(1), True)

    def test_read_blocks(self):
        with TempDir(name=True) as tdir:
            fname = join(tdir, 'a.mtpl')
            File(fname).touch("""
DUTFlow START
{
        DUTFlowItem ABC
        {
                Result -2 {
                        Property PassFail = "Pass";
                        Return  -1;
                }
                Result -1
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }
        }
}
DUTFlow END
{
        DUTFlowItem GHI {
        # {
                Result -2
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }
                Result -1
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }
        }
}
""")
            result = read_blocks(fname, ['DUTFlow START', 'DUTFlowItem GH*', 'MISSING'])
            expect = """DUTFlow START
{
        DUTFlowItem ABC
        {
                Result -2 {
                        Property PassFail = "Pass";
                        Return  -1;
                }
                Result -1
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }
        }
}

        DUTFlowItem GHI {
        # {
                Result -2
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }
                Result -1
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }
        }

"""
            self.assertTextEqual(''.join(result), expect)

            # multiple match case
            result = read_blocks(fname, ['Result -2'])
            expect = """                Result -2 {
                        Property PassFail = "Pass";
                        Return  -1;
                }

                Result -2
                {
                        Property PassFail = "Fail";
                        Return  -1;
                }

"""
            self.assertTextEqual(''.join(result), expect)

# class TestXmlRead(TestCase):
#
#     def test_basic(self):
#         ff = f'{UT_DIR}/xml_ut/tp.tpconfig.multiple'
#         # Last element is a list
#         self.assertEqual(XmlRead(ff).get('plist', 'Configuration,SupportedBomGroups,BomGroup,name=MTL_GCD64_SDS'),
#                          'PLIST_ALL.plist.xml')
#         self.assertEqual(XmlRead(ff).get('plist', 'Configuration.SupportedBomGroups.BomGroup'),
#                          'PLIST_ALL.plist.xml')
#         # Single
#         self.assertEqual(XmlRead(ff).get('ProductCodeName', 'Configuration.TestProgram'),
#                          'MTG')
#
#     def test_bscan_xml(self):
#         ff = f'{UT_DIR}/TGLXXXXBXH14P00S109/TPL/Modules/SIO_VIXVOX/InputFiles/BSCAN_TCSS_MIN_VOX.xml'
#         # analog_config,ConfigList,name=TCSS_MIN_VOL_U:config,Cores,Core,


class TestMtplBlock(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic(self):
        # read & write
        text = '''# Module Revision
Version 1.0;
ProgramStyle = Modular;
Counters
{
  ctr1;
}
# com line
Test PrimePatConfigTestMethod F1
{
        SetPoint;
        # comment
}
# com f2
DUTFlow F2
{
        SetPoint;

}
# com f3
MultiTrialTest F3 { ConfigurationFile; }
# com f4
Test abc F4 { ConfigurationFile; abc; }
# com last
'''
        File('a.mtpl').touch(text)

        cl = MtplBlocks('a.mtpl')
        cl.write('ut')
        expect = '''# Module Revision
Version 1.0;
ProgramStyle = Modular;
Counters
{
  ctr1;
}
# com line
Test PrimePatConfigTestMethod F1
{
        SetPoint;
        # comment
}
Test abc F4 { ConfigurationFile; abc; }
MultiTrialTest F3 { ConfigurationFile; }
DUTFlow F2
{
        SetPoint;

}
'''
        self.assertTextEqual(File('a.mtpl').read(), expect)
        self.assertEqual(sorted(os.listdir('.')), ['a.mtpl', 'a.mtpl.source'])
        self.assertTextEqual(File('a.mtpl.source').read(), text)

        # different output - new
        File('a.mtpl.source').unlink()
        File('a.mtpl').touch(text, newfile=True)
        mkdirs('out')
        cl.write('ut', 'out/b.mtpl')
        self.assertTextEqual(File('out/b.mtpl').read(), expect)
        self.assertTextEqual(File('out/b.mtpl.orig.txt').read(), expect)

        # different output - ok
        cl.write('ut', 'out/b.mtpl')
        self.assertTextEqual(File('out/b.mtpl').read(), expect)
        self.assertTextEqual(File('out/b.mtpl.orig.txt').read(), expect)

        # different output - changed
        File('out/b.mtpl').touch('appended')
        with self.assertRaisesRegex(ErrorUser, 'was modified. Compare'):
            cl.write('ut', 'out/b.mtpl')

    @with_(TempDir, chdir=True)
    def test_read_basic(self):
        # This include comments which must be preserved
        text = '''# Module Revision
Version 1.0;
ProgramStyle = Modular;
Counters
{
  ctr1;
}
Test PrimePatConfigTestMethod F1
{
        SetPoint;
        # comment
}
DUTFlow F2
# com1
{
        SetPoint;

}
MultiTrialTest F3 { ConfigurationFile; }
Flow F4 { ConfigurationFile; abc; }
CSharpTest PrimePatConfigTestMethod F5
{
        SetPoint;
}
'''
        File('a.mtpl').touch(text)

        cl = MtplBlocks('a.mtpl')

        # header
        expect = '''# Module Revision
Version 1.0;
ProgramStyle = Modular;
Counters
{
  ctr1;
}
'''
        self.assertTextEqual(''.join(cl.head), expect)

        # one instance
        expect = '''Test PrimePatConfigTestMethod F1
{
        SetPoint;
        # comment
}
'''
        self.assertTextEqual(''.join(cl.blocks['F1']), expect)

        # keys
        self.assertEqual(cl.blocks.keys(), {'F1', 'F2', 'F3', 'F4', 'F5'})
        self.assertEqual(cl.btype, {'F1': 'Test',
                                    'F2': 'DUTFlow',
                                    'F3': 'MultiTrialTest',
                                    'F4': 'Flow',
                                    'F5': 'CSharpTest'})
        self.assertEqual(set(cl.block_types), set(cl.btype.values()))   # Add new block types in test_read_basic()

        # another instance
        expect = '''DUTFlow F2
# com1
{
        SetPoint;

}
'''
        self.assertTextEqual(''.join(cl.blocks['F2']), expect)
        self.assertEqual(cl.blocks['F3'], ['MultiTrialTest F3 { ConfigurationFile; }\n'])
        self.assertEqual(cl.blocks['F4'], ['Flow F4 { ConfigurationFile; abc; }\n'])

    @with_(TempDir, chdir=True)
    def test_read_dutflow(self):
        text = '''# Module Revision
Version 1.0;
DUTFlow F2
{
   DUTFlowItem NEW_LINK IOE
       # linkname: two
       { line NEW_LINK; }
}
DUTFlow F3
{
   DUTFlowItem NEW_LINK IOE
       # linkname: two
       {
       {
       line NEW_LINK;
       }
       }
}
'''
        File('a.mtpl').touch(text)

        cl = MtplBlocks('a.mtpl')

        # header
        expect = '''# Module Revision
Version 1.0;
'''
        self.assertTextEqual(''.join(cl.head), expect)

        # F2
        expect = '''DUTFlow F2
{
   DUTFlowItem NEW_LINK IOE
       # linkname: two
       { line NEW_LINK; }
}
'''
        self.assertTextEqual(''.join(cl.blocks['F2']), expect)

        # F3
        expect = '''DUTFlow F3
{
   DUTFlowItem NEW_LINK IOE
       # linkname: two
       {
       {
       line NEW_LINK;
       }
       }
}
'''
        self.assertTextEqual(''.join(cl.blocks['F3']), expect)

    @with_(TempDir, chdir=True)
    def test_recurse_ut(self):
        text = '''
Test meth AA { line; }
Test meth BB { line; }
Test meth CC { line; }
 DUTFlow DEP {
    DUTFlowItem n1 AA {
    }
}
DUTFlow Main {
    DUTFlowItem n1 DEP {
    }
    DUTFlowItem n2 AA {
    }
    DUTFlowItem n3 BB {
    }
}
'''
        File('a.mtpl').touch(text)
        res = {}
        MtplBlocks('a.mtpl').recurse('Main', res)
        pprint(res)
        self.assertEqual(res, {'AA': ['Test meth AA { line; }\n'],
                               'BB': ['Test meth BB { line; }\n'],
                               'DEP': [' DUTFlow DEP {\n',
                                       '    DUTFlowItem n1 AA {\n',
                                       '    }\n',
                                       '}\n'],
                               'Main': ['DUTFlow Main {\n',
                                        '    DUTFlowItem n1 DEP {\n',
                                        '    }\n',
                                        '    DUTFlowItem n2 AA {\n',
                                        '    }\n',
                                        '    DUTFlowItem n3 BB {\n',
                                        '    }\n',
                                        '}\n']})

    def test_recurse(self):
        cl = MtplBlocks(f'{UT_DIR_REPO}/compositelink/PTH_DLVR_CXX_CLASS_P68G2.mtpl')
        res = {}
        cl.recurse('IREF_TRIM_ATOM0', res)
        self.assertEqual(len(list(keys_atlevel(res, 1))), 1018)
        self.assertEqual(len(res.keys()), 24)

        res = {}
        cl.recurse('IREF_TRIM', res)
        self.assertEqual(len(list(keys_atlevel(res, 1))), 10252)   # this includes several DUTFlow composites

        # Check the DUTFlow (composites) of IREF_TRIP
        dutflows = []
        for name in res:
            if res[name][0].strip().startswith('DUTFlow '):
                dutflows.append(res[name][0].strip())
        pprint(dutflows)
        self.assertEqual(len(dutflows), 11)

        # Check flatten
        cl.final = res
        self.assertEqual(len(list(cl.flatten_final())), 11331)

    def test_sort_dependent(self):
        text1 = '''DUTFlow a
{
   DUTFlowItem b b
   { }
}
'''
        text2 = '''DUTFlow b
{
   DUTFlowItem c c
   { }
}
'''
        text3 = '''Flow c
{
   DUTFlowItem z z
   { }
}
'''

        data = {'a': text1.split('\n'),
                'b': text2.split('\n'),
                'c': text3.split('\n')}
        self.assertEqual(MtplBlocks.sort_dependent(data, None), ['c', 'b', 'a'])
        self.assertEqual(MtplBlocks.sort_dependent(data, 'Test'), ['a', 'b', 'c'])

        data = {'a': text1.replace('DUTFlow ', 'Flow ').split('\n'),
                'b': text2.replace('DUTFlow ', 'Flow ').split('\n'),
                'c': text3.replace('DUTFlow ', 'Flow ').split('\n')}
        self.assertEqual(MtplBlocks.sort_dependent(data, None), ['c', 'b', 'a'])

    @with_(TempDir, chdir=True)
    def test_flatten_final(self):
        text1 = '''
MultiTrialTest meth a { }
Test meth q { }
Flow a
{
   DUTFlowItem b b
   { }
}
DUTFlow b
{
   DUTFlowItem c c
   { }
}
Flow c
{
   DUTFlowItem d d
   { }
}
DUTFlow d
{
   DUTFlowItem z z
   { }
}
'''
        File('a.mtpl').touch(text1)
        MtplBlocks('a.mtpl').write('ut')
        expect = '''
Test meth q { }
MultiTrialTest meth a { }
DUTFlow d
{
   DUTFlowItem z z
   { }
}
Flow c
{
   DUTFlowItem d d
   { }
}
DUTFlow b
{
   DUTFlowItem c c
   { }
}
Flow a
{
   DUTFlowItem b b
   { }
}
'''
        self.assertTextEqual(File('a.mtpl').read(), expect)

    def test_dependent_values(self):
        # complex case
        data = {'a': set(),
                'b': set('a'),
                'c': set('b'),
                'd': set('cb'),
                'e': set('d')}
        self.assertEqual(MtplBlocks.dependent_values(data), {'a': 1,
                                                             'b': 2,
                                                             'c': 3,
                                                             'd': 4,
                                                             'e': 5})
        # complex case2
        data = {'e': set(),
                'd': set('e'),
                'c': set('d'),
                'b': set('dc'),
                'a': set('b')}
        self.assertEqual(MtplBlocks.dependent_values(data), {'e': 1,
                                                             'd': 2,
                                                             'c': 3,
                                                             'b': 5,
                                                             'a': 6})
        # simple case
        data = {'a': set(),
                'b': set(),
                'c': set('a'),
                'd': set('a'),
                'e': set('d')}
        self.assertEqual(MtplBlocks.dependent_values(data), {'a': 1,
                                                             'b': 2,
                                                             'c': 2,
                                                             'd': 2,
                                                             'e': 3})

        # no dependency
        data = {x: set() for x in 'abcdef'}
        self.assertEqual(MtplBlocks.dependent_values(data), {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6})
        data = {x: set() for x in 'fedcba'}
        self.assertEqual(MtplBlocks.dependent_values(data), {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6})

        # not found case
        data = {'a': set('c'),
                'b': set('b'),
                'c': set('a')}
        with self.assertRaisesRegex(ErrorUser, 'Cannot find ordering'):
            MtplBlocks.dependent_values(data)


class TestCheckerLog(TestCase):

    def test_get_log_path(self):
        if EXIST_PDX_I_DRIVE:
            self.assertEqual(CheckerLog.get_log_path(), cfg.log_dir)

        # main path
        with MockVar(cfg, 'log_dir', '/notexist'):
            with MockVar(sys, 'argv', ['/intel/tpvalidation/engtools/tptools/mtl/beta/latest/main/checkers.py']):
                result = CheckerLog.get_log_path()
        if IS_UNIX:
            self.assertEqual(result, cfg.log_dir)
        else:
            result = re.sub(r'^[A-Z]:\\intel', '', result, flags=re.IGNORECASE)
            self.assertEqual(Env.xpath("I:" + result), cfg.log_dir)

        # not exist
        with MockVar(cfg, 'log_dir', '/notexist'):
            with MockVar(sys, 'argv', ['/intel/tpvalidation/engtools/tptools/mtl/beta/main/checkers.py']):
                with self.assertRaisesRegex(ErrorEnv, 'This must be created first'):
                    CheckerLog.get_log_path()

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_get_tool_sha(self):
        # current tool
        self.assertEqual(len(CheckerLog.get_tool_sha()), 40)

        # specific area
        self.assertEqual(len(CheckerLog.get_tool_sha(f'{UT_DIR}/ARL_68_repo_full')), 40)
        self.assertEqual(len(CheckerLog.get_tool_sha(f'{UT_DIR}/ARL_68_repo_full/Modules/CLK')), 40)
        with self.assertRaisesRegex(ErrorInput, 'git does not exist'):
            CheckerLog.get_tool_sha(f'{UT_DIR}/ARL_68_repo_full/Modules')

    def test_setup(self):
        # unittest run
        self.assertEqual(CheckerLog.setup(), 1)

        # real run
        with MockVar(gadget_helperclass, 'IS_UT', False):
            with TempDir(name=True) as tdir:
                with MockVar(CheckerLog, 'get_log_path', Mock(return_value=tdir)):
                    CheckerLog.setup()
                    self.assertEqual(os.listdir(tdir), ['checkers'])
                    self.assertEqual(len(os.listdir(f'{tdir}/checkers')), 1)    # this is date
                    log.close()

    def test_build_checks(self):
        with Chdir(f'{UT_DIR_REPO}/SimpleNVL'):
            CheckerLog.build_checks(['POR_TP/TGLH81/EnvironmentFile.env'], '*.env')

    def test_repo_sha(self):
        with TempDir(chdir=True):
            default = ('na', 'na')
            with MockVar(CheckerLog, 'repo_sha', default):
                # default
                self.assertEqual(CheckerLog.repo_sha, default)

                # no files
                CheckerLog.set_repo_sha()
                self.assertEqual(CheckerLog.repo_sha, ('none', 'not_available_logs_head_not_found'))

                # normal case
                content = '''
f26aa8e3780dd61f303734ee9abc568f979bcfd1 c5e653f82b5c7017dd7daae33dd90368e13e38a8 Delos Reyes, John Q <john.q.delos.reyes@intel.com> 1671331739 -0800   commit: torch_mv [-fast true] enabling, via datahost tar
c5e653f82b5c7017dd7daae33dd90368e13e38a8 720a3e60cba4c4226a15a084615c80629454d8a8 Delos Reyes, John Q <john.q.delos.reyes@intel.com> 1671393425 -0800   commit: generate recipe for full tp
'''
                File('.git/logs/HEAD').touch(content, mkdir=True)
                File('.git/HEAD').touch('ref: refs/heads/JDR/ybs_problem')
                CheckerLog.set_repo_sha()
                self.assertEqual(CheckerLog.repo_sha, ('JDR/ybs_problem', '720a3e60cba4c4226a15a084615c80629454d8a8'))

                # case 2 - specific commit
                File('.git/HEAD').touch('deadbeef', newfile=True)
                CheckerLog.set_repo_sha()
                self.assertEqual(CheckerLog.repo_sha, ('deadbeef', '720a3e60cba4c4226a15a084615c80629454d8a8'))


class TestMathUnits(TestCase):

    def test_mathunits(self):
        obj = Units
        self.assertEqual(obj.math_units('1+1mv+1V-.1mv+(1+.1V)'), '1+(1*0.001)+(1)-(.1*0.001)+(1+(.1))')
        self.assertEqual(obj.math_units('a+"1.1mV"+a1v'), 'a+"(1.1*0.001)"+a1v')
        self.assertEqual(obj.math_units('a+.1mV+a1v+.1V'), 'a+(.1*0.001)+a1v+(.1)')
        self.assertEqual(obj.math_units('a.(4)'), 'a.(4)')   # as-is
        self.assertEqual(obj.math_units('1V+1v'), '(1)+(1)')
        self.assertEqual(obj.math_units('1mV+1mv'), '(1*0.001)+(1*0.001)')
        self.assertEqual(obj.math_units('1mV/5mv'), '(1*0.001)/(5*0.001)')
        self.assertEqual(obj.math_units('1mV/-5mV+5mV'), '(1*0.001)/-(5*0.001)+(5*0.001)')
        self.assertEqual(obj.math_units('aa1mv'), 'aa1mv')
        self.assertEqual(obj.math_units('"1V+1v"'), '"1V+1v"')

        self.assertEqual(obj.to_number('2nS'), 2e-09)
        self.assertEqual(obj.to_number('20nS'), 2e-08)
        self.assertEqual(obj.to_number('-20.1nS'), -2.01e-08)
        self.assertEqual(obj.to_number('-20.ns'), -2e-08)   # small case
        self.assertEqual(obj.to_number('20'), 20)
        self.assertEqual(obj.to_number('-20.1'), -20.1)
        self.assertEqual(obj.to_number('-.1'), -.1)
        self.assertEqual(obj.to_number('20Volts'), None)
        self.assertEqual(obj.to_number(20), 20)
        self.assertEqual(obj.to_number('somevar'), None)
        self.assertEqual(obj.to_number(''), None)
        self.assertEqual(obj.to_number('0nS'), 0.0)
        self.assertEqual(obj.to_number('0V'), 0.0)
        self.assertEqual(obj.to_number('0C'), 0.0)    # temperature

    def test_hz(self):
        self.assertEqual(Units.math_units('-.1khz'), '-(1.0/(.1*1000))')
        self.assertEqual(Units.math_units('-1-.1khz'), '-1-(1.0/(.1*1000))')
        self.assertEqual(Units.math_units('-1+.1khz'), '-1+(1.0/(.1*1000))')
        self.assertEqual(Units.math_units('2ghz-5ns)'), '(1.0/(2*1000000000))-(5*0.000000001))')
        self.assertEqual(Units.math_units('-2ns-2ghz'), '-(2*0.000000001)-(1.0/(2*1000000000))')
        self.assertEqual(Units.math_units('10nS*5GHz/5.05GHz'),
                         '(10*0.000000001)*(1.0/(5*1000000000))/(1.0/(5.05*1000000000))')
        self.assertEqual(Units.math_units('10nS*5GHz/-5.05GHz'),
                         '(10*0.000000001)*(1.0/(5*1000000000))/-(1.0/(5.05*1000000000))')
        self.assertEqual(Units.math_units('5-1khz'), '5-(1.0/(1*1000))')
        self.assertEqual(Units.math_units('5-0.1khz'), '5-(1.0/(0.1*1000))')
        self.assertEqual(Units.math_units('5-.1khz'), '5-(1.0/(.1*1000))')
        self.assertEqual(Units.math_units('-1khz'), '-(1.0/(1*1000))')
        self.assertEqual(Units.math_units('-0.1khz'), '-(1.0/(0.1*1000))')

        self.assertAlmostEqual(eval(Units.math_units('2hz')), 0.5)
        self.assertAlmostEqual(eval(Units.math_units('0.002khz')), 0.5)
        self.assertAlmostEqual(eval(Units.math_units('2mhz')), 0.0000005)
        self.assertAlmostEqual(eval(Units.math_units('2ghz')), 0.0000000005)

        self.assertAlmostEqual(Units.to_number('1hz'), 1)
        self.assertAlmostEqual(Units.to_number('10hz'), 0.1)
        self.assertAlmostEqual(Units.to_number('2hz'), 0.5)
        self.assertAlmostEqual(Units.to_number('2khz'), 0.0005)
        self.assertAlmostEqual(Units.to_number('2mhz'), 0.0000005)
        self.assertAlmostEqual(Units.to_number('2ghz'), 0.0000000005)
        self.assertAlmostEqual(Units.to_number('0.002khz'), 0.5)
        self.assertAlmostEqual(Units.to_number('20khz'), 0.00005)
        self.assertAlmostEqual(Units.to_number('20mhz'), 0.00000005)
        self.assertAlmostEqual(Units.to_number('2000khz'), Units.to_number('2mhz'))


class TestSDiff(TestCase):

    def tostr(self, arr):
        """Helper routine for easier compare of array"""
        return ''.join(x if x else ' ' for x in arr)

    def test_basic(self):
        #  mode0
        a = list('aBefghijk')
        b = list('abcdefijm')
        with CaptureStdoutLog() as p:
            print()
            char = SDiff().simple(a, b, 5)
        expect = '''
a       a
B     | b
      > c
      > d
e       e
f       f
g     <
h     <
i       i
j       j
k     | m
'''
        self.assertTextEqual(p.getvalue(), expect)
        self.assertEqual(self.tostr(char), ' |>>  <<  |')
        self.assertEqual(SDiff.count_diff(char), '+2/-2/2')

        # mode1
        a = list('aBefghijk')
        b = list('abcdefijm')
        with CaptureStdoutLog() as p:
            print()
            SDiff().simple(a, b, 5, mode=1)
        expect = '''
a       a
B     <
      > b
      > c
      > d
e       e
f       f
g     <
h     <
i       i
j       j
k     <
      > m
'''
        self.assertTextEqual(p.getvalue(), expect)

        # no match - mode0
        a = list('abcde')
        b = list('ghijk')
        SDiff().simple(a, b)
        self.assertEqual(self.tostr(a), 'abcde')
        self.assertEqual(self.tostr(b), 'ghijk')

        # no match - mode1
        a = list('abcde')
        b = list('ghijk')
        SDiff().simple(a, b, mode=1)
        self.assertEqual(self.tostr(a), 'abcde     ')
        self.assertEqual(self.tostr(b), '     ghijk')

        # first 3 match
        a = list('abcde')
        b = list('abc')
        SDiff().simple(a, b)
        self.assertEqual(self.tostr(a), 'abcde')
        self.assertEqual(self.tostr(b), 'abc  ')
        a = list('abc')
        b = list('abcde')
        SDiff().simple(a, b)
        self.assertEqual(self.tostr(a), 'abc  ')
        self.assertEqual(self.tostr(b), 'abcde')

        # last 3 match
        a = list('abcde')
        b = list('cde')
        SDiff().simple(a, b)
        self.assertEqual(self.tostr(a), 'abcde')
        self.assertEqual(self.tostr(b), '  cde')
        a = list('cde')
        b = list('abcde')
        SDiff().simple(a, b)
        self.assertEqual(self.tostr(a), '  cde')
        self.assertEqual(self.tostr(b), 'abcde')

        # maxdisp - case1
        a = list('aBefghijk')
        b = list('abcdefijm')
        with CaptureStdoutLog() as p:
            print()
            char = SDiff().simple(a, b, 5, maxdisp=4)
        expect = '''
a       a
B     | b
      > c
      > d
'''
        self.assertTextEqual(p.getvalue(), expect)

        with CaptureStdoutLog() as p:
            print()
            char = SDiff().simple(a, b, 0, maxdisp=4, diffonly=True)
        expect = '''
  B
| b
  (none)
> c
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_simple_multiline(self):
        a = '''
LineSame
Line2
LineEnd
'''
        b = '''
LineSame
Line3diff
Line4
LineEnd
'''
        with CaptureStdoutLog() as p:
            SDiff().simple(a.split('\n'), b.split('\n'), 15)
        expect = '''
LineSame          LineSame
Line2           | Line3diff
                > Line4
LineEnd           LineEnd

'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_advanced(self):
        # left case
        a = list('aBcefG1ZzhiJk')
        b = list('aCefg2hik')
        with CaptureStdoutLog() as p:
            print()
            SDiff().simple(a, b, 5)
        expect = '''
a       a
B     | C
c     <
e       e
f       f
G     | g
1     | 2
Z     <
z     <
h       h
i       i
J     <
k       k
'''
        self.assertTextEqual(p.getvalue(), expect)

        # left case - mode1
        a = list('aBcefG1ZzhiJk')
        b = list('aCefg2hik')
        with CaptureStdoutLog() as p:
            print()
            SDiff().simple(a, b, 5, mode=1)
        expect = '''
a       a
B     <
c     <
      > C
e       e
f       f
G     <
1     <
Z     <
z     <
      > g
      > 2
h       h
i       i
J     <
k       k
'''
        self.assertTextEqual(p.getvalue(), expect)

        # right case
        a = list('aCefg2hik')
        b = list('aBcefG1ZzhiJk')
        with CaptureStdoutLog() as p:
            print()
            SDiff().simple(a, b, 5)
        expect = '''
a       a
C     | B
      > c
e       e
f       f
g     | G
2     | 1
      > Z
      > z
h       h
i       i
      > J
k       k
'''
        self.assertTextEqual(p.getvalue(), expect)

        # right case - mode1
        a = list('aCefg2hik')
        b = list('aBcefG1ZzhiJk')
        with CaptureStdoutLog() as p:
            print()
            SDiff().simple(a, b, 5, mode=1)
        expect = '''
a       a
C     <
      > B
      > c
e       e
f       f
g     <
2     <
      > G
      > 1
      > Z
      > z
h       h
i       i
      > J
k       k
'''
        self.assertTextEqual(p.getvalue(), expect)

        # exception on found
        a = list('abcdedfg')
        b = list('dg')
        SDiff().simple(a, b)
        self.assertEqual(self.tostr(a), 'abcdedfg')
        self.assertEqual(self.tostr(b), '     d g')

        # exception on found, mode=1
        a = list('abcdedfg')
        b = list('dg')
        SDiff().simple(a, b, mode=1)
        self.assertEqual(self.tostr(a), 'abcdedfg')
        self.assertEqual(self.tostr(b), '   d   g')

    def test_emptyend(self):
        # change and add
        a = list('abce') + ['']
        b = list('aBe') + ['']
        SDiff().simple(a, b)
        self.assertEqual(self.tostr(a), 'abce ')
        self.assertEqual(self.tostr(b), 'aB e ')

        # change and add, reverse
        a = list('aBe') + ['']
        b = list('abce') + ['']
        SDiff().simple(a, b)
        self.assertEqual(self.tostr(a), 'aB e ')
        self.assertEqual(self.tostr(b), 'abce ')

        # change and add, mode=1
        a = list('abce') + ['']
        b = list('aBe') + ['']
        SDiff().simple(a, b, mode=1)
        self.assertEqual(self.tostr(a), 'abc e ')
        self.assertEqual(self.tostr(b), 'a  Be ')

        # change and add, reverse, mode=1
        a = list('aBe') + ['']
        b = list('abce') + ['']
        SDiff().simple(a, b, mode=1)
        self.assertEqual(self.tostr(a), 'aB  e ')
        self.assertEqual(self.tostr(b), 'a bce ')

    def test_single(self):

        def run(mode):
            # case1
            a = list('abcdefg')
            b = list('a')
            SDiff().simple(a, b, mode=mode)
            self.assertEqual(self.tostr(a), 'abcdefg')
            self.assertEqual(self.tostr(b), 'a      ')

            # case2
            a = list('abcdefg')
            b = list('d')
            SDiff().simple(a, b, mode=mode)
            self.assertEqual(self.tostr(a), 'abcdefg')
            self.assertEqual(self.tostr(b), '   d   ')

            # case3
            a = list('abcdefg')
            b = list('g')
            SDiff().simple(a, b, mode=mode)
            self.assertEqual(self.tostr(a), 'abcdefg')
            self.assertEqual(self.tostr(b), '      g')

            # case4
            a = list('a')
            b = list('abcdefg')
            SDiff().simple(a, b, mode=mode)
            self.assertEqual(self.tostr(a), 'a      ')
            self.assertEqual(self.tostr(b), 'abcdefg')

            # case5
            a = list('d')
            b = list('abcdefg')
            SDiff().simple(a, b, mode=mode)
            self.assertEqual(self.tostr(a), '   d   ')
            self.assertEqual(self.tostr(b), 'abcdefg')

            # case6
            a = list('g')
            b = list('abcdefg')
            SDiff().simple(a, b, mode=mode)
            self.assertEqual(self.tostr(a), '      g')
            self.assertEqual(self.tostr(b), 'abcdefg')

            # case7a - single misalign
            a = list('b')
            b = list('ab')
            SDiff().simple(a, b, mode=mode)
            self.assertEqual(self.tostr(a), ' b')
            self.assertEqual(self.tostr(b), 'ab')

            # case7b - single misalign
            a = list('ab')
            b = list('b')
            SDiff().simple(a, b, mode=mode)
            self.assertEqual(self.tostr(a), 'ab')
            self.assertEqual(self.tostr(b), ' b')

            # case8 - same
            a = list('a')
            b = list('a')
            SDiff().simple(a, b, mode=mode)
            self.assertEqual(self.tostr(a), 'a')
            self.assertEqual(self.tostr(b), 'a')
            return 3

        # mode=0
        self.assertEqual(run(mode=0), 3)
        # mode=1
        self.assertEqual(run(mode=1), 3)

        # case9 - different
        aa = list('z')
        bb = list('a')
        SDiff().simple(aa, bb)
        self.assertEqual(self.tostr(aa), 'z')
        self.assertEqual(self.tostr(bb), 'a')

        # case9 - mode1
        aa = list('z')
        bb = list('a')
        SDiff().simple(aa, bb, mode=1)
        self.assertEqual(self.tostr(aa), 'z ')
        self.assertEqual(self.tostr(bb), ' a')

    def test_keyval(self):
        d1 = {'a': 2, 'b': 2, 'd': 3, 'e': 4, 'g': 5}
        d2 = {'a': 1, 'c': 2, 'd': 4, 'f': 4, 'g': 5}
        with CaptureStdoutLog() as p:
            print()
            SDiff().keyval(d1, d2, col=10)
        expect = '''
a 2        - a 1
b 2        <
           > c 2
d 3        + d 4
e 4        <
           > f 4
g 5          g 5
'''
        self.assertTextEqual(p.getvalue(), expect)

        # diffonly keyval, and check output
        with CaptureStdoutLog() as p:
            print()
            a, c, b = SDiff().keyval(d1, d2, col=10, diffonly=True, indent=3)
        expect = '''
   a 2        - a 1
   b 2        <
              > c 2
   d 3        + d 4
   e 4        <
              > f 4
'''
        self.assertTextEqual(p.getvalue(), expect)
        self.assertEqual(self.tostr(a), 'ab de g')
        self.assertEqual(self.tostr(c), '-<>+<> ')
        self.assertEqual(self.tostr(b), 'a cd fg')

        # no change
        with CaptureStdoutLog() as p:
            print()
            SDiff().keyval(d1, d1, col=10, diffonly=True, nc=True)
        expect = '''
No change
'''
        self.assertTextEqual(p.getvalue(), expect)

        # no change empty
        with CaptureStdoutLog() as p:
            print()
            SDiff().keyval({}, {}, col=10, diffonly=True, nc=True)
        expect = '''
No change
'''
        self.assertTextEqual(p.getvalue(), expect)

        # col=0
        with CaptureStdoutLog() as p:
            print()
            SDiff().keyval(d1, d2, col=0, diffonly=True)
        expect = '''
  a 2
- a 1
  b 2
< (none)
  (none)
> c 2
  d 3
+ d 4
  e 4
< (none)
  (none)
> f 4
'''
        self.assertTextEqual(p.getvalue(), expect)

        # type check
        d1 = {'a': 1, 'b': 2.2, 'c': '2', 'd': 3}
        d2 = {'a': '1', 'b': 2.3, 'c': '2.1', 'd': 3}
        with CaptureStdoutLog() as p:
            print()
            SDiff().keyval(d1, d2, col=10)
        expect = '''
a 1        - a 1
b 2.2      + b 2.3
c 2        - c 2.1
d 3          d 3
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_autowrap(self):
        d1 = {'key1': 'value1 same',
              'key1a': 'value1 same very long long',
              'key2': 'value2 very long long',
              'key3': 'value3 short',
              'key4': 'uniq short',
              'key5': 'uniq very very long long'}
        d2 = {'key1': 'value1 same',
              'key1a': 'value1 same very long long',
              'key2': 'value2a very long long',
              'key3': 'value3a short',
              'key4a': 'uniq short',
              'key5a': 'uniq very very long long'}

        # autowrap
        with CaptureStdoutLog() as p:
            print()
            SDiff().keyval(d1, d2, col=20, diffonly=False, autowrap=True)
        expect = '''
key1 value1 same       key1 value1 same
  key1a value1 same very long long
= key1a value1 same very long long
  key2 value2 very long long
+ key2 value2a very long long
key3 value3 short    + key3 value3a short
key4 uniq short      <
  key5 uniq very very long long
< (none)
                     > key4a uniq short
  (none)
> key5a uniq very very long long
'''
        self.assertTextEqual(p.getvalue(), expect)

        a1 = ['line1',
              'line1a'
              'line2 very very long',
              'linexxxxxxxxxxx',
              'line2 very very long also',
              'lineend']
        a2 = ['line1 diff',
              'line1a'
              'line2 very very long diff',
              'line2 very very long also',
              'line3xxxxxxxxxxx',
              'lineend']
        with CaptureStdoutLog() as p:
            print()
            SDiff().simple(a1, a2, col=13, autowrap=True)
        expect = '''
line1         | line1 diff
  line1aline2 very very long
| line1aline2 very very long diff
  linexxxxxxxxxxx
< (none)
  line2 very very long also
= line2 very very long also
  (none)
> line3xxxxxxxxxxx
lineend         lineend
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_display(self):
        # keyval display off
        with CaptureStdoutLog() as p:
            SDiff().keyval({'a': 1}, {'b': 1}, col=10, disp=False)
        self.assertTextEqual(p.getvalue(), '')

        # simple display off
        with CaptureStdoutLog() as p:
            SDiff().simple(list('abf'), list('aef'), disp=False)
        self.assertTextEqual(p.getvalue(), '')

        # diffonly simple
        a = list('aBefghijk')
        b = list('abcdefijm')
        with CaptureStdoutLog() as p:
            print()
            SDiff().simple(a, b, 5, diffonly=True, indent=3)
        expect = '''
   B     | b
         > c
         > d
   g     <
   h     <
   k     | m
'''
        self.assertTextEqual(p.getvalue(), expect)

    def test_set2key(self):
        d1 = {'a': {1, 7},         # match
              'b': {2, 3, 4},   # 2 match, 1 remove, 1 add
              'c': {6},         # not match
              'd': set(),       # missing
              'e': {1},         # missing
              'f': set(),       # both empty
              'g': {1}}         # key missing
        d2 = {'a': {1, 7},
              'b': {2, 4, 5},
              'c': {5},
              'd': {1},
              'e': set(),
              'f': set(),
              'h': {1}}
        r1, r2 = SDiff.set2key(d1, d2)
        self.assertEqual(r1, {'a': 1,
                              'a-1': 7,
                              'b': 2,
                              'b-1': 3,
                              'b-2': 4,
                              'c': 6,
                              'd': '',
                              'e': 1,
                              'f': '',
                              'g': 1,
                              })
        self.assertEqual(r2, {'a': 1,
                              'a-1': 7,
                              'b': 2,
                              'b-1': 5,
                              'b-2': 4,
                              'c': 5,
                              'd': 1,
                              'e': '',
                              'f': '',
                              'h': 1})

        # must be unmodified
        self.assertEqual(d1, {'a': {1, 7}, 'b': {2, 3, 4}, 'c': {6}, 'd': set(), 'e': {1}, 'f': set(), 'g': {1}})
        self.assertEqual(d2, {'a': {1, 7}, 'b': {2, 4, 5}, 'c': {5}, 'd': {1}, 'e': set(), 'f': set(), 'h': {1}})

        r1, r2 = SDiff.set2key(d1, d2, aligned=True)
        self.assertEqual(r1, {'a#0': 1,
                              'a#1': 7,
                              'b#0': 2,
                              'b#1': 3,
                              'b#2': 4,
                              'c#0': 6,
                              'd#0': '',
                              'e#0': 1,
                              'f#0': '',
                              'g#0': 1})
        self.assertEqual(r2, {'a#0': 1,
                              'a#1': 7,
                              'b#0': 2,
                              'b#1': 5,
                              'b#2': 4,
                              'c#0': 5,
                              'd#0': 1,
                              'e#0': '',
                              'f#0': '',
                              'h#0': 1})

        # reverse
        r3, r4 = SDiff.set2key(d2, d1)
        self.assertEqual(r3, {'a': 1, 'a-1': 7, 'b': 2, 'b-1': 4, 'b-2': 5, 'c': 5, 'd': 1, 'e': '', 'f': '', 'h': 1})
        self.assertEqual(r4, {'a': 1, 'a-1': 7, 'b': 2, 'b-1': 4, 'b-2': 3, 'c': 6, 'd': '', 'e': 1, 'f': '', 'g': 1})

    def test_set2key2(self):
        # full set compare
        d1 = {'a': {2, 3, 6, 7, 9, 11}}
        d2 = {'a': {1, 2, 3, 4, 5, 6, 7, 8}}
        r1, r2 = SDiff.set2key(d1, d2)
        self.assertEqual(r1, {'a': 2,
                              'a-1': 3,
                              'a-2': 6,
                              'a-3': 7,
                              'a-4': 9,
                              'a-5': 11})
        self.assertEqual(r2, {'a': 2,
                              'a-1': 3,
                              'a-2': 6,
                              'a-3': 7,
                              'a-4': 1,
                              'a-5': 4,
                              'a-6': 5,
                              'a-7': 8})

        r3, r4 = SDiff.set2key(d2, d1)
        self.assertEqual(r3, {'a': 1,
                              'a-1': 2,
                              'a-2': 3,
                              'a-3': 4,
                              'a-4': 5,
                              'a-5': 6,
                              'a-6': 7,
                              'a-7': 8})
        self.assertEqual(r4, {'a-1': 2,
                              'a-2': 3,
                              'a-5': 6,
                              'a-6': 7,
                              'a': 9,
                              'a-3': 11})

        r3, r4 = SDiff.set2key(d2, d1, aligned=True)
        self.assertEqual(r3, {'a#0': 1,
                              'a#1': 2,
                              'a#2': 3,
                              'a#3': 4,
                              'a#4': 5,
                              'a#5': 6,
                              'a#6': 7,
                              'a#7': 8})
        self.assertEqual(r4, {'a#1': 2,
                              'a#2': 3,
                              'a#5': 6,
                              'a#6': 7,
                              'a#0': 9,
                              'a#3': 11})

    def test_get_num(self):
        self.assertEqual(SDiff.get_num('21 tids'), 21)
        self.assertEqual(SDiff.get_num('tids'), 'tids')
        self.assertEqual(SDiff.get_num(21), 21)
        self.assertEqual(SDiff.get_num(''), '')

    def test_is_reorder(self):
        self.assertEqual(SDiff().is_reorder(list('abcdef'), list('abcdef')), [])
        self.assertEqual(SDiff().is_reorder(list('addh'), list('acdfgh')), ['d'])
        self.assertEqual(SDiff().is_reorder(list('abcdef'), list('acdfgh')), [])
        self.assertEqual(SDiff().is_reorder(list('acdfgh'), list('abcdef')), [])

        self.assertEqual(SDiff().is_reorder(list('abcdef'), list('c')), [])
        self.assertEqual(SDiff().is_reorder(list('c'), list('abcdef')), [])
        self.assertEqual(SDiff().is_reorder(list('abcdef'), list('ceg')), [])

        self.assertEqual(SDiff().is_reorder(list('abcdef'), list('abfcde')), ['f'])
        self.assertEqual(SDiff().is_reorder(list('abfcde'), list('abcdef')), ['c', 'd', 'e'])

        self.assertEqual(SDiff().is_reorder(list('abcdef'), list('fabcde')), ['f'])
        self.assertEqual(SDiff().is_reorder(list('abcdef'), list('dc')), ['d'])

        # Make sure input is not modified
        a1 = list('abccdef')
        a2 = list('ec')
        with CaptureStdoutLog() as p:
            print()
            result = SDiff().is_reorder(a1, a2, disp=True)
        self.assertEqual(result, ['e', 'c'])
        self.assertEqual(a1, list('abccdef'))
        self.assertEqual(a2, list('ec'))
        expect = '''
   a          <
   b          <
              R e
   c            c
   c          R
   d          <
   e          <
   f          <
'''
        self.assertTextEqual(p.getvalue(), expect)


class TestOtpl(TestCase):

    def test_text_readline(self):
        # case 1
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''
valid line

    # comment
another line   # comment
a,"#",c
a,"#",c   # comment
a {} b
a {} b    # c
a "{}" b    # c
;
''', newfile=True)
            self.assertEqual(list(OtplFile(f1.get_name()).text_readline()),
                             [(2, 'valid line'),
                              (5, 'another line'),
                              (6, 'a,"#",c'),
                              (7, 'a,"#",c'),
                              (8, 'a {} b'),
                              (9, 'a { } b'),
                              (10, 'a "{}" b'),
                              (11, ';'),
                              ])

    def test_otpl_bline_single(self):
        f1 = OtplFile('/notfound')

        # normal line, no brackets and no comments
        def otpl_bline(line):
            return f1._otpl_bline(line, [''], 1, 1)
        self.assertEqual(list(otpl_bline('some')), ['some'])
        self.assertEqual(list(otpl_bline('')), [])
        self.assertEqual(list(otpl_bline('some "{}#" and \'{}"#\'')), ['some "{}#" and \'{}"#\''])
        self.assertEqual(list(otpl_bline('some "li" \'ne\'')), ['some "li" \'ne\''])
        self.assertEqual(list(otpl_bline('some = "{spec}";')), ['some = "{spec}";'])
        # TPIE case
        self.assertEqual(list(otpl_bline('some = {spec};')), ['some = "{spec}";'])
        self.assertEqual(list(otpl_bline('some = {spec}')), ['some = "{spec}"'])
        self.assertEqual(list(otpl_bline('so{ }me = {spec}')), ['so', '{', ' ', '}', 'me = ', '{', 'spec', '}'])
        # with comment
        self.assertEqual(list(otpl_bline('some "li" # {')), ['some "li"'])
        # with comment inside
        self.assertEqual(list(otpl_bline('some "l#i" # ne')), ['some "l#i"'])
        # with comment inside
        self.assertEqual(list(otpl_bline("some 'l#i{}' # ne")), ["some 'l#i{}'"])
        # starts with comment
        self.assertEqual(list(otpl_bline('#some "l#i" # ne')), [])
        # with bracket
        self.assertEqual(list(otpl_bline('some {"l#i"} # ne')), ['some ', '{', '"l#i"', '}'])
        # with bracket inside quote
        self.assertEqual(list(otpl_bline('some {"{l#i}"} # {')), ['some ', '{', '"{l#i}"', '}'])
        # with bracket inside quote
        self.assertEqual(list(otpl_bline('some " {"a" }#" # {')), ['some " {"a" }#"'])
        # no quotes
        self.assertEqual(list(otpl_bline('{{{a}{b}}')),
                         ['{', '{', '{', 'a', '}', '{', 'b', '}', '}'])
        self.assertEqual(list(otpl_bline('} result')), ['}', 'result'])
        self.assertEqual(list(otpl_bline('result; {')), ['result;', ' ', '{'])
        self.assertEqual(list(otpl_bline('{')), ['{'])
        # semicolon
        self.assertEqual(list(otpl_bline('a; { b; a="a{b};"; c; }')),
                         ['a;', ' ', '{', ' b;', ' a="a{b};";', ' c;', ' ', '}'])
        self.assertEqual(list(otpl_bline('a;; a=d{{}}')),
                         ['a;', ' a=d', '{', '{', '}', '}'])
        #  bugs
        self.assertEqual(list(otpl_bline('fai_l = CLK_Rules.LJ("","","VDAC!SetVDACFrom");')),
                         ['fai_l = CLK_Rules.LJ("","","VDAC!SetVDACFrom");'])
        self.assertEqual(list(otpl_bline("fai_l = CLK_Rules.LJ('','','VDAC!SetVDACFrom');")),
                         ["fai_l = CLK_Rules.LJ('','','VDAC!SetVDACFrom');"])

        # make sure it is the same
        input = '{ text {}{} "{end#a{}}" {}{} "all" \'all\' "a#a" "#" "{" }'
        result = list(otpl_bline(input))
        self.assertEqual(''.join(result), input)
        self.assertEqual(len(result), 13)

    def test_otpl_bline_multi(self):
        f1 = OtplFile('/notfound')

        # simple case
        alines = '''
a
= var;
'''.split('\n')
        lno = 2
        self.assertEqual(list(f1._otpl_bline(alines[lno - 1], alines, lno, len(alines))),
                         ['a= var;'])
        self.assertEqual(alines, ['', 'a', '', ''])

        # multiple lines
        alines = '''
a

=
var
;
b;
'''.split('\n')
        lno = 2
        self.assertEqual(list(f1._otpl_bline(alines[lno - 1], alines, lno, len(alines))),
                         ['a=var;'])
        self.assertEqual(alines, ['', 'a', '', '', '', '', 'b;', ''])

        # bracket {
        alines = '''
a

=
var
{
b;
'''.split('\n')
        lno = 2
        self.assertEqual(list(f1._otpl_bline(alines[lno - 1], alines, lno, len(alines))),
                         ['a=var'])
        self.assertEqual(alines, ['', 'a', '', '', '', '{', 'b;', ''])

        # bracket }
        alines = '''
a

=
var
}
b;
'''.split('\n')
        lno = 2
        self.assertEqual(list(f1._otpl_bline(alines[lno - 1], alines, lno, len(alines))),
                         ['a=var'])
        self.assertEqual(alines, ['', 'a', '', '', '', '}', 'b;', ''])

        # commas
        alines = '''
a,
b,
c,
d
} # end
'''.split('\n')
        lno = 2
        self.assertEqual(list(f1._otpl_bline(alines[lno - 1], alines, lno, len(alines))),
                         ['a,b,c,d'])
        self.assertEqual(alines, ['', 'a,', '', '', '', '} # end', ''])

        with self.assertRaisesRegex(Exception, 'max loop'):
            list(f1._otpl_bline(alines[lno - 1], alines, lno, len(alines), maxloop=1))

    def test_bug_quoted(self):
        # Vikram's Torch ticket 74505, Dec 25
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch(r'''
        String;
        String SC_PPR_LUT_CONTENT = "{\r\n  \"LutTimeStamp\": \"20210421T010203004\",\r\n  \"PreEmphasisTimeOut\": 10\r\n}";
        String \
        a = \
        "{\"a\": \"1\"}";
''', newfile=True)
            expect = r'''String;
String SC_PPR_LUT_CONTENT = "{\r\n  \"LutTimeStamp\": \"20210421T010203004\",\r\n  \"PreEmphasisTimeOut\": 10\r\n}";
String a = "{\"a\": \"1\"}";'''
            self.assertTextEqual('\n'.join(x[1] for x in OtplFile(f1.get_name()).readline()), expect)

    def test_comment(self):
        # Return comment
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''Version1;

t"#"est {
   text; text2; # EOL com
   # PPR {}
   # FSM:#
} # comment { ZZZ }
# com2
param = value;
''', newfile=True)
            result = list(OtplFile(f1.get_name()).readline(comments=True))
            expect = [(1, 'Version1;'),
                      (3, 't"#"est'),
                      (3, '{'),
                      (4, 'text;'),
                      (4, 'text2;'),
                      (5, '# PPR {}'),
                      (6, '# FSM:#'),
                      (7, '}'),
                      (8, '# com2'),
                      (9, 'param = value;')]
            self.assertEqual(result, expect)

            result = list(OtplFile(f1.get_name()).with_eol_comment())
            pprint(result)
            expect = [(1, 'Version1;'),
                      (2, ''),
                      (3, 't"#"est'),
                      (3, '{'),
                      (4, 'text;'),
                      (4, 'text2;    # EOL com'),
                      (5, '# PPR {}'),
                      (6, '# FSM:#'),
                      (7, '}    # comment { ZZZ }'),
                      (8, '# com2'),
                      (9, 'param = value;'),
                      (10, '')]

            self.assertEqual(result, expect)

    def test_with_eol_comment(self):
        # Return comment
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''Version1;
\tDutflow ABC {   # com1
\t# com2
# com3
{{ Te\tst A }}  # com4
val = a,
b,c
''', newfile=True)

            result = list(OtplFile(f1.get_name()).with_eol_comment())
            pprint(result)
            expect = [(1, 'Version1;'),
                      (2, 'Dutflow ABC'),
                      (2, '{    # com1'),
                      (3, '# com2'),
                      (4, '# com3'),
                      (5, '{'),
                      (5, '{'),
                      (5, 'Te st A'),
                      (5, '}'),
                      (5, '}'),
                      (6, 'val = a,b,c'),
                      (7, ''),
                      (8, '')]

            self.assertEqual(result, expect)

    def test_with_eol_comment2(self):
        # Using textequal
        # case1: counter with comment
        # case2: normal param with comment and squashed
        # case3: end bracket at end of line
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''Version1;

Counters {
   a,   # abc
   b,
   c
}
param(a, # comnt
b,  # comnt2_lost
c);  # comnt3_lost
Result -1 {
 Property PassFail = "Fail"; SetBin SoftBins.b90; Return -1;}
''', newfile=True)

            result = list(OtplFile(f1.get_name()).with_eol_comment())
            text = '\n'.join(x[1] for x in result)
            expect = '''Version1;

Counters
{
a,    # abc
b,
c
}
param(a,b,c);    # comnt


Result -1
{
Property PassFail = "Fail";
SetBin SoftBins.b90;
Return -1;
}
'''
            self.assertTextEqual(text, expect)

    def test_emptyline(self):
        # Return emptyline
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''Version1;

t"#"est {
   text; text2; # EOL com
   # PPR {}

   # FSM:#
} # comment { ZZZ }
# com2
param = value;
''', newfile=True)
            result = list(OtplFile(f1.get_name()).readline(emptyline=True))
            expect = [(1, 'Version1;'),
                      (2, ''),
                      (3, 't"#"est'),
                      (3, '{'),
                      (4, 'text;'),
                      (4, 'text2;'),
                      (6, ''),
                      (8, '}'),
                      (10, 'param = value;'),
                      (11, '')]
            self.assertEqual(result, expect)

    @with_(TempDir, chdir=True, delete=True)
    def test_reformat(self):
        text = '''Version 1.0;
   Test method A {    # hi

# comment
    Result { SetBin A; Setbin B; }
}
'''
        ff = File('a.mtpl').touch(text, mkdir=True)
        OtplFile('a.mtpl').reformat()
        expect = '''Version 1.0;
Test method A
{    # hi

\t# comment
\tResult
\t{
\t\tSetBin A;
\t\tSetbin B;
\t}
}
'''
        self.assertTextEqual(ff.read(), expect)

        # run again
        OtplFile('a.mtpl').reformat()
        self.assertTextEqual(ff.read(), expect)

        # no eof newline
        text = '''Version 1.0;

   Test method A {    # hi
# comment
       param x;  # com1
    }  # com2'''
        ff = File('a.mtpl').touch(text, mkdir=True, newfile=True)
        OtplFile('a.mtpl').reformat()
        expect = '''Version 1.0;

Test method A
{    # hi
\t# comment
\tparam x;    # com1
}    # com2
'''
        self.assertTextEqual(ff.read(), expect)

    def test_bracket_end(self):
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''
Result -1 {
 Property PassFail = "Fail"; SetBin SoftBins.b90; Return -1;}
Result -1 {
 Property PassFail = "Fail"; }
Result -1 { Property PassFail = "Fail"; }
Result -1 { Property PassFail = "Fail"; ab1; }

Counters {
 ab,
 de, # a
 fg
}
''', newfile=True)
            expect = '''
Result -1
{
Property PassFail = "Fail";
SetBin SoftBins.b90;
Return -1;
}
Result -1
{
Property PassFail = "Fail";
}
Result -1
{
Property PassFail = "Fail";
}
Result -1
{
Property PassFail = "Fail";
ab1;
}
Counters
{
ab,
de,
fg
}
'''
            self.assertTextEqual('\n'.join(x[1] for x in OtplFile(f1.get_name()).readline()), expect)

    def test_basic(self):
        # case 1
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''
} Test abc
  {
one
  } # end {
Test ghi {{

two}}
# Test a {
#  Pat;
# }
Test jkl
{  { {
three
}
} }
a {
} b {
}{}
{c}
''', newfile=True)
            expect = '''}
Test abc
{
one
}
Test ghi
{
{
two
}
}
Test jkl
{
{
{
three
}
}
}
a
{
}
b
{
}
{
}
{
c
}'''.split('\n')
            self.assertEqual(list(x[1] for x in OtplFile(f1.get_name()).readline()), expect)

            # case2
            f1 = File(join(tdir, 'plain.txt')).touch('''
{{a}{b}{c}}{"d#{}"} # {e}
''', newfile=True)
            expect = '''{
{
a
}
{
b
}
{
c
}
}
{
"d#{}"
}'''.split('\n')
            self.assertEqual(list(x[1] for x in OtplFile(f1.get_name()).readline()), expect)
            self.assertEqual(set(x[0] for x in OtplFile(f1.get_name()).readline()), {2})

            # case 3 - line number
            f1 = File(join(tdir, 'plain.txt')).touch('''Version1;


t"#"est {
   text
} # comment { ZZZ }
# com2 {
# {
{{a}{b}\t\t{c}}
a}{b#} {ZZZ}
''', newfile=True)
            expect = [(1, 'Version1;'),
                      (4, 't"#"est'),
                      (4, '{'),
                      (5, 'text'),
                      (6, '}'),
                      (9, '{'),
                      (9, '{'),
                      (9, 'a'),
                      (9, '}'),
                      (9, '{'),
                      (9, 'b'),
                      (9, '}'),
                      (9, '{'),
                      (9, 'c'),
                      (9, '}'),
                      (9, '}'),
                      (10, 'a'),
                      (10, '}'),
                      (10, '{'),
                      (10, 'b')
                      ]
            self.assertEqual(list(OtplFile(f1.get_name()).readline()), expect)

            # case4 - real scenario
            f1 = File(join(tdir, 'plain.txt')).touch('''Version 1.0;
ConcurrentFlow PRL4_SubFlow # [Parallel]
{
\tConcurrentFlowItem1;
\tConcurrentFlowItem2;

        ConcurrentResultTable
        {
            ifpm_modifygroups = "bt!ps_clk!{SAPS_F5_FREQ}"}
            patlist_to_modify = "[PATTERNS:tgl_pre_*_0k3c_Mpth_*_boot_ol]# [PATTERNS]"}
        }
} # end of concurrent
} DutFlow {
# } ignore
# ignore {
# {
# }
realline
# com3 {}
''', newfile=True)
            expect = '''Version 1.0;
ConcurrentFlow PRL4_SubFlow
{
ConcurrentFlowItem1;
ConcurrentFlowItem2;
ConcurrentResultTable
{
ifpm_modifygroups = "bt!ps_clk!{SAPS_F5_FREQ}"
}
patlist_to_modify = "[PATTERNS:tgl_pre_*_0k3c_Mpth_*_boot_ol]# [PATTERNS]"
}
}
}
}
DutFlow
{
realline'''
            self.assertTextEqual('\n'.join(x[1] for x in OtplFile(f1.get_name()).readline()), expect)

    def test_semicolon(self):
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''Version 1.0;
ConcurrentFlow PRL4_SubFlow # [Parallel]
{
ConcurrentFlowItem1

;
ConcurrentFlowItem2
    ; Moreline;

        ConcurrentResultTable

        {
            EndVoltageLimits  = toString(
            Specs.GT_HIGH_SEARCH_F4
            );
            ifpm_modifygroups =
            "bt!ps_clk;{SAPS_F5_FREQ}"
            ;
            result = 1; result = 2;
}
}
Counters
{
        n90940161_fail,
        n90940162_fail,
        n90990001_fail
}
''', newfile=True)

            expect = '''Version 1.0;
ConcurrentFlow PRL4_SubFlow
{
ConcurrentFlowItem1;
ConcurrentFlowItem2;
Moreline;
ConcurrentResultTable
{
EndVoltageLimits  = toString(Specs.GT_HIGH_SEARCH_F4);
ifpm_modifygroups ="bt!ps_clk;{SAPS_F5_FREQ}";
result = 1;
result = 2;
}
}
Counters
{
n90940161_fail,
n90940162_fail,
n90990001_fail
}'''
            self.assertTextEqual('\n'.join(x[1] for x in OtplFile(f1.get_name()).readline()), expect)

    def test_usertodo(self):
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''Version 1.0;
Test iCFuncTest CCXfloating {
        patlist = "shops_H_list"; #USER TODO: define value blah; #USER TODO: define value
        base_number = 2161;
}
''', newfile=True)

            expect = '''
Version 1.0;
Test iCFuncTest CCXfloating
{
patlist = "shops_H_list";
base_number = 2161;
}
'''
            self.assertTextEqual('\n'.join(x[1] for x in OtplFile(f1.get_name()).readline(comments=True)),
                                 expect)

    def test_oneline(self):
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''Version 1.0;
ConcurrentFlow PRL4_SubFlow # [Parallel]
{ ConcurrentFlowItem1; ConcurrentFlowItem2  ; Moreline; ConcurrentResultTable { ifpm_modifygroups = "bt!ps_clk;{SAPS_F5_FREQ}"; result = 1; result = 2; } }
''', newfile=True)

            expect = '''Version 1.0;
ConcurrentFlow PRL4_SubFlow
{
ConcurrentFlowItem1;
ConcurrentFlowItem2  ;
Moreline;
ConcurrentResultTable
{
ifpm_modifygroups = "bt!ps_clk;{SAPS_F5_FREQ}";
result = 1;
result = 2;
}
}'''
            self.assertTextEqual('\n'.join(x[1] for x in OtplFile(f1.get_name()).readline()), expect)

    def test_multilinechar(self):
        with TempDir(name=True) as tdir:
            backslash = '\\'
            f1 = File(join(tdir, 'plain.txt')).touch(f"""
Test iCSimpleScoreboardTest CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST
{{
        fail_process_level = CLK_Rules.LJ( {backslash}
        "", {backslash}
        "","VDAC!SetVDACFromHardwareLevels");    # more comment {backslash}
        level = "BASE::DDR_univ_lvl_nom_{backslash}lvl";
}}
""")
            expect = """Test iCSimpleScoreboardTest CCF_XXXXX_FUNC_E_END_080812_X_F1_0800_RETENTION_ALL_TEST
{
fail_process_level = CLK_Rules.LJ( "", "","VDAC!SetVDACFromHardwareLevels");
level = "BASE::DDR_univ_lvl_nom_\\lvl";
}"""
            self.assertTextEqual('\n'.join(x[1] for x in OtplFile(f1.get_name()).readline()), expect)

    def test_optimizations(self):
        # optimization tests
        OtplFile._ADV_CNT[0] = 0
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'a.mtpl')).touch('''Version 1.0;
ProgramStyle = Modular;   #KEEP#
a = 5;   #USER TODO: define value
ab {
 good;
} # end
de {
  end;  }
''', newfile=True)
            expect = '''Version 1.0;
ProgramStyle = Modular;
a = 5;
ab
{
good;
}
de
{
end;
}'''
            self.assertTextEqual('\n'.join(x[1] for x in OtplFile(f1.get_name()).readline()), expect)
            self.assertEqual(OtplFile._ADV_CNT[0], 1)   # This is #KEEP# only

            # try plist
            f1.rename('a.plist')
            OtplFile._ADV_CNT[0] = 0
            self.assertTextEqual('\n'.join(x[1] for x in OtplFile(f1.get_name()).readline()), expect)
            self.assertEqual(OtplFile._ADV_CNT[0], 0)

            # should not optimize these
            OtplFile._ADV_CNT[0] = 0
            f1 = File(join(tdir, 'b.mtpl')).touch('''Version 1.0;
ProgramStyle = Modular;
bracket_open; # {
bracket_close; # }
bracket_open1, { a; } {  #USER TODO: define value
bracket_open2, { b; }
}} # end
de {
last; # }
''', newfile=True)
            expect = '''Version 1.0;
ProgramStyle = Modular;
bracket_open;
bracket_close;
bracket_open1,
{
a;
}
{
bracket_open2,
{
b;
}
}
}
de
{
last;'''
            self.assertTextEqual('\n'.join(x[1] for x in OtplFile(f1.get_name()).readline()), expect)
            self.assertEqual(OtplFile._ADV_CNT[0], 6)   # This is #KEEP# only

    def test_nobline(self):
        with TempDir(name=True) as tdir:
            f1 = File(join(tdir, 'plain.txt')).touch('''Version 1.0;
ProgramStyle = Modular;
Counters
{
        n90940161_fail_CTRL_X_BMFC_K_SRHIAF1_X_X_X_X_POP_0,
        n90990001_fail_FAIL_DPS_ALARM
} # End of Test Counter Definition
Test iCBinMatrixFlowControlTest CTRL_X_BMFC_K_END_X_X_X_X_POP
{
        active_bingroup_uservar = "BOMGroups.CLASS_RPL8161S";
        active_test_domain = "default_domain";
        bin_matrix_file_path = "./BMFC.xml";
        dff_ssid = TPI_FLOWCTRL_Rules.CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP_dff_ssid("NA","NA","NA","NA","NA","NA","NA","PKG");
        flowid_gsds_for_domain = TPI_FLOWCTRL_Rules.CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP_flowid_gsds_for_domain("G.U.S.DFFCHECK_IAFLWD","G.U.S.DFFCHECK_IAFLWD");
        loop_mode = "VLOOP";
        operating_mode = TPI_FLOWCTRL_Rules.CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP_operating_mode("POP");
        port_to_test_value = TPI_FLOWCTRL_Rules.CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP_port_to_test_value("2:2,4:4,3:3,1:1","2:2,4:4,3:3,1:1","2:2,4:4,3:3,1:1","2:2,4:4,3:3,1:1","2:2,4:4,3:3,1:1");
        set_dff_olb_token = TPI_FLOWCTRL_Rules.CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP_set_dff_olb_token("NA","NA","NA","NA","NA","NA","NA","ENABLED");
        single_recovery_olb_optype = TPI_FLOWCTRL_Rules.CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP_single_recovery_olb_optype("","","","","","","","PBIC_DAB");
        single_recovery_variable = TPI_FLOWCTRL_Rules.CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP_single_recovery_variable("","","","","","","","G.U.S.DFFCHECK_IAFLWD");
}
DUTFlow TPI_FLOWCTRL_CHKIAF1
{
        DUTFlowItem CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP
        {
                Result -2
                {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90999901_fail_FAIL_DPS_ALARM;
                        Return -2;
                }
                Result -1
                {
                        Property PassFail = "Fail";
                        SetBin SoftBins.b90989801_fail_FAIL_SYSTEM_SOFTWARE;
                        Return -1;
                }
                Result 0
                {
                        Property PassFail = "Fail";
                        IncrementCounters TPI_FLOWCTRL::n90940168_fail_CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP_0;
                        SetBin SoftBins.b90949425_fail_TPI_FLOWCTRL_CTRL_X_BMFC_K_CHKIAF1_X_X_X_X_POP_SHARED_BIN;
                        Return 0;
                }
                Result 1
                {
                        Property PassFail = "Pass";
                        Return 1;
                }
        }
}
''', newfile=True)
            OtplFile._ADV_CNT[0] = 0
            self.assertEqual(len(list(OtplFile(f1.get_name()).readline())), 51)
            self.assertEqual(OtplFile._ADV_CNT[0], 0)

    def test_get_block_comment(self):
        with TempDir(name=True, chdir=True):
            text = '''
DUTFlow AA
# com1
{
    line1;
    # com2
    # com3
    { line2 };
}
            '''
            File('a').touch(text)

            # simple case - one match block and name
            expect = '''DUTFlow AA
# com1
{
    line1;
    # com2
    # com3
    { line2 };
}
'''
            self.assertTextEqual(''.join(OtplFile('a').get_block('DUTFlow', 'AA')), expect)

    def test_get_block_dutflow(self):
        with TempDir(name=True, chdir=True):
            text = '''
DUTFlow AA
{
    DUTFlowItem BB BB
    {
       line1;
    }
}
DUTFlow BB
{
    DUTFlowItem AA AA
    {
       line2;
    }
}
            '''
            File('a').touch(text)

            # simple case - one match block and name
            expect = '''DUTFlow AA
{
    DUTFlowItem BB BB
    {
       line1;
    }
}
'''
            ofile = OtplFile('a')
            self.assertTextEqual(''.join(ofile.get_block('DUTFlow', 'AA')), expect)

    def test_readline_list(self):
        text = '''Test meth A { line; } # commment
DUTFlow A {
   DUTFlowItem B { }
}
# last line
'''
        result = OtplFile().readline(text.split('\n'))
        self.assertEqual(list(result), [(1, 'Test meth A'),
                                        (1, '{'),
                                        (1, 'line;'),
                                        (1, '}'),
                                        (2, 'DUTFlow A'),
                                        (2, '{'),
                                        (3, 'DUTFlowItem B'),
                                        (3, '{'),
                                        (3, '}'),
                                        (4, '}')])

    def test_get_block_rule(self):
        with TempDir(name=True, chdir=True):
            text = '''
SelectorRuleCollection  YBS_UPSS_YXX_Rules
{
        SelectorRule aa(CLASSHOTHVM, DEFAULT)

        {
                CLASSHOTHVM => contains('{a}');
                DEFAULT;
        }

        SelectorRule bb(QRE, CLASSHOTHVM, DEFAULT) {
                CLASSHOTHVM => contains('{a}');
        }
}
            '''
            File('a').touch(text)

            # simple case - one match block and name
            expect = '''        SelectorRule aa(CLASSHOTHVM, DEFAULT)

        {
                CLASSHOTHVM => contains('{a}');
                DEFAULT;
        }
'''
            ofile = OtplFile('a')
            self.assertTextEqual(''.join(ofile.get_block('SelectorRule', 'aa')), expect)

    def test_raw(self):
        # make sure no line endings is lost
        orig = f'{UT_DIR_REPO}/misc_files/EnvironmentFile.unix.txt'

        alltext = ''.join(OtplFile(orig).raw())
        with TempDir(name=True, chdir=True):
            File(f'a.unix.txt').touch().rewrite(alltext, 'a')
            self.assertGoldEqual('a.unix.txt', f'{UT_DIR_REPO}/misc_files/EnvironmentFile.unix.txt.gold')

        alltext = OtplFile(orig).raw(islist=False)
        with TempDir(name=True, chdir=True):
            File(f'a.unix.txt').touch().rewrite(alltext, 'a')
            self.assertGoldEqual('a.unix.txt', f'{UT_DIR_REPO}/misc_files/EnvironmentFile.unix.txt.gold')

    def test_get_block(self):
        with TempDir(name=True, chdir=True):
            text = '''
DUTFlow AA
{
    line1;
    { line2 };
}
DUTFlow AB { line1b; { line2b; }}
Resource
{
    lineonly;
    # com
}
Test blah AC
{
    line3;
}

            '''
            File('a').touch(text)

            # simple case - one match block and name
            expect = '''DUTFlow AA
{
    line1;
    { line2 };
}
'''
            ofile = OtplFile('a')
            self.assertTextEqual(''.join(ofile.get_block('DUTFlow', 'AA')), expect)
            self.assertTextEqual(''.join(ofile.get_block(name='AA')), expect)
            self.assertTextEqual(''.join(ofile.get_block('DUTFlow', 'AB')),
                                 'DUTFlow AB { line1b; { line2b; }}\n')
            expect = '''DUTFlow AB
{
line1b;
{
line2b;
}
}'''
            self.assertTextEqual('\n'.join(ofile.get_block('DUTFlow', 'AB', parsed=True)),
                                 expect)

            # no match
            self.assertTextEqual(''.join(ofile.get_block('DUTFlow', 'A')), '')
            self.assertTextEqual(''.join(ofile.get_block('DUTFlowx', 'AA')), '')
            self.assertTextEqual(''.join(ofile.get_block('DUTFlowx')), '')

            # multiple match - block name only
            expect = '''DUTFlow AA
{
    line1;
    { line2 };
}
'''
            self.assertTextEqual(''.join(OtplFile('a').get_block('DUTFlow')),
                                 expect)

            # one match - block name only
            expect = '''Resource
{
    lineonly;
    # com
}
'''
            self.assertTextEqual(''.join(OtplFile('a').get_block('Resource')),
                                 expect)
            expect = '''Resource
{
lineonly;
}'''
            self.assertTextEqual('\n'.join(OtplFile('a').get_block('Resource', parsed=True)),
                                 expect)

            # simple case - testinstance
            expect = '''Test blah AC
{
    line3;
}
'''
            self.assertTextEqual(''.join(OtplFile('a').get_block('Test', 'AC', 2)), expect)
            self.assertTextEqual(''.join(OtplFile('a').get_block(name='AC')), expect)

    def benchmark(self):
        # otpl reader benchmark
        # 12/30/21:
        # text_readline() - non-otpl
        # Non-otpl: Total lines: 802369, 0.638 Secs
        # Non-otpl: Total lines: 802369, 0.625 Secs
        # Non-otpl: Total lines: 802369, 0.578 Secs
        #
        # readline() - otpl
        # Otpl: Total lines: 802666, _ADV_CNT=[547], 1.427 Secs
        # Otpl: Total lines: 802666, _ADV_CNT=[547], 1.444 Secs
        # Otpl: Total lines: 802666, _ADV_CNT=[547], 1.442 Secs

        from tp.testprogram import TestProgram
        from gadget.gizmo import Elapsed

        tp = TestProgram(f'{UT_DIR_REPO}/RPLS8P5A0H10P60S051/POR_TP/RPL_1ST_SILICON/EnvironmentFile.env')
        print()
        print("text_readline() - non-otpl")
        for _ in range(3):
            sw = Elapsed()
            total = 0
            for ff in tp.get_all_mtpl_files():
                total += len(list(OtplFile(ff).text_readline()))
            print(f"Non-otpl: Total lines: {total}, {sw}")

        print()
        print("readline() - otpl")
        for _ in range(3):
            sw = Elapsed()
            total = 0
            OtplFile._ADV_CNT[0] = 0
            for ff in tp.get_all_mtpl_files():
                total += len(list(OtplFile(ff).readline()))
            print(f"Otpl: Total lines: {total}, _ADV_CNT={OtplFile._ADV_CNT}, {sw}")


class TestRead(TestCase):

    @with_(TempDir, chdir=True)
    def test_jsonread_error(self):
        File('a.json').touch("{'}")

        # raise exception case
        with self.assertRaisesRegex(ErrorInput, 'Error on'):
            data = JsonRead('a.json').load()

        # no raise case
        data = JsonRead('a.json', error_out=False).load()
        self.assertEqual(data, {})

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_jsonread_special(self):
        # This has the wierd first line and various comments
        data = JsonRead(f'{UT_DIR}/special_files/FUN_UTP_setpoints.json').load()
        self.assertEqual(len(list(keys_atlevel(data, 1))), 205)

    @with_(TempDir, chdir=True)
    def test_jsonread2(self):
        # with block comments and wierd comments
        File('a.json').touch('''
{
  "Registers": [
    {
      "r1": [
        "SOCS0_MAINBURN" //OPENFUSEBURN // Change the //naming if needed
      ],
      "r2": [
        "SOCS0_MAINBURN", //OPENFUSEBURN - Change // the naming if needed
      ],
      // "LabelName2": "FUSE_DATA_//STREAM_WR",
      "LabelName": "FUSE_DATA_//STREAM_WR",
      "LabelOffset": 0,
      /* "LabelOffset1": 0, */
    },
    /*
    {
      "RegisterName": [
        "SOCS0_EFUSE1",
      ],
      "LabelOffset": 1
    },
    */
    {
      "RegisterName": [
        "SOCS0_EFUSE",
        /* "SOCS1_EFUSE",
        */
      ],
      "LabelOffset": 0
    },

  ],
}
''')
        data = JsonRead('a.json').load()
        expect = '''
{'Registers': [{'LabelName': 'FUSE_DATA_//STREAM_WR',
                'LabelOffset': 0,
                'r1': ['SOCS0_MAINBURN'],
                'r2': ['SOCS0_MAINBURN']},
               {'LabelOffset': 0, 'RegisterName': ['SOCS0_EFUSE']}]}
'''
        self.assertTextEqual(pformat(data), expect)

        # too many comments in the line - coverage
        File('a.json').touch('''
{
  "Registers": "r1"   // 1 // 2 // 3 // 4 // 5 // 6 // 7 // 8 // 9 // 10 // 11 // 12
}
''', newfile=True)
        with self.assertRaisesRegex(ErrorInput, 'json read exception'):
            JsonRead('a.json').load()

    @with_(TempDir, chdir=True)
    def test_jsonread(self):
        File('a.json').touch('''
{
  "Registers": [
    {
      "r1": [
        "SOCS0_MAINBURN" //OPENFUSEBURN - Change the naming if needed
      ],
      "r2": [
        "SOCS0_MAINBURN", //OPENFUSEBURN - Change the naming if needed
      ],
      "LabelName": "FUSE_DATA_//STREAM_WR",
      "LabelOffset": 0,
    },
    {
      "RegisterName": [
        "SOCS0_EFUSE",
      ],
      "LabelOffset": 0
    },

  ],
}
''')
        data = JsonRead('a.json').load()
        expect = '''
{'Registers': [{'LabelName': 'FUSE_DATA_//STREAM_WR',
                'LabelOffset': 0,
                'r1': ['SOCS0_MAINBURN'],
                'r2': ['SOCS0_MAINBURN']},
               {'LabelOffset': 0, 'RegisterName': ['SOCS0_EFUSE']}]}
'''
        self.assertTextEqual(pformat(data), expect)

        # fail case
        File('a.json').touch('''
{
  "Registers": [
    {
      "r1": [
''', newfile=True)
        with self.assertRaisesRegex(ErrorInput, 'json read exception'):
            JsonRead('a.json').load()

        # pass case asis
        File('a.json').touch('''
{
  "Registers": []
}
''', newfile=True)
        data = JsonRead('a.json').load()
        self.assertEqual(data, {'Registers': []})

    @with_(TempDir, chdir=True)
    def test_xmlread(self):
        # success case
        File('a.xml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="AAA_drv_gdie_GMD_MB3P_hdmt2class_class_s68g1.plist" />
    <PListFile name="clk_gcd_class_s68g1.plist" />
  </PList>
</HdmtReferenceFile>
''')
        tree = XmlRead('a.xml').load()
        root = tree.getroot()
        plists = []
        for plist in root.iter('PListFile'):
            plists.append(plist.attrib.get('name'))
        self.assertEqual(plists, ['AAA_drv_gdie_GMD_MB3P_hdmt2class_class_s68g1.plist',
                                  'clk_gcd_class_s68g1.plist'])

        expect = {'HdmtReferenceFile': {'PList': {'PListFile': [{'name': 'AAA_drv_gdie_GMD_MB3P_hdmt2class_class_s68g1.plist'},
                                                                {'name': 'clk_gcd_class_s68g1.plist'}]}}}
        self.assertEqual(XmlRead('a.xml').todict(), expect)

        # fail case
        File('b.xml').touch('''
<HdmtReferenceFile>
  <PList>
    <PListFile name="AAA_drv_gdie_GMD_MB3P_hdmt2class_class_s68g1.plist" />
    <PListFile name="clk_gcd_class_s68g1.plist" />
</HdmtReferenceFile>
''')
        with self.assertRaisesRegex(ErrorInput, 'Check b.xml'):
            XmlRead('b.xml').load()
        with self.assertRaisesRegex(ErrorInput, 'Check b.xml'):
            XmlRead('b.xml').todict()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
