#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
runner pre-checks
This will raise exception if there are problems

"""
import setenv      # must be first in the imports
import glob
from gadget.shell import SystemCall
from gadget.pylog import log
from gadget.gizmo import Elapsed
import os
from gadget.errors import confirm


class PreCheck:

    def main(self):
        """Main entry point"""
        sw = Elapsed()

        self.no_engtp()

        log.info(f"Runner PreCheck() complete in {sw}")

    def get_changed_files(self):
        """Return what changed in this commit"""
        ecode, out = SystemCall('git diff HEAD^ HEAD --name-only').run_outtxt()
        confirm(ecode == 0,
                f"Something went wrong with git command: {out}",
                "Check output")
        files = out.split('\n')
        return files

    def no_engtp(self):
        pass


if __name__ == '__main__':  # pragma: no cover
    PreCheck().main()
