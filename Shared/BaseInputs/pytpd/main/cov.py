#!/usr/intel/pkgs/python3/3.12.3/bin/python3
"""
Wrapper script to covmain.py (from coverage package). By default, only the test_<abc>.py and
corresponding module <abc>.py file will be included in the coverage report generated.

Single Script Usage:
    cov.py <yourscript.py> [arguments]                # Run one script then generate html file from a /tmp dir
    cov.py <yourscript.py> [arguments] --include_all  # Run one script then generate html for all modules touched
    cov.py text <yourscript.py> [arguments]           # Run one script, generates text report for that module only
    cov.py xml <yourscript.py> [arguments]            # Run one script, generates XML report for VS Code

Accumulated Coverage Usage:
    cov.py curdir <yourscript.py> [arguments]   # for accumulated coverage. Do this for all scripts.
                                                # Coverage result is stored in current directory
    cov.py html                                 # Execute this once coverage execute is done for all scripts.
                                                # Creates html file (from current dir) and transfers to tvpv web.
    cov.py report                               # Generates the combined text report
    cov.py xml                                  # Generates XML report for VS Code from accumulated coverage

Coverage Arguments:
    --include_all                               # Shows coverage in all modules, not just the module under test
    --rawcov                                    # Show raw coverage output in 'text' mode

"""
# copied from mtl 5/5/21

# Single Script is the same as: (without the need for a dir)
#   covmain.py run --branch <script>
#   covmain.py html
#
# Accumulated Coverage is the same as:
#   covmain.py -x -p --branch <script>
#   # Repeat above command for all scripts. Then to generate html:
#   covmain.py combine
#   covmain.py html

import setenv      # must be first in the imports
import os
import sys
import os.path
import time
import shutil
import subprocess
import shlex

from gadget.shell import USERNAME, SystemCall
from gadget.files import TempDir
from gadget.disk import chmodr
from gadget.pylog import log
from gadget.errors import confirm
from gadget.strmore import putquotes
from os.path import exists, isdir, join
from os.path import basename, dirname, realpath
from gadget.strmore import regex
from gadget.gizmo import IS_UNIX
from main.setenv import ROOT_ENV
import re

coverage = os.path.join(dirname(realpath(__file__)), 'covmain.py')


