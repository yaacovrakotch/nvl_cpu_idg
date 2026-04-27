#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
QGate for validating Hermes-generated plist configuration for NVL test programs.

This module checks speedflow test plist naming conventions and the structure and
consistency of master plists produced by Hermes. It enforces:

* Presence of a master plist for speedflow tests and absence for non-speedflow
    tests (QGates 372, 373).
* Valid structure and matching of RefPList entries in the master plist, including
        alignment between master and child plists (QGates 374, 375, 376).
* Use of approved templates and naming patterns for speedflow tests (QGate 377).

Current implementation notes:

* Master/child plist structure checks use `tpobj.plists` helper maps (`get_refplist`,
    `get_plist_dependent`, `get_pats_from_plb`) instead of local raw plist parsing.
* For QGate365, full speedflow token consistency (`F[1-5]X[A-Z0-9]*`) between
    speedflow test name and plist names is checked before deeper __0/__1 mismatch
    checks, and both checks are reported when both fail.
* QGate364 allows specific non __0/__1 helper entries when names indicate known
    exceptions (for example dts/acm/midcat/init/reset/preburst patterns, including
    Pat-style and RefPList-style naming forms).
"""
import re
import xml.etree.ElementTree as ETree
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from gadget.files import File
from os.path import dirname, join, exists, basename
import sys
import glob


class HermesPlistChk(QGateBase):
    TEMPLATE_APEX = 'ApexTC'
    VMIN_SPEEDFLOW_TEST_RE = re.compile(r'_VMIN_[A-Z0-9]+_F[1-5]X[A-Z0-9]*_')
    APEX_SPEEDFLOW_TEST_RE = re.compile(r'_APEX_[A-Z0-9]+_F[1-5]X[A-Z0-9]*_')
    SPEEDFLOW_FN_RE = re.compile(r'_F([1-5])X', re.IGNORECASE)
    SPEEDFLOW_TOKEN_RE = re.compile(r'_(F[1-5]X[A-Z0-9]*)_', re.IGNORECASE)
    DISABLE_DEEP_PAT_365 = True
    ALLOWED_SPEEDFLOW_TEMPLATES = {'VminTC', TEMPLATE_APEX, 'DDGShmooTC', 'CtvTokensTC'}
    SPEEDFLOW_362_SKIP_TEMPLATES = {'DDGShmooTC', 'CtvTokensTC'}
    NONSPEEDFLOW_363_SKIP_TEMPLATES = {'DDGShmooTC', 'CtvTokensTC'}
    POR_TAG_RE = re.compile(r'<PORRoot\b([^>]*)>')
    ATTR_RE = re.compile(r'(\w+)="([^"]+)"')
    IP_RE = re.compile(r'<IPName>\s*([^<]+)\s*</IPName>')
    PLIST_DECL_RE_TEMPLATE = r'^\s*(PList|GlobalPList)\s+{name}\b'
    PREEXEC_REF_RE = re.compile(r'^\s*PreExecRefPList\s+(\w+)\b')
    REF_SUFFIX_0 = '__0'
    REF_SUFFIX_1 = '__1'
    NONPAIR_ALLOWED_TOKENS = ('_acm_', 'midcat', '_init_', 'reset', '_preburst_', '__preburst_')

    @staticmethod
    def _get_first_present(params, keys):
        """Return first present value for candidate keys, else None."""
        for key in keys:
            if key in params:
                return params[key]
        return None

    def _is_speedflow_test(self, testname):
        """Return True if test name matches VMIN/APEX speedflow regex."""
        return bool(self.VMIN_SPEEDFLOW_TEST_RE.search(testname) or self.APEX_SPEEDFLOW_TEST_RE.search(testname))

    @staticmethod
    def _is_master_patlist(patlist):
        """Return True if patlist ends with _master."""
        if not patlist:
            return False
        return str(patlist).lower().endswith('_master')

    @staticmethod
    def _normalize_path(path):
        """Return normalized forward-slash path."""
        return path.replace('\\', '/').replace('//', '/')

    def _get_plist_names_from_ipxml(self, ipname):
        """Return set of plist filenames from PLIST_ALL_<IP>.plist.xml if present."""
        candidates = [
            join(self.tpobj.envdir, f'PLIST_ALL_{ipname}.plist.xml'),
            join(self.tpobj.envdir, f'PLIST_ALL_{ipname}.plist.ipxml'),
        ]
        for xmlfile in candidates:
            if not exists(xmlfile):
                continue
            try:
                root = ETree.parse(xmlfile).getroot()
                return {x.attrib.get('name') for x in root.iter('PListFile') if x.attrib.get('name')}
            except Exception:
                names = set(re.findall(r'<PListFile\s+name="([^"]+)"', File(xmlfile).read()))
                if names:
                    return names
        return set()

    def _build_modinfo(self, target_mods=None):
        """Return {module: {'ipname': str, 'plb_path': str, 'plist_names': set}} from module.mconfig."""
        result = {}
        modfolder2mod = self.tpobj.mtpl.get_modfolder2mod()
        env_bomgroup = basename(self.tpobj.envdir).strip().upper()

        for mtpl in self.tpobj.get_all_mtpl_from_stpl():
            if 'Modules' not in mtpl:
                continue
            modfolder = basename(dirname(mtpl))
            mod = modfolder2mod.get(modfolder)
            if not mod or mod in result:
                continue

            if target_mods is not None and mod not in target_mods:
                continue

            mconfigs = glob.glob(f'{dirname(mtpl)}/*.mconfig')
            if not mconfigs:
                continue

            text = File(mconfigs[0]).read()
            ip_match = self.IP_RE.search(text)
            if not ip_match:
                continue

            por_entries = []
            for tag_attrs in self.POR_TAG_RE.findall(text):
                attrs = {k.upper(): v for k, v in self.ATTR_RE.findall(tag_attrs)}
                if {'PATH', 'REV', 'PATCH'}.issubset(attrs):
                    por_entries.append(attrs)

            if not por_entries:
                continue

            selected = None
            for entry in por_entries:
                if entry.get('BOMGROUP', '').strip().upper() == env_bomgroup:
                    selected = entry
                    break

            if selected is None:
                selected = por_entries[0]

            ipname = ip_match.group(1).strip()
            por_path = selected['PATH']
            rev = selected['REV']
            patch = selected['PATCH']
            plb_path = self._normalize_path(join(por_path, rev, patch, 'plb'))
            plist_names = self._get_plist_names_from_ipxml(ipname)
            result[mod] = {
                'ipname': ipname,
                'plb_path': plb_path,
                'plist_names': plist_names,
            }

        return result

    def _find_master_in_plists(self, master_plist, modinfo, plb_map):
        """Return a plist file path that contains the given master plist for this module context."""
        plist_names = modinfo.get('plist_names', set())
        fallback = plb_map.get(master_plist)
        if not fallback:
            return None

        fallback = self._normalize_path(str(fallback))
        fallback_name = basename(fallback)
        if fallback_name not in plist_names:
            return None

        rev_plist_map = self._get_rev_plist_file_map()
        found_path = rev_plist_map.get(fallback_name)
        if found_path:
            return found_path
        return fallback

    def _get_rev_plist_file_map(self):
        """Return cached map of plist filename to full path from get_rev_paths()."""
        cached_map = getattr(self, '_rev_plist_file_map', None)
        if cached_map is not None:
            return cached_map

        result = {}
        for rev_path in self.tpobj.plists.get_rev_paths():
            for plist_file in glob.glob(join(rev_path, '*.plist')):
                plist_name = basename(plist_file)
                if plist_name not in result:
                    result[plist_name] = self._normalize_path(plist_file)

        self._rev_plist_file_map = result
        return result

    def _parse_master_block_sections(self, master_file, master_plist):
        """
        Parse one master plist block and return direct RefPList checks.

        :return: tuple(found_master, direct_ref_names, lines_after_0, lines_after_1, refs_0, refs_1)
        """
        refplist_map = self.refplist_map
        plist_dep_map = self.plist_dep_map

        refs = list(refplist_map.get(master_plist, []))
        refs_0 = [x for x in refs if str(x).endswith(self.REF_SUFFIX_0)]
        refs_1 = [x for x in refs if str(x).endswith(self.REF_SUFFIX_1)]

        plist_name = basename(master_file)
        found_master = (master_plist in refplist_map) and (plist_name in plist_dep_map)
        return found_master, refs, [], [], refs_0, refs_1

    def _get_preexec_refplist_names(self, master_file, master_plist):
        """Return PreExecRefPList names from tpobj.plists parsed structures for a master plist."""
        self.tpobj.plists.get_refplist()

        plb2n = getattr(self.tpobj.plists, '_plb2n', {}) or {}
        plbattr = getattr(self.tpobj.plists, '_plbattr', {}) or {}

        node_id = plb2n.get(master_plist)
        if node_id is None:
            return set()

        attrs = plbattr.get(node_id, {}) or {}
        preexec_ref = attrs.get('PreExecRefPList')
        if preexec_ref is not None:
            if isinstance(preexec_ref, (list, tuple, set)):
                return {str(item) for item in preexec_ref if str(item)}
            return {str(preexec_ref)}

        preexec_refs = set()
        try:
            lines = File(master_file).read().splitlines()
            block_start_re = re.compile(self.PLIST_DECL_RE_TEMPLATE.format(name=re.escape(master_plist)), re.IGNORECASE)

            in_block = False
            brace_depth = 0
            for line in lines:
                if not in_block:
                    if not block_start_re.search(line):
                        continue
                    in_block = True

                for match in self.PREEXEC_REF_RE.finditer(line):
                    ref_name = match.group(1)
                    preexec_refs.add(ref_name)

                brace_depth += line.count('{')
                brace_depth -= line.count('}')
                if in_block and brace_depth <= 0:
                    break
        except Exception:
            return set()

        return preexec_refs

    @staticmethod
    def _normalize_refpair_key(refname):
        """Return normalized key for __0/__1 order comparison."""
        name = str(refname)
        name = re.sub(r'__(0|1)$', '', name)
        name = re.sub(r'_(short|long)$', '', name, flags=re.IGNORECASE)
        return name

    @staticmethod
    def _is_allowed_nonpair_ref(refname):
        """Return True for allowed non __0/__1 RefPList names."""
        ref_text = str(refname).strip()
        ref_lower = ref_text.lower()

        if ref_lower.startswith('pat '):
            return HermesPlistChk._is_allowed_master_pat_line(ref_text)

        if ref_lower.startswith('refplist '):
            ref_lower = ref_lower[len('refplist '):].strip()

        return 'dts' in ref_lower or any(token in ref_lower for token in HermesPlistChk.NONPAIR_ALLOWED_TOKENS)

    @staticmethod
    def _is_allowed_master_pat_line(line):
        """Return True for allowed inline Pat lines in master plist block."""
        stripped = str(line).strip()
        stripped_lower = stripped.lower()
        return stripped.startswith('Pat ') and any(
            token in stripped_lower for token in HermesPlistChk.NONPAIR_ALLOWED_TOKENS
        )

    @staticmethod
    def _is_362_363_exempt_by_testname(testname):
        """Return True when test name qualifies for 372/373 exemption."""
        test_upper = str(testname).upper()
        return 'FFSEARCH' in test_upper or '_RAW' in test_upper

    @classmethod
    def _extract_speedflow_fn(cls, testname):
        """Return speedflow Fn number string from test name, else None."""
        match = cls.SPEEDFLOW_FN_RE.search(str(testname))
        if not match:
            return None
        return match.group(1)

    @classmethod
    def _extract_speedflow_token(cls, testname):
        """Return full speedflow token (for example F2XCR) from test name, else None."""
        match = cls.SPEEDFLOW_TOKEN_RE.search(str(testname))
        if not match:
            return None
        return match.group(1).upper()

    @staticmethod
    def _get_speedflow_match_tokens(speedflow_token):
        """Return token variants for plist-name matching (full token and optional -2 suffix form)."""
        token = str(speedflow_token).upper()
        variants = [token]
        if len(token) > len('F1X') + 2:
            variants.append(token[:-2])
        return variants

    @staticmethod
    def _get_speedflow_display_token(speedflow_tokens):
        """Return token text used in error messages for matching context."""
        tokens = list(speedflow_tokens)
        if not tokens:
            return ''
        return tokens[-1]

    @staticmethod
    def _plist_name_has_fn(plist_name, speedflow_tokens):
        """Return True when plist name contains any matching speedflow token variant."""
        plist_text = str(plist_name)
        for token in speedflow_tokens:
            token_text = str(token).lower()
            pattern = re.compile(rf'(^|[^a-z0-9]){re.escape(token_text)}(?![a-z0-9])', re.IGNORECASE)
            if pattern.search(plist_text):
                return True
        return False

    def _parse_plist_block_pat_lines(self, plist_name):
        """Return (found, ordered Pat statements) for a given plist block name."""
        try:
            return True, self.tpobj.plists.get_pats_from_plb(plist_name, order=True)
        except Exception:
            return False, []

    def main(self):
        """
        Validate Hermes plist naming and structure rules for speedflow/non-speedflow tests.

        Flow summary:
        -> Speedflow tests require `_master` patlists (with explicit template/testname exemptions for 372/373).
        -> `_master` block must have valid RefPList structure with expected `__0` and `__1` pairing (QGate374).
        -> Known nonpair helper entries are exempted by tokenized naming rules (dts/acm/midcat/init/reset/preburst).
        -> For QGate375, speedflow-token consistency between test name and plist names is checked first.
        -> Order/content consistency checks for `__0` and `__1` are also applied and reported independently.
        -> Non-speedflow tests must not use `_master` patlists unless exempted.

        """
        flow_rows = list(self.tpobj.mtpl.iter_flows('MAIN', bypass=True, edict=True, pdict=True))

        target_mods = set()
        for mod, test, data, _ in flow_rows:
            patlist = data.get('patlist')
            if not patlist:
                continue

            if not self._is_speedflow_test(test):
                continue

            if not self._is_master_patlist(patlist):
                continue

            template = self._get_first_present(data, ('TEMPLATE', 'Template', 'template'))
            clean_template = str(template).strip() if template is not None else None
            if clean_template == self.TEMPLATE_APEX:
                continue

            target_mods.add(mod)

        modinfo_map = self._build_modinfo(target_mods=target_mods)
        plb_map = self.tpobj.plists.get_plb_map()
        self.refplist_map = self.tpobj.plists.get_refplist()
        self.plist_dep_map = self.tpobj.plists.get_plist_dependent()
        checked_master = set()

        for mod, test, data, _ in flow_rows:
            patlist = data.get('patlist')
            if not patlist:
                continue

            template = self._get_first_present(data, ('TEMPLATE', 'Template', 'template'))
            clean_template = str(template).strip() if template is not None else None
            is_master_patlist = self._is_master_patlist(patlist)
            is_speedflow_test = self._is_speedflow_test(test)

            is_apex_template = clean_template == self.TEMPLATE_APEX

            if is_apex_template:
                if is_master_patlist:
                    self.add_error(373, mod,
                                   f'{test} uses TEMPLATE "{self.TEMPLATE_APEX}" and Patlist "{patlist}" must not end with _master')
                else:
                    self.add_pass(372, mod)
                continue

            if is_speedflow_test:
                is_template_ok = clean_template in self.ALLOWED_SPEEDFLOW_TEMPLATES
                if is_template_ok:
                    self.add_pass(377, mod)
                else:
                    self.add_error(377, mod,
                                   f'{test} matches speedflow regex and must use TEMPLATE in '
                                   f'{sorted(self.ALLOWED_SPEEDFLOW_TEMPLATES)}, but found "{template}"')

                if is_master_patlist:
                    self.add_pass(372, mod)
                else:
                    is_362_template_exempt = clean_template in self.SPEEDFLOW_362_SKIP_TEMPLATES
                    is_362_testname_exempt = self._is_362_363_exempt_by_testname(test)
                    if is_362_template_exempt or is_362_testname_exempt:
                        self.add_pass(372, mod)
                    else:
                        self.add_error(372, mod,
                                       f'{test} matches speedflow regex but Patlist "{patlist}" does not end with _master')

                if not is_master_patlist:
                    continue

                master_plist = str(patlist).strip().split('::')[-1]
                master_key = (mod, master_plist)
                if master_key in checked_master:
                    continue
                checked_master.add(master_key)

                modinfo = modinfo_map.get(mod)
                is_modinfo_ok = bool(modinfo)
                if is_modinfo_ok:
                    self.add_pass(376, mod)
                else:
                    self.add_error(376, mod,
                                   f'{test} cannot validate {master_plist}: module.mconfig IP/PORRoot info not found')
                if not is_modinfo_ok:
                    continue

                master_file = self._find_master_in_plists(master_plist, modinfo, plb_map)
                is_master_file_ok = bool(master_file)
                if is_master_file_ok:
                    self.add_pass(376, mod)
                else:
                    self.add_error(376, mod,
                                   f'{test} cannot find {master_plist} in {modinfo["plb_path"]} for PLIST_ALL_{modinfo["ipname"]}.plist.xml')
                if not is_master_file_ok:
                    continue

                found_master, refs, lines_0, lines_1, refs_0, refs_1 = self._parse_master_block_sections(master_file,
                                                                                                         master_plist)
                if found_master:
                    self.add_pass(376, mod)
                else:
                    self.add_error(376, mod,
                                   f'{test} cannot parse master plist block {master_plist} in {master_file}')
                if not found_master:
                    continue

                candidate_invalid_refs = [
                    x for x in refs
                    if not (x.endswith(self.REF_SUFFIX_0) or x.endswith(self.REF_SUFFIX_1)
                            or self._is_allowed_nonpair_ref(x))
                ]
                if candidate_invalid_refs:
                    preexec_refs = self._get_preexec_refplist_names(master_file, master_plist)
                    invalid_refs = [x for x in candidate_invalid_refs if x not in preexec_refs]
                else:
                    invalid_refs = []
                has_0 = any(x.endswith(self.REF_SUFFIX_0) for x in refs)
                has_1 = any(x.endswith(self.REF_SUFFIX_1) for x in refs)

                if not invalid_refs:
                    self.add_pass(374, mod)
                else:
                    self.add_error(374, mod,
                                   f'{master_plist} has non __0/__1 RefPList under _master: {invalid_refs}; '
                                   f'master found in {master_file}')
                if has_0 and has_1:
                    self.add_pass(374, mod)
                else:
                    self.add_error(374, mod,
                                   f'{master_plist} under _master must include both RefPList __0 and __1; '
                                   f'master found in {master_file}')

                if has_0 and has_1:
                    has_365_error = False
                    speedflow_token = self._extract_speedflow_token(test)
                    if speedflow_token is None:     # pragma: no cover
                        self.add_error(
                            375,
                            mod,
                            f'{master_plist} cannot extract speedflow token from test name {test}; '
                            f'master found in {master_file}'
                        )
                        continue

                    speedflow_tokens = self._get_speedflow_match_tokens(speedflow_token)
                    speedflow_display_token = self._get_speedflow_display_token(speedflow_tokens)

                    fn_mismatch = [
                        plist_name for plist_name in [master_plist] + refs_0 + refs_1
                        if not self._plist_name_has_fn(plist_name, speedflow_tokens)
                    ]
                    if fn_mismatch:
                        self.add_error(
                            375,
                            mod,
                            f'{test} with {master_plist} plist names must match test token={speedflow_display_token}; '
                            f'non-matching plist(s): {fn_mismatch}; master found in {master_file}'
                        )
                        has_365_error = True

                    refs_0_norm = [self._normalize_refpair_key(x) for x in refs_0]
                    refs_1_norm = [self._normalize_refpair_key(x) for x in refs_1]
                    is_ref_order_ok = refs_0_norm == refs_1_norm
                    is_inline_ok = lines_0 == lines_1

                    if not (is_inline_ok and is_ref_order_ok):
                        has_365_error = True
                        self.add_error(375, mod,
                                       f'{master_plist} RefPList __0 and __1 contents/order mismatch '
                                       f'(inline or RefPList sequence); '
                                       f'master found in {master_file}')
                    else:
                        if has_365_error:
                            continue
                        if self.DISABLE_DEEP_PAT_365:
                            self.add_pass(375, mod)
                            continue

                        pat_pair_mismatch = None
                        for idx, ref0 in enumerate(refs_0):
                            ref1 = refs_1[idx]
                            found_0, pats_0 = self._parse_plist_block_pat_lines(ref0)
                            found_1, pats_1 = self._parse_plist_block_pat_lines(ref1)

                            if not found_0 or not found_1:
                                pat_pair_mismatch = (
                                    f'{master_plist} cannot locate referenced RefPList block(s) '
                                    f'{ref0} / {ref1} in {master_file}'
                                )
                                break

                            if pats_0 != pats_1:
                                pat_pair_mismatch = (
                                    f'{master_plist} Pat contents/order mismatch between '
                                    f'{ref0} and {ref1}; master found in {master_file}'
                                )
                                break

                        if pat_pair_mismatch:
                            self.add_error(375, mod, pat_pair_mismatch)
                        else:
                            self.add_pass(375, mod)
            else:
                is_363_template_exempt = clean_template in self.NONSPEEDFLOW_363_SKIP_TEMPLATES
                is_363_testname_exempt = self._is_362_363_exempt_by_testname(test)
                if is_363_template_exempt or is_363_testname_exempt:
                    continue

                if not is_master_patlist:
                    self.add_pass(373, mod)
                else:
                    self.add_error(373, mod,
                                   f'{test} does not match speedflow regex but Patlist "{patlist}" ends with _master')


if __name__ == '__main__':  # pragma: no cover
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    HermesPlistChk(TestProgram(sys.argv[1]).pickle_init()).run()
