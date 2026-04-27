#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Qgate base classes
"""
from pprint import pprint
from collections import defaultdict
from tp.testprogram import TestProgram
from gadget.pylog import log
from gadget.disk import Chdir
from gadget.gizmo import Elapsed
from gadget.shell import untar
from gadget.files import TempDir
from os.path import basename, dirname, exists
import os


class QGateBase:
    """Base class for qgates"""
    fulltpobj = None
    fulltp_tempdir = None

    def __init__(self, tpobj: TestProgram, frompr=False):
        """

        :param tpobj: TestProgram object
        :param frompr: bool (Set to True for standalone runs or unittests)
        """

        self.tpobj = tpobj
        self._frompr = frompr

        # error list of dictionary of {'message': <error message string>
        #                              'id': int,
        #                              'module': <module name>}
        self.result = []

        # passing list of dictionary of {(id, mod): <count>}
        self.passed = defaultdict(int)

        self._init_fulltp()

    def _init_fulltp(self):
        """Initialize once"""
        if QGateBase.fulltpobj:
            return 1    # do nothing
        self._fulltp_untar(self.tpobj)

    @classmethod
    def _fulltp_untar(cls, tpobj):
        """Create a Tempdir of the fulltp and store it in self.fulltpobj"""
        if not exists('complete_tp.tar.gz'):
            log.info('-i- Qgate: complete_tp.tar.gz does not exist')
            return

        QGateBase.fulltp_tempdir = TempDir()
        root = os.getcwd()
        with Chdir(QGateBase.fulltp_tempdir.get_name()):
            sw = Elapsed()
            untar(f'{root}/complete_tp.tar.gz', '.')
            QGateBase.fulltpobj = TestProgram(f'POR_TP/{basename(dirname(tpobj.envfile))}/EnvironmentFile.env')
            log.info(f'-i- complete_tp.tar.gz took: {sw}')

    def ut_result(self):
        """
        Return a string equivalent of self.result for easy self.assertTextEqual use
        :return: String (multi-line)
        """
        final = []
        for item in self.result:
            final.append(f'{item["id"]} {item["module"]} {item["message"]}')
        for item in sorted(self.passed):
            final.append(f'{item}: {self.passed[item]}')
        return '\n'.join(final)

    def add_pass(self, number, mod):
        """Increment the counter"""
        self.passed[(number, mod)] += 1

    def add_error(self, number, mod, text):
        """Add the error in the result"""
        self.result.append({'message': text,
                            'id': number,
                            'module': mod})

    def not_from_pr(self):
        """
        Normal usage, add below block of code at very top of main.

        # This qgate is applicable only on PR. Ignore for tpbuild.
        if self.not_from_pr():     # pragma: no cover
            log.info(f'-i- {self.__class__.__name__} is skipped, not from PR.')
            return 1

        :return: bool (True if caller not from PR, False if caller from PR)
        """
        if self._frompr:
            return False      # always False (based on usage)

        from_pr = (os.environ.get('FROM_PR', 'False')).strip().upper()      # this env var identifies if from PR
        return bool(from_pr != 'TRUE')

    def check(self, cond, number, mod, text):
        """
        Checks for cond, if True (passing), call add_pass(), else call add_error()
        :param cond: boolean condition
        :param number: number code
        :param mod: module
        :param text: error message
        :return: None
        """
        if cond:
            self.add_pass(number, mod)
        else:
            self.add_error(number, mod, text)

    def main(self):     # pragma: no cover
        raise Exception(f"Sorry! class {self.__class__.__name__} did not implement main()")

    def run(self):
        """Use this when calling from individual routine so the output is interpreted"""
        from main.qgate import QGateExecute
        self.main()    # execute

        print("Passing stats:")
        for (n, mod), cnt in sorted(self.passed.items()):
            print(f'Qgate#{n}: {mod:25s} pass count={cnt}')

        if not self.result:
            print()
            print("Success! no errors")
        else:
            print()
            print(f"There are errors: {len(self.result)}")
            for cnt, item in enumerate(self.result, 1):
                print(QGateExecute.get_error_line((item['module'], item['id'], item['message'])))