class MyCov:

    def __init__(self, args):
        self.include_all = False  # Include all modules executed, not just module under test
        if '--include_all' in args:
            self.include_all = True
            args.remove('--include_all')

        self.rawcov = False  # Report line numbers of missing coverage
        if '--rawcov' in args:
            self.rawcov = True
            args.remove('--rawcov')

        self.webfile = "{user}_{py}".format(user=USERNAME, py=os.path.basename(args[0]))
        self.fullcmd = os.path.realpath(args[0])
        self.ut_file = self.fullcmd.split()[0]
        module_filename = basename(self.ut_file).replace('test_', '')
        module_dir = dirname(dirname(self.ut_file))
        self.module_file = os.path.join(module_dir, module_filename)
        self.omit = "--omit '*/pylib/*,*.txt,*.fsdb,*.vcd,*.bz2,*.gz,*.pkl,*.itpp' "
        self.include = ''
        self.anyargs = ""
        self.show_missing = True

        if os.path.exists(self.module_file) and not self.include_all:
            self.include = " --include=%s,%s " % (self.module_file, self.ut_file)

        if len(args) >= 2:
            self.anyargs = " " + " ".join(putquotes(args[1:]))

        self.webloc = '/p/pde/tvpv/tvpvweb/htdocs/py_coverage2'
        self.weburl = "https://tvpv.pdx.intel.com/htdocs/py_coverage2"
        self.covcmd = coverage
        if IS_UNIX:
            self.dirweb = self.webloc + "/" + self.webfile
        else:  # Store locally on Windows.
            self.dirweb = os.path.join(ROOT_ENV, self.webfile)

        confirm(exists(self.covcmd), "{} does not exist. This is the coverage executable".format(self.covcmd),
                "This tool is required")

    def timext(self, tymsec):
        """Returns a string of year+month+day+hour+min"""
        tym = time.gmtime(tymsec)
        return "{0}{1:02d}{2:02d}".format(tym.tm_year, tym.tm_mon, tym.tm_mday)

    def proc_text(self, res):
        """Given output of 'report', display the coverage result of the module being tested"""
        if self.rawcov:
            log.info(res)
        else:
            mod = basename(self.module_file)
            for line in res.split('\n'):
                token = line.split()
                if basename(token[0]) == mod:
                    if self.show_missing and len(token) >= 7:
                        lines = ' '.join(token[6:])
                        log.info("Missing Lines: {}".format(lines))
                    log.info("Missing: {}".format(token[2]))
                    log.info("BrMiss:  {}".format(token[4]))
                    log.info("Coverage: {} - {} lines".format(token[5], token[1]))

    def delete_cgic(self, fullpathname):
        """
        Given a fullpath unittest filename, delete <script>.cgic file
        Eg: input file is <fullpath>/web/cgi/test/test_abc.py,
            delete cgic file in <fullpath>/web/cgi/abc.cgic

        Need to delete cgic so that coverage tool will show .cgi file in html report.
        If .cgic exist then it will not show up.
        """
        dname = re.sub('/test$', '', dirname(fullpathname))
        fname = basename(fullpathname).replace('test_', '').replace('.py', '')

        for ff in os.listdir(dname):
            if ff.endswith(".cgic") and regex(fname, ff):
                log.info("Deleting cgic stale file: {}".format(join(dname, ff)))
                os.unlink(join(dname, ff))

    def do_html(self):
        """
        Calls coverage 'combine' and 'html' for accumulated results.
        Displays where the final html report is
        """
        try:
            subprocess.check_output(self._adapt_command(self.covcmd + " combine"), stderr=subprocess.STDOUT)
            subprocess.check_output(self._adapt_command(self.covcmd + " html"), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            log.error(e.output)

        if not isdir("htmlcov"):
            raise SystemExit("No coverage data found.... Exiting")
        chmodr("htmlcov", "777")
        if os.path.isdir(self.dirweb):
            shutil.rmtree(self.dirweb)
        shutil.move("htmlcov", self.dirweb)
        if IS_UNIX:
            log.info("\nCoverage report is in: {url}/{file}\n".format(url=self.weburl, file=self.webfile))
        else:   # windows
            log.info("\nCoverage report is in: {path}\n".format(path=self.dirweb))

    def build_reportcmd(self):
        """Small helper function b/c this command is used in multiple places"""
        report_cmd = self.covcmd + " report"
        if self.show_missing:
            report_cmd = report_cmd + " --show-missing"
        return report_cmd

    def do_report(self):
        """
        Calls coverage 'combine' and 'report' for accumulated results.
        Display the final report to stdout
        """
        try:
            res1 = subprocess.check_output(self._adapt_command(self.covcmd + " combine"), stderr=subprocess.STDOUT)
            log.info(res1)
            res2 = subprocess.check_output(self._adapt_command(self.build_reportcmd()), stderr=subprocess.STDOUT)
            log.info(res2)
        except subprocess.CalledProcessError as e:
            log.error(e.output)

    def do_xml(self):
        """
        Calls coverage 'combine' and 'xml' for accumulated results.
        Generates coverage.xml file for VS Code Coverage Gutters extension.
        """
        try:
            # Combine coverage files if multiple exist
            combine_result = subprocess.check_output(self._adapt_command(self.covcmd + " combine"), stderr=subprocess.STDOUT)

            # Generate XML file
            xml_result = subprocess.check_output(self._adapt_command(self.covcmd + " xml -o coverage.xml"), stderr=subprocess.STDOUT)

            log.info("Generated coverage.xml for VS Code")
        except subprocess.CalledProcessError as e:
            log.error("Failed to generate coverage.xml:")
            log.error(e.output)
            raise SystemExit("Error generating XML coverage report")

    def do_curdir(self):
        """
        Executes one coverage run for accumulated coverage.
        Displays output to stdout.
        Result are stored in the current directory.
        Call do_html() to generate the html report.
        """
        log.debug("============ Output Start of {}".format(self.fullcmd))
        if os.path.exists(".coverage"):
            os.unlink(".coverage")

        # This coverage run should test all modules since it is a cumulative coverage. Do not include the
        # specific list of modules to be covered
        self._execute_and_print(self.covcmd + " run -p --branch " + self.omit + self.fullcmd + self.anyargs)
        log.info("============ End of execution\n")
        log.info("To Clear accumulated results: delete '.coverage*' files.")
        log.info("Execute more commands to accumulate coverage. Once done, execute:\n    cov.py html\n")

    def do_cov(self):
        """
        Run one script then generate html coverage report from a /tmp dir
        Displays output to stdout
        """
        log.info("============ Output Start of {}".format(self.fullcmd))

        if IS_UNIX:
            confirm(isdir(self.webloc),
                    "{} directory does not exist. This is the cgi web directory for html results.".format(self.webloc),
                    "Pls run this tool in unix and in pdx")

            # delete cgic file
            self.delete_cgic(self.fullcmd)

        with TempDir(chdir=True) as t:
            fullcmd = self.covcmd + " run --branch " + self.omit + self.include + self.fullcmd + self.anyargs
            log.debug("   covcmd: %s" % fullcmd)
            self._execute_and_print(fullcmd)
            try:
                htmlout = subprocess.check_output(self._adapt_command(self.covcmd + " html"), stderr=subprocess.STDOUT)
                log.debug(htmlout)
            except subprocess.CalledProcessError as e:
                log.error(e.output)

            log.info("============ End of execution")
            if not isdir("htmlcov"):
                raise SystemExit("Errors found while running {}. Pls fix first".format(self.fullcmd + self.anyargs))
            chmodr("htmlcov", "777")
            if os.path.isdir(self.dirweb):
                shutil.rmtree(self.dirweb)
            shutil.move("htmlcov", self.dirweb)

        if IS_UNIX:
            log.info("\nCoverage report is in: {url}/{file}\n".format(url=self.weburl, file=self.webfile))
        else:
            log.info("\nCoverage report is in: {path}\n".format(path=self.dirweb))

    def do_text(self):
        """
        Run one script then generate coverage report from a /tmp dir and display results
        Displays output to stdout.
        """
        log.info("============ Output Start of {}".format(self.fullcmd))
        with TempDir(chdir=True) as t:
            self._execute_and_print(self.covcmd + " run --branch " + self.omit + self.include +
                                    self.fullcmd + self.anyargs)

            cmd = self.build_reportcmd()
            _, res = SystemCall(cmd).run_outtxt()
            log.info("============ End of execution")
            self.proc_text(res)

            # Now lets see how many things were skipped in the module code
            if os.path.exists(self.module_file):
                with open(self.module_file, 'r') as mfile:
                    contents = mfile.read()
                    count = len(re.findall(r"#\s*pragma:\s*no cover", contents))
                    if count > 0:
                        print(("Pragmas Skipped: %s" % count))

    def do_xml_single(self):
        """
        Run one script then generate XML coverage report in current directory for VS Code.
        This is useful for quick coverage checks with VS Code Coverage Gutters.
        """
        log.info("============ Output Start of {}".format(self.fullcmd))

        # Delete old coverage files
        if os.path.exists(".coverage"):
            os.unlink(".coverage")
        if os.path.exists("coverage.xml"):
            os.unlink("coverage.xml")

        # Run test with coverage
        fullcmd = self.covcmd + " run --branch " + self.omit + self.fullcmd + self.anyargs
        log.debug("   covcmd: %s" % fullcmd)
        self._execute_and_print(fullcmd)

        log.info("============ End of execution")

        # Generate XML report
        try:
            xml_result = subprocess.check_output(self._adapt_command(self.covcmd + " xml -o coverage.xml"), stderr=subprocess.STDOUT)
            log.info("Generated coverage.xml for VS Code")
        except subprocess.CalledProcessError as e:
            log.error("Failed to generate coverage.xml:")
            log.error(e.output)
            raise SystemExit("Error generating XML coverage report")

    def _adapt_command(self, command):
        """
        Convert command to an executable argument list for the current operating system
        """
        if IS_UNIX:
            cmd = shlex.split(command)
        else:   # Windows
            cmd = shlex.split(command.replace('\\', '/'))
            if cmd[0].endswith('.py'):
                cmd = ['python'] + cmd
        return cmd

    def _execute_and_print(self, command):
        """
        Provides real-time output from the command running in subprocess
        """
        cmd = self._adapt_command(command)
        for item in SystemCall(cmd).run_stream():
            log.info(item)


if __name__ == '__main__':  # pragma: no cover
    log.fmt_stdout_info = "%(message)s"
    log.stdout("INFO")
    help_list = ['-h', '-help', '--help']

    # Cannot use argparse since this requires other script's command lines
    if len(sys.argv) == 1 or len([i for i in help_list if i in sys.argv]) > 0:
        print(__doc__)
        exit(0)

    if sys.argv[1] == "curdir":
        if len(sys.argv) == 2:
            raise SystemExit("Nothing to do. Pls provide executable command after curdir")
        MyCov(sys.argv[2:]).do_curdir()

    elif sys.argv[1] == "html":
        if len(sys.argv) != 2:
            raise SystemExit("Using 'html' requires no other arguments. Extra arguments found.")
        MyCov([os.getcwd()]).do_html()

    elif sys.argv[1] == "report":
        MyCov([os.getcwd()]).do_report()

    elif sys.argv[1] == "xml":
        if len(sys.argv) == 2:
            # Generate XML from accumulated coverage (like html/report commands)
            MyCov([os.getcwd()]).do_xml()
        else:
            # Run single test and generate XML
            MyCov(sys.argv[2:]).do_xml_single()

    elif sys.argv[1] == "text":
        MyCov(sys.argv[2:]).do_text()

    else:
        MyCov(sys.argv[1:]).do_cov()
