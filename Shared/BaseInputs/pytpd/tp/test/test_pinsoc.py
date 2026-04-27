#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for pinsoc.py
"""
from setenv_unittest import UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE    # must be first import for unittests
from tp.pinsoc import *
from tp.testprogram import TestProgram
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir, File
from gadget.dictmore import keys_atlevel
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock


class TestPinSoc(TestCase):

    def test_basic(self):
        with TempDir(name=True) as tdir:
            code = """
Import a.pin
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code = """
Version 1.0;

IPPinDescription IP_CPU b.pin;
IPPinDescription IP_CPU b.pin;

PinDescription
{
        Resource HPCC.dpin
        {
            AUDCLK;
            BUDCLK;

                Group all_dmn_scoped
                {
                        IP_PCH::AUDCLK,
                        IP_CPU::AUDCLK
                }
        }
        Resource VirtualScs
        {
           PINX;
           PIXY;
        }
       DomainDefinitions
        {
                Domain ALL
                {
                        all_dmn_scoped
                }
        }
        SerialCaptureDomainDefinitions
        {
           SCDomain CPU_TAP_ALL
           {
               PINX,
               PIXY
            }
        }
}
"""
            File('%s/a.pin' % tdir).touch(code, mkdir=True)
            code2 = '\n'.join(x for x in code.split('\n') if 'IPPinDescription' not in x)
            File('%s/b.pin' % tdir).touch(code2, mkdir=True)
            File('%s/Modules/ARR/a.mtpl' % tdir).touch('', mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            tp.pin.set_data()
            tp.pin.set_data()
            self.assertEqual(len(tp.pin.get_resources()), 4)
            self.assertEqual(len(tp.pin.get_groups()), 2)
            self.assertEqual(len(tp.pin.get_domains()), 4)
            self.assertEqual(tp.pin.get_resource('dpin'), {'AUDCLK', 'BUDCLK'})
            self.assertEqual(tp.pin.get_resource('hc'), set())

            self.assertEqual(len(list(keys_atlevel(tp.pin.get_resources(), 1))), 8)
            self.assertEqual(len(list(keys_atlevel(tp.pin.get_groups(), 1))), 4)
            self.assertEqual(len(list(keys_atlevel(tp.pin.get_domains(), 1))), 6)

            self.assertEqual(tp.pin.get_pin2domain(),
                             {'AUDCLK': {'ALL'},
                              'PINX': {'SCDomain::CPU_TAP_ALL', 'SCDomain::IP_CPU::CPU_TAP_ALL'},
                              'PIXY': {'SCDomain::CPU_TAP_ALL', 'SCDomain::IP_CPU::CPU_TAP_ALL'}})

            self.assertTrue(tp.pin.is_resource('IP_PCH::AUDCLK'))
            self.assertFalse(tp.pin.is_resource('all_dmn_scoped'))

            # invalid 1
            code = """
Version 1.0;

IPPinDescription IP_CPU b.pin;

PinDescription
{
}}
"""
            File('%s/a.pin' % tdir).touch(code, newfile=True, mkdir=True)
            tp.pin.__init__(tp)
            with self.assertRaisesRegex(ErrorInput, 'Mismatched closed parenthesis'):
                tp.pin.set_data()

            # invalid 2
            code = """
Version 1.0;

IPPinDescription IP_CPU b.pin;

Description
{
}
"""
            File('%s/ax.pin' % tdir).touch(code, newfile=True, mkdir=True)
            with self.assertRaisesRegex(ErrorCockpit, 'Unknown pin line'):
                tp.pin.set_data(f'{tdir}/ax.pin')

    def test_ipread(self):
        with TempDir(name=True) as tdir:
            code = """
Import a.pin
"""
            File('%s/y.tpl' % tdir).touch(code, mkdir=True)
            code1 = """
Version 1.0;

IPPinDescription IP_CPU b.pin;

PinDescription
{
        Resource HPCC.dpin
        {
            AUDCLK;
            BUDCLK;

                Group all_dmn_scopedmain
                {
                        IP_PCH::AUDCLK,
                        IP_CPU::AUDCLK
                }
        }
}
"""
            File('%s/a.pin' % tdir).touch(code1, mkdir=True)

            code2 = """
Version 1.0;

PinDescription
{
        Resource HPCC.dpin
        {
            AUDCLK;
            BUDCLK;

                Group all_dmn_scoped
                {
                        IP_PCH::AUDCLK,
                        IP_CPU::AUDCLK
                }
        }
        Group AA {
            all_dmn_scoped
        }
}
"""
            File('%s/b.pin' % tdir).touch(code2, mkdir=True)
            File('%s/Modules/ARR/a.mtpl' % tdir).touch('', mkdir=True)

            envfile = '%s/env.env' % tdir
            File(envfile).touch()
            tp = TestProgram(envfile)._ut_write_stpl()
            tp.pin.set_data()
            self.assertEqual(tp.pin.get_groups().keys(), {'IP_CPU::all_dmn_scoped',
                                                          'IP_CPU::AA',
                                                          'all_dmn_scopedmain',
                                                          'all_dmn_scoped',
                                                          'AA'})

    def test_flatten(self):
        # tests Independent Usage (no TP needed)
        with TempDir(name=True) as tdir:
            code = """
Version 1.0;

PinDescription
{
        Resource DPin
        {
            AUDCLK;
            BUDCLK;
            CUDCLK;

                Group all
                {
                        IP_PCH::AUDCLK,
                        bc_clk
                }
                Group bc_clk
                {
                   BUDCLK,
                   CUDCLK,
                }
        }
}
"""
            File(f'{tdir}/a.pin').touch(code, mkdir=True)

            pin = PinSoc(None)
            pin.set_data(f'{tdir}/a.pin')
            self.assertEqual(list(pin.flatten('all')), ['IP_PCH::AUDCLK', 'BUDCLK', 'CUDCLK'])
            self.assertEqual(list(pin.flatten('all', strip_ip=True)), ['AUDCLK', 'BUDCLK', 'CUDCLK'])
            self.assertEqual(list(pin.flatten('AUDCLK')), ['AUDCLK'])
            self.assertEqual(list(pin.flatten('IP_PCH::AUDCLK')), ['IP_PCH::AUDCLK'])
            self.assertEqual(list(pin.flatten('IP_PCH::AUDCLK', strip_ip=True)), ['AUDCLK'])
            with self.assertRaisesRegex(ErrorInput, 'blah. is not found in any domain/resource/group'):
                list(pin.flatten('blah'))

    def test_flatten2(self):
        with TempDir(name=True) as tdir:
            code = """
Version 1.0;

PinDescription
{
        Resource DPin
        {
            AA; BB;
            CC;
            DD;

                Group all
                {
                        aa_bb, cc,
                        DD,
                }
                Group aa_bb
                {
                   AA,
                   BB
                }
                Group cc {
                 CC
                }
        }
}
"""
            File(f'{tdir}/a.pin').touch(code, mkdir=True)

            pin = PinSoc(None)
            pin.set_data(f'{tdir}/a.pin')
            self.assertEqual(list(pin.flatten('all')), ['AA', 'BB', 'CC', 'DD'])
            self.assertEqual(list(pin.flatten('aa_bb')), ['AA', 'BB'])
            self.assertEqual(list(pin.flatten('AA')), ['AA'])

            # Error case
            code = """
Version 1.0;

PinDescription
{
        Resource DPin
        {
            AA; BB;
            DD;

                Group all
                {
                        aa_bb, cc,
                        DD,
                }
                Group aa_bb
                {
                   AA,
                   BB
                }
                Group cc {
                 CC
                }
        }
}
"""
            File(f'{tdir}/b.pin').touch(code, mkdir=True)
            with self.assertRaisesRegex(ErrorInput, 'is not found in any domain'):
                pin.set_data(f'{tdir}/b.pin')

    def test_pin2ip(self):
        # tests Independent Usage (no TP needed)
        with TempDir(name=True) as tdir:
            code = """
Version 1.0;

PinDescription
{
        Resource DPin
        {
            AUDCLK;
            BCLK;
            CCLK;
            DCLK;

            Group BCLKx
            {
                    IP_PCH::BCLK,
            }
            Group CCLKx
            {
                    IP_CPU::CCLK,
            }
            Group DCLKx
            {
                   DCLK,
            }
        }
        ThermalDomainDefinitions {
           ThermalDomain ALL_DPIN_MTL {
               DCLKx
           }
        }
}
"""
            File(f'{tdir}/a.pin').touch(code, mkdir=True)

            pin = PinSoc(None)
            pin.set_data(f'{tdir}/a.pin')
            self.assertEqual(pin.get_pin2ip(), {'AUDCLK': None,
                                                'BCLK': 'IP_PCH',
                                                'CCLK': 'IP_CPU',
                                                'DCLK': None})

    def test_socfile(self):
        with TempDir(name=True) as tdir:
            code = """
Version 1.0;

SocketDef
{
        PinDescription PinDefinitions.pin;
        DUT 1
        {
                Resource DPin
                {
                        IP_CPU::XX_CORE_DLVR_VIEWANA_0     01.025;   #CORE_DLVR_VIEWANA0
                        IP_PCH::XX_CORE_DLVR_VIEWANA_1     01.026;   #CORE_DLVR_VIEWANA1
                     XXJTAG_TCK_ec     01.016;   #SOC:JTAG_TCK
                }
                Resource GPIO
                {
                        IO_RLY_00     [U] 00.000;   #IO_RLY_00
                        IO_RLY_01     [U] 00.000;   #IO_RLY_01
                }
        }
}
"""
            File(f'{tdir}/a.soc').touch(code, mkdir=True)

            pin = PinSoc(None)
            result = pin.read_soc(f'{tdir}/a.soc')
            expect = {'XX_CORE_DLVR_VIEWANA_0':
                      {'ip': 'IP_CPU', 'u': False, 'ch': '01.025', 'resource': 'DPin', 'dut': '1'},
                      'XX_CORE_DLVR_VIEWANA_1':
                          {'ip': 'IP_PCH', 'u': False, 'ch': '01.026', 'resource': 'DPin', 'dut': '1'},
                      'XXJTAG_TCK_ec':
                          {'ip': '', 'u': False, 'ch': '01.016', 'resource': 'DPin', 'dut': '1'},
                      'IO_RLY_00':
                          {'ip': '', 'u': True, 'ch': '00.000', 'resource': 'GPIO', 'dut': '1'},
                      'IO_RLY_01':
                          {'ip': '', 'u': True, 'ch': '00.000', 'resource': 'GPIO', 'dut': '1'}}
            self.assertEqual(result, expect)

            # invalid 1
            code = """
SocketDef
{
        DUT 1
        {
                Resource GPIO
                {
                        IO_RLY_01     [U] 00.000;   #IO_RLY_01
                }
        }
}
}
"""
            File(f'{tdir}/b.soc').touch(code, mkdir=True)
            with self.assertRaisesRegex(ErrorInput, 'Mismatched closed parenthesis'):
                pin.read_soc(f'{tdir}/b.soc')

            # invalid 2
            code = """
SocketDef
{
        DUT 1
        {
                Unknown GPIO
                {
                        IO_RLY_01     [U] 00.000;   #IO_RLY_01
                }
        }
}
"""
            File(f'{tdir}/c.soc').touch(code, mkdir=True)
            with self.assertRaisesRegex(ErrorCockpit, 'Unknown soc line'):
                pin.read_soc(f'{tdir}/c.soc')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    def test_soc_sha(self):
        # TPIE style
        tp = TestProgram(f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env')
        self.assertEqual(tp.pin.get_soc_sha(), '6c1f59')
        # Torch style
        tp = TestProgram(f'{UT_DIR}/ut_23/POR_TP/Class_MTL_P68/EnvironmentFile.env')
        self.assertEqual(tp.pin.get_soc_sha(), 'be5fc3')

    @unittest.skipIf(not EXIST_PDX_I_DRIVE, r'This unittest needs pdx I:\ drive mapped')
    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_fulltp(self):
        tp = TestProgram(UT_DIR + '/TGLXXXXBXH14P00S109/TPL/EnvironmentFile.env')
        tp.pin.set_data()
        self.assertEqual(len(tp.pin._resource), 21)
        self.assertEqual(len(tp.pin._groups), 2888)
        self.assertEqual(len(tp.pin._domain), 27)

        self.assertEqual(len(list(keys_atlevel(tp.pin._resource, 1))), 2036)
        self.assertEqual(len(list(keys_atlevel(tp.pin._groups, 1))), 73710)
        self.assertEqual(len(list(keys_atlevel(tp.pin._domain, 1))), 27)

        self.assertEqual(tp.pin._check_flat_all(), (2915, 90553))

    @unittest.skipIf(*is_ut_option('SLOW', message="not needed for coverage"))
    def test_fulltp_mtls(self):
        ps = PinSoc(None)
        ps.set_data(f'{UT_DIR_REPO}/pinfile_mtls_case/PinDefinitions.pin')
        self.assertEqual(len(ps._resource), 27)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
