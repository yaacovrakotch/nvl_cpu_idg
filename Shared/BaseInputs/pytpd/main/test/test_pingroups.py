#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for pingroups
"""
from setenv_unittest import UT_DIR    # must be first import for unittests
from gadget.ut import TestCase, unittest, is_ut_option
from main.pingroups import *
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from gadget.shell import IS_UNIX, IS_WIN
from os.path import join
import main.pingroups as pingroups
import sys


class TestCheck(TestCase):

    def test_check_scoping(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''IP_CPU::cpu1
IP_CPU::cpu2
IP_PCH::pch1
IP_PCH::pch2
pkg1
pkg2
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            pg = PinGroups('testing')

            # Success
            pg.check_scoping(['cpu1', 'cpu2'], 'pingroupa')
            pg.check_scoping(['pch1', 'pch2'], 'pingroupb')
            pg.check_scoping(['IP_PCH::pch1', 'IP_CPU::cpu1'], 'pingroupc')
            pg.check_scoping(['cpu1', 'IP_CPU::cpu2'], 'pingroupd')
            pg.check_scoping(['cpu1', 'grp1'], 'pingroupe')
            pg.check_scoping(['IP_CPU::cpu1', 'pkg1'], 'pingroupf')

            # Failure
            with self.assertRaisesRegex(ErrorCheck, 'group pingroupg has mixed scope. cpu1 must be scoped'):
                pg.check_scoping(['cpu1', 'pch1'], 'pingroupg')
            with self.assertRaisesRegex(ErrorCheck, 'group pingrouph has mixed scope. cpu1 must be scoped'):
                pg.check_scoping(['cpu1', 'pkg1'], 'pingrouph')

    def test_check_lowercase(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            SqlDict(f'{cfg.pingroup}/testing.sqlite')
            pg = PinGroups('testing')

            pg.check_lowercase('a1', ['somepin'])    # pass case
            pg.check_lowercase('A1', ['A1'])    # pass case - pin wrapper
            with self.assertRaisesRegex(ErrorCheck, 'has uppercase chars'):
                pg.check_lowercase('A1', ['somepin'])

    def test_check_unscoped(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            SqlDict(f'{cfg.pingroup}/testing.sqlite')
            pg = PinGroups('testing')

            pg.check_unscoped('a1', ['a'])    # pass case
            pg.check_unscoped('ut_except', ['IP_CPU::a'])
            pg.check_unscoped('a1', ['IP_CPU::a1'])   # pass case
            with self.assertRaisesRegex(ErrorCheck, 'has scoping '):
                pg.check_unscoped('a1', ['IP_CPU::a', 'b'])

            # pinwrapper
            self.assertEqual(pg.is_pin_wrapper('tdo', ['IP_CPU::tdo']), True)
            self.assertEqual(pg.is_pin_wrapper('tdo', ['IP_CPU::tdo', 'tdi']), False)
            self.assertEqual(pg.is_pin_wrapper('tdo', ['tdi']), False)

    def test_check_dieletname(self):
        with TempDir(name=True) as tdir,\
                MockVar(pingroups, 'IS_UT', False),\
                MockVar(cfg, "pingroup", tdir):

            SqlDict(f'{cfg.pingroup}/testing.sqlite')
            pg = PinGroups('testing')

            pg.check_dieletname('cpu_blah', ['a', 'b'])    # pass case
            pg.check_dieletname('ut_except', ['a', 'b'])    # pass case
            pg.check_dieletname('tap', ['tap'])    # pass case
            pg.check_dieletname('thermal', ['thermtrip'])    # pass case, pin-wrapper

            with self.assertRaisesRegex(ErrorCheck, 'Expecting <dielet'):
                pg.check_dieletname('a1', ['a', 'b'])

    def test_check_belong(self):
        with TempDir(name=True) as tdir,\
                MockVar(pingroups, 'IS_UT', False),\
                MockVar(cfg, "pingroup", tdir):

            SqlDict(f'{cfg.pingroup}/testing.sqlite')
            pg = PinGroups('testing')
            pg.ipmap = {'pin1': 'IP_CPU',
                        'pin2': 'IP_CPU',
                        'pin3': 'IP_PCH',
                        'pin4': None}

            pg.check_belong('cpu_abc', ['pin1', 'pin2'])   # success
            pg.check_belong('pkg_abc', ['pin1', 'pin3'])   # success
            pg.check_belong('soc_abc', ['pin1', 'pin3'])   # success
            pg.check_belong('gcd_abc', ['pin3'])   # success
            pg.check_belong('ut_except', ['pin1', 'pin3'])   # success
            pg.check_belong('pin4', ['pin4'])      # pin wrapper
            pg.check_belong('ioe_abc', ['pin4'])   # sort pin, no scoping

            with self.assertRaisesRegex(ErrorCheck, '.cpu. should only contain IP_CPU'):
                pg.check_belong('cpu_abc', ['pin1', 'pin3'])

    def test_check_pkg_but_iponly(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            SqlDict(f'{cfg.pingroup}/testing.sqlite')
            pg = PinGroups('testing')
            pg.ipmap = {'pin1': 'IP_CPU',
                        'pin2': 'IP_CPU',
                        'pin3': 'IP_PCH'}

            pg.check_pkg_but_iponly('pkg_abc', ['pin1', 'pin2', 'pin3'])   # success (normal pass)
            pg.check_pkg_but_iponly('cpu_abc', ['pin1', 'pin2'])           # success (non-pkg)
            pg.check_pkg_but_iponly('pkg_abc', ['pin4'])                   # success (unknown)
            pg.check_pkg_but_iponly('pkg_abc', ['pin1', 'pin4'])           # success (one unknown)
            pg.check_pkg_but_iponly('ut_except', ['pin1', 'pin2'])

            with self.assertRaisesRegex(ErrorCheck, 'but pins is 100% IP_CPU'):
                pg.check_pkg_but_iponly('pkg_abc', ['pin1', 'pin2'])

    def test_check_duplicate_content(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - real pins
            File(fname).write('''HVMBCLK_P
    TDO''')
            cmd = "pingroups.py testing -name group1 -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create an exact group
            cmd = "pingroups.py testing -name group2 -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorCheck, 'pingroup .group2. has exact pin content as .group1.'):
                    PinGroupsArgs().main()

            # create an exact group - pass
            code = PinGroups.code('group2')
            cmd = "pingroups.py testing -name group2 -new %s -resource HPCC.dpin -why new_group -force %s" % (fname, code)
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()


class PinGroupTest(TestCase):

    def test_deletegroup(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - grp1
            File(fname).write('''HVMBCLK_P
    TDO''')
            cmd = "pingroups.py testing -name grp1 -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            pingroup = PinGroups('testing')
            self.assertTrue('grp1' in pingroup.db)

            # delete it
            cmd = "pingroups.py testing -name grp1 -deletegroup -why not_needed_anymore"
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # check value of db
            self.assertFalse('grp1' in pingroup.db)
            # history should be saved
            self.assertTrue('2' in pingroup.db)

    def test_report(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - grp1
            File(fname).write('''HVMBCLK_P
    TDO''')
            cmd = "pingroups.py testing -name grp1 -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - grp3
            File(fname).write('''HVMBCLK_N
    TDO''')
            cmd = "pingroups.py testing -name grp3 -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - grp4
            File(fname).write('''TDO''')
            cmd = "pingroups.py testing -name grp4 -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # make a snapshot
            cmd = "pingroups.py testing -snapshot"
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # update group4
            File(fname).write('''HVMBCLK_N''')
            cmd = "pingroups.py testing -name grp4 -modify %s -why pin_changed" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            cmd = "pingroups.py testing -name grp3 -deletegroup -why not_needed"
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - grp2
            File(fname).write('''TDO''')
            cmd = "pingroups.py testing -name grp2 -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # do a diff with "0"
            cmd = "pingroups.py testing 4 -report 0"
            with MockVar(sys, "argv", cmd.split()):
                with CaptureStdoutLog() as p:
                    PinGroupsArgs().main()
                expect = """grp3 is removed
