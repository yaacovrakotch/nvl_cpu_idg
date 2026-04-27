#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Purpose of QGATE Check:
Ensures that all bypassing at COLD and PHM should be handled by FSM and not via TOSRules or pgm_rules
Since it's for prods with full PRIME, so no pgm_rules check
"""

import sys
import setenv
import re
import ast
from gadget.pylog import log
from qgates.qgate_base import QGateBase
from tp.testprogram import TestProgram
from tp.mtpl import ExprParser


class BypassRulesChk(QGateBase):
    def __init__(self, tpobj):
        super().__init__(tpobj)
        self.all_rules_in_usrv = {}     # TosRules
        self.bypassport_in_mtpl = {}     # Bypassports which involve TosRules
        self.mapping_results = {}     # raw mapping of values in bypassports and TosRules
        self.loc_sets_d2l = {}
        self.final_mapping = {}     # only includes rules need to check, subset of mapping_results
        self.isdefault = {}  # indicates if the rule has a default condition

    @staticmethod
    def _split_args(arg_str: str):
        """Split a function‐style argument list while respecting nesting."""
        args, buf, depth = [], '', 0
        for ch in arg_str:
            if ch == "," and depth == 0:
                args.append(buf.strip())
                buf = ''
            else:
                buf += ch
                depth += (ch == "(") - (ch == ")")
        if buf:
            args.append(buf.strip())
        return args

    @staticmethod
    def _is_rule_call(s: str) -> bool:
        return "(" in s and ")" in s and "." in s

    @staticmethod
    def _safe_eval(s: str):
        """Return a literal value if possible, otherwise the original string."""
        try:
            return ast.literal_eval(s)
        except Exception:
            return s

    @classmethod
    def _raw_mapping(cls, rule_call: str, rule_dict: dict):
        name, arg_str = re.match(r"([^ (]+?)\s*\((.*)\)", rule_call.strip()).groups()
        mapping = {}
        isdefault = {}
        for cond, arg in zip(rule_dict[name], cls._split_args(arg_str)):
            arg = arg.strip()
            if cls._is_rule_call(arg):
                mapping.update(cls._raw_mapping(arg, rule_dict))
            else:
                mapping[cond] = cls._safe_eval(arg)
        return mapping

    def _extract_bypass_ports(self):
        self.bypassport_in_mtpl = {
            f"{md}:{tn}": re.sub(r"\b\w+::", '', data["BypassPort"])
            for md, tn, data, _ in self.tpobj.mtpl.iter_tests()
            if "BypassPort" in data and "(" in data["BypassPort"]
            and "." in data["BypassPort"].split("(")[0]
        }

        if not self.bypassport_in_mtpl:
            self.add_pass(262, "base")
            log.info("No TosRule in BypassPort to check")
            return False

        self.all_rules_in_usrv = {
            n: [ExprParser.to_py(e).strip() for e in expr]
            for grp in self.tpobj.usrv._src_orig.values()
            for n, expr in grp.items()
        }

        self.mapping_results = {
            tn: self._raw_mapping(expr, self.all_rules_in_usrv)
            for tn, expr in self.bypassport_in_mtpl.items()
        }

        self.isdefault = {
            tn: (
                1
                if '""' in self.all_rules_in_usrv.get(
                    re.match(r"([^ (]+?)\s*\((.*)\)", expr.strip()).group(1), []
                )
                else 0
            )
            for tn, expr in self.bypassport_in_mtpl.items()
        }

        return True

    def _extract_zq_locn(self):
        extracted = {}
        for tn, expr_map in self.mapping_results.items():
            res = {}
            for expr, val in expr_map.items():
                if not isinstance(val, int):
                    continue
                if expr == '""':
                    if val > 0:
                        res['""'] = val
                    continue
                for m in re.findall(r"contains\s*\(\s*LocationSets_ZQ_([A-Z0-9_]+)", expr, re.I):
                    res[m] = val
            if res and not (len(res) == 1 and '""' in res):
                extracted[tn] = res
        return extracted

    def _final_map_with_locsets(self):
        DD = self.tpobj.usrv.get_usrv_map()
        self.loc_sets_d2l = {
            k.split(".")[-1]: set(filter(None, v.replace("[", "").replace("]", "").split(",")))
            for k, v in DD.items() if "LocationSets." in k
        }
        all_loc = self.loc_sets_d2l.get("ALL_CLASS", set())
        for tn, expr_map in self._extract_zq_locn().items():
            pairs, nondefault = {}, set()
            for k, v in expr_map.items():
                if k == '""':
                    continue
                locs = self.loc_sets_d2l.get(k, set())
                nondefault |= locs
                pairs[",".join(sorted(locs))] = v
            if '""' in expr_map:
                pairs[",".join(sorted(all_loc - nondefault))] = expr_map['""']

            self.final_mapping[tn] = pairs
            self.nondefault = nondefault

    def main(self):
        if not self._extract_bypass_ports():
            return
        self._final_map_with_locsets()

        cold_phm = (self.loc_sets_d2l.get("COLD", set()) | self.loc_sets_d2l.get("PHM", set()))
        chot = (self.loc_sets_d2l.get("CHOT", set()))
        for inst, pair_map in self.final_mapping.items():
            if self.isdefault[inst] == 0 and self.nondefault != self.loc_sets_d2l.get("ALL_CLASS", set()):
                self.add_pass(262, "base")     # if no default condition and LOCationSets.ALL_CLASS is not fully covered
                log.info(f"WARNING: {inst} lacks default condition")
            if any(({p.strip() for p in locs.split(",")}.issubset(chot) and val > 0)
               or (any(p in chot for p in {p.strip() for p in locs.split(",")}) and val > 0)
               for locs, val in pair_map.items()):     # if CHOT bypass, then no need to check bypass status in cold_phm
                self.add_pass(262, "base")
                continue
            for locs, val in pair_map.items():
                locs_set = {p.strip() for p in locs.split(",")}
                if locs_set.issubset(cold_phm) and val > 0:
                    self.add_error(262, "base", f'{inst}: bypasses PHM/COLD in TosRule, need change to FSM')
                else:
                    self.add_pass(262, "base")


if __name__ == "__main__":
    assert len(sys.argv) == 2, 'Usage Error!\n\nPls specify .env file as first args'
    BypassRulesChk(TestProgram(sys.argv[1]).pickle_init()).run()
