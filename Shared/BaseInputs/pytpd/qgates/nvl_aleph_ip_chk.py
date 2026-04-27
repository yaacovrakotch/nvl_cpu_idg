#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
QGate 378: Validates IP group consistency between ALEPH_FILES entries and the
patterns they target via PatternsRegEx.

This module checks that each JSON aleph file listed in ALEPH_FILES is assigned
to the correct IP group (IPC/IPG/IPH/IPP/PKG) and that any PatternsRegEx values
inside those files only match patterns that belong to the same IP group.

IP group classification rules for ALEPH_FILES entries:

* FUSE_ROOT_DIR_HUB          -> IPH
* FUSE_ROOT_DIR_G*           -> IPG
* FUSE_ROOT_DIR_PCD*         -> IPP
* FUSE_ROOT_DIR_CPU          -> IPC
* Other FUSE_ROOT_DIR_*      -> PKG
* "Common" in path           -> PKG
* Modules/<folder>/ in path  -> IPName from that module's .mconfig
* $M[GCPH]*_PATMODIFY_PATH   -> IPG / IPC / IPP / IPH respectively
* $M[N]*_PATMODIFY_PATH      -> PKG
* CLK_*_G* variable          -> IPG
* CLK_*_C* variable          -> IPC
* CLK_*_H* variable          -> IPH
* CLK_*_P* variable          -> IPP
* CLK_*_* other              -> PKG

If a PatternsRegEx is absent from an aleph file the file is silently skipped.

