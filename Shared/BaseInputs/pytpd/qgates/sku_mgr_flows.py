#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Ensures that VminTC MTT tests are using the proper uservars and parameters
"""
import ast
import sys
import os
import re
from os.path import basename
from gadget.dictmore import xmlfunc, iter_dot_items, find_dot_items
from gadget.pylog import log
from gadget.strmore import curtime, strvalue, truncate, to_str
from qgates.qgate_base import QGateBase
from gadget.tputil import remove_ip
from tp.testprogram import TestProgram
from pprint import pprint
from xml.etree import cElementTree as ElementTree
from mod.setting import cfg
import json
import glob


class SkuMgrChk(QGateBase):

    def main(self):
        """
        Ensures that VminTC MTT tests are using the proper uservars and parameters
        Notes from Danny Pham:
        Correct Usage Model for MTT VminTC Tests in SpeedFlow
        •	Hermes POC Wiki Notes for MTT Setup: https://wiki.ith.intel.com/display/ITSpdxtp/NVL+HERMES#NVLHERMES-FlowMatrixChanges
        •	Tests using TrialVariables from the FlowDomain collection for lower speed flows (also called base/mid frequencies), should use single length string arrays for their expansion.
        o	Conversely, MTTs at top speed flow should use the Corners uservar collection for their domain (length 3 for CPU/GCD to match F7/F6/F5; length 2 for HUB to match F4/F3)
        •	Examples
            o	MultiTrialTest ARR_ATOM_VMIN_K_F1XAT_HITO_VCCIA_F1_X_COMBINEDTrialVariable IPC::CPU_TRIALS::FlowDomain.ATOM;
            	CSharpTrialTest VminTC "ARR_ATOM_K_F1XAT_HITO_VCCIA_F1_" + __shared__::CustomFlowMatrixSpecs.AT_F1_FREQ_MHz + "_COMBINED"
            o	MultiTrialTest ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_X_COMBINED
            	TrialVariable IPC::CPU_TRIALS::FlowDomain.ATOM_TOP;
            	CSharpTrialTest VminTC "ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_" + __shared__::Corners.AT_C5 + "_COMBINED"

        Failcase Model and Tracing the b9803 Error
        •	MultiTrialTests (MTT) using VminTC template that do not have matching TrialVariable (FlowDomain.ATOM/CORE/RING/GT/HUB) with a correct expansion of tests
            o	Example. F1-F4 speedflows are single-flow, meaning that they will only run 1 test. In comparison, F5 speedflows have 3 flows (examples. F7/F6/F5 for CPU; F4/F3 for HUB)
        •	Example:
            o	MultiTrialTest ARR_ATOM_VMIN_K_F5XAT_HITO_VCCIA_F5_X_SSA_L2TAG
            	TrialVariable IPC::CPU_TRIALS::FlowDomain.ATOM;
            	CSharpTrialTest VminTC "ARR_ATOM_K_F5XAT_HITO_VCCIA_F5_" + __shared__::Corners.AT_C5 + "_SSA_L2TAG"
        """
        domains = self._parse_corners()
        if not domains:
            return

        all_mods = self.tpobj.mtpl.get_mod2fname()
        for mod_path, file_path in all_mods.items():
            self._check_module(mod_path, file_path, domains)

    def _parse_corners(self):
        bom = basename(self.tpobj.envdir)
        flowmatrix = f'{self.tpobj.tpldir}/Shared/BaseInputs/Common/Common_{bom}/BinMatrixSpecs.flm.usrv'
        if not os.path.isfile(flowmatrix):
            self.add_error(263, "BASE", f'{flowmatrix} DOES NOT EXIST')
            return None

        with open(flowmatrix, 'r') as file:
            lines = file.readlines()

        # Initialize a dictionary to store the results
        domains = {}
        current_section = None
        skip_block = False

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check for the start of the CustomFlowMatrixSpecsManual block
            if line.startswith("UserVars CustomFlowMatrixSpecsManual"):
                skip_block = True
                continue

            # Check for the end of a block
            if line == "}":
                skip_block = False
                continue

            # Skip lines within the CustomFlowMatrixSpecsManual block
            if skip_block:
                continue

            # Check for section headers
            if line.startswith("UserVars"):
                current_section = line.split()[1]
                continue

            # Process lines within a section
            if current_section and line.startswith("Array<String>"):
                try:
                    # Extract the key and values
                    key, values = line.split(" = ")
                    key = key.split()[1]
                    values = values.strip("[];").split(",")

                    # Remove any surrounding quotes and whitespace from values
                    values = [value.strip().strip('"') for value in values]

                    # Add to the result dictionary
                    if key not in domains:
                        domains[key] = []
                    domains[key].extend(values)
                except ValueError:
                    # Skip lines that don't match the expected format
                    print(f"Skipping line due to unexpected format: {line}")

        return domains

    def _check_module(self, mod_path, file_path, domains):
        pattern = r"_F\d_"
        pattern2 = r'__shared__::(?:Corners|FreqInMHZ|FreqValues|CornerIdentifiers)\.(\w+)'
        with open(file_path, 'r') as f:
            flag = fd = prm = False
            tname = tnamefreq = flowdomain = param = crnfid = None
            for line in f:
                line = line.strip()
                if 'MultiTrialTest' in line:
                    flag = True
                    tname = line.split()[1]
                    freq = re.findall(pattern, tname)
                    tnamefreq = freq[-1].replace('_', '') if freq else None
                elif flag and line.startswith('TrialVariable '):
                    flowdomain = line.split()[1]
                    fd = True
                elif flag and 'CSharpTrialTest VminTC' in line:

                    param = line
                    prm = True
                    # pattern = r'__shared__::(?:Corners|FreqInMHZ|FreqValues|CornerIdentifiers)\.(\w+)'
                    crnfid = re.findall(pattern2, line)
                    crnfid = crnfid[0] if crnfid else None
                if flag and fd and prm:
                    self._validate_test(mod_path, tname, tnamefreq, flowdomain, param, crnfid, domains)
                    flag = fd = prm = False

    def _validate_test(self, mod_path, tname, tnamefreq, flowdomain, param, crnfid, domains):
        # module = os.path.basename(os.path.dirname(mod_path))
        module = mod_path
        if crnfid in domains:
            if tnamefreq in domains[crnfid]:  # TOP Frequency
                if ('Corners' in param or 'FreqInMHZ' in param or 'FreqValues' in param or 'CornerIdentifiers' in param) and '_TOP' in flowdomain:
                    self.add_pass(263, module)
                elif ('Corners' not in param and 'FreqInMHZ' not in param and 'FreqValues' not in param and 'CornerIdentifiers' not in param) and '_TOP' not in flowdomain:
                    self.add_pass(263, module)
                else:
                    self.add_error(263, module, f'TOP Freq test: {tname} is not using the correct _TOP FlowDomain and BinMatrixSpecs.flm.usrv Collection combo')
            else:
                if tnamefreq and 'VMAX' not in tname:
                    self.add_error(264, module, f'{tname} is using a wrong/nonexistent frequency "_{tnamefreq}_" but using Corners.{crnfid}. Valid Freq: {domains[crnfid]}')
                else:
                    self.add_pass(264, module)
        else:
            if '_TOP' in flowdomain:
                self.add_error(264, module, f'"{tname}" should NOT be using _TOP in FlowDomain when not using any collection from BinMatrixSpecs.flm.usrv')
            else:
                self.add_pass(264, module)


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    SkuMgrChk(TestProgram(sys.argv[1]).pickle_init()).run()
