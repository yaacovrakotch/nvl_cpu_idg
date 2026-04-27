#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Various torch fixer routines.
usage:
cd <your_root_path>
torch_fixer.py     # no args means fix .bdef
torch_fixer.py <file.mtpl> ... -link
torch_fixer.py <file.mtpl> ... -counters
torch_fixer.py <file.mtpl> -removeme <composite_name>
torch_fixer.py <file.mtpl> -format
torch_fixer.py -lockall <env>
torch_fixer.py <exported_tp_path> -tar /destination/file.tar
torch_fixer.py path1.env path2.env -multibom /destination_path
torch_fixer.py path1.env -bin

"""
import setenv      # must be first in the imports
import glob
from gadget.vepargs import Args, TA_StoreTrue, TA_All, TA_Store
from gadget.helperclass import OPT
from gadget.dictmore import DictDot
from gadget.pylog import log
from gadget.files import File, TempDir
from gadget.gizmo import Elapsed, count_iter
from gadget.shell import HOSTNAME, SystemCall, IS_UNIX
from gadget.strmore import curtime, truncate
from gadget.tputil import OtplFile, CheckerLog, MtplBlocks
from gadget.errors import ErrorUser, ErrorInput, confirm, ErrorCockpit
from gadget.printmore import PctIndicator
from gadget.disk import Chdir, Allfiles, mkdirs
from tp.testprogram import TestProgram, Env
from tp.mtpl import BM
from mod.mtplencode import MtplEncode
from mod.tppostproc import BinHack, BinHack2
from main.torch_postproc import TorchPostProc
from qgates.check_pattern_lock import CheckLock
from os.path import basename, realpath, dirname, exists, abspath
from collections import defaultdict
from pprint import pprint
import re
import os
import tarfile


# Below is a simple way to inform user if they are python version <3.5. This is checked before any other code during the Parsing phase.
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: http://python.org/downloads'


class Fixer(Args):

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.all = TA_All('see usage')
        cfg.multibom = TA_Store('CMD: Do multibom run', metavar='dest_dir')
        cfg.tar = TA_Store('CMD: tar <first arg> directory', metavar='dest_dir/filename.tar')
        cfg.lockall = TA_Store('CMD: lock all unlocked pattern paths', metavar='file.env')
        cfg.link = TA_StoreTrue('CMD: Update the .mtpl for composite links.')
        cfg.stencil = TA_StoreTrue('CMD: Create the Stencil .mtpls.')
        cfg.counters = TA_StoreTrue('CMD: Update the .mtpl for new counters')
        cfg.removeme = TA_Store('CMD: remove a composite given .mtpl', metavar='composite_to_remove')
        cfg.reorder = TA_StoreTrue('CMD: Reorder the .mtpl for diff')
        cfg.format = TA_StoreTrue('CMD: Auto-format .mtpl / fix indents')
        cfg.sort = TA_StoreTrue('Do not run MTL class BinHack routine.')
        cfg.bin = TA_StoreTrue('Run tos4 binhack only')
        return cfg

    def main(self):
        """Main Entry point"""
        self.call_methods(['multibom',    # this will call do_multibom(), if -multibom
                           'tar',         # this will call do_tar(), if -tar
                           'lockall',     # this will call do_lockall(), if -lockall
                           'link',        # this will call do_link(), if -link
                           'stencil',     # this will call do_stencil(), if -stencil
                           'counters',    # this will call do_counters(), if -counters
                           'removeme',    # this will call do_removeme(), if -removeme
                           'reorder',     # this will call do_reorder(), if -reorder
                           'format',      # this will call do_format(), if -format
                           'bin',         # this will call do_bin(), if -bin
                           ])

    def do_bin(self):
        """
        -bin  (for TOS4)
        """
        confirm(OPT.all, 'Usage: torch_fixer.py path/file.env -bin', 'Pls specify tp env file')
        tp = TestProgram(OPT.all[0])
        BinHack2(tp).main()

    def do_format(self):
        """
        -format
        """
        assert OPT.all, 'Usage: torch_fixer.py <file.mtpl> ... -format'
        for fname in OPT.all:
            log.info(f'-i- Processing {fname}')
            OtplFile(fname).reformat()

    def do_reorder(self):
        """-reorder"""
        assert OPT.all, 'Usage: torch_fixer.py <file.mtpl> ... -reorder'
        for fname in OPT.all:
            log.info(f'-i- Processing {fname}')
            mb = MtplBlocks(fname)
            mb.write('-reorder')

    def do_counters(self):
        """-counters"""
        assert OPT.all, 'Usage: torch_fixer.py <file.mtpl> ... -counters'
        for fname in OPT.all:
            log.info(f'-i- Processing {fname}')
            mb = MtplBlocks(fname)
            MtplEdit(mb).update_counters()
            mb.write('counters()')

    def do_removeme(self):
        """-removeme"""
        assert len(OPT.all) == 1, 'Usage: torch_fixer.py <file.mtpl> -removeme composite_to_remove'
        fname = OPT.all[0]
        log.info(f'-i- Processing {fname}')
        mb = MtplBlocks(fname)
        MtplEdit(mb).removeme(OPT.removeme)
        mb.write('removeme')

    def do_link(self):
        """-link"""
        print("Executing -link")
        assert OPT.all, 'Usage: torch_fixer.py <file.mtpl> ... -link'
        for mtpl in OPT.all:
            CompLink(mtpl).main()

    def do_stencil(self):
        """-stencil"""
        print("Executing -stencil")
        assert OPT.all, 'Usage: torch_fixer.py <file.mtpl> ... -stencil'
        for mtpl in OPT.all:
            Stencil(mtpl).main()

    def do_lockall(self):
        """-lockall"""
        print("Executing -lockall:")
        return CheckLock(OPT.lockall).lock_it()

    def do_multibom(self):
        """-multibom"""
        MultiBom(OPT.all).main(OPT.multibom)

    def do_tar(self):
        """Create tar file"""
        # create tar file
        tarname = f'{OPT.tar}.gz'
        mkdirs(dirname(tarname))
        print(f'-i- Creating tarfile...')
        with TempDir(name=True) as tdir:
            tmptar = os.path.join(tdir, basename(tarname))
            with Chdir(OPT.all[0]):
                sw1 = Elapsed()
                with tarfile.open(tmptar, "w:gz") as tarfh:
                    tarfh.add('.')

            print(f'-i- Transferring tarfile...')
            sw2 = Elapsed()
            if IS_UNIX:
                cmd = ['cp', tmptar, tarname]
            else:
                cmd = ['copy', '/Y', os.path.normpath(tmptar), os.path.normpath(tarname)]
            code, out = SystemCall(cmd).run_outtxt()

        confirm(not code,
                "Something went wrong while calling cp. Output:\n%s" % out,
                "Pls use gitbash or check output above.")

        log.info(f'Done! tarfile create: {sw1}, tarfile transfer: {sw2}')
        log.info(f'Execute below in unix:')
        log.info(f'   cd {dirname(tarname)}      # convert to unix path: /i is /intel')
        log.info(f'   tar -z -xvf {basename(tarname)}')

    def do_else(self):
        """
        Entry point to various fixers.
        Calling this script the 2nd time should *do nothing*
        """
        DoFixer().main(bdef_mods=OPT.all)


class DoFixer:

    def __init__(self):
        self.env_glob = './POR_TP/*/EnvironmentFile*.env'
        self.envs = glob.glob(self.env_glob)
        self.start_sw = Elapsed()

    def main(self, bdef_mods=[]):
        """Main entry point"""
        if TorchPostProc.is_tos4():
            self.main_tos4(bdef_mods)
        else:
            log.info('-i- ARL fixer')
            self.main_arl(bdef_mods)

    def main_tos4(self, bdef_mods):
        """TOS4 fixer"""
        TorchPostProc.common_checks(self.envs, self.env_glob)
        TorchPostProc.set_repo_sha()

        # Initialize: Create tp_shared list
        tp_shared = self.get_tp_shared()    # list of tpobj

        # Per tpobj
        for tpobj in tp_shared:
            # Call meta_info
            MtplEncode(tpobj).generate_meta()

        log.info(f'-i- Fixer: Runtime: {self.start_sw}, at {HOSTNAME}, {curtime()}')

    def main_arl(self, bdef_mods):
        """ARL fixer"""
        TorchPostProc.common_checks(self.envs, self.env_glob)
        TorchPostProc.set_repo_sha()

        # Initialize: Create tp_shared list
        tp_shared = self.get_tp_shared()    # list of tpobj

        # Call Composite link only
        for mtpl in CompLink.find_comp_modules('_LINK'):
            CompLink(mtpl).main()

        # Call Stencil
        for mtpl in CompLink.find_comp_modules('_SRC'):
            Stencil(mtpl).main()

        # Per tpobj
        for tpobj in tp_shared:
            # Call meta_info
            MtplEncode(tpobj).generate_meta()

        # Call BdefFix() twice
        BdefFix(*tp_shared, mods=bdef_mods).main(shared=False)    # first run
        if not OPT.sort:
            BinHack(tp_shared[0].envfile).main()    # one only .env only

        # second run (sorting, after BdefHack is called)
        BdefFix(*tp_shared, mods=bdef_mods).main(shared=False)
        if not OPT.sort:
            BinHack(tp_shared[0].envfile).main()    # one only .env only

        log.info(f'-i- Fixer: Runtime: {self.start_sw}, at {HOSTNAME}, {curtime()}')

    def get_tp_shared(self):
        """Return list of tpobj"""
        tp_shared = []
        for env in sorted(self.envs):
            if env.endswith('.g.env'):     # Cannot process these - torch generated in pobj cache
                log.info(f'-i- Fixer: skipping env {env}')
                continue
            tpobj = TestProgram(env)
            tp_shared.append(tpobj)
        return tp_shared


class CompLink:
    """
    Composite Link - one mtpl

    Strategy:
    1. Find all composite link, process it in proc_composite()
       * Read all "Test" and "DUTFlow" blocks in the composite link and put in result dict
       * Search and replace in result dict, then accumulate to self.mb.final
    2. result and self.mb.final is a dictionary {block_name: list_of_modified_lines}
    3. new block_names are added, modified block_names are renamed (and DUTFlowInfo updated)
    4. Rewrite to destination .mtpl
    """

    def __init__(self, mtpl):
        """
        :param mtpl: input mtpl file
        """
        self.mtpl = mtpl
        self.mb = MtplBlocks(mtpl)

    def main(self, iswrite=True):
        """
        Process one mtpl file
        :param iswrite: Set to False to not write
        """
        # step1: Find composite with "_LINK$"
        comp_links = list(self.find_comp_links())
        if not len(comp_links):
            log.info(f"No composite link found in {self.mtpl}. Skipping...")
            return

        # step2: Iterate to all composites
        for comp_line, cfg in comp_links:

            # Process this composite ============================
            result = {}         # resulting block: {block_name: list_of_lines}
            dutflowitem_linkname = comp_line.split()[1]
            src_composite = comp_line.split()[2]

            # Get Definition block of source_composite, including testinstance blocks, put in a list, recursive
            self.mb.recurse(src_composite, result)

            # Do search and replace for the resulting block
            self.search_and_replace(result, cfg)
            self.connect_new(result, comp_line, src_composite, cfg)
            self.instance_options(result, cfg['linkname'])
            self.dutflow_options(result, cfg['linkname'])

            # Integrate into final list
            self.integrate_to_final(result, dutflowitem_linkname)
            # end composite ======  check result and self.mb.final here for debug ======================

        # step3: Update counters
        MtplEdit(self.mb).update_counters()

        # step4: Write mtpl
        if iswrite:
            self.mb.write('CompLink', self.destination())

    def get_config_info(self, link_block, src_composite):
        """
        Process the config information for the link_block

        :param link_block: input link block that has configuration
        :param src_composite: source composite name
        :return: cfg dictionary: {'find': [{'search': <value>, 'group': 1, 'replace': <value>}]}
        """
        cfg = {'find': [],
               'status': None}
        robj = re.compile(r'#\s+find:(.*)\s+replace:([-\d]+):(.*)$')
        robj2 = re.compile(r'#\s+(status|linkname):(.*)$')
        for line in self.mb.ofile.get_block('DUTFlowItem', link_block):    # cannot use parsed here because of the comments
            res = robj.search(line)
            if res:
                r_replace = res.group(3)
                r_replace.rstrip()
                if r_replace == 'NONE':
                    r_replace = ''    # Empty
                cfg['find'].append({'search': res.group(1),
                                    'group': int(res.group(2)),
                                    'replace': r_replace.replace('$', '\\')})
            res = robj2.search(line)
            if res:
                cfg[res.group(1)] = res.group(2).strip()

        # Required configs
        confirm('linkname' in cfg,
                f'[# linkname:] configuration is not found for composite-link for {link_block}',
                f'Pls check {link_block}, see https://wiki.ith.intel.com/x/afRQmw')

        return cfg

    def search_and_replace(self, result, cfg):
        """
        Search and replace all items in result given cfg dictionary
        :param result: {key: list_of_lines}
        :param cfg: dictionary (see get_config_info)
        :return: Total replaced
        """
        ctr = 0
        for finditem in cfg['find']:
            # intialization
            item_group = finditem['group']
            item_replace = finditem['replace']
            search_str = finditem['search']
            if '(' not in search_str:
                search_str = f'({search_str})'
            robj = re.compile(search_str)

            # search and replace all blocks
            for name in result:
                linelist = result[name]
                for idx in range(len(linelist)):
                    res = robj.search(linelist[idx])
                    if res:
                        ctr += 1
                        if item_group == -1:
                            linelist[idx] = robj.sub(item_replace, linelist[idx])
                        else:
                            linelist[idx] = linelist[idx].replace(res.group(item_group), item_replace)

            # index (key) replace
            for name in list(result):
                res = robj.search(name)
                if res:
                    if item_group == -1:
                        newname = robj.sub(item_replace, name)
                    else:
                        newname = name.replace(res.group(item_group), item_replace)
                    result[newname] = result[name]
                    del result[name]

        return ctr

    def connect_new(self, result, comp_line, src_composite, cfg):
        """
        Connect the new composite link
        :param result: result dictionary
        :param comp_line: original composite line
        :param src_composite: source composite name
        :param cfg: config dictionary
        """
        newname = cfg['linkname']
        from_name = '__NOT_FOUND__'
        to_name = '__NOT_FOUND__'
        if cfg['find']:
            from_name = cfg['find'][0]['search']
            to_name = cfg['find'][0]['replace']

        # step1: replace the original composite line
        new_dutflow_name = None
        for item in self.mb.blocks.values():    # This is original values
            found = False
            for idx in range(len(item)):
                if item[idx].strip().startswith(comp_line):
                    elems = item[idx].strip().split()
                    if from_name in elems[2]:
                        new_dutflow_name = elems[2].replace(from_name, to_name)
                    else:
                        new_dutflow_name = f'{elems[2]}_{newname}'

                    if len(elems) > 3:    # @EDC case
                        item[idx] = f'    DUTFlowItem {elems[1]} {new_dutflow_name} {" ".join(elems[3:])}\n'
                    else:
                        item[idx] = f'    DUTFlowItem {elems[1]} {new_dutflow_name}\n'
                    found = True
                if found and item[idx].strip().startswith('#') and 'linkname:' in item[idx]:
                    item.insert(idx, '    # status: DONE\n')
                    found = False

        # step2: replace the src composite block
        confirm(new_dutflow_name, f'Cannot find [{comp_line}] in [{self.mtpl}]', 'Contact jqdelosr')
        if src_composite in result:
            result[new_dutflow_name] = result[src_composite]
            del result[src_composite]
            result[new_dutflow_name][0] = result[new_dutflow_name][0].replace(src_composite, new_dutflow_name)
        else:
            confirm(new_dutflow_name in result,
                    f'[{src_composite}] is not found in {self.mtpl}.',
                    f'Pls check mtpl')

    def instance_options(self, result, linkname, keyword='LINK'):
        """
        Update Test instances with composite link options - param based
        :param result: result dictionary
        :param linkname: linkname
        :param keyword: string keyword
        """
        robj = re.compile(fr'^\s*# {keyword}:{linkname}:(.*)$')
        for lines in result.values():
            if not lines[0].strip().startswith(('Test ', 'CSharpTest ')):
                continue    # Only look at Test instances
            for idx in range(len(lines)):
                res = robj.search(lines[idx])
                if res:
                    # config exist, replace this
                    newval = res.group(1)
                    param = newval.strip().split()[0]
                    found = False
                    for idx2 in range(len(lines)):
                        if lines[idx2].strip().startswith(f'{param} '):
                            found = True
                            lines[idx2] = f'    {newval}\n'

                    confirm(found,
                            f"Error: param [{param}] is not found in [{lines[0].rstrip()}] of {self.mtpl}",
                            f"[{param}] must be defined, eg. '{param} = <value>;'")

    def dutflow_options(self, result, linkname, keyword='LINK'):
        """
        Update DUTFlow instances with composite link options - replace immediate line above it
        :param result: result dictionary
        :param linkname: linkname
        :param keyword: string keyword
        """
        robj = re.compile(fr'^\s*# {keyword}:{linkname}:(.*)$')
        prev_idx = None
        for lines in result.values():
            if not lines[0].strip().startswith('DUTFlow '):
                continue    # Only look at DUTFlow
            for idx in range(len(lines)):
                if not lines[idx].strip():
                    continue    # ignore empty lines
                res = robj.search(lines[idx])
                if res:
                    # config exist, replace immediate line above
                    resindent = re.search(r'^(\s*)', lines[prev_idx])
                    lines[prev_idx] = '%s%s\n' % (resindent.group(1), res.group(1))
                else:
                    prev_idx = idx

    def integrate_to_final(self, result, comp_link):
        """
        Integrate result into final list.
        Strategy: Existing testinstance blocks should be unchanged
        :param result: input dictionary
        :param comp_link: Name of composite link
        """
        # rename first if the Test|DUTFlow content is different
        for _ in range(500):
            updated = False
            for name in list(result):
                is_test = bool(result[name][0].strip().startswith(('Test ', 'DUTFlow ', 'CSharpTest ')))
                if is_test and name in self.mb.final and self.mb.final[name] != result[name]:
                    self.rename_test(name, result)
                    updated = True
            if not updated:
                break    # Done
        else:  # pragma: no cover  - safety check only
            raise ErrorCockpit('Reached maximum iteration in integrate_to_final().',
                               'Contact jqdelosr and give him your .mtpl testcase so this corner case can be fixed.')

        # add in final
        for name in result:
            if name in self.mb.final:
                confirm(self.mb.final[name] == result[name],
                        f'Generated contents are different for block [{name}] in [{comp_link}].',
                        f'Check {self.mtpl}')
                continue
            self.mb.final[name] = result[name]

    def rename_test(self, name, result, _maxiter=100):
        """
        Rename testinstance or dutflow
        :param name: target name
        :param result: dictionary
        :param _maxiter: maximum iteration
        :return: None
        """
        # get new name first
        for idx in range(_maxiter):
            newname = f'{name}_{idx}'
            if newname in self.mb.final or newname in self.mb.blocks:   # mb.blocks is original values
                _ = None     # coverage
                continue
            break     # Done we have a new name
        else:
            raise ErrorCockpit("Maximum name iteration in rename_test()", "Pls contact jqdelosr")

        # rename key
        result[newname] = result[name]
        del result[name]
        result[newname][0] = result[newname][0].replace(name, newname)

        # rename DUTFlow lines. Make sure it is exact match
        robj = re.compile(r'^(.*)\b' + name + r'\b(.*)$')
        for item in result:
            if result[item][0].strip().startswith(('Test ', 'MultiTrialTest ', 'CSharpTest ')):
                continue     # Do not process Test. Process only all other blocks
            for idx in range(len(result[item])):
                for _ in range(10):
                    if robj.search(result[item][idx]):
                        result[item][idx] = robj.sub(r'\1' + newname + r'\2', result[item][idx])
                    else:
                        break
                else:
                    raise ErrorCockpit("Maximum replace iteration in rename_test()", "Pls contact jqdelosr")

    def find_comp_links(self):
        """
        Iterator Find all composite links
        :return: (line, cfg); line is DUTFlow with _LINK; cfg is dictionary
        """
        for _, line in self.mb.ofile.mlines:
            elems = line.split()
            if elems[0] == 'DUTFlowItem':
                dutflowitem_linkname = elems[1]
                src_composite = elems[2]
                if dutflowitem_linkname.endswith('_LINK'):
                    cfg = self.get_config_info(dutflowitem_linkname, src_composite)    # get the link configuration
                    if not cfg['status']:
                        yield line, cfg

    def destination(self):
        """
        :return: destination mtpl file name
        """
        # method1 - different directory
        dname = dirname(abspath(self.mtpl))
        res = re.search('^(.*)(_LINK|_SRC)$', dname)
        if res:
            targetpath = res.group(1)
            confirm(exists(targetpath),
                    f'{targetpath} does not exist',
                    f'Pls copy files from {dname} to {targetpath}')
            bname = basename(self.mtpl)
            if bname.startswith('src_'):
                return f'{targetpath}/{bname[4:]}'
            else:
                return f'{targetpath}/{bname}'

        # method2 - update the source / same directory
        return self.mtpl

    @classmethod
    def find_comp_modules(cls, which):
        """
        Iterator Find all composite modules (w/ _LINK)
        :param which: '_LINK' for comp link or '_SRC' for Stencil
        :return: path to mtpl
        """
        confirm(exists('Modules'),
                f'[Modules/] folder is not found in {os.getcwd()}',
                f'Check current working directory.')
        for ff in (glob.glob('Modules/*/*.mtpl') + glob.glob('Modules/*/*/*.mtpl')):
            modname = basename(dirname(ff))
            if modname.endswith(which):
                yield ff


class Stencil:
    """
    Template based mtpl
    """

    def __init__(self, mtpl):
        """
        :param mtpl: input mtpl file
        """
        self.mtpl = mtpl

    def main(self):
        """Entry point: read source mtpl and write many mtpls"""
        for cfg in self.get_stencil_info():
            cl = CompLink(self.mtpl)     # This has the main MTplBlocks object

            # remove composite first
            for removeblock in cfg['remove']:
                MtplEdit(cl.mb).removeme(removeblock)

            # call composite link routine (composite copy and link)
            cl.main(iswrite=False)       # Just update mb, do not write to file

            # search and replace global
            total = cl.search_and_replace(cl.mb.final, cfg)
            cl.mb.head.insert(0, f'# {cfg["name"]}: Total Replaced {total}\n')

            # instance options
            cl.instance_options(cl.mb.final, cfg['name'], 'stencil')

            # dutflow options
            cl.dutflow_options(cl.mb.final, cfg['name'], 'stencil')

            # update counters then write it
            MtplEdit(cl.mb).update_counters()
            cl.mb.write('Stencil', cfg['filename'])

    def get_stencil_info(self):
        """
        Iterator: Process the config information for the link_block
        :return: list of dictionaries, cfg dictionary: [{'find': [{'search': <value>, 'group': 1, 'replace': <value>}]}]
        """
        mb = MtplBlocks(self.mtpl)
        r_start = re.compile(r'^\s*#\s+stencil start:\s*(\w+)')
        r_find = re.compile(r'#\s+find:(.*)\s+replace:([-\d]+):(.*)$')
        r_attrib = re.compile(r'#\s+(filename|remove):\s*(\S.*)$')
        final = []   # may contian None
        cfg = None
        for lno, line in enumerate(mb.ofile.alines):    # mlines does not have comments
            if line.strip().startswith('ProgramStyle'):
                final.append(cfg)   # Add the final one
                break

            # config start
            res = r_start.search(line)
            if res:
                final.append(cfg)    # Add previous
                cfg = {'name': res.group(1),
                       'remove': [],
                       'find': []}

            # attrib
            res = r_attrib.search(line)
            if res:
                confirm(cfg, f'Config error: "stencil start:" is missing!', f'Check {self.mtpl}, line#{lno+1}')
                cfg[res.group(1)] = res.group(2).strip()

            # search and replace
            res = r_find.search(line)
            if res:
                confirm(cfg, f'Config error: "stencil start:" is missing!', f'Check {self.mtpl}, line#{lno+1}')
                r_replace = res.group(3)
                r_replace.rstrip()
                if r_replace == 'NONE':
                    r_replace = ''    # Empty
                cfg['find'].append({'search': res.group(1).strip(),
                                    'group': int(res.group(2)),
                                    'replace': r_replace.replace('$', '\\')})
        else:
            raise ErrorUser(f'Cannot find "ProgramStyle" - required on {self.mtpl}')

        # Required configs and processing
        if final == [None]:
            log.info(f"No Stencil found in {self.mtpl}")

        for cfg in final:
            if cfg:
                # convert remove to list
                if cfg['remove']:
                    cfg['remove'] = [x.strip() for x in cfg['remove'].split(',')]

                # check
                confirm('filename' in cfg,
                        f'[# filename:] configuration is not found for composite-link for {cfg["name"]}',
                        f'Pls check {cfg["name"]}')

                if realpath(cfg['filename']) == realpath(self.mtpl):
                    log.info(f'Skipping {cfg["filename"]}, output file')
                else:
                    yield cfg


class MtplEdit:
    """
    Independent Routines that act on MtplBlock

    # Usage example:
    mb = MtplBlocks('a.mtpl')
    MtplEdit(mb).update_counters()
    mb.write('caller_name')
    """

    def __init__(self, mb):
        """
        :param mb: MtplBlock object
        """
        self.mb = mb

    def update_counters(self):
        """
        Update counters for newly added stuff, based on self.mb.final
        """
        # read the counters
        counters = set()
        for line in self.mb.ofile.get_block('Counters', parsed=True):
            if line.startswith(('Counters', '}', '{')):
                continue
            counters.add(line.replace(',', ''))

        # get all counters to add
        to_add = set()
        robj = re.compile(r'^\s*IncrementCounters\s+([\w:]+)\s*;')
        for lines in self.mb.final.values():
            for line in lines:
                if line.strip().startswith('IncrementCounters'):
                    res = robj.search(line)
                    if res:
                        ctr = res.group(1)
                        if ':' in ctr:
                            ctr = ctr.split(':')[2]
                        if ctr not in counters:
                            to_add.add(ctr)

        if not to_add:
            return 1   # Nothing to add

        # update the counters - add them
        for idx in range(len(self.mb.head)):
            if self.mb.head[idx].strip() == 'Counters':
                for item in sorted(to_add):
                    self.mb.head.insert(idx + 2, f'    {item},\n')
                break
        else:   # pragma: no cover  - safety check only
            raise ErrorUser(f'Check {self.mb.fname}. Cannot find "Counters"')
        return 0

    def removeme(self, block):
        """
        :param block: block to remove
        :return: Unneeded blocks
        """
        rblock = {}    # dictionary of items needed by removeme block
        self.mb.recurse(block, rblock)

        # get all composites
        df = set()     # All DutFlow composites
        for name in self.mb.btype:
            if self.mb.btype[name] == 'DUTFlow':
                df.add(name)
        assert block in df, f'[DUTFlow {block}] is not found in {self.mb.fname}'
        df.remove(block)

        # Identify parent dutflows. Cannot remove these
        parent = set()
        for name in df:
            target = {}
            self.mb.recurse(name, target)
            if block in target:
                parent.add(name)
        df = df - parent

        # get all needed blocks
        needed = {}
        for name in df:
            self.mb.recurse(name, needed)

        # display unneeded
        not_needed = set()
        for item in rblock:
            if item not in needed:
                del self.mb.final[item]    # not needed
                not_needed.add(item)
        return not_needed


class MultiBom:

    def __init__(self, list_path):
        self.list_path = [abspath(x) for x in list_path]
        self.errors = {}    # path: error_string

    def main(self, destdir):
        """
        Main entry point
        :param destdir: Output dir
        :return:
        """
        confirm(not exists(destdir),
                f'[{destdir}] is an existing folder.',
                'Delete the folder first. Destination dir must not exist.')

        destdir = abspath(destdir)
        start_sw = Elapsed()

        # step1: run postprocess
        self.postprocess()

        # step2: compare next
        self.compare()

        # step3: copy
        self.copy(destdir)

        # step4: put in runcard
        self.runcard(destdir)

        # step5: Run BdefFixer
        self.run_bdeffixer(destdir)

        log.info(f'-i- MultiBom: Runtime: {start_sw}, at {HOSTNAME}, {curtime()}')

        if self.errors:
            log.info('')
            log.info('There are ERRORS!')
            for path in self.errors:
                log.info(f'Error on {path}:')
                log.info(self.errors[path])
        else:
            log.info('SUCCESS via torch_fixer.py!')

    def run_bdeffixer(self, destdir):
        """Call BdefFix() as one multi-bom TP"""
        with Chdir(destdir):
            tp_shared = DoFixer().get_tp_shared()

            # first run
            BdefFix(*tp_shared).main()
            BinHack(tp_shared[0].envfile).main()    # one only .env only

            # second run (sorting, after BdefHack is called)
            BdefFix(*tp_shared).main()
            BinHack(tp_shared[0].envfile).main()    # one only .env only

    def postprocess(self):
        """Execute the postprocess"""
        for path in self.list_path:
            with Chdir(path):
                try:
                    TorchPostProc().main(bdeffix=False)
                except Exception as e:
                    self.errors[path] = str(e)

    def compare(self):
        """Compare the testprograms"""
        # skip these files
        rskip = re.compile('(/runcard/|'       # special handling
                           'Reports/EnvironmentFile.env.old)')          # TPIE old stuff

        ref = self.list_path[0]
        with Chdir(ref):
            files_ref = list(Allfiles('.'))   # for pct indicator
        with PctIndicator(len(files_ref)) as pct:
            for ctr, fref in enumerate(files_ref):
                pct.disp(ctr)
                if rskip.search(fref):     # skip these
                    continue
                with open(f'{ref}/{fref}', 'rb') as fh:
                    blob = fh.read()
                for ntp in range(1, len(self.list_path)):
                    targfile = f'{self.list_path[ntp]}/{fref}'
                    if exists(targfile):
                        with open(targfile, 'rb') as fh:
                            blob2 = fh.read()
                        confirm(blob == blob2,
                                f'Expecting [{fref}] to match between {ref} vs {self.list_path[ntp]}',
                                'Delete the expanded testprogram folders (both) and re-do Torch export')

    def copy(self, destdir):
        """
        Copy to TempDir, then transfer to destdir via tar
        :param destdir: destination dir
        """
        print(f"-i- Copying files to destination {destdir}")

        # copy to tdir first
        for ntp in range(len(self.list_path)):
            CopyTree(self.list_path[ntp], destdir)

    def runcard(self, destdir):
        """
        copy runcard files. These files require special handling since the file name is the same
        :param destdir: destination dir
        """
        with Chdir(self.list_path[0]):
            rfiles = glob.glob(f'astra/astra_hdmx_v*/runcard/*')
            for rfile in rfiles:
                lines = File(rfile).raw()
                for ntp in range(1, len(self.list_path)):
                    targpath = f'{self.list_path[ntp]}/{rfile}'
                    if exists(targpath):
                        addlines = File(targpath).raw()
                        lines = self.add_runcard_lines(lines, addlines)
                File(f'{destdir}/{rfile}').rewrite(''.join(lines), 'MultiBom().runcard()')

    def add_runcard_lines(self, lines, addlines):
        """
        Add runcard new lines into source lines
        :param lines: source lines
        :param addlines: new lines
        :return: resulting lines
        """
        to_add = [x for x in addlines if x.strip().startswith('<Row')]
        result = []
        for line in lines:
            if line.strip().startswith('</CorrelationTable'):
                result.extend(to_add)
            result.append(line)
        return result


class BdefFix:
    """
    Rewrite the bdefs file, given 1 or more tpobjs
    """

    def __init__(self, *tpobjs, mods=[]):
        self.tpobjs = tpobjs                        # Many POR_TP for one shared .bdef file
        self.all_mtpl = self._all_mtpl()            # set of mtpl files
        self.bdef = self._get_bdef()                # path to bdef file. This guarantee all tpobj is using the same .bdefs
        self.softbin = {}                           # {softbin: name}: by read_mtl_softbins()
        self.src = {}                               # {softbin: orig_line}: by read_mtl_softbins()
        self.fix = defaultdict(set)                 # {file: set_of(lno, softbin_no): by read_mtl_softbins()
        self.usedloc = defaultdict(set)             # {softbin: set_of(file, lno)}: by read_mtl_softbins()
        self.shared_modules = set()                 # set of module folder names, populated in modules_wo_shared()
        self.mod2modify = self.modules_wo_shared(mods)    # list of modules to modify, from args
        self.bm = None                              # used for unittest

    def main(self, shared=True):
        """Main entry point"""
        # read thru all mtpl and populate self.softbin, self.src, self.fix, self.usedloc
        self.read_mtl_softbins()

        # update self.softbin for "Shared"
        # Cannot run this in torch_fixer since it affect git submodule shared .mtpl files.
        # TP-Integration cannot change git submodule files
        # Run this in postproc instead
        if shared:
            self.shared_update()
            self.unshared_update()

        # update module mtpls that need fixing based on self.fix and self.src
        self.fix_mtpl()

        # read bdefs file and write, plus mtl specific updates
        self.update_bdefs()

    def modules_wo_shared(self, mods):
        """
        Return modules to modify (which are non-shared modules), if mods is not given

        :param mods: Input from user: modules to modify
        :return: modules to modify
        """
        result = set()
        for tpobj in self.tpobjs:
            for fp in tpobj.get_all_mtpl_from_stpl():
                modulename = basename(dirname(fp))
                if not (exists(f'{dirname(fp)}/.git') or exists(f'{dirname(dirname(fp))}/.git')):
                    result.add(modulename)
                else:
                    self.shared_modules.add(modulename)

        if mods:
            return mods     # return input if user-provided list, but need self.shared_modules populated
        else:
            return sorted(result)

    def _all_mtpl(self):
        """
        :return: set of mtpl paths used by all tpobjs
        """
        result = set()
        for tpobj in self.tpobjs:
            result.update(realpath(x) for x in tpobj.get_all_mtpl_from_stpl())
        return result

    def _get_bdef(self):
        """
        :return: the shared bdefs file
        """
        bdefs = None
        for tpobj in self.tpobjs:
            for ff in tpobj.get_import_files('bdefs'):
                targ = realpath(ff)
                if bdefs:
                    confirm(bdefs == targ,
                            f'Testprogram found has multiple bdefs file: {bdefs}, {targ}. ',
                            f'BdefFix() expects one bdef only.')
                else:
                    bdefs = targ

        confirm(bdefs, f'No .bdefs found in Testprogram!', 'Check your current workding directory')
        return bdefs

    def read_mtl_softbins(self):
        """
        Update self.softbin {softbin: (name, file)}
        """
        self.bm = BM(self.tpobjs[0])
        is_error = False
        for ff in self._mtpl_order(self.all_mtpl, self.mod2modify):
            oline = OtplFile(ff).raw()

            try:
                for lno, line in OtplFile(ff).readline():
                    if not line.startswith('SetBin '):
                        continue
                    for subline in self.bm.expand(line):
                        self.proc_setbin(subline, ff, lno, oline[lno - 1])

            except Exception as e:      # Since it's possible some module may have issues
                log.info(f'-e- Error: {ff}: {e}')
                is_error = True

        if is_error:
            raise ErrorInput('There are errors in the .mtpl. Pls see above for details.')

    def proc_setbin(self, line, ff, lno, oline, _robj=re.compile(r'\bb(\d+)')):
        """
        Process one SetBin line (expanded), and assign self.softbin, self.src, self.usedloc

        :param line: SetBin line
        :param ff: filename
        :param lno: line number
        :param oline: original line
        :return:
        """
        name = line.split()[1].replace(';', '').replace('SoftBins.', '')
        res = _robj.search(name)
        assert res, f'Cannot determine softbin number for [{name}]'
        number = res.group(1)
        self.usedloc[number].add((ff, lno))

        if number in self.softbin:
            if self.softbin[number].replace('"', '') != name.replace('"', ''):
                self.fix[ff].add((lno, number))
            return

        # assign new one
        self.softbin[number] = name
        self.src[number] = oline

    @staticmethod
    def get_module_shared(fullpath):
        """
        Derive the module and remove last two chars. The two character identifies the die type (for most cases)
        :param fullpath: full path of mtpl
        :return: module name without two chars
        """
        return basename(dirname(fullpath))[:-2]

    def shared_update(self):
        """
        Update below if there are shared bins
            self.fix     - which lines to fix
            self.softbin - name of softbin
            self.src     - what line to put
        structure:
            self.softbin = {}                           # {softbin: name}: by read_mtl_softbins()
            self.src = {}                               # {softbin: orig_line}: by read_mtl_softbins()
            self.fix = defaultdict(set)                 # {file: set_of(lno, softbin_no): by read_mtl_softbins()
            self.usedloc = defaultdict(set)             # {softbin: set_of(file, lno)}: by read_mtl_softbins()
        """
        # identify shared bins first. Shared bins are bins that are used in 2 or more different files.
        must_shared = set()
        special = re.compile('(fail_FAIL_DPS_ALARM|fail_FAIL_SYSTEM_SOFTWARE)')
        for softbin in self.usedloc:
            if special.search(self.softbin[softbin]):
                continue
            prevff = None
            for item in self.usedloc[softbin]:
                if prevff is None:
                    prevff = item[0]   # file
                if self.get_module_shared(prevff) != self.get_module_shared(item[0]):
                    must_shared.add(softbin)

        # make the mods
        fyi = []
        for softbin in must_shared:
            if 'SHARED_BIN' not in self.softbin[softbin]:
                origname = self.softbin[softbin]
                fyi.append(f"BdefFix: Making sharedbin: {origname}")
                self.softbin[softbin] = f'{self.softbin[softbin]}_SHARED_BIN'
                if origname in self.src[softbin]:
                    self.src[softbin] = self.src[softbin].replace(origname, self.softbin[softbin])
                else:
                    self.src[softbin] = self.src[softbin].replace('";', '_SHARED_BIN";')
                for ff, lno in self.usedloc[softbin]:
                    self.fix[ff].add((lno, softbin))

        log.info(truncate(fyi))

    def unshared_update(self):
        """
        Similar to shared_update(), but remove SHARED_BIN if it is not shared anymore.
        as of 12/11: Always execute unshared bin, since it is in postprocess.
        """
        not_shared = set()
        for softbin in self.usedloc:
            if 'SHARED_BIN' in self.softbin[softbin]:
                ff = {self.get_module_shared(item[0]) for item in self.usedloc[softbin]}
                if len(ff) == 1:
                    not_shared.add(softbin)

        # make the mods
        fyi = []
        for softbin in not_shared:
            fyi.append(f"BdefFIx: Making UNsharedbin: {self.softbin[softbin]}")
            self.softbin[softbin] = self.softbin[softbin].replace('_SHARED_BIN', '')
            self.src[softbin] = self.src[softbin].replace('_SHARED_BIN', '')
            for ff, lno in self.usedloc[softbin]:
                self.fix[ff].add((lno, softbin))

        log.info(truncate(fyi))

    def fix_mtpl(self):
        """
        Based on self.fix and self.src, do mods
        {file: list_of_(lno, softbin_no)
        """
        # read the file, goto this line number, update it with the same value as original one
        for ff in self.fix:
            result = OtplFile(ff).raw()
            for lno, softbin in sorted(self.fix[ff]):
                # make sure no issue on parsing
                token1 = result[lno - 1].lstrip().split()[0]
                token2 = self.src[softbin].lstrip().split()[0]
                msg = f'Fail in parsing algo for {ff}, line#{lno}: [{token1}] [{token2}]'
                assert token1 == token2, msg

                # make sure the MTT-SetBin vs standard-SetBin is the same
                msg = f'BdefFix: Mismatch type on {softbin}, in {ff}, line#{lno}'
                assert ('"' in result[lno - 1]) == ('"' in self.src[softbin]), msg

                # print("")
                # print(f"Orig: {result[lno - 1]}")
                # print(f"new : {self.src[softbin]}")
                result[lno - 1] = self.src[softbin]    # make it the same
            File(ff).rewrite(''.join(result), 'BdefFix().fix_mtpl()')

            # Check for new line ending consistency
            # with open(ff, 'rb') as fh:
            #     text = fh.read()
            # assert text.count(b'\n') == text.count(b'\r'), f'oopsie: {ff}'

    @staticmethod
    def _mtpl_order(mtpls, mods):
        """
        Determine the correct order of mtpl to read.
        This determines which softbin to use as the correct one, and which .mtpl to modify
        :return: list of sorted .mtpl
        """
        ref = {}
        for idx, mtpl in enumerate(sorted(mtpls), start=1000):
            modname = basename(dirname(mtpl))
            if modname.startswith(('TPI_', 'FUS_', 'PTH_DLVR')):
                ref[Env.xpath(mtpl)] = idx - 1000    # priority
            elif modname in mods:
                ref[Env.xpath(mtpl)] = idx + 1000    # not priority, bottom
            else:
                ref[Env.xpath(mtpl)] = idx

        return sorted(ref, key=lambda x: ref[x])

    def update_bdefs(self):
        """
        Update the bdefs file given self.softbin
        :return:
        """
        # First pass, Get bins which are not in .mtpl but still needed for some reason. This is why *magic* bin.
        # Bins cleanup is a separate activity, however, need to be careful as some bins are *just* needed by some method.
        magicbin = {}    # {softbin: orig line}
        for line in File(self.bdef).raw():
            if line.strip().startswith('LeafBin '):
                elem = line.strip().split()
                if elem[2] not in self.softbin:
                    magicbin[elem[2]] = line

        # Second pass, process it
        result = []
        first = True
        hbin = {}
        hardbin = False
        for line in File(self.bdef).raw():
            if line.strip().startswith('BinGroup HardBins'):
                hardbin = True
            if line.strip().startswith('Bin ') and hardbin:
                elem = line.strip().split()
                hbin[int(elem[2])] = elem[1]
            if line.strip().startswith('# Start add bins from'):
                continue
            if line.strip().startswith('LeafBin '):
                if not first:
                    continue  # skip everything else
                first = False

                # Add magic bins first
                for bin in sorted(magicbin):
                    result.append(magicbin[bin])

                result.append('            # Start add bins from .mtpl\n')
                for bin in sorted(self.softbin):
                    t = self.softbin[bin].replace('"', '')

                    # get the tray
                    if len(bin) == 3:
                        nn = int(bin[0])
                        tray = hbin[nn]
                    elif len(bin) == 8:
                        nn = int(bin[2:4])
                        if bin[0] in ('1', '2', '3', '4', '5', '6'):
                            tray = 'b1_PASS_CMTTRAY_1'
                        else:
                            tray = hbin[nn]
                    else:
                        raise ErrorUser(f"Expecting 8-digit bin: {bin}: {t}")

                    newline = f'            LeafBin {t}  {bin}  : "{t}",  {tray};\n'
                    result.append(newline)
                continue
            result.append(line)

        # Rewrite
        File(self.bdef).rewrite(''.join(result), 'BdefFix()')


from shutil import copy2, Error, copystat


class CopyTree:
    """
    Usage:
    CopyTree(sourcedir, destdir)
    """

    def __init__(self, src, dest):
        self.indicator = PctIndicator(count_iter(Allfiles(src)))
        self.counter = 0
        self.copytree(src, dest)

    def copytree(self, src, dst, symlinks=False, ignore=None, copy_function=copy2,
                 ignore_dangling_symlinks=False):   # pragma: no cover
        """
        Exact copy of shutil.copytree ver 3.6.3a, with check of existing dir and indicator. See ADDED.
        Default version of copytree() errors out if directory already exist
        """
        names = os.listdir(src)
        if ignore is not None:
            ignored_names = ignore(src, names)
        else:
            ignored_names = set()

        if not os.path.isdir(dst):      # ADDED
            os.makedirs(dst)
        errors = []
        for name in names:
            if name in ignored_names:
                continue
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    if symlinks:
                        # We can't just leave it to `copy_function` because legacy
                        # code with a custom `copy_function` may rely on copytree
                        # doing the right thing.
                        os.symlink(linkto, dstname)
                        copystat(srcname, dstname, follow_symlinks=not symlinks)
                    else:
                        # ignore dangling symlink if the flag is on
                        if not os.path.exists(linkto) and ignore_dangling_symlinks:
                            continue
                        # otherwise let the copy occurs. copy2 will raise an error
                        if os.path.isdir(srcname):
                            self.copytree(srcname, dstname, symlinks, ignore,
                                          copy_function)
                        else:
                            copy_function(srcname, dstname)
                elif os.path.isdir(srcname):
                    self.copytree(srcname, dstname, symlinks, ignore, copy_function)
                else:
                    self.counter += 1     # ADDED
                    self.indicator.disp(self.counter)    # ADDED
                    # Will raise a SpecialFileError for unsupported file types
                    copy_function(srcname, dstname)
            # catch the Error from the recursive copytree so that we can
            # continue with other files
            except Error as err:
                errors.extend(err.args[0])
            except OSError as why:
                errors.append((srcname, dstname, str(why)))
        try:
            copystat(src, dst)
        except OSError as why:
            # Copying file access times may fail on Windows
            if getattr(why, 'winerror', None) is None:
                errors.append((src, dst, str(why)))
        if errors:
            raise Error(errors)
        return dst


if __name__ == '__main__':  # pragma: no cover
    CheckerLog.setup()
    obj = Fixer()
    obj.main()
