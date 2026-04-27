#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
unittest for simple_ut.py
"""
from setenv_unittest import ROOT_ENV     # must be first import for unittests
from gadget import toml
from gadget.ut import TestCase, unittest
from gadget.files import File, TempDir
import pprint


class TomlTest(TestCase):

    def test_basic(self):
        # This is not a comprehensive test. This is just basic to make sure it works
        with TempDir(name=True) as tdir:
            File(f'{tdir}/a.toml').touch('''
# This is a TOML document

title = "TOML Example"

[owner]
name = "Tom Preston-Werner"

[database]
enabled = true
ports = [ 8000, 8001, 8002 ]
data = [ ["delta", "phi"], [3.14] ]
temp_targets = { cpu = 79.5, case = 72.0 }

[servers]

[servers.alpha]
ip = "10.0.0.1"
role = "frontend"

[servers.beta]
ip = "10.0.0.2"
role = "backend"
''')
            with open(f'{tdir}/a.toml') as fh:
                result = toml.load(fh)

            expect = """
{'database': {'data': [['delta', 'phi'], [3.14]],
              'enabled': True,
              'ports': [8000, 8001, 8002],
              'temp_targets': {'case': 72.0, 'cpu': 79.5}},
 'owner': {'name': 'Tom Preston-Werner'},
 'servers': {'alpha': {'ip': '10.0.0.1', 'role': 'frontend'},
             'beta': {'ip': '10.0.0.2', 'role': 'backend'}},
 'title': 'TOML Example'}
 """
            pprint.pprint(result)
            self.assertTextEqual(pprint.pformat(result), expect)

            # dumps
            output = toml.dumps(result)
            expect = '''
title = "TOML Example"

[owner]
name = "Tom Preston-Werner"

[database]
enabled = true
ports = [ 8000, 8001, 8002,]
data = [ [ "delta", "phi",], [ 3.14,],]

[database.temp_targets]
cpu = 79.5
case = 72.0

[servers.alpha]
ip = "10.0.0.1"
role = "frontend"

[servers.beta]
ip = "10.0.0.2"
role = "backend"
'''
            self.assertTextEqual(output, expect)

    def test_tz(self):
        text = '''
title = "TOML Example"
[owner]
dob = 1979-05-27T07:32:00-08:00
'''
        result = toml.loads(text)
        self.assertEqual(result['owner']['dob'].isocalendar(), (1979, 21, 7))

        expect = '''
title = "TOML Example"

[owner]
dob = 1979-05-27T07:32:00-08:00
'''
        self.assertTextEqual(toml.dumps(result), expect)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