QGate 378: Aleph file IP group vs matched pattern plist IP group must match.
"""
import setenv  # must be first in the imports
import re
import json
import time
import xml.etree.ElementTree as ETree
from collections import defaultdict
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from gadget.files import File
from gadget.pylog import log
from os.path import dirname, join, exists, basename
import sys
import glob

_MAX_ERRORS_PER_ALEPH = 10    # cap to avoid flooding output


class AlephIpChk(QGateBase):
    IP_RE = re.compile(r'<IPName>\s*([^<]+)\s*</IPName>', re.IGNORECASE)
    _VALID_IPS = frozenset({'IPC', 'IPG', 'IPH', 'IPP', 'PKG'})
    _REGEX_META_RE = re.compile(r'[.\^$*+?{}\[\]|()\\]')
    _FIELD_LIST_RE = re.compile(r'"(?P<key>PatternsRegEx)"\s*:\s*\[(?P<body>.*?)\]', re.DOTALL)
    _FIELD_SCALAR_RE = re.compile(r'"(?P<key>PatternsRegEx)"\s*:\s*"(?P<val>(?:\\.|[^"\\])*)"')
    _QUOTED_RE = re.compile(r'"((?:\\.|[^"\\])*)"')
    FALLBACK_TO_GLOBAL_PATTERNS = True
    FALLBACK_SKIP_MODULES = frozenset({'BASE'})
    _GLOBAL_SCOPE = '__GLOBAL_PAT_SCOPE__'

    # ------------------------------------------------------------------ #
    # IP classification helpers                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_ip(name):
        """
        Return one of IPC / IPG / IPH / IPP / PKG.

        :param name: raw IP name string
        :return: canonical IP string
        """
        n = str(name).strip().upper()
        if n in ('IPC', 'IPG', 'IPH', 'IPP'):
            return n
        return 'PKG'

    @staticmethod
    def _ip_from_fuse_varname(varname):
        """
        Return IP for a FUSE_ROOT_DIR_* variable name, or None if not applicable.

        :param varname: environment variable name (any case)
        :return: IP string or None
        """
        vu = varname.upper()
        if not vu.startswith('FUSE_ROOT_DIR_'):
            return None
        suffix = vu[len('FUSE_ROOT_DIR_'):]
        if suffix == 'HUB':
            return 'IPH'
        if suffix.startswith('G'):
            return 'IPG'
        if suffix.startswith('PCD'):
            return 'IPP'
        if suffix == 'CPU':
            return 'IPC'
        return 'PKG'

    @staticmethod
    def _ip_from_patmodify_varname(varname):
        """
        Return IP for a M[GCPHN]*_PATMODIFY_PATH variable, or None.

        :param varname: environment variable name (any case)
        :return: IP string or None
        """
        vu = varname.upper()
        if 'PATMODIFY_PATH' not in vu:
            return None
        # Match M<letter> pattern: handles both plain M[GCPHN] and _M[GCPHN]
        m = re.search(r'_M([GCPHN])', vu) or re.match(r'M([GCPHN])', vu)
        if m:
            return {'G': 'IPG', 'C': 'IPC', 'P': 'IPP', 'H': 'IPH', 'N': 'PKG'}[m.group(1)]
        return None

    @staticmethod
    def _ip_from_clk_varname(varname):
        """
        Return IP for a CLK_*_<G|C|H|P>* variable, or None if not applicable.

        :param varname: environment variable name (any case)
        :return: IP string or None
        """
        vu = varname.upper()
        if not vu.startswith('CLK_') and 'CLK' not in vu:
            return None
        m = re.search(r'CLK_[A-Z0-9]+_([GCPH])', vu)
        if m:
            return {'G': 'IPG', 'C': 'IPC', 'H': 'IPH', 'P': 'IPP'}[m.group(1)]
        return None

    def _build_prefix_ip_map(self):
        """
        Build {resolved_path_prefix: ip} by classifying env variable names via
        FUSE_ROOT_DIR, PATMODIFY_PATH and CLK rules, then resolving their values.

        Each resolved value (which may be semicolon-separated) is split and each
        part is stored as a path prefix mapped to its IP.

        :return: dict {resolved_prefix: ip}
        """
        result = {}
        env_dict = self.tpobj.env.get_env_dict()

        for varname in env_dict:
            ip = (self._ip_from_fuse_varname(varname)
                  or self._ip_from_patmodify_varname(varname)
                  or self._ip_from_clk_varname(varname))
            if ip is None:
                continue
            resolved = self.tpobj.env.get_contents(varname)
            for part in resolved.replace('\\', '/').replace('//', '/').split(';'):
                part = part.strip()
                if part:
                    result[part] = ip

        return result

    @staticmethod
    def _get_module_from_path(path, modfolder2mod):
        """
        Return the module name for a given path, or 'BASE' if not found.

        The TP folder structure is .../Modules/<CATEGORY>/<MODULE_FOLDER>/...
        so multiple segments after /Modules/ are tried against modfolder2mod
        until a match is found.  Falls back to 'BASE' if no match exists.

        :param path: normalized forward-slash path
        :param modfolder2mod: {modfolder_upper: module_name} from get_modfolder2mod()
        :return: module name string
        """
        m = re.search(r'/[Mm]odules/(.*)', path)
        if m:
            for segment in m.group(1).split('/'):
                if not segment:
                    continue
                mod = modfolder2mod.get(segment.upper())
                if mod:
                    return mod
        return 'BASE'

    def _build_modfolder_ip_map(self):
        """
        Build {MODULE_FOLDER_UPPER: ip} by reading IPName from each module's
        .mconfig file.

        :return: dict {modfolder_upper: ip}
        """
        result = {}
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            if 'Modules' not in mtpl:
                continue
            modfolder = basename(dirname(mtpl))
            modfolder_upper = modfolder.upper()
            if modfolder_upper in result:
                continue
            mconfigs = glob.glob(f'{dirname(mtpl)}/*.mconfig')
            if not mconfigs:
                continue
            text = File(mconfigs[0]).read()
            ip_match = self.IP_RE.search(text)
            result[modfolder_upper] = self._normalize_ip(ip_match.group(1)) if ip_match else 'PKG'

        return result

    def _classify_aleph_path(self, resolved_path, prefix_ip_map, modfolder_ip_map):
        """
        Classify a resolved aleph file path into an IP group.

        Resolution order:
        1. Longest-prefix match against prefix_ip_map (from env variable rules).
        2. "/common/" anywhere in path -> PKG.
        3. "/Modules/<folder>/" in path -> modfolder_ip_map lookup.
        4. Default -> PKG.

        :param resolved_path: resolved absolute path string
        :param prefix_ip_map: {path_prefix: ip} built from env vars
        :param modfolder_ip_map: {MODULE_FOLDER_UPPER: ip} from mconfigs
        :return: ip string
        """
        norm = resolved_path.replace('\\', '/').replace('//', '/')

        # Longest matching prefix
        best_prefix = ''
        best_ip = None
        for prefix, ip in prefix_ip_map.items():
            if norm.startswith(prefix) and len(prefix) > len(best_prefix):
                best_prefix = prefix
                best_ip = ip
        if best_ip is not None:
            return best_ip

        # Common path
        if '/common/' in norm.lower():
            return 'PKG'

        # Modules path -- try all segments after /Modules/ against modfolder_ip_map
        m = re.search(r'/[Mm]odules/(.*)', norm)
        if m:
            for segment in m.group(1).split('/'):
                if not segment:
                    continue
                ip = modfolder_ip_map.get(segment.upper())
                if ip:
                    return ip

        return 'PKG'

    # ------------------------------------------------------------------ #
    # Plist -> IP map                                                     #
    # ------------------------------------------------------------------ #

    def _build_plist_ip_map(self):
        """
        Build {plist_filename: ip} from two sources:

        1. PLIST_ALL_<IP>.plist.[ip]xml files in envdir (authoritative).
        2. module.mconfig PlistFile entries per BomGroup-selected PORRoot (fill gaps).

        :return: dict {plist_filename: ip}
        """
        result = {}
        envdir = self.tpobj.envdir
        env_bomgroup = basename(envdir).strip().upper()

        # Source 1: PLIST_ALL_*.plist.ipxml / .plist.xml in envdir
        candidates = (glob.glob(join(envdir, 'PLIST_ALL_*.plist.ipxml'))
                      + glob.glob(join(envdir, 'PLIST_ALL_*.plist.xml')))
        for xmlfile in candidates:
            fname = basename(xmlfile)
            m = re.match(r'PLIST_ALL_([^.]+)\.plist', fname, re.IGNORECASE)
            if not m:
                continue
            ip = self._normalize_ip(m.group(1))
            try:
                root = ETree.parse(xmlfile).getroot()
                for node in root.iter('PListFile'):
                    name = node.attrib.get('name')
                    if name and name not in result:
                        result[name] = ip
            except Exception:
                for name in re.findall(r'<PListFile\s+name="([^"]+)"', File(xmlfile).read()):
                    if name not in result:
                        result[name] = ip

        # Source 2: module.mconfig PlistFiles (fills gaps not covered by ipxml)
        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            if 'Modules' not in mtpl:
                continue
            mconfigs = glob.glob(f'{dirname(mtpl)}/*.mconfig')
            if not mconfigs:
                continue
            text = File(mconfigs[0]).read()
            ip_match = self.IP_RE.search(text)
            ip = self._normalize_ip(ip_match.group(1)) if ip_match else 'PKG'
            try:
                root = ETree.parse(mconfigs[0]).getroot()
            except Exception:
                continue

            # Select BomGroup-matching PORRoot, fall back to first
            por_roots = root.findall('.//PORRoot')
            selected = None
            for pr in por_roots:
                bg = (pr.attrib.get('BomGroup') or pr.attrib.get('BOMGROUP') or '').strip().upper()
                if bg == env_bomgroup:
                    selected = pr
                    break
            if selected is None and por_roots:
                selected = por_roots[0]
            if selected is None:
                continue

            for pf in selected.findall('.//PlistFile'):
                plist_name = (pf.text or '').strip() or pf.attrib.get('name', '').strip()
                if plist_name and plist_name not in result:
                    result[plist_name] = ip

        return result

    # ------------------------------------------------------------------ #
    # Pattern extraction from plist files                                 #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_pats_from_plist_file(plist_path):
        """
        Return set of pattern names from a .plist file by scanning Pat lines.

        Strips trailing ';' terminators from pattern names, which are present
        in standard HDMT plist syntax (Pat <name>;).

        :param plist_path: full path to .plist file
        :return: set of pattern name strings
        """
        pats = set()
        with open(plist_path, errors='ignore') as fh:
            for line in fh:
                stripped = line.lstrip()
                if stripped.startswith('Pat '):
                    parts = stripped.split(None, 2)
                    if len(parts) >= 2:
                        pats.add(parts[1].rstrip(';').strip())
        return pats

    def _build_pat_ip_map(self, plist_ip_map):
        """
        Build {pattern_name: (ip, plist_path)} by reading .plist files.

        Uses tpobj.plists.get_plist_list() (already cached, no disk scan) to
        build a {basename: full_path} index, then reads Pat lines from each
        file that appears in plist_ip_map.

        :param plist_ip_map: {plist_filename: ip}
        :return: dict {pattern_name: (ip, plist_path)}
        """
        # Build basename -> full_path index from already-loaded plist list
        file_index = {}
        for full_path in self.tpobj.plists.get_plist_list():
            bn = basename(full_path)
            if bn not in file_index:
                file_index[bn] = full_path

        result = {}
        for plist_name, ip in plist_ip_map.items():
            plist_path = file_index.get(plist_name)
            if not plist_path:
                continue
            for pat in self._get_pats_from_plist_file(plist_path):
                if pat not in result:
                    result[pat] = (ip, plist_path)
        return result

    def _build_module_pat_map(self, pat_ip_map):
        """
        Build {module_name: [(pattern_name, ip, plist_path), ...]} by keeping only
        patterns from plists referenced by non-bypassed tests in each module.

        :param pat_ip_map: dict {pattern_name: (ip, plist_path)}
        :return: dict {module_name: list of (pattern_name, ip, plist_path)}
        """
        plb_map = self.tpobj.plists.get_plb_map()   # {patlist_name: plist_full_path}

        # module -> set of plist basenames used by non-bypassed tests
        mod2plist = defaultdict(set)
        for mod, _tn, data in self.tpobj.mtpl.iter_flows('MAIN',
                                                         bypass=True,
                                                         keyparam='patlist',
                                                         edict=True):
            raw_patlist = str(data.get('patlist', '')).strip()
            if not raw_patlist:
                continue
            plb = raw_patlist.split('::')[-1]
            plist_path = plb_map.get(plb)
            if not plist_path:
                continue
            mod2plist[mod].add(basename(plist_path))

        # Index patterns by plist basename for efficient module selection
        plist2patterns = defaultdict(list)
        for pat_name, (pat_ip, plist_path) in pat_ip_map.items():
            plist2patterns[basename(plist_path)].append((pat_name, pat_ip, plist_path))

        result = {}
        for mod, plist_names in mod2plist.items():
            pats = []
            for plist_name in plist_names:
                pats.extend(plist2patterns.get(plist_name, []))
            if pats:
                result[mod] = pats

        return result

    # ------------------------------------------------------------------ #
    # Aleph JSON processing                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_aleph_match_fields(aleph_path):
        """
          Return extracted match fields from an aleph file.

          Behavior:
          1. For non-JSON paths, return an empty PatternsRegEx set.
          2. For JSON files, try json.loads() and recursively collect
              PatternsRegEx values.
          3. If JSON parsing fails, fall back to text-based extraction of
              PatternsRegEx list/scalar fields.
          4. If file read fails, return an empty PatternsRegEx set.

        :param aleph_path: full path to aleph .json file
        :return: dict {'PatternsRegEx': set}
        """
        if not aleph_path.lower().endswith('.json'):
            return {'PatternsRegEx': set()}
        fields = {
            'PatternsRegEx': set(),
        }

        try:
            with open(aleph_path, errors='replace') as fh:
                text_data = fh.read()
        except Exception:
            return fields

        try:
            data = json.loads(text_data)
        except Exception:
            data = None

        def _add_values(name, value):
            if isinstance(value, list):
                items = value
            else:
                items = [value]

            for item in items:
                if not item:
                    continue
                text = str(item).strip()
                fields[name].add(text)

        def _walk(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in fields:
                        _add_values(k, v)
                    else:
                        _walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    _walk(item)

        if data is not None:
            _walk(data)
            return fields

        # Fallback for malformed JSON: extract field values directly from text.
        for m in AlephIpChk._FIELD_LIST_RE.finditer(text_data):
            key = m.group('key')
            body = m.group('body')
            values = [bytes(x, 'utf-8').decode('unicode_escape') for x in AlephIpChk._QUOTED_RE.findall(body)]
            _add_values(key, values)

        for m in AlephIpChk._FIELD_SCALAR_RE.finditer(text_data):
            key = m.group('key')
            val = bytes(m.group('val'), 'utf-8').decode('unicode_escape')
            _add_values(key, val)

        return fields

    # ------------------------------------------------------------------ #
    # Main                                                                #
    # ------------------------------------------------------------------ #

    def main(self):
        """
        For each ALEPH_FILES entry, validate PatternsRegEx matches against
        module-scoped (or optional global fallback) non-PKG patterns and report
        cross-IP matches.

        Implementation notes are annotated inline using [F1]..[F10] comments
        at the corresponding code blocks.
        """
        t0 = time.time()

        # [F1] Build plist -> IP map.
        plist_ip_map = self._build_plist_ip_map()
        log.info(f'-i- AlephIpChk: plist_ip_map built: {len(plist_ip_map)} plists, {time.time() - t0: .1f}s')

        # [F2] Build pattern -> (IP, plist_path) map.
        pat_ip_map = self._build_pat_ip_map(plist_ip_map)
        log.info(f'-i- AlephIpChk: pat_ip_map built: {len(pat_ip_map)} patterns, {time.time() - t0: .1f}s')

        if not pat_ip_map:
            return

        # [F3] Restrict patterns to module-referenced plists from non-bypassed tests.
        module_pat_map = self._build_module_pat_map(pat_ip_map)
        log.info(f'-i- AlephIpChk: module_pat_map built: {len(module_pat_map)} modules, {time.time() - t0: .1f}s')

        # [F4]/[F5] Build classification maps for path-based aleph IP resolution.
        prefix_ip_map = self._build_prefix_ip_map()
        modfolder_ip_map = self._build_modfolder_ip_map()
        modfolder2mod = self.tpobj.mtpl.get_modfolder2mod()
        log.info(f'-i- AlephIpChk: classification maps built, {time.time() - t0: .1f}s')

        aleph_files = self.tpobj.env.get_contents('ALEPH_FILES', islist=True)

        # KEY OPTIMISATION: collect unique (module, aleph_ip, regex_str, scope)
        # aleph files before any matching.  Thousands of configs in one JSON file
        # typically share the same regex string -- deduplication avoids re-matching
        # the same regex against module-specific pattern sets repeatedly.
        # unique_checks: {(module_name, aleph_ip, regex_str, pattern_scope): aleph_name}
        # [F6]/[F7] Scan ALEPH_FILES and build unique scoped checks.
        unique_checks = {}
        for aleph_raw_path in aleph_files:
            aleph_path = aleph_raw_path.strip().replace('\\', '/').replace('//', '/')
            if not aleph_path.lower().endswith('.json'):
                continue
            if not exists(aleph_path):
                continue
            aleph_ip = self._classify_aleph_path(aleph_path, prefix_ip_map, modfolder_ip_map)
            if aleph_ip == 'PKG':   # skip PKG-mapped aleph files entirely
                continue

            aleph_name = basename(aleph_path)
            mod_name = self._get_module_from_path(aleph_path, modfolder2mod)

            # Keep aleph in scope even when module has no active non-bypassed
            # patlist map, optionally falling back to global non-PKG patterns.
            allow_fallback = (self.FALLBACK_TO_GLOBAL_PATTERNS
                              and mod_name not in self.FALLBACK_SKIP_MODULES)
            if mod_name not in module_pat_map and not allow_fallback:
                continue

            fields = self._get_aleph_match_fields(aleph_path)
            regexes = fields['PatternsRegEx']

            if not regexes:
                continue

            for regex_str in regexes:
                if mod_name in module_pat_map:
                    pattern_scope = mod_name
                else:
                    pattern_scope = self._GLOBAL_SCOPE

                key = (mod_name, aleph_ip, regex_str, pattern_scope)
                if key not in unique_checks:
                    unique_checks[key] = aleph_name

        log.info(f'-i- AlephIpChk: {len(unique_checks)} unique (module, ip, regex) checks, {time.time() - t0: .1f}s')

        # Group checks by (pattern_scope, regex) so each regex is compiled/scanned
        # once per scope. This avoids repeated global scans for fallback modules.
        # [F8] Group checks by scope+regex for compile-once evaluation.
        regex_checks = defaultdict(list)
        for (mod_name, aleph_ip, regex_str, pattern_scope), aleph_name in unique_checks.items():
            regex_checks[(pattern_scope, regex_str)].append((mod_name, aleph_ip, aleph_name))

        log.info(f'-i- AlephIpChk: {len(regex_checks)} unique (scope, regex) groups to evaluate, {time.time() - t0: .1f}s')

        # Match each scope+regex exactly once
        global_non_pkg_pats = [(n, ip, path) for n, (ip, path) in pat_ip_map.items() if ip != 'PKG']

        errors_per_aleph = defaultdict(int)   # aleph_name -> error count
        # [F9]/[F10] Evaluate matches: emit mismatch errors and pass on same-IP hits.
        for (pattern_scope, regex_str), checks in regex_checks.items():
            if pattern_scope == self._GLOBAL_SCOPE:
                all_pats = global_non_pkg_pats if self.FALLBACK_TO_GLOBAL_PATTERNS else []
            else:
                all_pats = [x for x in module_pat_map.get(pattern_scope, []) if x[1] != 'PKG']

            if not all_pats:
                continue

            active_checks = []
            for mod_name, aleph_ip, aleph_name in checks:
                if errors_per_aleph[aleph_name] >= _MAX_ERRORS_PER_ALEPH:
                    continue
                active_checks.append({'aleph_ip': aleph_ip,
                                      'aleph_name': aleph_name,
                                      'mod_name': mod_name,
                                      'passed': False,
                                      'needs_scan': True})

            if not active_checks:
                continue

            rx = re.compile(regex_str)

            outstanding = len(active_checks)
            for pat_name, pat_ip, plist_path in all_pats:
                if outstanding <= 0:
                    break
                if not rx.search(pat_name):
                    continue
                for check in active_checks:
                    if not check['needs_scan']:
                        continue

                    if pat_ip == check['aleph_ip']:
                        check['passed'] = True
                    elif errors_per_aleph[check['aleph_name']] < _MAX_ERRORS_PER_ALEPH:
                        msg = ('IP mismatch: aleph "%s" (%s) matched pattern "%s"'
                               ' in plist "%s" IP=%s; regex="%s"'
                               % (check['aleph_name'],
                                  check['aleph_ip'],
                                  pat_name,
                                  plist_path,
                                  pat_ip,
                                  regex_str))
                        self.add_error(378, mod_name, msg)
                        errors_per_aleph[check['aleph_name']] += 1

                    # Once a same-IP match is found for this aleph+regex check,
                    # stop checking additional patterns for that check.
                    still_needs_scan = (not check['passed']
                                        and errors_per_aleph[check['aleph_name']] < _MAX_ERRORS_PER_ALEPH)
                    if check['needs_scan'] and not still_needs_scan:
                        outstanding -= 1
                    check['needs_scan'] = still_needs_scan

            for check in active_checks:
                if check['passed']:
                    self.add_pass(378, mod_name)

        log.info(f'-i- AlephIpChk: done. Elapsed={time.time() - t0: .1f}s')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    AlephIpChk(TestProgram(sys.argv[1]).pickle_init()).run()
