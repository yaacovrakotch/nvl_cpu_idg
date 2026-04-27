#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Affected Boms module
"""
from gadget.disk import Chdir, listdir_noerror
from gadget.tputil import OtplFile, JsonRead
from gadget.pylog import log
from gadget.errors import confirm
from gadget.getgit import GitHub
from gadget.files import glob_one_only, File
from os.path import exists, dirname, basename
from pprint import pprint, pformat
import glob
import os
import re


class AffectedBom:
    """
    Given cwd or REPO_DIR, return affected boms by reading tpproj of each of the boms
    Strategy is for this to be independent, that is, it does not need tpobj.
    Note that torch fixer is not yet called when AffectedBom is invoked.

    Optional affected_boms.json support:
    Modules can include an affected_boms.json file in their folder to map file paths
    to BOMs. The JSON file format is a dictionary mapping path patterns (string or regex)
    to BOM patterns (string or regex).

    Example affected_boms.json:
    {
        "InputFiles/.*\\.csv": "BOM1|BOM2",
        "patterns/special_.*": "BOM3",
        "configs/": "BOM.*"
    }

    The JSON file only affects files in subfolders of the module, not the immediate
    module folder or external folders.
    """

    def __init__(self):
        self.modified_files = self._get_modified_files()
        self.allboms = self._get_all_boms()
        self.iscommon = False
        self.json_mappings_cache = {}  # Cache for affected_boms.json files per module
        self.json_pattern_matches = None  # Computed once in main() for efficiency
        self.files_with_json_patterns = None  # Computed once in main() for efficiency

    def main(self):
        """
        :return: list of affected boms
        """
        log.info(f'-i- Starting AffectedBom(). Modified_files={len(self.modified_files)}')

        # Compute JSON pattern matches once for all BOMs (not BOM-dependent)
        self.json_pattern_matches = self._get_json_pattern_matches()

        # Extract files that match any JSON pattern (for exclusion from legacy logic)
        self._set_files_with_json_patterns()

        final = []
        for bom in self.allboms:
            stplinfo = self._read_stpl(bom)
            if self._is_affected(bom, stplinfo):
                final.append(bom)

        log.info(f'-i- AffectedBom Result: {final}')
        return final

    def _read_stpl(self, bom):
        """
        Read the stpl (Common) or tpproj (dielet) for this bom
        :return: list of paths (Modules/<team>/<modname>) with Modules/
        """
        if exists('Shared'):
            # dielet
            tpproj = glob_one_only(f'POR_TP/{bom}/*.tpproj')       # stpl is not complete during AffectedBom invokation
        else:
            # common
            self.iscommon = True
            tpproj = glob_one_only(f'POR_TP/{bom}/*.stpl')         # tpproj is not accurate/correct for Common

        robj = re.compile(r'(Modules/.*/)\w+\.')
        result = []
        log.info(f'-i- Reading: {tpproj}')
        for line in File(tpproj).chomp():
            line = line.replace('\\', '/')
            res = robj.search(line)

            # safety check
            confirm(not ('Modules/' in line and (not res)), f'Error in {line}', 'Pls check regex. Contact jqdelosr')

            if res:
                result.append(res.group(1))

        confirm(result, f'Error: No Modules found in {tpproj}', 'Expecting at least 1 Modules/ in tpproj')

        return result

    def _get_module_paths_from_modified_files(self):
        """
        Extract unique module paths from modified files.
        This discovers modules that have modified files, regardless of whether they're in stplinfo.
        This is important for common repo context where modules may not be in common's stpl files.

        :return: Set of module paths (e.g., {'Modules/TPI/ARR_COMMON_CKX/', 'Modules/TPI/OTHER_MOD/'})
        """
        module_paths = set()

        for fname in self.modified_files:
            fname_normalized = fname.replace('\\', '/')

            # Check if file is in a Modules subfolder
            if fname_normalized.startswith('Modules/'):
                # Extract module path: Modules/{area}/{module_name}/
                parts = fname_normalized.split('/')
                if len(parts) >= 3:
                    # Construct module path: Modules/{area}/{module_name}/
                    module_path = '/'.join(parts[:3]) + '/'
                    module_paths.add(module_path)

        return module_paths

    def _load_json_mappings(self, modpath):
        """
        Load affected_boms.json file for a given module path.
        The JSON file should be in the same directory as the module's mtpl file.

        :param modpath: Module path (e.g., 'Modules/TPI/ARR_COMMON_CKX/')
        :return: dict with path patterns mapped to BOM patterns, or empty dict if file doesn't exist
        """
        # Use cached result if already loaded
        if modpath in self.json_mappings_cache:
            return self.json_mappings_cache[modpath]

        # Construct the path to the affected_boms.json file
        json_path = os.path.join(modpath, 'affected_boms.json')

        # Initialize with empty dict
        mappings = {}

        # Check if the file exists
        if exists(json_path):
            data = JsonRead(json_path).load()

            # Validate that data is a dict
            if isinstance(data, dict):
                # Validate that all keys and values are valid regex patterns
                validated_mappings = {}
                for path_pattern, bom_pattern in data.items():
                    try:
                        # Validate path pattern can compile as regex
                        re.compile(path_pattern)
                        # Validate bom pattern can compile as regex
                        re.compile(bom_pattern)
                        validated_mappings[path_pattern] = bom_pattern
                    except re.error as e:
                        log.warning(f'-w- Invalid regex in {json_path}: pattern "{path_pattern}" or "{bom_pattern}" - {e}')
                        continue

                mappings = validated_mappings
                if mappings:
                    log.info(f'-i- Loaded affected_boms.json from {json_path}')
            else:
                log.warning(f'-w- Invalid format in {json_path}: expected dict, got {type(data).__name__}')

        # Cache the result
        self.json_mappings_cache[modpath] = mappings
        return mappings

    def _get_relevant_files_for_module(self, modpath):
        """
        Get relevant files and their relative paths for a given module.
        Only includes files in subfolders (not the immediate module folder).

        :param modpath: Module path (e.g., 'Modules/TPI/ARR_COMMON_CKX/')
        :return: Dict mapping full file path to relative path within module
        """
        modpath_normalized = modpath.rstrip('/')
        relevant_files = {}

        for fname in self.modified_files:
            fname_normalized = fname.replace('\\', '/')

            # Check if the file is within a subfolder of modpath
            if not fname_normalized.startswith(modpath_normalized + '/'):
                continue

            # Get the relative path from the module folder
            rel_path = fname_normalized[len(modpath_normalized) + 1:]

            # If rel_path has no '/', it's in the immediate folder - should not be affected by JSON
            if '/' not in rel_path:
                continue

            relevant_files[fname_normalized] = rel_path

        return relevant_files

    def _get_json_pattern_matches(self):
        """
        Get detailed information about which files match JSON path patterns.
        This method centralizes the logic for matching files against JSON patterns.

        :return: Dict with structure:
                 {modpath: {path_pattern: {'bom_pattern': str, 'matched_files': set()}}}
        """
        match_info = {}
        module_paths = self._get_module_paths_from_modified_files()

        for modpath in module_paths:
            mappings = self._load_json_mappings(modpath)
            if not mappings:
                continue

            relevant_files = self._get_relevant_files_for_module(modpath)
            if not relevant_files:
                continue

            # Join all relevant paths into a multi-line string for efficient regex matching
            paths_string = '\n'.join(relevant_files.values())

            match_info[modpath] = {}

            # Check each pattern to see which files match
            for path_pattern, bom_pattern in mappings.items():
                # Check if any file matches the path pattern (case-insensitive)
                if re.search(path_pattern, paths_string, re.MULTILINE | re.IGNORECASE):
                    matched_files = set()
                    # Find which specific files match this pattern
                    for fname, rel_path in relevant_files.items():
                        if re.search(path_pattern, rel_path, re.IGNORECASE):
                            matched_files.add(fname)

                    if matched_files:
                        match_info[modpath][path_pattern] = {
                            'bom_pattern': bom_pattern,
                            'matched_files': matched_files
                        }

        return match_info

    def _set_files_with_json_patterns(self):
        """
        Extract and set the files that match any JSON pattern.
        Uses self.json_pattern_matches to populate self.files_with_json_patterns.
        This should be called after _get_json_pattern_matches() has been run.
        """
        self.files_with_json_patterns = set()
        for modpath, patterns in self.json_pattern_matches.items():
            for path_pattern, info in patterns.items():
                self.files_with_json_patterns.update(info['matched_files'])

    def _check_json_mapping(self, bom):
        """
        Check if any modified files match JSON mappings that affect the given BOM.
        Uses pre-computed self.json_pattern_matches for efficiency when available.

        :param bom: BOM to check against
        :return: True if any file matches a mapping that includes this BOM, False otherwise
        """
        # If called before main(), compute on-demand
        if self.json_pattern_matches is None:
            match_info = self._get_json_pattern_matches()
        else:
            match_info = self.json_pattern_matches

        for modpath, patterns in match_info.items():
            for path_pattern, info in patterns.items():
                # Check if BOM matches the pattern (case-insensitive)
                if re.search(info['bom_pattern'], bom, re.IGNORECASE):
                    return True

        return False

    def _is_affected(self, bom, stplinfo):
        """
        Given a bom and stpl info for that bom, return if this bom is affected
        This routine is the main logic
        """
        if not self.modified_files:    # in cases of too many changes
            return True    # affected

        # Check JSON mappings first
        if self._check_json_mapping(bom):
            return True

        # Use pre-computed files_with_json_patterns (computed once in main())
        # These files should NOT fall back to old logic
        notbom = '|'.join(x for x in self.allboms + ['ZZZBOMZZZ'] if x != bom)
        rnotbom = re.compile(r'(%s)' % notbom)
        for fname in self.modified_files:
            fname = fname.replace('\\', '/')

            # Skip files that match JSON path patterns - they are handled exclusively by JSON logic
            if fname in self.files_with_json_patterns:
                continue

            # case1 - easy, bom is in path
            if bom in fname:
                return True

            # case1 - the other bom is in the path
            if rnotbom.search(fname):
                continue     # this file is unaffected

            # submodule - partial path
            for modpath in stplinfo:
                if fname in modpath:      # 'Modules/TPI' in 'Modules/TPI/TPI_XXX/'
                    return True

            # Modules/ case - it is in stpl
            if 'Modules/' in fname:
                if self.iscommon:
                    return True        # stpl and tpproj is not accurate in common repo. Thus, return always

                for modpath in stplinfo:
                    if modpath in fname:
                        return True
                continue    # this file is unaffected, goto next one

            # non-testprogram files
            if fname.startswith(('.github', 'TPConfig', 'CODEOWNERS')):
                continue    # this file is unaffected, goto next one

            # Shared is special - this is tested in common repo separately.
            if fname.startswith('Shared'):
                continue    # this file is unaffected, goto next one

            return True     # catch all, conservative case

        return False        # unaffected

    def _get_all_boms(self):
        """Return list of all boms"""
        return sorted(basename(x) for x in glob.glob('POR_TP/*'))

    def _get_modified_files(self):
        """
        :return: list of modified files from the PR
        """
        with Chdir(os.environ.get('REPO_DIR', '.')):
            return GitHub.get_modfiles()
