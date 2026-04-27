#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for bgrep.py
"""
from setenv_unittest import UT_DIR    # must be first import for unittests
from main.mconfig_update import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.gizmo import MockVar, with_
from gadget.helperclass import CaptureStdoutLog
from gadget.files import TempDir
import sys


class BTest(TestCase):

    @with_(TempDir, chdir=True)
    def test_basic(self):
        mtext = '''<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot IP="IP_CPU" Path="I:\\hdmxpats\\mtl\\MCarrPbistCCF\" Rev="RevTCCXXA2.1" Patch="p1">
        <PlistFiles>
            <PlistFile BomGroup="CLASS_P68G2">a.plist</PlistFile>
            <PlistFile BomGroup="CLASS_P68G2">b.plist</PlistFile>
        </PlistFiles>
    </PORRoot>
    <!--<ENGRoot Path = "">
        <PlistFiles>
            <PlistFile></PlistFile>
        </PlistFiles>
    </ENGRoot>-->
    </Patterns>
        <IPName>IP_CPU</IPName>
</ModuleConfiguration>'''
        ptext = '''<?xml version="1.0" encoding="utf-8"?>
<Patterns>
  <PORRoot Path="I:\\hdmxpats\\mtl\\MCarrPbistCCF\" Rev="RevTCCXXA2.1" Patch="p3">
    <PlistFiles>
            <PlistFile BomGroup="CLASS_P68G2">anew.plist</PlistFile>
            <PlistFile BomGroup="CLASS_P68G2">bnew.plist</PlistFile>
    </PlistFiles>
  </PORRoot>
  <!--<ENGRoot Path = "">
<PlistFiles>
<PlistFile></PlistFile>
</PlistFiles>
</ENGRoot>-->
</Patterns>'''
        File(f'ABC/module.mconfig').touch(mtext, mkdir=True)
        File(f'REF/Modules/ABC/patterns.pconfig').touch(ptext, mkdir=True)
        cmd = "mconfig_update.py ABC -ref REF"

        with MockVar(sys, "argv", cmd.split()):
            MConfig().main()
        expect = '''<?xml version="1.0" encoding="utf-8"?>
<ModuleConfiguration>
<Patterns>
  <PORRoot IP="IP_CPU" Path="I:\\hdmxpats\\mtl\\MCarrPbistCCF" Rev="RevTCCXXA2.1" Patch="p3">
    <PlistFiles>
            <PlistFile BomGroup="CLASS_P68G2">anew.plist</PlistFile>
            <PlistFile BomGroup="CLASS_P68G2">bnew.plist</PlistFile>
    </PlistFiles>
  </PORRoot>
  <!--<ENGRoot Path = "">
<PlistFiles>
<PlistFile></PlistFile>
</PlistFiles>
</ENGRoot>-->
</Patterns>
        <IPName>IP_CPU</IPName>
</ModuleConfiguration>
'''
        self.assertTextEqual(File(f'ABC/module.mconfig').read(), expect)

    @with_(TempDir, chdir=True)
    def test_basic2(self):
        mtext = '''<?xml version="1.0" encoding="UTF-8"?>
<ModuleConfiguration>
    <Patterns>
        <PORRoot Path="I:\\hdmxpats\\mtl\\MCarrPbistCCF\" Rev="RevTCCXXA2.1" Patch="p1">
        <PlistFiles>
            <PlistFile BomGroup="CLASS_P68G2">a.plist</PlistFile>
            <PlistFile BomGroup="CLASS_P68G2">b.plist</PlistFile>
        </PlistFiles>
    </PORRoot>
    <!--<ENGRoot Path = "">
        <PlistFiles>
            <PlistFile></PlistFile>
        </PlistFiles>
    </ENGRoot>-->
    </Patterns>
</ModuleConfiguration>'''
        ptext = '''<?xml version="1.0" encoding="utf-8"?>
<Patterns>
  <PORRoot Path="I:\\hdmxpats\\mtl\\MCarrPbistCCF\" Rev="RevTCCXXA2.1" Patch="p3">
    <PlistFiles>
            <PlistFile BomGroup="CLASS_P68G2">anew.plist</PlistFile>
            <PlistFile BomGroup="CLASS_P68G2">bnew.plist</PlistFile>
    </PlistFiles>
  </PORRoot>
  <!--<ENGRoot Path = "">
<PlistFiles>
<PlistFile></PlistFile>
</PlistFiles>
</ENGRoot>-->
</Patterns>'''
        File(f'ABC/module.mconfig').touch(mtext, mkdir=True)
        File(f'REF/Modules/ABC/patterns.pconfig').touch(ptext, mkdir=True)
        cmd = "mconfig_update.py ABC -ref REF"

        with MockVar(sys, "argv", cmd.split()):
            MConfig().main()
        expect = '''<?xml version="1.0" encoding="utf-8"?>
<ModuleConfiguration>
<Patterns>
  <PORRoot Path="I:\\hdmxpats\\mtl\\MCarrPbistCCF" Rev="RevTCCXXA2.1" Patch="p3">
    <PlistFiles>
            <PlistFile BomGroup="CLASS_P68G2">anew.plist</PlistFile>
            <PlistFile BomGroup="CLASS_P68G2">bnew.plist</PlistFile>
    </PlistFiles>
  </PORRoot>
  <!--<ENGRoot Path = "">
<PlistFiles>
<PlistFile></PlistFile>
</PlistFiles>
</ENGRoot>-->
</Patterns>
</ModuleConfiguration>
'''
        self.assertTextEqual(File(f'ABC/module.mconfig').read(), expect)

    @with_(TempDir, chdir=True)
    def test_others(self):
        File(f'ABC/module.mconfig').touch(mkdir=True)
        File(f'REF/blah').touch(mkdir=True)

        # No patterns.pconfig
        cmd = "mconfig_update.py ABC -ref REF"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdoutLog() as p:
                MConfig().main()
        print(p.getvalue())
        self.assertIn('Ignoring this module', p.getvalue())

        # incorrect args
        cmd = "mconfig_update.py ABC"
        with MockVar(sys, "argv", cmd.split()):
            with CaptureStdoutLog() as p:
                with self.assertRaises(SystemExit):
                    MConfig().main()
        print(p.getvalue())
        self.assertIn('Nothing to do', p.getvalue())


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
