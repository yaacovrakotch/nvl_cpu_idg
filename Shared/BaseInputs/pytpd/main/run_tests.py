#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Execute all unittests for pytpd
"""
from setenv import ROOT_ENV      # must be first in the imports
from gadget.vepargs import Args, TA_StoreTrue, TA_StoreDir
from gadget.helperclass import OPT
from gadget.dictmore import DictDot
from gadget.shell import SystemCall, BgCmd, USERNAME
from gadget.helperclass import TagOnce
from gadget.disk import scandir_mtime, mkdirs
from gadget.files import File
from gadget.errors import ErrorCockpit
from gadget.getgit import GitHub, GetCmd
from gadget.printmore import PrintAlign
from tp.testprogram import TestProgram
from mod.setting import cfg
from glob import glob
from os.path import dirname, realpath, basename, join
from main.test.setenv_unittest import UT_DIR, UT_DIR_REPO, EXIST_PDX_I_DRIVE
import multiprocessing
import sys
import re
import time
import os


# testtime config, so slow test go first
CFG_TT = {'main/test/test_sort_class_tp_diff.py': 22,
          'main/test/test_torch_fixer.py': 34,
          'main/test/test_slim_tpload.py': 75,
          'main/test/test_torch_postproc.py': 123,
          'main/test/test_autocounter.py': 29,
          'main/test/test_nvl_buildtp.py': 73,
          'tp/test/test_mtpl.py': 76,
          'tp/test/test_timlvl.py': 62,
          'qgates/test/test_gen_sku_chk.py': 39,
          'qgates/test/test_plist_chk.py': 24,
          'tp/test/test_regres_tgl81.py': 23,
          'tp/test/test_regres_rpl.py': 37,
          'tp/test/test_regres_tgl42_39.py': 32,
          'tp/test/test_regres_mtlp6828.py': 59,
          'tp/test/test_regres_mtlp68prq.py': 62,
          'tp/test/test_regres_nvl.py': 75,
          }

# use default compiler (because of pandas)
DEF_COMPILER = {'test_sort_class_tp_diff.py'}
GH_EXECUTABLE = '/intel/tpvalidation/engtools/tptools/mtl/tools/gh/gh_2.82.0_linux_amd64/gh'


class RunTests(Args):   # parent: ArgsBase
    """
    Main class
    """
    root = dirname(dirname(realpath(sys.argv[0])))
    log_dir = f'{cfg.ut_dir}/ut_logs/{USERNAME}' if EXIST_PDX_I_DRIVE else f'{UT_DIR_REPO}/ut_logs/{USERNAME}'
    ncpu = multiprocessing.cpu_count()

    def pre_pickle(self):    # pragma: no cover    - pickle init sample
        """Run pickle init so that parallel jobs will without any issues"""
        # No need to specify if the pickle_init run is used once. It will still improve unittest time on reruns.
        # specify paths here which are used by more than 1 unittests
        if EXIST_PDX_I_DRIVE:
            tps = [f'{UT_DIR}/Integ_2A/ENG_TP/Class_MTL_P68/EnvironmentFile.env',
                   f'{UT_DIR}/Integ_2A_2/ENG_TP/Class_MTL_P68/EnvironmentFile.env',
                   # f'{UT_DIR_REPO}/Simple1/TPL/EnvironmentFile.env',
                   f'{UT_DIR}/MTLXXXXXXX39A0KSXXX/POR_TP/Class_MTL_P28/EnvironmentFile.env']
        else:
            tps = []
        for path in tps:
            TestProgram(path).pickle_init()

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.f = TA_StoreTrue('Do not run slow tests')
        cfg.gadget = TA_StoreTrue('Run gadget unittests')
        cfg.nt = TA_StoreTrue('No Thread, run serially')
        cfg.c = TA_StoreTrue('Run coverage')
        cfg.asserts = TA_StoreDir('CMD: Create pytpd for assert runs.', metavar='output_dir')
        cfg.ut = TA_StoreTrue('Run test_strmore.py only')
        cfg.show = TA_StoreTrue('Show details on failure')
        cfg.coverage = TA_StoreTrue('Show coverage numbers on modified files only')
        return cfg

    def _derive_mainpy(self, test_file):
        """
        Derive the main source file path from a test file path.

        :param test_file: Path to test file (e.g., 'pymtpl/test/test_binctr.py')
        :return: Path to source file (e.g., 'pymtpl/binctr.py') or None if not found

        Examples:
            'pymtpl/test/test_binctr.py' -> 'pymtpl/binctr.py'
            './gadget/test/test_strmore.py' -> 'gadget/strmore.py'
            'main/test/test_orphan.py' -> None (if main/orphan.py doesn't exist)
        """
        # Normalize relative paths (strip leading ./)
        test_file_norm = test_file[2:] if test_file.startswith('./') else test_file

        # Only process files in /test/ directories with test_ prefix
        if '/test/test_' not in test_file_norm:
            return None

        # Extract the parent directory and filename
        # e.g., 'pymtpl/test/test_binctr.py' -> test_dir='pymtpl/test', parent_dir='pymtpl'
        test_dir = dirname(test_file_norm)
        parent_dir = dirname(test_dir)
        base = basename(test_file_norm)

        # Strip 'test_' prefix from filename
        if not base.startswith('test_'):
            return None

        source_name = base[len('test_'):]
        source_file = join(parent_dir, source_name)

        # Verify source file exists
        abs_source = join(self.root, source_file)
        if os.path.exists(abs_source):
            return source_file

        return None

    def get_pr_modified_files(self):
        """
        Get list of modified Python files from the current PR using GitHub API.
        Now also includes source files when only their test files are modified.

        :return: List of modified .py file paths relative to repository root
        """
        try:
            github = GitHub()
            modified_files = github.get_modfiles()
        except Exception as e:
            print(f'Warning: Could not get PR modified files: {e}')
            return []

        # Filter for Python files only
        py_files = set()
        test_files = []

        for f in modified_files:
            if f.endswith('.py'):
                # Separate test files from regular files
                if '/test/' in f or basename(f).startswith('test_'):
                    source_file = self._derive_mainpy(f)
                    if source_file:
                        py_files.add(source_file)
                        print(f'Added source file {source_file} (test file {f} was modified)')
                else:
                    py_files.add(f)

        print(f'Found {len(py_files)} modified Python files in PR (excluding test files)')
        return py_files

    def get_tests_for_modified_files(self, modified_files):
        """
        Map modified source files to their corresponding test files.

        :param modified_files: List of modified Python files
        :return: List of test files to run (absolute paths, sorted)
        """
        test_files = set()

        for mod_file in modified_files:
            # Normalize relative paths (strip leading ./) to be robust
            mod_file_norm = mod_file[2:] if mod_file.startswith('./') else mod_file

            # If it's already a test file, add it (make absolute)
            if '/test/test_' in mod_file_norm or basename(mod_file_norm).startswith('test_'):
                test_files.add(join(self.root, mod_file_norm))
                continue

            # Find corresponding test file(s)
            # e.g., pymtpl/binctr.py -> pymtpl/test/test_binctr.py
            mod_path = dirname(mod_file_norm)
            mod_name = basename(mod_file_norm).replace('.py', '')
            test_path = join(self.root, mod_path, 'test', f'test_{mod_name}.py')

            if os.path.exists(test_path):
                test_files.add(test_path)
            else:
                # Fallback: search the repo for any test_{mod_name}.py
                fallback_tests = []
                pattern = join(self.root, '**', f'test_{mod_name}.py')
                for match in glob(pattern, recursive=True):
                    test_files.add(match)
                    fallback_tests.append(match)
                # If still none found, continue
                if fallback_tests:
                    print(f'Fallback found test files for modified file {mod_file}: {fallback_tests}')
                else:
                    print("No test file found for modified file:", mod_file)
                    print("Skipping coverage for this file.")
                continue

        # Return sorted list to have deterministic order
        return sorted(test_files)

    def run_pr_coverage(self, test_files, modified_files):
        """
        Run coverage for specific test files and report only on modified files.
        Updates the PR description with the coverage report.

        :param test_files: List of test files to run
        :param modified_files: List of modified source files to check coverage for
        """
        print(f'\nRunning coverage on modified files:')
        for mf in modified_files:
            print(f'  - {mf}')
        print()

        count_fail = 0
        coverage_data = {}  # Dict to store: {source_file: {coverage_pct, tests, missing, brmiss, lines}}

        for test_file in test_files:
            name = test_file.replace(self.root, '')[1:]
            cmd = f'{os.path.join(self.root, "main", "cov.py")} text {test_file} -v -b -t'

            print(cmd)

            print(f'Running coverage for {name}...')
            _, out = SystemCall(cmd).run_outtxt()
            tests, runtime, failed, pass_fail_line = self._parse_ut_info(out)

            if failed:
                count_fail += 1
                File(f'{self.log_dir}/{basename(name)}.log').write(out)

            print('%-40s %s tests, %s %s Secs' % (name, tests, pass_fail_line, runtime))

            # Extract coverage info for modified files
            coverage_pct = None
            missing = None
            missing_lines = None
            brmiss = None
            lines = None

            for line in out.split('\n'):
                # display elapsed time per test
                if ': Timeit:' in line and (not line.startswith('[')):
                    print(line)

                # Parse coverage line: "Coverage: XX% - YYY lines"
                cov_match = re.search(r'Coverage:\s*(\d+)%\s*-\s*(\d+)\s*lines?', line)
                if cov_match:
                    coverage_pct = cov_match.group(1)
                    lines = cov_match.group(2)

                # Parse missing line: "Missing: XX"
                miss_match = re.search(r'Missing:\s*(\d+)', line)
                if miss_match:
                    missing = miss_match.group(1)

                # Parse detailed missing lines: "Missing Lines: 1, 2-5, ..."
                miss_lines_match = re.search(r'Missing Lines?:\s*(.+)$', line)
                if miss_lines_match:
                    missing_lines = miss_lines_match.group(1).strip()

                # Parse branch miss line: "BrMiss: XX"
                brmiss_match = re.search(r'BrMiss:\s*(\d+)', line)
                if brmiss_match:
                    brmiss = brmiss_match.group(1)

            # Map test file to source file
            # e.g., pymtpl/test/test_binctr.py -> pymtpl/binctr.py
            # Robustly map test file to source file
            test_dir = dirname(test_file)
            parent_dir = dirname(test_dir)
            base = basename(test_file)

            # Strip 'test_' prefix if present
            if base.startswith('test_'):
                base = base[len('test_'):]

            # Construct source file path
            source_file = join(parent_dir, base)

            # Verify the source file actually exists before using it
            if os.path.exists(source_file):
                source_file = os.path.relpath(source_file, self.root)
            else:
                # Fallback: if source file doesn't exist, skip coverage for this test
                print(f'Warning: No source file found for test {test_file}')
                source_file = None
                continue

            # Only include if it's in modified files and we have coverage data
            if source_file in modified_files and coverage_pct is not None:
                coverage_data[source_file] = {
                    'coverage': coverage_pct,
                    'tests': tests,
                    'missing': missing or 'N/A',
                    'brmiss': brmiss or 'N/A',
                    'lines': lines or 'N/A',
                    'missing_lines': missing_lines or 'N/A',
                    'runtime': runtime
                }

        # Create Markdown table for coverage report
        table_lines = ['### Coverage Report for Modified Files', '']
        table_lines.append('| File Name | Coverage | Tests | Missing | Branch Miss | Total Lines | Runtime |')
        table_lines.append('|-----------|----------|-------|---------|-------------|-------------|---------|')

        for source_file in sorted(coverage_data.keys()):
            data = coverage_data[source_file]
            coverage_pct = data['coverage']
            tests_count = data['tests']
            missing = data['missing']
            brmiss = data['brmiss']
            lines = data['lines']
            runtime = f"{data['runtime']} Secs"

            # Add emoji for visual feedback
            try:
                cov_int = int(coverage_pct)
                emoji = '✅' if cov_int >= 90 else '⚠️' if cov_int >= 80 else '❌'
            except (TypeError, ValueError):      # pragma: no cover     (safety check only)
                emoji = '❓'
            table_lines.append(f'| `{source_file}` | {coverage_pct}% {emoji} | {tests_count} | {missing} | {brmiss} | {lines} | {runtime} |')

        if not coverage_data:
            table_lines.append('| No coverage data available | - | - | - | - | - | - |')

        table_lines.append('')
        # Print any missing line info per modified file
        if coverage_data:
            table_lines.append('#### Missing Lines Details')
            table_lines.append('')
            for source_file in sorted(coverage_data.keys()):
                missing_lines = coverage_data[source_file].get('missing_lines', 'N/A')
                if missing_lines and missing_lines != 'N/A':
                    table_lines.append(f'- `{source_file}`: {missing_lines}')
            table_lines.append('')

        table_lines.append(f'**Tests Run:** {len(test_files)} test file(s)')
        table_lines.append(f'**Modified Files:** {len(modified_files)} file(s)')

        if count_fail:
            table_lines.append(f'\n⚠️ **Warning:** {count_fail} test(s) failed. Check logs for details.')

        coverage_report = '\n'.join(table_lines)

        # Update PR description with coverage report
        self._update_pr_description_with_coverage(coverage_report)

        # Display coverage summary for modified files
        if coverage_data:
            print()
            print('Coverage Summary for Modified Files:')
            pa = PrintAlign(sep='|')
            pa('File', 'Coverage', 'Tests', 'Missing', 'BrMiss', 'Lines', 'RunTime')
            for source_file, data in sorted(coverage_data.items()):
                pa(source_file, data["coverage"], data["tests"], data["missing"], data["brmiss"], data["lines"], data['runtime'])
            pa.disp()

        # Exit with appropriate code
        if count_fail:
            print(f"\nFail tests: {count_fail} - {self.log_dir}")
            exit(1)
        else:
            print("\nSuccess! All tests passed.")

    def _update_pr_description_with_coverage(self, coverage_report):
        """
        Update the PR description with the coverage report, replacing any existing coverage section.

        :param coverage_report: Markdown formatted coverage report to insert
        """
        # Get current commit SHA
        print('Getting current commit SHA...')
        rc, commit_sha, _ = SystemCall('git rev-parse HEAD').run_sout_serr()

        if rc == 0:
            commit_sha = commit_sha.strip()
            short_sha = commit_sha[:7]  # Short SHA for display
        else:
            commit_sha = 'unknown'
            short_sha = 'unknown'

        # Get current PR description
        print('\nFetching current PR description...')
        rc, pr_body, _ = SystemCall(GetCmd.exe(f'{GH_EXECUTABLE} pr view --json body -q .body')).run_sout_serr()

        if rc != 0:
            print('Warning: Could not fetch PR description. Coverage report not updated.')
            return

        # Define markers for coverage section
        start_marker = '<!-- COVERAGE_REPORT_START -->'
        end_marker = '<!-- COVERAGE_REPORT_END -->'

        # Add commit SHA header to coverage report
        coverage_report_with_sha = f'**Coverage Report for Commit:** `{short_sha}`\n\n{coverage_report}'

        # Check if markers exist in the PR description
        if start_marker in pr_body and end_marker in pr_body:
            # Find the positions of the markers
            start_pos = pr_body.find(start_marker)
            end_pos = pr_body.find(end_marker) + len(end_marker)

            # Replace the content between markers (including the old coverage report)
            new_body = (
                pr_body[:start_pos] +
                start_marker + '\n' +
                coverage_report_with_sha + '\n' +
                end_marker +
                pr_body[end_pos:]
            )
        else:
            # Markers not found - append coverage section at the end
            print('Warning: Coverage report markers not found in PR description. Appending coverage report.')
            new_body = (
                pr_body + '\n\n---\n\n' +
                start_marker + '\n' +
                coverage_report_with_sha + '\n' +
                end_marker
            )

        # Write new body to temp file
        temp_file = f'{self.log_dir}/pr_description.txt'
        File(temp_file).write(new_body)

        # Update PR description
        print(f'Updating PR description with coverage report (commit: {short_sha})...')
        SystemCall(GetCmd.exe(f'{GH_EXECUTABLE} pr edit --body-file {temp_file}'), disp=True).run_sout_serr()
        print('PR description updated successfully.')

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        # Call other routines here
        self.do_asserts()

        # Delete log dirs first
        mkdirs(self.log_dir, mode='02770')
        for ff in os.listdir(self.log_dir):
            File(join(self.log_dir, ff)).unlink()

        # Handle PR coverage mode
        if OPT.coverage:
            modified_files = self.get_pr_modified_files()
            if not modified_files:
                print('No modified Python files found in PR. Exiting.')
                return

            test_files = self.get_tests_for_modified_files(modified_files)
            if not test_files:
                print('No corresponding test files found for modified files. Exiting.')
                return

            print(f'Running coverage for {len(test_files)} test files')
            self.run_pr_coverage(test_files, modified_files)
            return

        # pre-run pickle init to avoid collisions during parallel runs
        self.pre_pickle()

        # welcome header
        print(f'Starting unittest runs... logdir: {self.log_dir}')
        count_fail = 0
        bg = BgCmd(ncpu=self.ncpu, startid=1000, timeout=60 * 90, min_load_add=0)

        # Start the tests
        for ff in self.files_to_test(glob(f'{self.root}/*/test/test_*.py')):
            name = ff.replace(self.root, '')[1:]
            cmd = self.get_cmd(ff)

            # launch
            if OPT.nt or basename(ff) in ('test_shell.py', 'test_ut.py'):
                # serial
                count_fail += self.execute_test(cmd, name)
            else:
                # parallel
                bg.send(cmd, name=name.replace('\\', '/').replace('/', '___',), seqid=1000 - CFG_TT.get(name, 0))

        if not OPT.nt:
            count_fail += len(self.parallel_finish(bg))

        # display result
        print()
        if count_fail:
            print("Fail tests: %s - %s" % (count_fail, self.log_dir))
            if OPT.show:
                for ff in os.listdir(self.log_dir):
                    print(f'\n======= {ff}')
                    print(File(f'{self.log_dir}/{ff}').read())
            exit(1)
        else:
            print("Success! no fails.")

    @staticmethod
    def files_to_test(file_list):
        """
        Iterator of files to test

        :return: file to test
        """
        for ff in file_list:

            # unittest hook
            if OPT.ut:
                if basename(ff) == 'test_simple_ut.py':       # pragma: no cover - python optimization, branch miss, it is actually covered
                    yield ff
                continue

            # test always (in gadget)
            if basename(ff) == 'test_tputil.py':
                yield ff
                continue

            # -gadget
            if (not OPT.gadget) and 'gadget/' in ff.replace('\\', '/'):
                continue     # ignore gadget by default

            yield ff

    def get_cmd(self, ff):
        """
        Return cmd
        :return: cmd to run
        """
        if OPT.f:
            args = ''
        else:
            args = '-s '   # default

        if OPT.c:
            return f'{os.path.join(self.root, "main", "cov.py")} text {ff} -v -b'

        if basename(ff) in DEF_COMPILER and EXIST_PDX_I_DRIVE:
            return f'{ff} -v -b -a {args}'
        else:
            return f'{sys.executable} {ff} -v -b -a {args}'

    def execute_test(self, cmd, name):
        """
        Execute one test

        :param cmd: command line
        :param name: name of mod being tested
        :return:
        """
        sys.stdout.write('%s\r' % name)
        _, out = SystemCall(cmd).run_outtxt()
        tests, runtime, failed, pass_fail_line = self._parse_ut_info(out)
        if failed:
            File(f'{self.log_dir}/{basename(name)}.log').write(out)
        print('%-40s %s tests, %s %s Secs' % (name, tests, pass_fail_line, runtime))
        return failed

    def parallel_finish(self, bg):
        """
        Finish the parallel tasks

        :param bg: bg object
        :return: number of fails
        """
        fails = []
        # Start of BgCmd block ===========================================================
        # Run the jobs
        while bg.run():
            for job in bg.queue(done=True):   # these are completed jobs
                self.process(job, fails)
                bg.purge(job.name)
            time.sleep(0.05)

        # Wait for all jobs to complete
        for job in bg.queue(wip=True):
            print(f"Waiting for {self.jobname(job.name)}, pid={job.pr.pid}")

        once = TagOnce()
        while bg.count() > 0:
            for job in bg.queue(done=True):
                if once(job.name):
                    print(f"{self.jobname(job.name)} is done")
            time.sleep(0.5)

        # Process the rest of completed jobs
        for job in bg.queue(done=True):
            self.process(job, fails)
            bg.purge(job.name)
        # END of BgCmd block ============================================================

        return fails

    def jobname(self, name):
        """Returns the job name"""
        return name.replace('___', '/')

    def process(self, job, fails):
        """
        Process one bg job

        :param job: job object
        :param fails:
        :param stat
        """
        with open(job.serr) as serr_h, open(job.sout) as sout_h:
            stderr = serr_h.read().rstrip()
            stdout = sout_h.read().rstrip()
        out = stdout + '\n' + stderr
        tests, runtime, failed, pass_fail_line = self._parse_ut_info(out)
        if failed:
            File(f'{self.log_dir}/{basename(self.jobname(job.name))}.log').write(out)
        print('%-40s %3s tests, %-7s Secs, %s' % (self.jobname(job.name), tests, runtime, pass_fail_line))
        if failed:
            fails.append(job.name)

    @staticmethod
    def _parse_ut_info(stdout):
        """
        Helper function to parse the output of a unit test run and extract needed information.

        :param stdout: UT screen output to parse for passing info and basic stats
        :return tests: count of UT tests run
        :return runtime: float in seconds of the UT runtime
        :return failed: flag for whether the UT passed or failed
        :return pass_fail_line: status line that can be used for reporting.
        """
        tests = 0
        runtime = 0.0
        pass_fail_line = ''
        failed = True
        for line in stdout.split('\n'):
            if re.search(r"^FAILED\s+", line):
                pass_fail_line = f'{line:20s}'
            elif re.search(r"^OK\s*(\(skipped=\d+\))?", line):
                pass_fail_line = f'{line:20s}'
                failed = False
            else:
                m = re.search(r'^Ran\s+(\d+)\s+tests?\s+in\s+([0-9\.]+)', line)
                if m:
                    tests = int(m.group(1))
                    runtime = float(m.group(2))

            if line.startswith(('Missing:', 'BrMiss:', 'Coverage:')):
                pass_fail_line = f'{pass_fail_line}, {line:14s}'

        return tests, runtime, failed, pass_fail_line

    def do_asserts(self):
        """
        Monkey all .py files and output to a directory, to make sure all assert prints does not error
        """
        if not OPT.asserts:
            return   # Do nothing
        Assertize().main(OPT.asserts)


class Assertize:
    """Create a project with assert checks"""
    re_ternary = None     # defined inline

    def main(self, outdir):

        assert not os.listdir(outdir), f'{outdir} is not empty. Expecting empty dir'

        for path, _ in scandir_mtime(ROOT_ENV):
            if '.git/' in path or path.endswith('.pyc'):
                continue
            npath = path.replace(ROOT_ENV, outdir)
            if npath.endswith('.py') and ('/test/' not in npath):
                File(npath).touch(self._proc_py_assert(path), mkdir=True).chmod('0750')
            else:
                mkdirs(dirname(npath))
                File(path).copy(npath)      # copy file as-is

        exit(0)

    def _proc_py_assert(self, fname):
        """Process one py file"""
        result = []
        all = []
        print(f'Processing {fname}')
        for line in File(fname).chomp():
            all.append(line)
        for lno in range(len(all)):
            # ternary line
            toadd = self._proc_ternary(all[lno], lno)
            if toadd:
                result.extend(toadd)
                continue

            # assert line
            indent, expr, disp = self._proc_py_line(all, lno)
            if expr:
                result.append(f'{indent}_dum = {disp}   # line#{lno}')
            result.append(all[lno])
        return '\n'.join(result)

    @classmethod
    def _proc_ternary(cls, line, lno):
        """Return a list of python lines given expression"""
        if not cls.re_ternary:
            cls.re_ternary = re.compile(r'^(\s+)(\w+)\s+=(.*) (if\b.*) else (.*)$')

        res = cls.re_ternary.search(line)
        output = []
        if res:
            indent = res.group(1)
            var = res.group(2)
            expr1 = res.group(3)
            ifs = res.group(4)
            elses = res.group(5)
            if not expr1.strip().startswith('{'):
                output.append(f'{indent}{ifs}:    # line#{lno}')
                output.append(f'{indent}    {var} ={expr1}')
                output.append(f'{indent}else:')
                output.append(f'{indent}    {var} = {elses}')
        return output

    @staticmethod
    def _proc_py_line(alines, lno, _ro=re.compile(r"^(\s*)assert (.*)$")):
        """
        process one line with assert

        :return: indent, expr, disp
        """
        line = alines[lno]
        res = _ro.search(line)
        if not res:
            return None, None, None
        indent = res.group(1)
        rest = res.group(2)
        stack = 0
        start = None
        for idx in range(len(rest)):
            char = rest[idx]
            if stack == 0 and (not start) and char == ',':
                break
            if char == '(':
                stack += 1
            if char == ')':
                stack -= 1
            if (not start) and char in ('"', "'"):
                start = char
                continue
            if start and char == start:
                start = None
        else:
            return None, None, None

        expr = rest[:idx]
        disp = rest[idx + 1:].strip()
        if not disp.startswith('('):
            disp = f'({disp})'
        if disp.startswith('(') and not disp.endswith(')'):
            for idx in range(lno + 1, len(alines)):
                disp = f'{disp}\n{alines[idx]}'
                if alines[idx].strip().endswith(')'):
                    break
            else:      # pragma: no cover
                raise ErrorCockpit("Close parenthesis not found!")
        return indent, expr, disp


if __name__ == '__main__':  # pragma: no cover
    RunTests(desc=__doc__).main()