grp4 has changed
grp2 is new
"""
                self.assertTextEqual(p.getvalue(), expect)

            # make a snapshot
            cmd = "pingroups.py testing -snapshot"
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            cmd = "pingroups.py testing 4 -report 8"
            with MockVar(sys, "argv", cmd.split()):
                with CaptureStdoutLog() as p:
                    PinGroupsArgs().main()
                expect = """grp3 is removed
grp4 has changed
grp2 is new
"""
                self.assertTextEqual(p.getvalue(), expect)

            # old snapshot does not exist
            cmd = "pingroups.py testing 44 -report 8"
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorInput, 'does not exist'):
                    PinGroupsArgs().main()

            # new snapshot does not exist
            cmd = "pingroups.py testing 4 -report 88"
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorInput, 'does not exist'):
                    PinGroupsArgs().main()

            # invalid args
            cmd = "pingroups.py testing -report 88"
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorInput, 'old_snapshot_no is not specified'):
                    PinGroupsArgs().main()

    def test_modify(self):
        with TempDir(name=True) as tdir,\
                MockVar(PinGroups, 'check_duplicate_content', Mock()),\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
TDI
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - real pins
            File(fname).write('''HVMBCLK_P
    TDO''')
            cmd = "pingroups.py testing -name new_group_name2 -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            cmd = "pingroups.py testing -name new_group_name -new %s -resource DOMAIN -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # diff first
            File(fname).write('''TDI

    TDO''')
            cmd = "pingroups.py testing -name new_group_name -modify %s -diff" % fname
            with MockVar(sys, "argv", cmd.split()),\
                    MockVar(SystemCall, "run_outtxt", Mock()):
                PinGroupsArgs().main()

            # update pingroup
            cmd = "pingroups.py testing -name new_group_name -modify %s -why modify_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # check value of pingroup
            pingroup = PinGroups('testing')
            id = pingroup.db['new_group_name']
            data = pingroup.db[id]
            self.assertEqual(data['pinlist'], ['TDI', 'TDO'])

            # invalid pin
            File(fname).write('''TDI
    TDOx''')
            cmd = "pingroups.py testing -name new_group_name -modify %s -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorCheck, 'is not valid'):
                    PinGroupsArgs().main()

            # do history on this pingroup
            cmd = "pingroups.py testing -name new_group_name -history"
            with MockVar(sys, "argv", cmd.split()):
                with CaptureStdoutLog() as p:
                    PinGroupsArgs().main()
                expect = """2 {user} new_group
