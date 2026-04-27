#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Implements AHMT quality gate checks for test programs.

This module validates that:

* AHMT module bins defined in AHMT mtpl files exist in the corresponding
  non-AHMT module subbindef files.
* Pattern revisions (PORRoot paths) referenced in AHMT mconfig files are
  present in the AHMT environment (.env) files.
* AlephFile entries from AHMT mconfig files are present in the AHMT
  environment (.env) files.
"""
import sys
import os
import re
from gadget.files import File
from gadget.pylog import log
from gadget.strmore import to_str
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from xml.etree import cElementTree as ElementTree
import glob


class AHMTCheck(QGateBase):

    def main(self):
        """
        Check only for AHMT TP.  If no AHMT in POR_TP folder skip this QGate
        * AHMT Module Bins should exist in the non-AHMT Module counterpart's subbindef file
        * Pattern rev in the AHMT Module's mconfig should exist in the AHMT env file
        """
        # if 'AHMT' not in self.tpobj.envdir:
        #    print("Skipping: Not an AHMT TP")
        #    return

        all_mods = self.tpobj.mtpl.get_mod2fname()
        for mod_path, file_path in all_mods.items():
            modfolder = file_path.split('/')[-2]
            if 'AHMT' in modfolder:
                # print(mod_path, file_path)
                ahmtpath = file_path.rsplit('/', 1)[0] + "/"
                porpath = (
                    re.sub(r'(/[^/]*?)AHMT([^/]*)/([^/]+)$', r'\1\2/\3', file_path.strip())
                ).rsplit('/', 1)[0] + "/"

                # Check if AHMT bins exist in non-AHMT SubBindef file
                self.check_ahmt_bins_in_subbindef(file_path, ahmtpath, porpath, modfolder)

                # Check if PORRoot paths from mconfig are in env file
                self.check_porroot_in_envfile(ahmtpath, modfolder)

                # Check if AlephFile values from mconfig are in env file
                self.check_alephfiles_in_envfile(ahmtpath, modfolder)

    def check_ahmt_bins_in_subbindef(self, ahmtfile, ahmtpath, porpath, modfolder):
        """
        Check if SetBin values from AHMT mtpl file exist in the non-AHMT SubBindef file.

        :param ahmtfile: Path to the AHMT mtpl file
        :param ahmtpath: Directory path containing AHMT mtpl file
        :param porpath: Directory path for the non-AHMT counterpart
        :param modfolder: AHMT module folder name
        :return: None
        """
        # Check if non-AHMT path exists
        if not os.path.isdir(porpath):
            log.info(f'-i- Non-AHMT counterpart directory does not exist: {porpath}')
            log.info(f'-i- Skipping SubBindef check for {modfolder}')
            return

        # Extract bins from AHMT mtpl file
        ahmt_bins = self.extract_setbin_from_mtpl(ahmtfile)

        if not ahmt_bins:
            log.info(f'-i- No SetBin calls found in AHMT file: {ahmtfile}')
            return

        # Find and parse the non-AHMT SubBindef file
        subbindef_bins = self.extract_bins_from_subbindef(porpath)

        if subbindef_bins is None:
            self.add_error(290, modfolder, f'SubBindef file not found in non-AHMT path: {porpath}')
            return

        # Check if all AHMT bins exist in the SubBindef file
        missing_bins = ahmt_bins - subbindef_bins

        if missing_bins:
            missing_bins_str = ', '.join(sorted(missing_bins))
            self.add_error(290, modfolder,
                           f'AHMT bins missing in non-AHMT SubBindef: {missing_bins_str}')
            log.info(f'-e- Missing bins in {porpath}: {missing_bins_str}')
        else:
            log.info(f'-i- All AHMT bins from {ahmtfile} exist in non-AHMT SubBindef')
            self.add_pass(290, modfolder)

    def extract_setbin_from_mtpl(self, mtpl_file):
        """
        Extract all SetBin values from an mtpl file.

        :param mtpl_file: Path to the mtpl file
        :return: Set of bin numbers (as strings) found in SetBin calls
        """
        bins = set()

        if not os.path.exists(mtpl_file):
            log.error(f'-e- AHMT mtpl file does not exist: {mtpl_file}')
            return bins

        lines = File(mtpl_file).read().splitlines()

        pattern_8dig = re.compile(r'b(\d{8})(?:_|["\s;])')
        pattern_7dig = re.compile(r'b(\d{7})(?:_|["\s;])')
        pattern_4dig = re.compile(r'[+\s]"(\d{4})(?:_|")')

        in_multiline_comment = False

        for line in lines:
            if '/*' in line:
                in_multiline_comment = True
            if '*/' in line:
                in_multiline_comment = False
                continue
            if in_multiline_comment:
                continue

            if '//' in line:
                line = line.split('//')[0]
            if '#' in line:
                line = line.split('#')[0]

            if not line.strip():
                continue
            if 'SetBin' not in line:
                continue

            bins.update(pattern_8dig.findall(line))

            bins_7dig = pattern_7dig.findall(line)
            for bin_7 in bins_7dig:
                if not any(bin_8.startswith(bin_7) for bin_8 in bins):
                    bins.add(bin_7)

            bins.update(pattern_4dig.findall(line))

        log.info(f'-i- Extracted {len(bins)} bins from {mtpl_file}')
        return bins

    def extract_bins_from_subbindef(self, porpath):
        """
        Extract all bin numbers from SubBindef (.sbdefs) file in the given path.

        :param porpath: Directory path to search for SubBindef file
        :return: Set of bin numbers (as strings), or None if file not found
        """
        sbdefs_files = glob.glob(f'{porpath}*.sbdefs')

        if not sbdefs_files:
            log.error(f'-e- No .sbdefs file found in {porpath}')
            return None

        if len(sbdefs_files) > 1:
            log.info(f'-i- Multiple .sbdefs files found, using first: {sbdefs_files[0]}')

        sbdefs_file = sbdefs_files[0]
        bins = set()

        if not os.path.exists(sbdefs_file):
            log.error(f'-e- SubBindef file does not exist: {sbdefs_file}')
            return None

        lines = File(sbdefs_file).read().splitlines()
        for line in lines:
            line = line.strip()

            if line.startswith('#') or line.startswith('//') or not line:
                continue

            if line.startswith('LeafBin') or line.startswith('Bin '):
                parts = line.split()
                if len(parts) >= 3:
                    bin_number = parts[2]
                    bin_number = bin_number.rstrip(':;,')
                    if bin_number.isdigit():
                        bins.add(bin_number)

        log.info(f'-i- Extracted {len(bins)} bins from SubBindef: {sbdefs_file}')
        return bins

    def check_porroot_in_envfile(self, ahmtpath, modfolder):
        """
        Check if PORRoot paths from module.mconfig exist in TORCH_AUTO_PLIST_PATH section of env file.

        :param ahmtpath: Directory path containing AHMT module
        :param modfolder: AHMT module folder name
        :return: None
        """
        mconfig_files = glob.glob(f'{ahmtpath}*module.mconfig')

        if not mconfig_files:
            log.info(f'-i- No module.mconfig file found in {ahmtpath}')
            return

        mconfig_file = mconfig_files[0]

        porroot_data = self.parse_mconfig_porroot(mconfig_file)

        if not porroot_data:
            log.info(f'-i- No PORRoot paths found in {mconfig_file}')
            return

        plist_paths = []
        pat_paths = []
        env_parse_failed = False

        # Use only explicitly attached env object. Mock objects auto-create attributes,
        # which can otherwise look like valid env parser objects.
        env_obj = getattr(self.tpobj, '__dict__', {}).get('env', None)

        def to_path_list(value):
            if not value:
                return []
            if isinstance(value, (list, tuple, set)):
                return list(value)
            if isinstance(value, str):
                return [value]
            return []

        if env_obj and hasattr(env_obj, 'get_item'):
            try:
                plist_paths = to_path_list(env_obj.get_item('TORCH_AUTO_PLIST_PATH', islist=True))
                pat_paths = to_path_list(env_obj.get_item('TORCH_AUTO_PAT_PATH', islist=True))
            except Exception as e:
                env_parse_failed = True
                log.info(f'-i- Failed parsing TORCH_AUTO paths from env object: {e}')

        # Compatibility fallback for tests/mocks that only provide envfile.
        if env_parse_failed or (not plist_paths and not pat_paths):
            env_file = getattr(self.tpobj, 'envfile', None)
            if env_file and os.path.exists(env_file):
                in_torch_section = False
                lines = File(env_file).read().splitlines()
                for line in lines:
                    line_stripped = line.strip()

                    if 'TORCH_AUTO_PLIST_PATH' in line or 'TORCH_AUTO_PAT_PATH' in line:
                        in_torch_section = True
                        continue

                    if not in_torch_section:
                        continue

                    if not line_stripped:
                        in_torch_section = False
                        continue

                    if line_stripped.startswith('[') or line_stripped.startswith('//['):
                        if not line_stripped.startswith('//'):
                            in_torch_section = False
                        continue

                    if line_stripped.startswith('//') or line_stripped.startswith('#'):
                        continue

                    raw = line_stripped.rstrip('+').strip().strip('"').strip("'").rstrip(';').strip()
                    if raw and not raw.startswith('$') and raw != '+':
                        plist_paths.append(raw)

        env_paths = set()
        for raw_path in list(plist_paths) + list(pat_paths):
            normalized = to_str(raw_path).strip().strip('"').strip("'").rstrip(';').rstrip('+').strip()
            if normalized and not normalized.startswith('$') and normalized != '+':
                env_paths.add(normalized)

        if not env_paths:
            self.add_error(291, modfolder, f'TORCH_AUTO_PLIST_PATH section not found in env file')
            return

        for porroot_info in porroot_data:
            porroot_path = porroot_info['full_path']
            base_path = porroot_info['path'].replace('\\', '/').rstrip('/')
            rev = porroot_info['rev']
            patch = porroot_info['patch']

            paths_to_check = []
            if patch and patch.startswith('p'):
                try:
                    patch_num = int(patch[1:])

                    path_components = [base_path, rev, patch]
                    base_patch_path = '/'.join(filter(None, path_components))

                    paths_to_check.append(f"{base_patch_path}/plb")

                    for i in range(patch_num, -1, -1):
                        pat_components = [base_path, rev, f"p{i}", "pat"]
                        pat_path = '/'.join(filter(None, pat_components))
                        paths_to_check.append(pat_path)
                except ValueError:
                    paths_to_check = [porroot_path]
            else:
                paths_to_check = [porroot_path]

            missing_paths = []
            for check_path in paths_to_check:
                path_found = False
                for env_path in env_paths:
                    if env_path == check_path or env_path.startswith(check_path + '/'):
                        path_found = True
                        log.info(f'-i- PORRoot "{check_path}" matched with env path "{env_path}"')
                        break

                if not path_found:
                    missing_paths.append(check_path)

            if missing_paths:
                missing_str = ', '.join(missing_paths)
                self.add_error(291, modfolder,
                               f'PORRoot paths missing in TORCH_AUTO_PLIST_PATH: {missing_str}')
                log.error(f'-e- Missing paths in env file: {missing_str}')
            else:
                log.info(f'-i- All PORRoot paths for "{porroot_path}" found in TORCH_AUTO_PLIST_PATH')
                self.add_pass(291, modfolder)

    def parse_mconfig_porroot(self, mconfig_file):
        """
        Parse module.mconfig XML file and extract PORRoot paths.
        Returns a list of dictionaries containing path components.

        :param mconfig_file: Path to module.mconfig file
        :return: List of dictionaries with 'path', 'rev', 'patch', 'full_path' keys
        """
        porroot_data = []

        if not os.path.exists(mconfig_file):
            log.error(f'-e- mconfig file does not exist: {mconfig_file}')
            return []

        try:
            tree = ElementTree.parse(mconfig_file)
            root = tree.getroot()

            for patterns in root.iter('Patterns'):
                for porroot in patterns.iter('PORRoot'):
                    path = porroot.get('Path', '').strip()
                    rev = porroot.get('Rev', '').strip()
                    patch = porroot.get('Patch', '').strip()

                    path_parts = []
                    if path:
                        path_parts.append(path)
                    if rev:
                        path_parts.append(rev)
                    if patch:
                        path_parts.append(patch)

                    if path_parts:
                        full_path = '\\'.join(path_parts)
                        full_path = full_path.replace('\\', '/')
                        while '//' in full_path:
                            full_path = full_path.replace('//', '/')

                        porroot_data.append({
                            'path': path,
                            'rev': rev,
                            'patch': patch,
                            'full_path': full_path
                        })
                        log.info(f'-i- Found PORRoot in mconfig: {full_path}')

        except Exception as e:
            log.error(f'-e- Error parsing mconfig file {mconfig_file}: {e}')
            return []

        return porroot_data

    def parse_mconfig_alephfiles(self, mconfig_file):
        """
        Parse module.mconfig XML file and extract AlephFile paths.

        :param mconfig_file: Path to module.mconfig file
        :return: List of AlephFile path strings
        """
        alephfile_paths = []

        if not os.path.exists(mconfig_file):
            log.error(f'-e- mconfig file does not exist: {mconfig_file}')
            return []

        try:
            tree = ElementTree.parse(mconfig_file)
            root = tree.getroot()

            # Find all AlephFile elements under AlephFiles
            for alephfiles in root.iter('AlephFiles'):
                for alephfile in alephfiles.iter('AlephFile'):
                    # AlephFile contains the path as text content
                    path = alephfile.text
                    if path:
                        path = path.strip()
                        if path:
                            alephfile_paths.append(path)
                            log.info(f'-i- Found AlephFile in mconfig: {path}')

        except Exception as e:
            log.error(f'-e- Error parsing mconfig file {mconfig_file}: {e}')
            return []

        return alephfile_paths

    def check_alephfiles_in_envfile(self, ahmtpath, modfolder):
        """
        Check if AlephFile values from module.mconfig are referenced in the env file.

        :param ahmtpath: Path to AHMT module folder
        :param modfolder: Name of the AHMT module folder
        """
        mconfig_file = ahmtpath + 'module.mconfig'

        # Check if mconfig file exists
        if not os.path.exists(mconfig_file):
            log.error(f'-e- module.mconfig not found: {mconfig_file}')
            return

        # Parse AlephFile paths from mconfig
        alephfile_paths = self.parse_mconfig_alephfiles(mconfig_file)
        if not alephfile_paths:
            log.info(f'-i- No AlephFile elements found in {mconfig_file}')
            return

        # Read the entire env file content
        env_file = self.tpobj.envfile
        if not os.path.exists(env_file):
            log.error(f'-e- Environment file does not exist: {env_file}')
            return

        env_content = File(env_file).read()

        # Check each AlephFile path appears somewhere in the env file
        for alephfile in alephfile_paths:
            if alephfile in env_content:
                self.add_pass(292, modfolder)
                log.info(f'-i- AlephFile "{alephfile}" from {modfolder} found in env file')
            else:
                self.add_error(292, modfolder,
                               f'AlephFile "{alephfile}" not found in env file')
                log.error(f'-e- AlephFile "{alephfile}" from {modfolder} not found in env file')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    AHMTCheck(TestProgram(sys.argv[1]).pickle_init()).run()
