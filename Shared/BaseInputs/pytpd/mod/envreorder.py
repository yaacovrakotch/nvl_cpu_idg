#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Env latest subroutine update.

Use main/tpenvreorder.py to call this routine as standalone tool.

Refer to this wiki for more info: https://wiki.ith.intel.com/x/4iEhag
"""
from gadget.gizmo import Elapsed
from gadget.errors import ErrorInput, ErrorCockpit, ErrorCheck
from gadget.files import File
from gadget.pylog import log
from gadget.disk import mkdirs
from gadget.strmore import utc2local
from pprint import pprint
from os.path import dirname, basename, exists
from collections import OrderedDict
from datetime import datetime
import glob


class EnvReorder:
    """Env HDST_PAT_PATH Reorder for latest subroutine"""

    def __init__(self, tpobj):
        self.tpobj = tpobj

    def main(self, disp=False, update=False):
        sw = Elapsed()

        # Calculate ordered path
        plistpath = self.tpobj.env.get_plist_paths()     # list of plist paths, with patches
        compath_list = [f'{dirname(x)}/pat/common_files' for x in plistpath if x.endswith('/plb')]
        compath_set = set(compath_list)                  # {/path/rev}
        pinobj = self.get_pinobj(compath_set)            # {/path/subrname: nn}
        subr_2nn = self.get_subr_2nn(pinobj)             # {subr: nn_latest}
        ordered_path = self.reorder_main(pinobj, subr_2nn)   # [/path/rev] final order

        # check
        pinobj_paths = {dirname(x) for x in pinobj}      # cannot use compath_set since compath_set does not include paths which have no subr
        assert len(ordered_path) == len(pinobj_paths), f'{len(ordered_path)} != {len(pinobj_paths)}'

        # update the env
        origpath = self.tpobj.env.get_contents('HDST_PAT_PATH', as_is=True)      # get from env; one big string
        origlist = origpath.split(';')                                           # convert to list
        mainpatlist = [x for x in origlist if not x.endswith('common_files')]    # remove common_files
        windows_ordered = [self.tpobj.env.to_winpath(x) for x in ordered_path]   # convert new paths (commonfiles) to windows
        finallist = self.build_final_list(mainpatlist, windows_ordered)          # build the final list
        self.tpobj.env.set_item('HDST_PAT_PATH', finallist)                      # replace env file with new list
        textenv = self.tpobj.env.rebuild()                                       # replace env file with new list

        if disp:
            print()
            print("Original list: =====")
            self.info(pinobj, subr_2nn, compath_list)

            print()
            print("New Re-ordered list: =====")
            self.info(pinobj, subr_2nn, ordered_path)

            print()
            print("Final Env: =====")
            print(textenv)

        if update:
            log.info(f"-i- Updating {self.tpobj.envfile} for latest subroutine order.")
            File(basename(f'{self.tpobj.envfile}.envreorder')).unlink()
            File(self.tpobj.envfile).rename(basename(f'{self.tpobj.envfile}.envreorder'))    # rename old file
            File(self.tpobj.envfile).touch(textenv)                                  # write new env file
            self.enverrchk()

        log.info(f'-z- EnvReorder(): Elapsed: {sw}')

        return ordered_path, windows_ordered, textenv

    def build_final_list(self, mainpatlist, windows_ordered):
        """
        Build the final list considering supercedes and D: and L: drives.
        Logic: Start the reorder when path starts with 'I:'

        :param mainpatlist: original list without commonfiles
        :param windows_ordered: commonfiles
        :return: final list
        """
        # Original code:
        # return [mainpatlist[0]] + windows_ordered + mainpatlist[1:]         # First one is supercede.

        # determine the index
        found = 0   # assume it starts at zero
        for idx in range(len(mainpatlist)):
            if mainpatlist[idx].startswith('I:'):
                found = idx
                break

        # return the final list
        return mainpatlist[:found] + windows_ordered + mainpatlist[found:]

    def enverrchk(self):
        """
        check if env.envreorder and .env exists
        Called after main
        """
        f = self.tpobj.envfile
        of = '%s.envreorder' % f
        if not exists(of) and exists(f):
            raise ErrorCheck('%s backup file is missing!' % of, 'Verify that the env reorder script has executed.')
        elif not exists(f) and exists(of):
            raise ErrorCheck('%s updated file is missing!' % f, 'tpenvreorder ran but updated env file is missing!')

        # if there are no errors, move the .env.envreorder files to the TPL/Reports directory
        mkdirs(f'{self.tpobj.tpldir}/Reports')
        File(of).move(f'{self.tpobj.tpldir}/Reports/', overwrite_rename=True)

    def reorder_main(self, pinobj, subr_2nn):
        """
        Try two algos: first brute force, second Ryan's reorder

        :param pinobj:
        :param subr_2nn:
        :return: ordered_path
        """
        # Algo 1
        try:
            return self.reorder(pinobj, subr_2nn)   # ryan's sorted algo
        except ErrorInput:
            pass

        # Algo 2 - last algo, Let it fail - for friendly error message
        log.info(f'-i- ENVREORDER_ALGO2 is running...')
        return self.reorder2(pinobj, subr_2nn)    # brute force algo

    @staticmethod
    def readlink_subr(fname, ut_arr):
        """
        Windows friendly equivalent of os.readlink(fname) specifically for subroutine files

        Assumptions:
        1. Files are softlink in the same dir (ie, direct file softlink)
        2. The filename based (same basename without extension)

        ut_arr is unittest hook
        """
        target = fname.replace('.pinObj', '_*.pinObj')
        refsha = File(fname).sha1()
        for ff in sorted(glob.glob(target), reverse=True):
            ut_arr.append(ff)
            if File(ff).sha1() == refsha:
                return basename(ff)   # Success

        return basename(fname)     # original. Cannot error out for flash, it does not have softlink

        # raise ErrorInput(f'Cannot find subroutine softlink equivalent of [{fname}].',
        #                  'Contact jqdelosr.')

    def get_pinobj(self, compath):
        """Return {/path/subrname: nn} datastructure"""
        pinobj = {}    # {/intel/Revxx/pat/common_files/mtl_comU_cf04y_sub11_J_0.pinObj: 15337}
        for path in compath:
            for ff in glob.glob(f'{path}/*_com*_0.pinObj'):
                ff = ff.replace('\\', '/')
                linkfile = self.readlink_subr(ff, [])
                # ntimestamp = linkfile.split('.')[0].split('_')[-1]

                # Do check
                # msg = f'Cannot derive rundir timestamp from [{linkfile}]. nn=[{ntimestamp}]'
                # assert len(ntimestamp) == 6 and ntimestamp.isdigit(), msg

                rtimestamp = self.get_nn_timestamp(f'{path}/{linkfile}')
                # print(ntimestamp, int(rtimestamp), ff)    # This is proof that timestamp is accurate, given a TP

                pinobj[ff] = int(rtimestamp)      # Previously ntimestamp is used, but due to PDX and ZSC10 (multi-site cfx) it does not work since rundir is different

        return pinobj

    @classmethod
    def get_nn_timestamp(cls, file_pinobj):
        """
        Get the internal timestamp, in secs, on pinobj file based on byte 38-43. Thanks to Ryan for deciphering this.

        byte 38 second
        byte 39 minute
        byte 40 hour
        byte 41 day
        byte 42 month
        byte 43 year

        :return: seconds (int)
        """
        with open(file_pinobj, 'rb') as ff:
            firstblock = ff.read(4096)

        sec = firstblock[38]
        min = firstblock[39]
        hr = firstblock[40]
        day = firstblock[41]
        mon = firstblock[42]
        yr = firstblock[43] + 1900

        # make sure structure is correct, in case where .pinobj changed
        assert 0 < day <= 31, f'Something changed in the {file_pinobj} structure: day is {day} (invalid)'
        assert 0 < mon <= 12, f'Something changed in the {file_pinobj} structure: month is {mon} (invalid)'
        assert 2015 < yr <= 2035, f'Something changed in the {file_pinobj} structure: year is {yr} (invalid)'

        dtobj = utc2local(f'{yr}-{mon:02}-{day:02}T{hr:02}:{min:02}:{sec:02}Z')

        # print(dobj.strftime("%Y-%m-%d %H:%M:%S"))    # Display normal time
        return datetime.timestamp(dtobj)

    def get_subr_2nn(self, pinobj):
        """Return {subr: nn_latest} datastructure given pinobj"""
        sorted_paths = sorted(pinobj, key=pinobj.get)       # [/rev/subr.pobj] ordered by nn descending
        subr_2nn = {basename(item): pinobj[item] for item in sorted_paths}
        return subr_2nn

    def reorder2(self, pinobj, subr_2nn):
        """
        Primary logic to reorder()

        Logic/Algo:
        1. Prepare data structures
              pinobj:   {/path/subroutine_name: nn}
              subr_2nn: {subroutine_namename: nn}
              pathset:  {set of paths}
        2. Initialize result array with one path
        3. Iterate each path (from pathset), insert path into result once it is a "success"
           "success" is when result has path when latest subroutine will be loaded.
           That is, try to insert path, one at a time, until first "success" order.

        :param pinobj: {path/subr: nn}
        :param subr_2nn: {subr: nn}
        :return: ordered path list
        """
        pathset = {dirname(x) for x in pinobj}

        # start with a path. Initialize array with one element.
        # It does not matter which one but choose first alphabetical so it's reproduceable
        result = [sorted(pathset, key=lambda x: x.lower())[0]]
        pathset.discard(result[0])
        # print(f'Initial: {result}')
        # pprint(pinobj)

        # iterate to each remaining path, then find where to insert, satisfying "latest" subroutine loaded
        for path in sorted(pathset, key=lambda x: x.lower()):
            # print(f"Target: {path}")
            for idx in reversed(range(len(result) + 1)):
                trial = list(result)   # make a copy
                trial.insert(idx, path)
                if self.success(pinobj, subr_2nn, trial):
                    result = trial
                    break
            else:
                print()
                print("Debug Information:")
                self.info(pinobj, subr_2nn, [path] + result)
                raise ErrorInput(f"Cannot insert {path} because it has new and old subroutine. "
                                 f"See above for detailed info.",
                                 f"Ask module {path} to run ci_plist to get latest subroutines.")

        return result

    def success(self, pinobj, subr_2nn, ordered_path, error_out=False):
        """
        Checks ordered_path if it good order. Return True if so

        :param pinobj: {path/subr: nn}
        :param subr_2nn: {subr: latest_nn}
        :param ordered_path: [list_of_ordered_path]
        :param error_out: Set to True to error out
        :return: Success state if ordered_path is correct
        """
        # These are the set of subr loaded for this ordered_path
        subr_valid = {basename(k): n for k, n in pinobj.items()
                      if dirname(k) in ordered_path and subr_2nn[basename(k)] == n}

        for subr in subr_valid:
            reference = subr_2nn[subr]

            for item in ordered_path:
                target = f'{item}/{subr}'
                if target in pinobj:
                    if pinobj[target] == reference:
                        break   # Success!
                    else:
                        if error_out:
                            raise ErrorInput('%s will load incorrectly from %s' % (subr, item),
                                             'Ask %s to rerun ci_plist' % item)
                        return False

            else:
                print("subr_valid:")
                pprint(subr_valid)
                print("pinobj:")
                pprint(pinobj)
                print("ordered_path:")
                pprint(ordered_path)
                raise ErrorCockpit("Unreachable code")

        return True

    def info(self, pinobj, subr_2nn, ordered_path):
        """Display info of ordered_path"""
        for item in ordered_path:
            print(f'{item}:')
            for subr in sorted(subr_2nn):
                target = f'{item}/{subr}'
                if target in pinobj:
                    if pinobj[target] == subr_2nn[subr]:
                        latest = ""
                    else:
                        latest = f"<< NOT LATEST (vs {subr_2nn[subr]})"
                    print(f"   {subr}: {pinobj[target]} {latest}")

    def reorder(self, pinobj, _):
        """
        Ryan's sorting algo - NOTE: cannot use this algo, it fails: test_new_may2

        IMPORTANT:
        They have to be sorted using a stable sort, otherwise the alphabetical order will get
        messed up because items will be sorted un-necessarily
        All standard library sorts in Python are stable sorts, in C# OrderBy is a stable
        variant of quicksort so it also works.

        :param pinobj: {path/subr: nn}
        :param _: unused, backwards compatibility with reorder2()
        :return: ordered path list
        """
        #       (module    , subr,        n_rev)
        rows = [(dirname(x), basename(x), pinobj[x]) for x in sorted(pinobj)]    # pinobj is dictionary, without order
        rows.sort(key=lambda x: x[0])    # sort by module first
        rows.sort(key=lambda x: x[2])    # sort by n_rev next low to high

        # At this point, rows is in correct order for module paths
        # get the unique module from the sorted list. Keep Order. Use OrderDict since there is no OrderSet.
        result = list(OrderedDict([(x[0], None) for x in rows]))

        # reverse the distinct list to get the subroutine order from biggest to smallest revision
        result.reverse()

        # Dependence cycle checking
        self.success(pinobj, self.get_subr_2nn(pinobj), result, error_out=True)

        return result