3 {user} modify_group
""".format(user=USERNAME)
                self.assertTextEqual(p.getvalue(), expect)

            # display the detail
            cmd = "pingroups.py testing 2 -detail 3"
            with MockVar(sys, "argv", cmd.split()),\
                    MockVar(SystemCall, 'run_outtxt', Mock()):
                with CaptureStdoutLog() as p:
                    PinGroupsArgs().main()
                self.assertEqual(p.getvalue(), 'See Diff of new_group_name\n')

            # invalid detail no.
            cmd = "pingroups.py testing 2 -detail 31"
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorInput, '31.*does not exist'):
                    PinGroupsArgs().main()

            # missing args
            cmd = "pingroups.py testing -detail 2"
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorInput, 'old_rev is not specified'):
                    PinGroupsArgs().main()

            # list
            expect = '''List of pingroup names:
=+
 new_group_name     2 pins  by \\w+  last update: \\S+
 new_group_name2    2 pins  by \\w+  last update: \\S+
=+
'''.split('\n')
            cmd = "pingroups.py testing -list"
            with MockVar(sys, "argv", cmd.split()):
                with CaptureStdoutLog() as p:
                    PinGroupsArgs().main()
            print("output: =====")
            print(p.getvalue())
            self.assertRegexpEachList(p.getvalue().split('\n'), expect)

            # pinlist
            expect = '''# List of defined names:
HVMBCLK_N
HVMBCLK_P
TDI
TDO
'''
            cmd = "pingroups.py testing -pinlist"
            with MockVar(sys, "argv", cmd.split()):
                with CaptureStdoutLog() as p:
                    PinGroupsArgs().main()
            self.assertTextEqual(p.getvalue(), expect)

    def test_read_pin_ip(self):
        with TempDir(name=True) as tdir,\
                MockVar(PinGroups, 'check_unscoped', Mock()),\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''IP_CPU::cpu1
IP_PCH::pch1
cpu2
pch2
pkg
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # get pins unittests
            pg = PinGroups('testing')
            self.assertEqual(pg.get_ip_only('IP_CPU::pin1'), 'IP_CPU')
            self.assertEqual(pg.get_ip_only('pin1'), None)
            self.assertEqual(pg.get_pin_only('IP_CPU::pin1'), 'pin1')
            self.assertEqual(pg.get_pin_only('pin1'), 'pin1')

            # create new group - real pins
            File(fname).write('''IP_CPU::cpu2
    IP_PCH::pch2''')
            pg.new('new_group_name', 'DPin', fname, 'why')

            # ipmap unittest
            pg = PinGroups('testing')
            self.assertEqual(pg.ipmap, {'pkg': None,
                                        'cpu2': 'IP_CPU',
                                        'pch2': 'IP_PCH',
                                        'pch1': 'IP_PCH',
                                        'cpu1': 'IP_CPU'})

            # create new group - scoping combinations
            File(fname).write('''cpu2
IP_CPU::cpu1
    ''')
            with MockVar(PinGroups, 'check_scoping', Mock()):
                pg.new('new_group_name1', 'DPin', fname, 'why')

            # create new group - invalid scoping
            File(fname).write('''IP_PCH::cpu2
    ''')
            with self.assertRaisesRegex(ErrorCheck, 'has incorrect scoping'):
                pg.new('new_group_name2', 'DPin', fname, 'why')

            # invalid initial run
            pg = PinGroups('testing')
            pg.db['_all_pins'] = {'IP_PCH::pch1', 'IP_PCH::cpu1', 'cpu2', 'pch2', 'pkg'}
            with self.assertRaisesRegex(ErrorCheck, 'however it is already'):
                PinGroups('testing')

    def test_flatten(self):
        with TempDir(name=True) as tdir,\
                MockVar(PinGroups, 'check_unscoped', Mock()),\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''IP_CPU::cpu1
IP_PCH::pch1
cpu2
pch2
pkg
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            pg = PinGroups('testing')

            # sub1
            File(fname).write('''IP_CPU::cpu1
''')
            pg.new('sub1', 'DPin', fname, 'why')

            # sub2
            File(fname).write('''cpu2
sub1
''')
            pg.new('sub2', 'DPin', fname, 'why')

            # sub3
            File(fname).write('''IP_PCH::pch1
sub2
''')
            pg.new('sub3', 'DPin', fname, 'why')
            self.assertEqual(pg.flatten('sub3'), {'cpu2', 'IP_PCH::pch1', 'IP_CPU::cpu1'})
            self.assertEqual(pg.flatten(['sub3']), {'cpu2', 'IP_PCH::pch1', 'IP_CPU::cpu1'})

            # error case
            with self.assertRaisesRegex(ErrorInput, 'sub4 is not a valid pingroup'):
                pg.flatten('sub4')

    def test_modify_calc(self):
        with TempDir(name=True) as tdir,\
                MockVar(PinGroups, 'check_duplicate_content', Mock()),\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
TDI
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - real pins
            File(fname).write('''HVMBCLK_P
    TDO''')
            cmd = "pingroups.py testing -name new_group_name1 -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            cmd = "pingroups.py testing -name new_group_name -new %s -resource DOMAIN -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # check value of pingroup
            pingroup = PinGroups('testing')
            id = pingroup.db['new_group_name']
            data = pingroup.db[id]
            self.assertEqual(data['pinlist'], ['HVMBCLK_P', 'TDO'])

            # update pingroup
            File(fname).write('''new_group_name1 - TDI''')
            cmd = "pingroups.py testing -name new_group_name -modify %s -why modify_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # check value of pingroup
            pingroup = PinGroups('testing')
            id = pingroup.db['new_group_name']
            data = pingroup.db[id]
            self.assertEqual(data['pinlist'], ['new_group_name1 - TDI'])

            # add new duplicate pin - should error
            File(fname).write('''HVMBCLK_N
TDI
TDI
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -name new_group_name -new %s -resource DOMAIN -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorCheck, 'pin TDI is duplicated in new_group_name'):
                    PinGroupsArgs().main()

    def test_ut(self):
        # no args
        cmd = "pingroups.py"
        with MockVar(sys, "argv", cmd.split()):
            with self.assertRaises(SystemExit):
                PinGroupsArgs().main()

    def test_snapshot(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - real pins
            File(fname).write('''HVMBCLK_P
    TDO''')
            cmd = "pingroups.py testing -name new_group_name -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # do snapshot
            cmd = "pingroups.py testing -snapshot"
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # list it
            cmd = "pingroups.py testing -snapshot -list"
            with MockVar(sys, "argv", cmd.split()):
                with CaptureStdoutLog() as p:
                    PinGroupsArgs().main()
                print("output: ===")
                print(p.getvalue())
                self.assertIn('snapshot:00002', p.getvalue())

    def test_xls(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - real pins
            File(fname).write('''HVMBCLK_P
    TDO''')
            cmd = "pingroups.py testing -name new_group_name -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - real pins
            File(fname).write('''TDO''')
            cmd = "pingroups.py testing -name all_leg -new %s -resource DOMAIN -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # snapshot first
            cmd = "pingroups.py testing -snapshot"
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # xls
            outfile = join(tdir, 'out.csv')
            cmd = "pingroups.py testing 3 -xls %s" % outfile
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()
            expect = """PINGROUP
