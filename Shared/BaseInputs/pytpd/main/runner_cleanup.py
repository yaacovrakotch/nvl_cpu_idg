#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This python file will be called from scheduler which will clean up the C and D drive if the storage space is less than 50GB.
One per physical machine/runner. Run hourly from scheduler.
"""
import setenv
from gadget.pylog import log
from gadget.files import File
from gadget.disk import get_free_diskspace
from gadget.gizmo import Elapsed
from os.path import exists, dirname, basename, isdir
import glob
import shutil
import os
import socket
from datetime import datetime, time
import time


# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class RunnerCleanUp:

    def __init__(self):
        self.runner_name = socket.gethostname()
        self.now_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.cleanup_file = f'I:/tpvalidation/engtools/tptools/mtl/infra/torch/runner_cleanup/{self.runner_name}_{self.now_str}_cleanup.txt'
        self.folder_to_cleanup = glob.glob(f'C:/Users/*/AppData/Local/Temp') + ['D:/TempDir']

    def cleanup_start(self):
        """
        Start cleanup process
        :return:
        """
        swtotal = Elapsed()
        sw = Elapsed()
        for folder in self.folder_to_cleanup:
            if os.path.exists(folder):
                log.info(f'Cleaning up folder: {folder}...')
                File(self.cleanup_file).logprint(f'Start cleaning up folder: {folder}...\n')
                # Get all the files and folders inside the target folder that is older than 24 hours and delete them
                todelete = []
                with os.scandir(folder) as fhdir:
                    for entry in fhdir:
                        if (time.time() - entry.stat().st_mtime) > 86400:
                            todelete.append(f'{folder}/{entry.name}')
                for item in todelete:
                    try:
                        if os.path.isfile(item) or os.path.islink(item):
                            os.remove(item)
                        elif os.path.isdir(item):
                            shutil.rmtree(item, ignore_errors=True)
                    except Exception as e:
                        log.warning(f'Could not remove {item}: {e}')
                        File(self.cleanup_file).logprint(f'Could not remove {item}: {e}\n')
                log.info(f'Successfully cleaned up folder: {folder}. Elapsed: {sw.elapsed(pretty=True, reset=True)}')
                File(self.cleanup_file).logprint(f'Finished cleaning up folder: {folder}. Elapsed: {sw.elapsed(pretty=True)}\n')
            else:
                log.info(f'Folder does not exist, skipping: {folder}')
                File(self.cleanup_file).logprint(f'Folder does not exist, skipping: {folder}\n')
        log.info(f'Total cleanup elapsed time: {swtotal.elapsed(pretty=True)}')
        File(self.cleanup_file).logprint(f'Total cleanup elapsed time: {swtotal.elapsed(pretty=True)}\n')

    def main(self):
        """
        Main entry point
        Check if the disk space is less than 50GB, if yes, start cleanup.
        :return:
        """
        log.info(f'Checking for runner {self.runner_name} to clean up...')
        cleanup_dir = ['C', 'D']
        for disk in cleanup_dir:
            log.info(f'Checking {disk}:/ drive...')
            disk_free = get_free_diskspace(f'{disk}:/')
            log.info(f"-i- DISKFREE_KB {disk}:/ : {disk_free}")
            if disk_free < 50000000:
                log.warning(f'{disk}:/ drive has less than 50GB free space. Start cleaning up space.')
                File(self.cleanup_file).touch(f"{disk} drive has less than 50GB free space. Clean up {disk} drive at {self.now_str}\n", newfile=True)
                self.cleanup_start()
                log.info(f'Finished cleaning up {disk}:/ drive. Log file: {self.cleanup_file}')

        log.info('Runner Clean Up Completed.')


if __name__ == '__main__':  # pragma: no cover
    RunnerCleanUp().main()
