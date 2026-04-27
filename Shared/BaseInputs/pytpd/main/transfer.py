#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Transfer module - Everything that has to do with transferring and cross site

a) Display list of TP
    transfer.py host source_tp_dir EnvironmentFile.env
    transfer.py host source_tp_dir POR_TP/Class_ARL_S68/EnvironmentFile.env
b) Transfer one TP
    transfer.py host source_tp_dir/tpname destination
c) Update one TP (copy .plists and update .env)
    transfer.py <path>/file.env
"""
import setenv
import re
from gadget.files import File, TempDir
from gadget.errors import ErrorCockpit, confirm
from gadget.disk import mkdirs
from gadget.pylog import log
from gadget.gizmo import Elapsed
from gadget.shell import SystemCall
from os.path import basename, exists, dirname
from tp.testprogram import TestProgram, Env
import os
import sys
import glob


class TTP:    # Transfer TP
    """
    This class is meant to transfer TP from one site to another site
    Usage1: as a cron (give a folder, it will transfer all TP that was not transferred yet).
       Call TTP().main()

    Usage2: as individual transfer TP - see commandline
    """

    def __init__(self, host='al4vprtptxap1.ra.intel.com', eseu=False):
        """

        :param host: remote host name
        :param eseu: use p6vector if True
        """
        self.host = f'{host}:'
        self.eseu = ''
        self.tpobj = None     # Used only in update_one_tp
        if eseu:
            self.eseu = 'eseu.py'

    def main(self, rpath, genv, tlpath, dest):
        """
        Main Entry point - copy testprograms and return a list

        :param rpath: Remote path to where testprograms are. Expected structure is <rpath>/<tpname>
        :param genv: glob env. First star should represent <tpname>. eg. */EnvironmentFile.env for sort.
        :param tlpath: temporary local path to store env files that is already transferred
        :param dest: destination dir
        :return list of tp paths transferred
        """
        final = []
        for tpname in self.get_new_list_tp(rpath, genv, tlpath):
            self.xfer_one_tp(rpath, tpname, dest)
            final.append(f'{dest}/{tpname}')

        return final

    def update_one_tp(self, envfile):
        """
        Copy patterns and update the plb paths
        :param tpname: tpname
        :param dest: dir
        """
        sw = Elapsed()
        self.tpobj = TestProgram(envfile)
        dest = self.tpobj.tpldir

        # step2 - Get all pattern paths and copy them
        if exists(f'{dest}/plists'):
            print(f"-i- Nothing to do - {dest}/plists already exist")
            return

        mkdirs(f'{dest}/plists', mode='02770')
        self.tpobj.plists.set_plist_list()
        for ff in sorted(self.tpobj.plists.get_plist_list()):
            File(ff).copy(f'{dest}/plists')

        # step4 - update env .plist path to include plist/
        self._update_env(None, f'~HDMT_TPL_DIR/plists')

        log.info(f'-i- Transfer complete for {envfile} in {sw}')

    def xfer_one_tp(self, rpath, tpname, dest):
        """
        Transfer one TP and update the plb paths
        :param rpath: Remote path
        :param tpname: tpname
        :param dest: dir
        """

        sw = Elapsed()

        # step1 - rsync tp to destination
        self._xfer_tp(f'{rpath}/{tpname}', dest)

        # step2 - Get all pattern paths and copy them
        mkdirs(f'{dest}/{tpname}/plists', mode='02770')
        allpaths = [f'{x}/*.plist' for x in self._plb_paths(f'{dest}/{tpname}')]
        self._xfer_tp(allpaths, f'{dest}/{tpname}/plists', chmod=False)

        # step4 - update env .plist path to include plist/
        self._update_env(f'{dest}/{tpname}', f'{dest}/{tpname}/plists')

        log.info(f'-i- Transfer complete for {tpname} in {sw}')

    def _update_env(self, tppath, dest):
        """
        Update .env file to include /plists
        :param tppath: path to TP
        :return: list of plbpath in remote site
        """
        tpobj = self.tpobj if self.tpobj else TestProgram(Env.get_envfile(tppath))
        newval = tpobj.env.get_item('HDST_PLIST_PATH', islist=True)
        if 'Supersedes' in newval[0]:
            newval.insert(1, dest)    # second
        else:      # pragma: no cover   (just in case only)
            newval.insert(0, dest)    # first
        tpobj.env.set_item('HDST_PLIST_PATH', newval)
        File(tpobj.envfile).rewrite(''.join(tpobj.env.rebuild()), 'TTP.UpdateEnv()')

    def _plb_paths(self, tppath):
        """

        :param tppath: path to TP
        :return: list of plbpath in remote site
        """
        tpobj = self.tpobj if self.tpobj else TestProgram(Env.get_envfile(tppath))
        for item in tpobj.env.get_contents('HDST_PLIST_PATH', islist=True):
            ipath = item.replace('\\', '/').replace('I:/', '/intel/')
            yield ipath

    def get_new_list_tp(self, rpath, genv, tlpath):
        """
        Get list of New TP in rpath
        :return: list of <TPname>
        """
        cmd = f'{self.eseu} rsync -rlptoDzvR {self.host}{rpath}/{genv} {tlpath}'
        _, res = SystemCall(cmd, disp=True).run_outtxt()

        result = self._proc_rsync_output(res, genv)
        return result

    def _proc_rsync_output(self, txt, genv):
        """
        Process rsync output
        :param txt: rsync output
        :param genv: */Environmentfile.env
        :return: set of directories
        """
        # rsync output
        # ./nfs/td_sdx_1278_arh_prod_vol/td_1278_arh_prod_sds/hdmtprogs/ARHSDSCA0H68A03AIRS/EnvironmentFile.env

        xsplit = genv.split('/')
        idx = len(xsplit) * -1
        result = set()
        # print(f'env=[{env}] idx={idx}')
        for line in txt.split('\n'):
            if not line or line.startswith(('receiving incremental', 'sent ', 'total size')):
                continue
            if line.endswith('.env'):       # yes, hardcoded so we can use glob on the name
                result.add(line.split('/')[idx])

        return sorted(result)

    def _xfer_tp(self, src, dest, chmod=True):
        """
        Transfer tpname to destination and update chmod to be writable
        :param src: string or list (path)
        :param dest: string (destination dir)
        :param chmod: Set to True to chmod
        :return:
        """
        cmd = [self.eseu] if self.eseu else []
        if isinstance(src, list):
            cmd += ['rsync', '-rlptoDzv'] + [f'{self.host}{x}' for x in src] + [dest]
        else:
            cmd += ['rsync', '-rlptoDzv', f'{self.host}{src}', dest]
        _, res = SystemCall(cmd, disp=True).run_outtxt()
        if chmod:
            # cmd = f'{self.eseu} chmod -R g+w,u+w {dest}/{basename(src)}'   # all files
            # _, res = SystemCall(cmd, disp=True).run_outtxt()
            cmd = f'{self.eseu} chmod -R 02770 {dest}/{basename(src)}'     # main folder
            _, res = SystemCall(cmd, disp=True).run_outtxt()


def main():

    # display TP list in remote site
    if len(sys.argv) == 4 and sys.argv[3].endswith('.env'):
        host = sys.argv[1]
        source = sys.argv[2]
        env = sys.argv[3]
        obj = TTP(host, eseu=False)
        with TempDir(name=True) as tdir:
            result = obj.get_new_list_tp(source, f'*/{env}', tdir)
            print()
            print(f'List of TP in {source}:')
            print('\n'.join(result))
        return

    # Transfer one TP
    if len(sys.argv) == 4 and not sys.argv[3].endswith('.env'):
        host = sys.argv[1]
        sourcetp = sys.argv[2]
        dest = sys.argv[3]
        obj = TTP(host, eseu=False)
        obj.xfer_one_tp(dirname(sourcetp), basename(sourcetp), dest)
        return

    # Update one TP (copy .plists and update .env)
    if len(sys.argv) == 2 and sys.argv[1].endswith('.env'):
        obj = TTP()
        obj.update_one_tp(sys.argv[1])
        return

    # Invalid usage
    print(__doc__)


if __name__ == '__main__':  # pragma: no cover
    main()

    # transfer.py /nfs/td_sdx_1278_arh_prod_vol/td_1278_arh_prod_sds/hdmtprogs '*/EnvironmentFile.env' /infrastructure/p6vector/temp/testing /infrastructure/p6vector/temp/destination
    # TTP(eseu=True).main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