new_group_name,HPCC.dpin,=,"HVMBCLK_P, TDO"
Domain Definitions
all_leg,DOMAIN,=,TDO
"""
            self.assertTextEqual(File(outfile).read(), expect)

            # missing arguments
            cmd = "pingroups.py testing -xls %s" % outfile
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorInput, 'snapshot_no is not specified'):
                    PinGroupsArgs().main()

            # provided snapshot not exist
            cmd = "pingroups.py testing 31 -xls %s" % outfile
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorInput, 'Provided snapshot.*31.*does not exist'):
                    PinGroupsArgs().main()

    def test_check(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            fname1 = join(tdir, 'allpins.txt')
            File(fname1).write('''csi_timd
EAR
mbp
DISP_UTILS
''')

            fname2 = join(tdir, 'grps.txt')
            File(fname2).write('''
noa_all,HPCC.dpin,=,"csi_timd,EAR",,
leakage_legacy,HPCC.dpin,=,"mbp,DISP_UTILS,EAR",,
LEG,DOMAIN,=,"leakage_legacy + noa_all",,
''')

            cmd = "pingroups.py %s -check %s" % (fname1, fname2)
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # error case
            cmd = "pingroups.py oops -check %s" % fname2
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorUser, 'This must be a valid pinlist.csv'):
                    PinGroupsArgs().main()

    def test_deletepin(self):
        # note: this test is a good template to copy
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - real pins
            File(fname).write('''HVMBCLK_P
    TDO''')
            cmd = "pingroups.py testing -name new_group_name -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # delete a pin from a pingroup
            cmd = "pingroups.py testing -name new_group_name -deletepin TDO -diff"
            with MockVar(sys, "argv", cmd.split()),\
                    MockVar(SystemCall, "run_outtxt", Mock()):
                PinGroupsArgs().main()

            cmd = "pingroups.py testing -name new_group_name -deletepin TDO -why so_and_so"
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # check value of pingroup
            pingroup = PinGroups('testing')
            id = pingroup.db['new_group_name']
            data = pingroup.db[id]
            self.assertEqual(data['pinlist'], ['HVMBCLK_P'])

            # make sure original pinlist is saved in history
            self.assertEqual(pingroup.db['1']['pinlist'], ['HVMBCLK_P', 'TDO'])

            # pin does not exist
            cmd = "pingroups.py testing -name new_group_name -deletepin TDOx -why so_and_so"
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorCheck, 'Can only delete existing pins'):
                    PinGroupsArgs().main()

            # pingroup does not exist
            cmd = "pingroups.py testing -name new_group_namex -deletepin TDO -why so_and_so"
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorUser, 'does not exist'):
                    PinGroupsArgs().main()

            # name was not provided
            cmd = "pingroups.py testing -deletepin TDO -why so_and_so"
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorUser, 'name is not provided'):
                    PinGroupsArgs().main()

    @unittest.skipIf(IS_WIN, 'unix only due to db access')
    def test_invalid_prod(self):
        # invalid product
        cmd = "pingroups.py not_exist -name new_group_name -deletepin ABC -why so_and_so"
        with MockVar(sys, "argv", cmd.split()):
            with self.assertRaisesRegex(ErrorInput, 'is not valid product'):
                PinGroupsArgs().main()

    def test_dump(self):
        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # create new group - real pins
            File(fname).write('''HVMBCLK_P
    TDO''')
            cmd = "pingroups.py testing -name new_group_name -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # dump the pingroup to a file
            outfile = join(tdir, 'out.txt')
            cmd = "pingroups.py testing -name new_group_name -dump %s" % outfile
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()
            self.assertEqual(File(outfile).read(), 'HVMBCLK_P\nTDO')

            # disp the pingroup
            cmd = "pingroups.py testing -name new_group_name -disp"
            with MockVar(sys, "argv", cmd.split()),\
                    CaptureStdoutLog() as p:
                PinGroupsArgs().main()
            self.assertEqual(p.getvalue(), 'HVMBCLK_P\nTDO\n')

    def test_reupload(self):

        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):
            # upload new set of all_pins ============================
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
HVMBCLK_P
TDO
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # test for create new group - real pins
            File(fname).write('''HVMBCLK_P
    TDO''')
            cmd = "pingroups.py testing -name new_group_name -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):

                PinGroupsArgs().main()

            # test for create new group - pingroup
            dbfile = join(tdir, 'testing.sqlite')
            File(fname).write('''new_group_name
    ''')
            cmd = "pingroups.py testing -name group2 -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):

                PinGroupsArgs().main()

            # check value of pingroup
            pingroup = PinGroups('testing')
            id = pingroup.db['new_group_name']
            data = pingroup.db[id]
            self.assertEqual(data['pinlist'], ['HVMBCLK_P', 'TDO'])

            # now, we re-upload a new allpins pin with TDO removed
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
HVMBCLK_P
VCC_FUSEPRG1_LC
''')
            cmd = "pingroups.py testing -set_pin %s" % fname
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            # check value of pingroup
            pingroup = PinGroups('testing')
            id = pingroup.db['new_group_name']
            data = pingroup.db[id]
            self.assertEqual(data['pinlist'], ['HVMBCLK_P'])

            id = pingroup.db['group2']
            data = pingroup.db[id]
            self.assertEqual(data['pinlist'], ['new_group_name'])

    def test_set_pins(self):

        with TempDir(name=True) as tdir:
            fname = join(tdir, 'allpins.txt')
            File(fname).write('''HVMBCLK_N
HVMBCLK_P

TDO,-
TDI,IP_PCH
''')
            cmd = "pingroups.py testing -set_pin %s -i_am_tpi" % fname
            with MockVar(sys, "argv", cmd.split()),\
                    MockVar(cfg, "pingroup", tdir):

                PinGroupsArgs().main()

                # now we want to check
                pingroup = PinGroups('testing')
                self.assertEqual(pingroup.db['_all_pins'],
                                 {'HVMBCLK_N', 'HVMBCLK_P', 'TDO', 'TDI', 'IP_PCH::TDI'})

    @unittest.skipIf(IS_WIN, 'unix only due to db access')
    def test_read_csv(self):
        result = PinGroups.read_csv('/p/pde/tvpv/tgl/db/tp_pingroups/unittest_tgl81_pingroups_tab.csv')
        self.assertEqual(result['vccst_leakage'], ('HPCC.dpin', ['EAR', 'csi_timd']))

    def test_invalid_resource(self):
        with TempDir(name=True) as tdir:
            fname = join(tdir, 'pin_lists.txt')

            # test for invalid -resource
            cmd = "pingroups.py testing -new %s -resource invalid" % fname
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaises(SystemExit):
                    PinGroupsArgs().main()

    def test_create_new(self):
        dbfile = './testing.sqlite'
        with TempDir(name=True, chdir=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):
            fname = join(tdir, 'pin_lists.txt')

            # test for create new group

            File(fname).write('''HVMBCLK_P

    TDO''')
            cmd = "pingroups.py testing -name new_group_name -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):

                # setup the initial database
                db = SqlDict(dbfile)
                db['_all_pins'] = {'HVMBCLK_P', 'TDO'}

                PinGroupsArgs().main()

                with self.assertRaisesRegex(ErrorCheck, 'already exist in testing'):
                    PinGroupsArgs().main()

                # do the check
                pingroup = PinGroups('testing')
                self.assertEqual(pingroup.db['new_group_name'], '1')
                result = pingroup.db['1']
                result['date'] = 'dummy'
                self.assertEqual(result, {'comment': 'new_group',
                                          'resource': 'HPCC.dpin',
                                          'name': 'new_group_name',
                                          'pinlist': ['HVMBCLK_P', 'TDO'],
                                          'user': USERNAME,
                                          'date': 'dummy'})

            # -why was not provided
            cmd = "pingroups.py testing -name new_group_name -new %s -resource HPCC.dpin" % fname
            with MockVar(sys, "argv", cmd.split()):

                with self.assertRaisesRegex(ErrorUser, 'why is not provided'):
                    PinGroupsArgs().main()

            # product is not provided
            cmd = "pingroups.py -name new_group_name -new %s -resource HPCC.dpin" % fname
            with MockVar(sys, "argv", cmd.split()):

                with self.assertRaisesRegex(ErrorUser, 'first argument must be product name'):
                    PinGroupsArgs().main()

            # nothing to do
            cmd = "pingroups.py testing"
            with MockVar(sys, "argv", cmd.split()):
                with CaptureStdoutLog() as p:
                    PinGroupsArgs().main()
                self.assertIn('Nothing to do', p.getvalue())

            # invalid pin case
            File(fname).write('''HVMBCLK_P
    TDOx''')
            cmd = "pingroups.py testing -name new_group_name -new %s -resource HPCC.dpin -why new_group" % fname
            with MockVar(sys, "argv", cmd.split()):

                with self.assertRaisesRegex(ErrorCheck, 'Provided pin/pingroup .TDOx. is not valid'):
                    PinGroupsArgs().main()

            # -receipt
            cmd = "pingroups.py testing -receipt 1"
            with MockVar(sys, "argv", cmd.split()),\
                    CaptureStdoutLog() as p:

                PinGroupsArgs().main()
            self.assertEqual(len(p.getvalue().split('\n')), 10)

            # -receipt error case1
            cmd = "pingroups.py testing -receipt a"
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorInput, 'must be digit'):
                    PinGroupsArgs().main()

            # -receipt error case2
            cmd = "pingroups.py testing -receipt 5"
            with MockVar(sys, "argv", cmd.split()):
                with self.assertRaisesRegex(ErrorInput, 'is not a valid receipt id'):
                    PinGroupsArgs().main()

    def test_upload(self):
        with TempDir(name=True) as tdir:
            dbfile = join(tdir, 'testing.sqlite')
            fname = join(tdir, 'mycsv.csv')
            File(fname).write('''PINGROUP,,,,,
noa_all,HPCC.dpin,=,"csi_timd,EAR",,
leakage_legacy,HPCC.dpin,=,"mbp,noa_all,DISP_UTILS,EAR",,
calc,HPCC.dpin,=,"leakage_legacy + noa_all",,
empty,,,,,
Domain Definitions,,,,,
leg,HPCC.dpin,=,EAR,,
''')
            cmd = "pingroups.py testing -upload %s" % fname
            with MockVar(sys, "argv", cmd.split()),\
                    MockVar(cfg, "pingroup", tdir):

                # setup the initial database
                db = SqlDict(dbfile)
                db['_all_pins'] = {'csi_timd', 'EAR', 'mbp', 'DISP_UTILS'}

                PinGroupsArgs().main()

                # now we want to check
                pingroup = PinGroups('testing')

                def check(name, resource, expect):
                    id = pingroup.db[name]
                    result = pingroup.db[id]
                    result['date'] = 'dummy'
                    self.assertEqual(result, {'comment': 'initial upload',
                                              'resource': resource,
                                              'name': name,
                                              'pinlist': expect,
                                              'user': USERNAME,
                                              'date': 'dummy'})

                check('leakage_legacy', 'HPCC.dpin', ['mbp', 'noa_all', 'DISP_UTILS', 'EAR'])
                check('leg', 'DOMAIN', ['EAR'])
                check('noa_all', 'HPCC.dpin', ['csi_timd', 'EAR'])
                check('calc', 'HPCC.dpin', ['leakage_legacy + noa_all'])
                self.assertTrue('empty' not in pingroup.db)

                # rerun
                with self.assertRaisesRegex(ErrorUser, 'already in database'):
                    PinGroupsArgs().main()

            # recheck
            cmd = "pingroups.py testing -recheck"
            with MockVar(sys, "argv", cmd.split()),\
                    MockVar(cfg, "pingroup", tdir):
                PinGroupsArgs().main()

    def test_upload_fail(self):
        with TempDir(name=True) as tdir:
            dbfile = join(tdir, 'testing.sqlite')
            fname = join(tdir, 'mycsv.csv')
            File(fname).write('''
noa_all,HPCC.dpin,=,"csi_timd,EAR",,
leakage_legacy,HPCC.dpin,=,"mbp,IP_CPU::noa_all,DISP_UTILS,EAR",,
LEG,HPCC.dpin,=,"leakage_legacy + noa_all",,
''')
            cmd = "pingroups.py testing -upload %s" % fname
            with MockVar(sys, "argv", cmd.split()),\
                    MockVar(cfg, "pingroup", tdir):

                # setup the initial database
                db = SqlDict(dbfile)
                db['_all_pins'] = {'csi_timd', 'EAR', 'mbp', 'DISP_UTILS'}

                with self.assertRaisesRegex(ErrorUser, 'Fail. Total of 2 errors'):
                    PinGroupsArgs().main()

    def test_cleanup(self):
        with TempDir(name=True) as tdir:
            fname = join(tdir, 'mycsv.csv')
            File(fname).write('''all_clock_pins,HPCC.EnabledClock,=,"HVMBCLK_N, HVMBCLK_P, TCK, STF_CLK_IN",,
sb_ctrl_lvl,HPCC.dpin,=,sb_ctrl_timl,,
pcie4_txn,HPCC.dpin,=,"PCIE4_TX_N_3,
PCIE4_TX_N_2,
PCIE4_TX_N_1,
PCIE4_TX_N_0",,
tcss_rx,HPCC.dpin,=,"TCP_3_TXRX_N_1,
TCP_0_TXRX_P_1, TCP_0_TXRX_P_0


",,

''')
            result = PinGroups.cleanup(fname)
            self.assertTextEqual(result, '''all_clock_pins,HPCC.EnabledClock,=,"HVMBCLK_N, HVMBCLK_P, TCK, STF_CLK_IN",,
sb_ctrl_lvl,HPCC.dpin,=,sb_ctrl_timl,,
pcie4_txn,HPCC.dpin,=,"PCIE4_TX_N_3,PCIE4_TX_N_2,PCIE4_TX_N_1,PCIE4_TX_N_0",,
tcss_rx,HPCC.dpin,=,"TCP_3_TXRX_N_1,TCP_0_TXRX_P_1, TCP_0_TXRX_P_0",,
''')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
