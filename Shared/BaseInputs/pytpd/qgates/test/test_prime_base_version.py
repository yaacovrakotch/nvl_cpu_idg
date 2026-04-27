#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for prime_base_version.py
"""
import sys
try:
    from setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests
except ImportError:
    sys.path.append('/intel/tpvalidation/engtools/tptools/mtl/beta/latest')
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')
    from qgates.test.setenv_unittest import UT_DIR_REPO, ROOT_ENV     # must be first import for unittests

from qgates.prime_base_version import *        # replace this with your checker py.
from gadget.ut import TestCase, unittest, is_ut_option, MockVar
from gadget.files import TempDir, File
from gadget.helperclass import CaptureStdoutLog
from unittest.mock import Mock
import shutil


class TestPrimeBase(TestCase):

    def test_failcase(self):
        with TempDir(name=True, chdir=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple3'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(envfile)

            text = r'''<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageRestore>
    <add key="enabled" value="True" />
    <add key="automatic" value="True" />
  </packageRestore>
  <packageSources>
        <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="DDG" value="\\amr.corp.intel.com\ec\proj\mdl\jf\prod\hdmx_intel\tpapps\userlibs\mtl\prime_v11.03.01-evg5040604-tos31020-ddg231501\NuGets" />
    <add key="Prime" value="\\amr.corp.intel.com\ec\proj\mdl\jf\prod\hdmx_intel\tpapps\tmmlibs\prime\prime_v11.03.01-evg5040604-tos31020\lib\NuGets" />
    <add key="PrimeFeed" value="\\amr.corp.intel.com\ec\proj\mpe\MIT_ATE_TM\NuGets" />
    <add key="TRACE" value="\\amr.corp.intel.com\ec\proj\MDO\Global\MIG\TRACE\Nuget\Prod" />
    <add key="FuseLogicEngine" value=".\UserCode\nuget\fuse" />
    <add key="MPE_MIT" value="\\amr.corp.intel.com\ec\proj\MDO\Global\MIG\MIT" />
    <add key="UpsProdFeed" value="\\amr.corp.intel.com\ec\proj\MDO\Global\YBSP\UPS22\prod\facade" />
  </packageSources>
  <config>
     <add key="globalPackagesFolder" value=".\temp\packages" />
  </config>
</configuration>
'''
            File('TPL/NuGet.Config').touch(text, mkdir=True, newfile=True)
            obj = PrimeChecker(tpobj)
            obj.main()

            pprint(obj.result)
            expect = [{'id': 224,
                       'message': 'Prime versions dont match between env and nuget.config: '
                                  'Expecting prime_v2.01.01-evg5030702-tos3613 in nuget.config '
                                  'line#9',
                       'module': 'BASE'},
                      {'id': 224,
                       'message': 'Prime versions dont match between env and nuget.config: '
                                  'Expecting prime_v2.01.01-evg5030702-tos3613 in nuget.config '
                                  'line#10',
                       'module': 'BASE'}]

            self.assertEqual(obj.result, expect)
            self.assertEqual(obj.passed, {})

    def test_passcase(self):
        with TempDir(name=True, chdir=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple3'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(envfile)

            text = r'''<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageRestore>
    <add key="enabled" value="True" />
    <add key="automatic" value="True" />
  </packageRestore>
  <packageSources>
        <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="DDG" value="\\amr.corp.intel.com\ec\proj\mdl\jf\prod\hdmx_intel\tpapps\userlibs\mtl\prime_v2.01.01-evg5030702-tos3613-ddg231501\NuGets" />
    <add key="Prime" value="\\amr.corp.intel.com\ec\proj\mdl\jf\prod\hdmx_intel\tpapps\tmmlibs\prime\prime_v2.01.01-evg5030702-tos3613\lib\NuGets" />
    <add key="PrimeFeed" value="\\amr.corp.intel.com\ec\proj\mpe\MIT_ATE_TM\NuGets" />
    <add key="TRACE" value="\\amr.corp.intel.com\ec\proj\MDO\Global\MIG\TRACE\Nuget\Prod" />
    <add key="FuseLogicEngine" value=".\UserCode\nuget\fuse" />
    <add key="MPE_MIT" value="\\amr.corp.intel.com\ec\proj\MDO\Global\MIG\MIT" />
    <add key="UpsProdFeed" value="\\amr.corp.intel.com\ec\proj\MDO\Global\YBSP\UPS22\prod\facade" />
  </packageSources>
  <config>
     <add key="globalPackagesFolder" value=".\temp\packages" />
  </config>
</configuration>
'''
            File('TPL/NuGet.Config').touch(text, mkdir=True, newfile=True)
            obj = PrimeChecker(tpobj)
            obj.main()

            self.assertEqual(obj.result, [])
            self.assertEqual(obj.passed, {(224, 'BASE'): 2})

    def test_caseforgot(self):
        with TempDir(name=True, chdir=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple3'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(envfile)

            text = r'''<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageRestore>
    <add key="enabled" value="True" />
    <add key="automatic" value="True" />
  </packageRestore>
  <packageSources>
        <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="DDG" value="\\amr.corp.intel.com\ec\proj\mdl\jf\prod\hdmx_intel\tpapps\userlibs\mtl\prime_v2.01.00-evg5030702-tos3613-ddg231501\NuGets" />
    <add key="Prime" value="\\amr.corp.intel.com\ec\proj\mdl\jf\prod\hdmx_intel\tpapps\tmmlibs\prime\prime_v2.01.01-evg5030702-tos3613\lib\NuGets" />
    <add key="PrimeFeed" value="\\amr.corp.intel.com\ec\proj\mpe\MIT_ATE_TM\NuGets" />
    <add key="TRACE" value="\\amr.corp.intel.com\ec\proj\MDO\Global\MIG\TRACE\Nuget\Prod" />
    <add key="FuseLogicEngine" value=".\UserCode\nuget\fuse" />
    <add key="MPE_MIT" value="\\amr.corp.intel.com\ec\proj\MDO\Global\MIG\MIT" />
    <add key="UpsProdFeed" value="\\amr.corp.intel.com\ec\proj\MDO\Global\YBSP\UPS22\prod\facade" />
  </packageSources>
  <config>
     <add key="globalPackagesFolder" value=".\temp\packages" />
  </config>
</configuration>
'''
            File('TPL/NuGet.Config').touch(text, mkdir=True, newfile=True)
            obj = PrimeChecker(tpobj)
            obj.main()
            expect = [{'id': 224,
                       'message': 'Prime versions dont match between env and nuget.config: '
                                  'Expecting prime_v2.01.01-evg5030702-tos3613 in nuget.config '
                                  'line#9',
                       'module': 'BASE'}]

            self.assertEqual(obj.result, expect)
            self.assertEqual(obj.passed, {(224, 'BASE'): 1})

    def test_nonuget(self):
        with TempDir(name=True, chdir=True) as tdir:
            tpref = f'{UT_DIR_REPO}/Simple3'
            shutil.copytree(tpref, f'{tdir}/TPL')
            envfile = f'TPL/POR_TP/TGLH81/EnvironmentFile.env'
            tpobj = TestProgram(envfile)
            obj = PrimeChecker(tpobj)
            obj.main()

            self.assertEqual(obj.result, [])
            self.assertEqual(obj.passed, {})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
