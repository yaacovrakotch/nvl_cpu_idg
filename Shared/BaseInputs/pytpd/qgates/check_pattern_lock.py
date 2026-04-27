#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures pattern revs are locked.
This qgate will only run if FROM_PR env variable is set
"""
import sys
import setenv

from gadget.pylog import log
from gadget.errors import ErrorUser, confirm
from qgates.qgate_base import QGateBase
from gadget.files import File
from gadget.shell import IS_UNIX, SystemCall
from tp.testprogram import TestProgram
from gadget.strmore import day_code
from main.path_win_unix import ToUnix
from os.path import exists
import os
import re
import glob


class CheckLock:
    """
    Check pattern patch lock
    """

    def __init__(self, env):
        self.tpobj = TestProgram(env)     # This must be it's own object bec EnvEdit will fail
        self.checked = []

    def main(self):
        """Do the check and error out"""
        if self.tpobj.is_eng_tp():
            log.info('-i- Skipping pattern-lock check: ENG_TP')
            return 1
        if day_code() in sys.argv:
            log.info('-i- Skipping pattern-lock check. Day-code entered.')
            return 2

        unlocked = [x for x in self.get_pat_patch_unlocked()]
        if unlocked:
            log.info('')
            log.info('The following pattern paths are unlocked:')
            for path in unlocked:
                log.info(f'   {path}')
            elem = self.tpobj.envfile.replace('\\', '/').split('/')
            log.info('Pls run below command in unix to lock them all:')
            log.info(f'   source /p/pde/tvpv/mtl/sourceme.rc')
            log.info(f'   source /intel/tpvalidation/engtools/tptools/mtl/beta/latest/sourceme.rc')
            log.info(f'   cd {ToUnix().to_unix([os.getcwd()])}')
            log.info(f'   torch_fixer.py -lockall {elem[-3]}/{elem[-2]}/{elem[-1]}')
            log.info('')
            if self.error_lock_check(unlocked):
                raise ErrorUser(f'Unlocked pattern patch found. Count: {len(unlocked)}: {unlocked}',
                                ('If this is TP integration, then lock the patch first, see above for the command. '
                                 'Otherwise, to skip this check, execute with skip '
                                 'code [%s]' % day_code()))

        log.info(f'-i- pattern-lock path check count: {len(self.checked)}')

    @classmethod
    def error_lock_check(cls, unlocked):
        """
        Return True if error out, False if not
        all unlocked must have a regex
        """
        skipfile = glob.glob('POR_TP/*/InputFiles/allow_unlocked.txt')    # Each line of this is a regex
        if not skipfile:
            return True    # error out
        confirm(len(skipfile) == 1, f'Expecting one file only: {skipfile}', 'Pls remove extra files.')
        relist = list(File(skipfile[0]).chomp(comment='#', strip=True))

        for item in unlocked:
            matched = False
            for rstr in relist:
                if re.search(rstr, item):
                    matched = True
            if not matched:
                log.info(f'-i- error_lock_check(): [{item}] is not in allow_unlocked.txt')
                return True    # error out
        return False    # do not error, all unlocked is matched

    def get_pat_patch_unlocked(self):
        """Iterator: returns the path of pattern patch for unlocked revs"""
        self.tpobj.env.set_env()
        for item in sorted(self.tpobj.env.get_plist_paths()):
            if not item.endswith('plb'):
                continue       # skip slim path
            patchpath = os.path.dirname(item)
            if not exists(patchpath):
                continue       # skip sort paths (aka, unknown)

            self.checked.append(patchpath)
            if not exists(f'{patchpath}/locked'):
                yield patchpath

    def lock_it(self):
        """Lock all unlocked patches, called by torch_fixer"""
        confirm(IS_UNIX,
                'torch_fixer.py must be executed in unix environment for -lockall.',
                'Goto unix, cd %s; Then re-execute same command.' % ToUnix().to_unix([os.getcwd()]))

        confirm('VEP2_ROOT' in os.environ,
                'TVPV environment is not sourced. This is required for ci_plist.py.',
                'execute: source /p/pde/tvpv/mtl/sourceme.rc')

        robj = re.compile(r'[^\w](\w+)[^\w](Rev[\w\.]+)[^\w](p\d+)')
        cmd = ''
        for item in self.get_pat_patch_unlocked():
            res = robj.search(item)
            assert res, 'Cannot derive module/rev/patch in %r' % item
            module, rev, patch = (res.group(1), res.group(2), res.group(3))
            cmd = f'ci_plist.py -module {module} -rev {rev}{patch} -lock -dev -comment Lock_for_tp_integration'
            log.info(f'-i- CMD: {cmd}')
            code, out = SystemCall(cmd).run_outtxt()
            log.info(out)
            confirm(not code, 'ERROR occurred during ci_plist run', 'Check the output above!')

        return cmd    # for unittest


class QgatePatternLock(QGateBase):

    def main(self):
        """Entry point of checker"""

        # This qgate is applicable only on PR. Ignore for tpbuild.
        if self.not_from_pr():     # pragma: no cover
            log.info(f'-i- {self.__class__.__name__} is skipped, not from PR.')
            return 1

        try:
            CheckLock(self.tpobj.envfile).main()
            self.add_pass(249, 'BASE')
        except Exception as e:
            self.add_error(249, 'BASE', ErrorUser.get_main_error(e))


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    QgatePatternLock(TestProgram(sys.argv[1]), frompr=True).run()
