#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
tiddb module
"""
from gadget.tputil import tid_from_pat, testname_from_pat
from gadget.gizmo import Elapsed
from collections import defaultdict
from tp.testprogram import TestProgram     # used for :type
from gadget.errors import ErrorInput
import re


class TidDb:
    """Creates the TidDb for a testprogram"""
    MOD = 0     # Module
    EKL = 1     # EDC/KILL
    COR = 2     # Corner (min, max, nom)
    FRQ = 3     # Freq based on name(F1, 0500, etc)
    TLT = 4     # Template name
    TI_ = 5     # Test instance name
    CNT = 6     # total elements. Code safety check
    HEADING = ('Module',
               'EDC_KILL',
               'VoltCorner',
               'Frequency',
               'Template',
               'TestInstance'
               )

    # Instance db fields
    INST = ('TEMPLATE',
            'patlist',
            'PLISTFILE',
            'level',
            'timings',
            '_BIN',
            'ifpm_modifygroups')

    def __init__(self, tpobj, istestname=False, init=True):
        """
        :param tpobj: TestProgram object
        :type tpobj: TestProgram
        :param istestname: use testname instead
        """
        self.tpobj = tpobj
        self.tids = defaultdict(set)     # {tid: set(<tuple, see above sequence>)}
        self.inst = {}                   # {(mod, tn): <tuple, see INST>}
        self.istestname = istestname

        if init:
            self._init()

    def _init(self):
        # Do initializations
        self.tpobj.check_init()      # it is required that TP is initted before this class is called
        self.tpobj.mtpl.set_tn_attrib()

        # Iterate to flows
        data = [x for x in range(self.CNT)]      # dummy initialization on empty list
        options = dict(passonly=False, bypass=True, keyparam='patlist', edict=True)
        for md, item, dd in self.tpobj.mtpl.iter_flows('MAIN', **options):
            pats = self.tpobj.plists.get_pats_from_plb(dd['patlist'], iserror=False)
            result_tidset = self.tpobj.plists.get_tid_from_pats(pats, self.istestname)

            # instance db
            data = []
            for fld in self.INST:
                if fld == 'PLISTFILE':
                    try:
                        set_plistfiles = self.tpobj.plists.plb_to_filename([dd['patlist']], fullpath=True)
                        data.append(set_plistfiles.pop())
                    except ErrorInput:
                        pass
                    continue      # pragma: no cover - coverage only
                data.append(dd.get(fld, ''))
            self.inst[(md, item)] = tuple(data)

            # tid db
            for tid in result_tidset:
                # assign the data tuple
                data = (md,
                        dd['_EDCKIL'],
                        dd['_CORNER'],
                        dd['_FREQ'],
                        dd['TEMPLATE'],
                        item)
                self.tids[tid].add(data)

        # check once
        assert len(data) == self.CNT, 'Fix TidDb() pls. Data structure is not correct: len(data)!=CNT'
        assert len(self.HEADING) == self.CNT, 'Fix TidDb(). HEADING is not right.'

    def summary_mod_tid(self):
        """Display the summary of mod_tid"""
        # {key: {0: set_of_tid_for_key,
        #        1: dict(MOD=mod, COR=cor, FRQ=freq, EKL=kill),
        #        2: set_of_tn_for_key}
        dctr = defaultdict(lambda: {0: set(), 1: {}, 2: set()})
        for tid in self.tids:
            for item in self.tids[tid]:
                key = ','.join([item[self.MOD], item[self.COR], item[self.FRQ], item[self.EKL]])
                dctr[key][0].add(tid)
                dctr[key][1] = {'MOD': item[self.MOD],
                                'COR': item[self.COR],
                                'FRQ': item[self.FRQ],
                                'EKL': item[self.EKL]}
                dctr[key][2].add(item[self.TI_])

        return dctr

    def dump(self, outfile, robj=re.compile(r"\w")):
        """Write the tid database to outfile"""
        alltid = set()
        with open(outfile, 'w') as fh:
            # tid first
            fh.write('TID,%s\n' % ','.join(self.HEADING))
            for tid in sorted(self.tids):
                for d in sorted(self.tids[tid]):
                    if robj.search(d[self.MOD]):
                        all_fields = ','.join([d[x] for x in range(self.CNT)])
                        fh.write(f'{tid},{all_fields}\n')
                        alltid.add(tid)

            # inst next
            fh.write('Module,Name,%s\n' % ','.join(self.INST))
            for md_tn in self.inst:
                if robj.search(md_tn[0]):
                    all_fields = ','.join(self.inst[md_tn])
                    fh.write(f'{md_tn[0]},{md_tn[1]},{all_fields}\n')

            # tid to pattern next
            all_pats = self.tpobj.plists.get_pats_all()
            dpat = {}
            for pat in all_pats:
                testname = testname_from_pat(pat)
                dpat[tid_from_pat(pat)] = (testname, pat)

            fh.write('TID,testname,pat\n')
            for tid in sorted(dpat):
                if tid in alltid:
                    item = dpat[tid]
                    fh.write(f'{tid},{item[0]},{item[1]}\n')

    def dumpfile(self, outfile, robj=re.compile(r"\w")):
        """Write the tid database to outfile"""
        alltid = set()
        fulllst = []
        instlist = []
        appStr = ""
        instStr = ""
        with open(outfile, 'w') as fh:
            # tid first
            sw = Elapsed()
            fh.write('TID,%s,Patlist,PlistFile\n' % ','.join(self.HEADING))
            for tid in sorted(self.tids):
                for d in sorted(self.tids[tid]):
                    if robj.search(d[self.MOD]):
                        all_fields = ','.join([d[x] for x in range(self.CNT)])
                        appStr = ','.join((tid, all_fields))
                        fulllst.append(appStr)
                        alltid.add(tid)
            # inst next
            instdict = {}
            for md_tn in self.inst:
                if robj.search(md_tn[0]):
                    all_fields = ','.join(self.inst[md_tn])
                    instStr = '%s, %s, %s' % (md_tn[0], md_tn[1], all_fields)
                    instdict[(md_tn[0], md_tn[1])] = instStr

            print(f"Done: {sw}, {len(fulllst)}")
            # i = 0573267_00,DRV_RESET_CXX,EDC,min,NONE,PrimeFunctionalTestMethod,RESET_X_SB_E_BEGCPU_X_INF_X_X_DFX_BABYSTEPS_STF_CTL_LPBK_100
            # j = TPI_SHOPS_XXX,SHOPS_X_FUNC_K_START_X_X_X_X_NEGATIVETESTM,iCFuncTest,mtlm_negative_ZBD_list,/intel/hdmxpats/mtl/MStpi/RevTCSxMA0.0/p0/plb/shopsm_class_allplist.plist,BASE::pkgm_shops_x_x_lower_pkg_lvl_strb_neg,BASE::pkgm_shops_hvm_timing_shops,,

            # join tid and inst with patlist
            for i in fulllst:
                x = i.split(',')
                key = (x[1], x[6])
                j = instdict[key]
                y = j.split(',')
                all_fields = ','.join((x[0], x[1], x[2], x[3], x[4], x[5], x[6], y[3], y[4]))
                fh.write(f'{all_fields}\n')

    def load(self, infile):
        """Read tid .csv file back into self.tids"""
        assert not self.tids, 'TidDb() is not empty. Cannot call load_tid()'
        with open(infile, 'r') as fh:
            section = 0
            for line in fh:
                tokens = line.strip().split(',')
                if tokens[0] == 'TID' and tokens[1] == 'Module':
                    section = 1
                elif tokens[0] == 'Module':
                    section = 2
                elif tokens[0] == 'TID' and tokens[1] == 'testname':
                    section = 3    # unused
                elif section == 1:
                    self.tids[tokens[0]].add(tuple(tokens[1:]))
                elif section == 2:
                    self.inst[(tokens[0], tokens[1])] = tuple(tokens[2:])

    def get_tid(self, tid) -> set:
        """Given tid, return set of items. Each item is tuple. Returns empty set if not found"""
        return self.tids.get(tid, set())

    def get_inst(self, mod, tn):
        """Given module and testname, return dictionary of fields"""
        key = (mod, tn)
        if key in self.inst:
            return {fld: self.inst[key][idx] for idx, fld in enumerate(self.INST)}
        return {}
