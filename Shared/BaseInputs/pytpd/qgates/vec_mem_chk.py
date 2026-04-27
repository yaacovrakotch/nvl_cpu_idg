#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Will check Vector Memory Usage per Slice and should not exceed 3.5G
"""
import sys
import setenv

from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from gadget.shell import SystemCall
from pprint import pprint
import json
import glob
import os
import csv
from collections import defaultdict
from gadget.files import check_and_del
from gadget.disk import mkdirs
from os.path import dirname, basename


class VecMemUse(QGateBase):
    """
    Will check Vector Memory Usage per Slice and should not exceed 3.5G
    """

    def main(self):
        """Entry point of checker"""
        vec_mem = 'I:/tpvalidation/engtools/tptools/mtl/infra/torch/validators/VecMem/TPPatternSuiteAnalyzer2.7.exe'
        if not os.path.exists(vec_mem):
            vec_mem = vec_mem.replace('I:/', 'J:/')       # for sort

        tpbase = self.tpobj.tpldir
        tpl = 'BaseTestPlan.tpl'

        bom = basename(dirname(self.tpobj.envfile))

        # use env var
        if 'SOCFILE' in os.environ:
            socfile = os.path.join(self.tpobj.tpldir, os.environ['SOCFILE'])
        else:
            socfile = f'{self.tpobj.tpldir}/Shared/BaseInputs/Common/Common_{bom}/HVM.soc'
        if not(os.path.exists(socfile)):
            self.add_error(257, 'BASE', f'{socfile} does not exist')
            return

        # plistxml = f'{self.tpobj.envdir}/PLIST_ALL_{bom}.plist.xml'
        plistxml = self.tpobj.get_file_allplist(fnameonly=True)
        envfile = self.tpobj.envfile
        # if not(os.path.exists(envfile)):
        #    self.add_error(257, 'BASE', f'{envfile} does not exist')
        #    return
        outputpath = f'{self.tpobj.envdir}/Reports'
        mkdirs(outputpath)
        delete = ['patternsizer_', 'perslicevectormem_']
        for j in os.listdir(outputpath):
            if any(j.startswith(prefix) for prefix in delete):
                file_path = os.path.join(outputpath, j)
                print(f'Deleting: {file_path}')
                check_and_del(file_path, error=False)

        cmd = f'{vec_mem} --tpbase {tpbase} --tpl {tpl} --env {envfile} --plistxml {plistxml} --soc {socfile} --of {outputpath}'
        log.info(f'CMD: {cmd}')
        code, out = SystemCall(cmd, disp=False).run_outtxt()
        if not(code == 1 or code == 0):
            # log.info(f'Error running tool.  Please run {cmd} separately to debug issue')
            print(out)
            self.add_error(257, 'BASE', f'Error running tool {code}.  Please run {vec_mem} separately. Use --h for command line details')
            return

        perslice1 = glob.glob(f'{self.tpobj.envdir}/Reports/perslicevectormem_*.csv')
        if not perslice1:
            print(out)  # Display output of TPPatternSuiteAnalyzer
            self.add_error(257, 'BASE', 'perslicevectormem_*.csv was not generated. Check TPPatternSuiteAnalyzer output')
        # self.check(perslice1, 257, 'BASE', 'perslicevectormem_*.csv was not generated. Check TPPatternSuiteAnalyzer output')
        self.compare(perslice1)
        return cmd

    def get_base_domain(self, domain):
        return domain.split("::")[-1]

    def compare(self, perslice1):

        filename = perslice1[0]

        # Threshold for flagging
        THRESHOLD = 3_500_000_000

        # domain → column → total
        domain_column_totals = defaultdict(lambda: defaultdict(int))

        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            column_names = header[1:]  # Skip 'Domain'

            for row in reader:
                raw_domain = row[0].strip()
                if not raw_domain or raw_domain == "TotalVectorMemLoadedFromPatterns":
                    continue
                base_domain = self.get_base_domain(raw_domain)
                values = row[1:]

                for col_name, val in zip(column_names, values):
                    if val.strip().isdigit():
                        domain_column_totals[base_domain][col_name] += int(val)

        # Output
        data_report = {}
        for domain in sorted(domain_column_totals):
            # print(f"\n{domain}:")
            for col in column_names:
                total = domain_column_totals[domain].get(col, 0)

                # save data to a report file
                if total:
                    data_report[f'{domain}:{col}'] = total

                # do the check
                if total > THRESHOLD:
                    self.add_error(257, 'BASE', f' Slice: {col}:{domain} {total} exceeded the {THRESHOLD} limit')
                else:
                    self.add_pass(257, 'BASE')

        # Write it
        with open(f'{self.tpobj.envdir}/Reports/vecmem.json', 'w') as fh:
            json.dump(data_report, fh, indent=4)

        # print it
        pprint(data_report)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    VecMemUse(TestProgram(sys.argv[1])).run()
