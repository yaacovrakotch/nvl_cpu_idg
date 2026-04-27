#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Query Tid

This module is dependent on pcar3 files on tvpvroot/pcar3 area
This module is readonly on tvpvroot/pcar3
Routines here are copied from MTL's pcar3.py and compas_query.py, then stripped down
"""
from gadget.pylog import log
from gadget.printmore import Dumper, PctIndicator
from gadget.gizmo import Elapsed, isany, get_caller_lno
from gadget.files import File, basename_delext
from gadget.shell import USERNAME
from gadget.errors import ErrorInput, ErrorUser, ErrorCockpit
from gadget.strmore import to_list, dict_to_args
from gadget.helperclass import OPT, IS_UT
from gadget.tputil import to_regex
from os.path import basename, join
from collections import defaultdict
from itertools import chain
from mod.setting import cfg
import re
import traceback
import pickle
import glob


class QBox:

    def __init__(self):
        """Initialize the singleton object"""
        self.root = cfg.pcar3_root
        self.expiry = 3600 * 24 * 365      # 1 year, aka, no expiry (since Qbox is readonly)
        self.file_location = None    # full path to pcar file, set during first obj register

        self.dict_vault = None       # cache dictionary of vault db - populated once in _run_vault, {<TID>: {field: value}}
        self.dict_linus = None       # cache dictionary of linus db - populated once in _run_linus, {<lineitem>: {field: value}}
        self.dict_finder_tid = None  # cache dictionary of finder db {tid: set_of_tups} - populated once in _read_finder
        self.dict_finder_tup = None  # cache dictionary of finder db {tup: {field: value}} - populated once in _read_finder
        self.orig_dict_vault = None  # original dict_vault vault. Set in common_vault
        self.vault_dict_csv = {}     # vault filters container: {<id>: {'filter_vault': [<filter>, <filter2>, etc]}}
        self.linus_dict_csv = {}     # linus filters container: {<id>: {'filter_linus': [<filter>, <filter2>, etc]}}
        self.finder_dict_csv = {}    # finder filters container: {<id>: {'filter_finder': [<filter>, <filter2>, etc]}}
        self.default_vault_field = {'attributes', 'directives', 'intent', 'module', 'owner', 'path',
                                    'plist_directives', 'product', 'purpose', 'run_args', 'status',
                                    'step', 'tag', 'test_id', 'testname', 'testtype'
                                    }
        self.default_linus_field = {'name', 'owner', 'producttag'}
        self.dict_objs = {}          # object registry: {"<id>": object}. <id> is "id#21"
        self.ctr_id = 0
        self.stlg = SuperTLG()       # Super test list gen

        # Preview objects
        self.preview = Preview()
        self.preview.outdir = self.root
        self.preview.age_cache = self.expiry
        self.preview.fastlookup = FastLookup()
        self.preview.prod = None    # Not known at init. Set at set_prod_step()
        self.preview.step = None

    def _register_obj(self, obj):
        """
        Register pcar3 objects into mother pcar3

        :param obj: any PlistFile, Plb, Pat, Query* objects
        :return: id string: "id#1"
        """
        self.ctr_id += 1
        id_str = "id#%d" % self.ctr_id
        self.dict_objs[id_str] = obj
        if self.file_location is None:
            self.file_location = Funcs.caller_info(filepath=True)
        return id_str

    def process(self, item=None):
        """Process all QueryTid objects"""
        if not self.dict_objs:
            return 1    # Nothing to process

        self.set_prod_step()     # Product and stepping is not known until processing time.
        self._run_linus_vault(item)
        self._run_finder(item)

    def _run_finder(self, item=None):
        """
        Execute finder and update the query objects
        Preview is smart enough to process only unique filters

        :param item: query_object - process only this specific one
        :return: resulting dictionary - unittest only
        """
        if not self.dict_finder_tup:
            self.dict_finder_tid, self.dict_finder_tup = self.preview.run_finder_pcar3()
            # Just in case we need to cache this, use Sqlite instead of pickle since it's faster. 3.377 Secs(sqlite) vs 3.723 Secs(pickle)

        if item is None:    # process all
            dict_csv = self.finder_dict_csv
        else:
            if item.id in self.finder_dict_csv:
                dict_csv = {item.id: self.finder_dict_csv[item.id]}
            else:
                return {}     # Nothing to process

        self.preview.expand_dict(dict_csv)

        result_finder = self.preview.filter_finder_pcar3(dict_csv, self.dict_finder_tup)
        ft = self.dict_finder_tup
        for str_id in result_finder:
            obj = self.dict_objs[str_id]

            if obj._is_tid:
                set_tid = {ft[tup]['tid'] for tup in result_finder[str_id]}
            else:
                set_tid = result_finder[str_id]

            if obj._tidlist is not None:
                set_tid &= set(obj._tidlist)      # AND operation with vault or linus
            obj.store(obj._sort(set_tid), new=True)
            log.info("-r- Query Finder(%s:%s): found %d %s: %s"
                     "" % (obj, obj.id, len(obj), "tid" if obj._is_tid else "tuple", Funcs.log_max(obj.result())))

        return result_finder

    def _run_linus_vault(self, item=None):
        """
        Execute linus and vault, then update the query objects
        Preview is smart enough to process only unique filters

        :param item: query_object - process only this specific one
        :return: resulting dictionary - unittest only
        """
        # intialize dictionaries
        if item is None:
            linus_dict_csv = self.linus_dict_csv
            vault_dict_csv = self.vault_dict_csv
        else:
            if item.id in self.linus_dict_csv:
                linus_dict_csv = {item.id: self.linus_dict_csv[item.id]}
            else:
                linus_dict_csv = {}
            if item.id in self.vault_dict_csv:
                vault_dict_csv = {item.id: self.vault_dict_csv[item.id]}
            else:
                vault_dict_csv = {}

        # execute vault
        self.preview.expand_dict(vault_dict_csv)
        if not self.dict_vault:
            vault_fields = self.default_vault_field - {'testname'}   # testname added in postprocessing
            self.dict_vault = self.preview.run_vault(vault_fields)

        result_vault = self.preview.filter_vault(vault_dict_csv, self.dict_vault, pcar3=True)

        self.preview.expand_dict(linus_dict_csv)

        # execute linus
        if self.dict_linus is None:
            self.dict_linus = {}
        result_linus, linus_info, dict_tstlg = self.stlg.execute_linus(linus_dict_csv, self.dict_linus)

        # save it in object
        for str_id in result_linus.keys() | result_vault.keys():
            obj = self.dict_objs[str_id]
            if str_id in result_linus:
                final = result_linus[str_id]    # initial result
                if str_id in result_vault:
                    final = final & result_vault[str_id]   # do intersection of vault and linus
            else:
                final = result_vault[str_id]    # pretty sure it is in vault if not found in linus

            obj.store(obj._sort(final), new=True)
            log.info("-r- QueryTid(%s:%s): found %d tid: %s" % (obj, obj.id, len(obj), Funcs.log_max(obj.result())))

            # display debug
            if obj.debugexpect:
                log.info("-d- start of DEBUGEXPECT: %s(%s)" % (obj.__class__.__name__, obj.id))

                # if linus data exist
                if dict_tstlg:
                    li_names = []
                    for ptag in dict_tstlg:
                        li_names.extend([name for name in sorted(dict_tstlg[ptag]) if obj.debugexpect in dict_tstlg[ptag][name]])
                    data = Dumper(li_names, p=False).string()
                    log.info("-d linus lineitems found for %s:\n%s" % (obj.debugexpect, data))
                    log.info("-d- linus filter:\n%s" % Dumper(linus_dict_csv.get(str_id, "N/A"), p=False).string())
                    li_name = ''
                    if str_id in linus_dict_csv:
                        for filtr in linus_dict_csv[str_id]['filter_linus']:
                            if filtr.startswith('name='):
                                li_name = filtr.split('=')[1]
                    if li_name:
                        data = Dumper(linus_info[str_id].get(li_name, "NOT_FOUND_IN_LINUS"), p=False).string()
                        log.info('-d- linus info for %s:\n%s' % (li_name, data))

                # vault data
                data = Dumper(self.dict_vault.get(obj.debugexpect, "NOT_FOUND_VAULT"), p=False).string()
                log.info("-d- vault info of %s:\n%s" % (obj.debugexpect, data))
                found = "FOUND" if obj.debugexpect in final else "NOT-FOUND"
                data = Dumper(vault_dict_csv.get(str_id, "N/A"), p=False).string()
                log.info("-d- vault filter below, result=%s:\n%s" % (found, data))
                log.info("-d- end of DEBUGEXPECT")

    def set_prod_step(self):
        """
        Get prod step and check the environment
        :return: tuple (prod, step)
        """
        if SetProdStep.get_prod() and SetProdStep.get_step():
            # success
            self.preview.prod = SetProdStep.get_prod()
            self.preview.step = SetProdStep.get_step()
            self.preview.outdir = self.root      # changed during unittests
            return

        # Display friendly message
        valid = []
        for ff in sorted(glob.glob(f'{self.root}/*.vault')):
            res = re.search(r"^(\w+)_(\w+)\.", basename(ff))
            assert res, f'Invalid pcar3 filename found. Cannot derive prod and step: [{ff}]'
            valid.append(f'prod={res.group(1)} step={res.group(2)}')
        raise ErrorUser("Product or Stepping is not Set. Pls set via SetProdStep(prod, stepping).",
                        "Valid product/step combinations: %s" % ', '.join(valid))


class SetProdStep:
    """Holder of product and stepping"""
    prod = [None]
    step = [None]

    def __init__(self, prod, step):
        # Make sure product and stepping is set once, since querytid can only do one prodstep at a time
        if self.prod[0] and (self.prod[0] != prod or self.step[0] != step):
            raise ErrorUser("prod=%s step=%s is already Set. Cannot set to a different value"
                            "" % (self.prod[0], self.step[0]),
                            "Pls execute tp_audit.py per die.")

        self.prod[0] = prod
        self.step[0] = step

    @classmethod
    def get_prod(cls):
        return cls.prod[0]

    @classmethod
    def get_step(cls):
        return cls.step[0]

    @classmethod
    def _clear(cls):
        assert IS_UT, "Cannot Execute clear(). clear() is only for unittest."
        cls.prod[0] = None
        cls.step[0] = None


class FastLookup:
    """
    Given a dictionary and many filters, return a set keys given the filters
    using very fast string processing (regex). See filter()
    """
    is_log_print = True     # This is set False in FastLookupPcar class

    def __init__(self):
        # below is used as field delimiter in large regex string. Assumed not used in linus and vault.
        # If character exist in linus/vault, then it is replaced with '@'
        # Using "%" is slower (554 secs) vs "~" (163 secs). Thus use "~".
        self.special_char = '~'
        self.faststr = {}

    def _gen_fast_string(self, dict_db, name_add=False, enum=[]):
        """
        :param dict_db: vault or linus or finder dictionary: {<key>: {<field>: <value>}}
        :param name_add: bool, if key will be added in the search string
        :param enum: list of enumerated fields
        :return: dictionary {<field>: <large_string>}

        Prepare a concatenated large string for use in re.findall() for very fast processing.

        Example: given:
        var = {111: {testtype=abc, tag=ghi}
               123: {testtype=def, tag=jkl}}
        Result is:
        res = {'testtype': '''
        ~111~abc~
        ~123~def~'''
               'tag': '''
        ~111~ghi~
        ~123~jkl~'''}

        This routine is 0.216 Secs, 4524684 bytes for 40557 vault records

        re.findall() performance: 1.138 sec for 1M entries. See findall_performance() in unittests.
        """
        lines = defaultdict(list)
        template = "{s}%s{s}%s{s}".format(s=self.special_char)
        for key in dict_db:
            # create a list of key=value, to be concatenated via join()
            dict_item = dict_db[key]
            for fld in dict_item:

                if fld in enum:
                    lines[fld].extend(template % (key, expr) for expr in dict_item[fld].split(','))
                else:
                    lines[fld].append(template % (key, dict_item[fld]))   # one item

            # for linus, add the name (key) as searchable
            if name_add:
                lines['name'].append(template % (key, key))

        # convert to string
        final = {item: '\n'.join(lines[item]) for item in lines}
        return final

    def filter(self, dict_csv, dict_db, filter_key, kyy, name_add=False, enum=[], lower=True, pcar3=False, refresh=False):
        """
        Get all keys for each group
        :param dict_csv: dictionary from input csv: {<group>: {<filter_key>: [<expr>]}}
        :param dict_db: This is the db dictionary: {<key>: {<field>: <value>}}
        :param filter_key: Which key to use in dict_csv
        :param kyy: regex string of key "(\\d+)" or "(\\w+)"
        :param name_add: bool, if key will be added in the search string
        :param enum: enumerated fields
        :param lower: bool, True for case-insensitive, False for case-sensitive
        :param pcar3: bool, True for pcar3:regex is as-is.
        :param refresh: bool, True to force regeneration of faststr filters (default False)
        :return: dictionary: {group: set_of_keys}
        """

        # Generate the large fast string
        sw = Elapsed()
        if refresh or filter_key not in self.faststr:
            self.faststr[filter_key] = self._gen_fast_string(dict_db, name_add=name_add, enum=enum)
        dstr = self.faststr[filter_key]

        # profile for 10K cache rows: 169 secs, 482 findall() calls at 0.351 per call.
        if self.is_log_print:
            log.info("-i- Running %s for %s groups, length_string=%s, genfast_str: %s"
                     "" % (filter_key, len(dict_csv), sum(len(dstr[x]) for x in dstr), sw(reset=True)))
        result = {}
        cache = defaultdict(dict)
        all_set = set(dict_db)
        regex_all = '.*'
        indicator = PctIndicator(len(dict_csv))
        for group in dict_csv:
            indicator.disp()

            filters = dict_csv[group].get(filter_key, None)
            if not filters:
                result[group] = all_set    # all
                continue

            final = None
            for filtr in filters:

                # find all keys that match the filter
                if pcar3:
                    filtr_cleaned = filtr.replace('!=', '=')
                else:
                    filtr_cleaned = filtr.replace('*', regex_all).replace('%', regex_all).replace('!=', '=')

                if lower:
                    filtr_cleaned = filtr_cleaned.lower()

                fld, value = filtr_cleaned.split('=', 1)
                expr = self.get_expr(kyy, value)

                if expr not in cache[fld]:
                    # print("expr: %r dstr:\n%s" % (expr, dstr[fld]))    # __DEBUG

                    # Below is the main technology to get fast filtering capability. When changing this be sure to re-benchmark performance.
                    cache[fld][expr] = {x if isinstance(x, str) else x[0] for x in re.findall(expr, dstr[fld])}
                found_keys = cache[fld][expr]

                # process the not
                if '!=' in filtr:
                    found_keys = all_set - found_keys

                # do a "and" operation on the found tids
                if final is None:
                    final = set(found_keys)   # make a copy
                else:
                    final &= found_keys    # intersection

            result[group] = final
            log.dev("%s: %s: %s" % (filter_key, group, Func.disp_set_debug(final)))

        if self.is_log_print:
            log.info("-i- %s, unique expr=%s, Elapsed %s" % (filter_key, sum(len(cache[x]) for x in cache), sw))
        return result

    def get_expr(self, key, value):
        """
        Return the regular expression to use on the large string
        Returns partial match - for use with pcar

        :param key: regular expression
        :param value: value regular expression
        :return: string regex
        """
        if value.endswith('$'):
            value = value[:-1]
            endkey = self.special_char
        else:
            endkey = r"\b"

        if value.startswith('^'):
            expr = r'{d}{key}{d}{value}{endkey}'.format(d=self.special_char, key=key, value=value[1:], endkey=endkey)
        else:
            expr = r'{d}{key}{d}.*\b{value}{endkey}'.format(d=self.special_char, key=key, value=value, endkey=endkey)

        return expr


class _TidQueryBase:
    """
    Base class for Tid related Queries
    Holds list of tid numbers, 7-char padded length

    Usage example:
    # intent=='feature_ring' and attributes=='hvm'
    QueryTid(intent='feature_ring', attributes='hvm')

    # intent=='feature_ring' or attributes=='hvm'
    OR(QueryTid(intent='feature_ring'), QueryTid(attributes='hvm'))

    # intent=='feature_ring' and (attributes=='hvm' or attributes='south')
    QueryTid(intent='feature_ring', attributes='(hvm|south)')

    # intent=='feature_ring' and (attributes=='hvm' and attributes='south')
    QueryTid(intent='feature_ring', attributes=('hvm', 'south'))
    QueryTid(intent='feature_ring', attributes='hvm south')   # pcar2 style

    # intent=='feature_ring' or (attributes=='hvm' and lineitem_name=='burnin')
    OR(QueryTid(intent='feature_ring'), AND(QueryTid(attributes='hvm'), QueryTid(linus_name=='burnin')))
    """
    _length = 7     # digit length of tid

    def __init__(self, input_str='BaseClass'):
        """Initialize: should be very slim since there are lots of these objects"""
        self._tidlist = None                   # list of tid string of length 7. Will be populated in .process()
        self._input_str = input_str
        self._caller_info = f'line {self._lno}'
        self._is_tid = True                    # True if this object contain tid, False if contain tuples
        self.id = qbox._register_obj(self)     # register it
        self.repeat = 1                        # default
        self.latesttestname = False            # default
        self.debugexpect = None                # default
        log.info("-i- %s(%s) on %s, is registered" % (self.__class__.__name__, self.id, self._caller_info))

    def __iter__(self):
        """Iterator: Return the stored tid(s)"""
        raise ErrorInput("%r is being accessed via iterator. This is not allowed." % self,
                         "To access the contents of the object, call .result(process=True) method.")

    def __repr__(self):
        """Return string representation of the class"""
        return '%s(%s)' % (self.__class__.__name__, self._input_str)

    def __str__(self):
        """Return args of the class"""
        return self._input_str

    def __bool__(self):
        """
        Boolean check of the class
        Will always return True.

        # Example usage:
        if something:
            obj = QueryTid()
        else:
            obj = None

        if obj:    # This should return True, even if qbox.process() is not called yet.
            # do something

        # Note: The correct way to know if obj has result is:
        qbox.process(obj)
        if len(obj):
            # code if obj has found TID(s)
        """
        return True    # always non-zero

    def __len__(self):
        """Return length of the data"""
        return len(self.result())

    def __hash__(self):
        """Value of dictionary key when object is stored as key"""
        return id(self)

    def result(self, process=False):
        """
        :return: list of tid(s)
        """
        # Explicit call to process for this object
        if process:
            qbox.process(self)

        self._check_processed()
        final = self._tidlist

        # latesttestname processing
        if self.latesttestname:
            latest = defaultdict(int)
            for item in self._tidlist:
                if item in qbox.dict_vault:
                    testname = qbox.dict_vault[item].get('testname', item)
                else:
                    testname = item
                latest[testname] = latest[testname] if int(latest[testname]) > int(item) else item
            valid_set = {latest[testname] for testname in latest}

            # preserve order
            final = [tid for tid in self._tidlist if tid in valid_set]

        if self.repeat == 1:
            return final
        else:
            # below will make [1, 2, 3] to [1, 1, 1, 2, 2, 2, 3, 3, 3] if repeat is 3.
            return list(chain(*([i] * self.repeat for i in final)))

    def store(self, tid_or_seq, new=False):
        """
        Store tid_or_seq in class in object.
        Guarantee 7 digit length (zero padded)

        :param tid_or_seq: str|int|list of tid
        :param new: Set to True if initialize list to empty
        :return: None
        """
        if new or self._tidlist is None:
            self._set_empty()

        if isinstance(tid_or_seq, (str, int)):
            self._tidlist.append(str(tid_or_seq).zfill(self._length))
        else:
            self._tidlist.extend(str(x).zfill(self._length) for x in tid_or_seq)

    def _gen_filter_list(self, filters):
        """
        Generate the filter list for Preview use
        Special handling on "not": intent='!core' is translated to intent!='core'

        :param filters: dictionary of {<field>: <query>}
                        <query> can be string or tuple|list.
                        On tuple|list, they are treated as AND conditions. See example on class docstring for usage.
        :return: list of '<field>=<query>' strings
        """
        result = []
        for field in sorted(filters):
            query = filters[field]

            for item1 in to_list(query):      # list of filters (ie. inherit)
                if field in qbox.preview.enum and isinstance(item1, str):
                    item1 = item1.replace(',', ' ')

                for item in Funcs.to_list_split(item1):     # convert space to list
                    if item.startswith('!'):
                        result.append("%s!=%s" % (field, item[1:]))
                    else:
                        result.append('%s=%s' % (field, item))

        return result

    def _set_empty(self):
        """
        Set the object empty since some error occurred

        :return: Nothing
        """
        self._tidlist = []

    def _check_type(self, obj):
        """
        Check the type of obj

        :param obj: input object, must be TidQueryBase
        :return: Nothing
        """
        if not isinstance(obj, _TidQueryBase):
            raise ErrorInput("%s() on %s: Input %r is of type %s. Expecting Query object."
                             "" % (self.__class__.__name__, self._caller_info, obj, type(obj)),
                             "Maybe use Tids(%r)" % obj)

    def _check_processed(self):
        """
        Check if this object is processed
        :return: None
        """
        if self._tidlist is None:
            raise ErrorInput("%s(%s) on %s is not yet processed." % (self.__class__.__name__, self, self._caller_info),
                             "Use .result(process=True) instead of .result() to get list of tid numbers. "
                             "For more info on usage, see FAQ on wiki at https://wiki.ith.intel.com/x/Y7mcTw")

    @staticmethod
    def _regex_convert(field):
        """
        Process regex string to work with intent or similar fields

        :param field: string regex
        :return: (isregex, isnot, rawregex)
        """
        # take care of NOT first
        if field.startswith('!'):
            isnot = True
            field = field[1:]
        else:
            isnot = False

        if isany('^$()[]*{}.\\', field):
            # it's a regex ==============
            end = r'\b'
            if field.endswith('$'):
                end = ''

            start = r'\b'
            if field.startswith('^'):
                start = ''
            return True, isnot, '%s%s%s' % (start, field, end)

        # not a regex
        return False, isnot, field

    @classmethod
    def _sort_item(cls, order, ordercmd, inc, ctr, dd):
        """
        Update order dict with correct sorting

        :param order: dictionary {tid: <order_number>}
        :param ordercmd: list of 'field=regex' (self.orderbottom or self.ordertop)
        :param inc: increment: 1 for ascending, -1 for descending
        :param ctr: starting number
        :param dd: dictionary {tid: {field: <value>}}
        :return: None
        """
        done = set()
        for item in ordercmd:
            start_ctr = ctr + 1     # starting counter
            field, value = item.split('=', 1)

            isregex, isnot, raw = _TidQueryBase._regex_convert(value)
            ordergrp = []
            if isregex:
                robj = re.compile(raw)

                # get the numeric order list (used with ordertop='testname=(\w+)'
                for idx in sorted(order, key=lambda x: order[x][1]):
                    tid = order[idx][0]
                    if tid in dd:
                        result = robj.search(dd[tid].get(field, ""))
                        if result:
                            for grp in result.groups():
                                ordergrp.append(grp)
                ordergrp = sorted(ordergrp)

            tdone = set()
            for idx in sorted(order, key=lambda x: order[x][1]):
                tid = order[idx][0]
                if tid in dd:
                    ctr += inc
                    ctr_to_use = ctr

                    # special handling
                    if item == 'rapttr=DECODE':
                        raise ErrorCockpit("rapttr=DECODE is not supported in plans")

                    elif isregex:
                        result = robj.search(dd[tid].get(field, ""))
                        if result:
                            for grp in result.groups():
                                if grp.isdigit():
                                    ctr_to_use = start_ctr + int(grp) * inc
                                else:
                                    idx_order = ordergrp.index(grp)
                                    ctr_to_use = start_ctr + idx_order * inc
                                    ordergrp[idx_order] = None   # clear this item
                                ctr = max(ctr, ctr_to_use)    # use max of two
                    else:
                        result = raw in dd[tid].get(field, "")

                    if (not isnot and result) or (isnot and not result):
                        if tid not in done:    # assign only those which have not matched yet. aka, assign order only once
                            # print "ORDERING:", tid, ctr, ctr_to_use, raw
                            order[idx][1] = ctr_to_use
                            tdone.add(tid)
            done.update(tdone)

    def _sort(self, seq):
        """
        Sort the input list of tid depending on ordertop or orderbottom
        For Advanced sorting, this method can be overridden

        :param seq: list of tid
        :return: Sorted list of tid
        """
        if (not self.orderbottom) and (not self.ordertop):
            return sorted(seq)     # default, sort according to tid number

        # setup initial order: {tid: numerical_order}
        order = {idx: [tid, idx + 1000000] for idx, tid in enumerate(sorted(seq))}   # keep the order

        dv = qbox.dict_vault

        # ascending first
        _TidQueryBase._sort_item(order, self.ordertop, 1, 0, dv)

        # descending next (This takes higher priority)
        _TidQueryBase._sort_item(order, self.orderbottom, -1, 2000000, dv)

        result = sorted(order, key=lambda x: order[x][1])    # final order
        return [order[x][0] for x in result]
        # performance: 0.182 sec for 40944 tids, 0.099 for non-regex
        # performance: 0.018 sec for 4042 tids


class QueryTid(_TidQueryBase):
    """
    Given vault/linus/finder query, get the tid(s)
    linus queries are "linus_<field>"
    finder queries are "finder_<field>"
    """
    common = {}     # common queries

    # Below are fields which are used in linus, vault and finder filters
    set_fields = set('attributes directives intent module owner path plist_directives product '
                     'purpose run_args status step tag test_id testname testtype '
                     'linus_name linus_owner linus_producttag '
                     'finder_tag finder_testname finder_regex'.split())

    def __init__(self,
                 inherit=None,          # inherit must be first one
                 dummyarg=None,         # Check only, if user accidentally use positional args
                 attributes=None,
                 directives=None,
                 intent=None,
                 module=None,
                 owner=None,
                 path=None,
                 plist_directives=None,
                 product=None,
                 purpose=None,
                 run_args=None,
                 status=None,
                 step=None,
                 tag=None,
                 test_id=None,
                 testname=None,          # derived from vault path and directives TEST_NAME
                 testtype=None,
                 linus_name=None,        # query linus lineitem name
                 linus_owner=None,       # query linus owner
                 linus_producttag=None,  # query linus producttag
                 finder_tag=None,        # query finder tag
                 finder_testname=None,   # query finder testname
                 finder_regex=None,      # query finder using any regex on tracename
                 # non-field-name keywords below
                 add_trctag_linus_name=None,   # True by default
                 repeat=1,                     # repeat each TID this number of times
                 ordertop=None,                # ordered list -> put on top
                 orderbottom=None,             # ordered list -> put on bottom
                 latesttestname=None,          # return tid with latest testname only
                 debugexpect=None,             # Display debug info given this tid number
                 _utlno=None,
                 **kwargs,
                 ):
        """
        Query vault, linus (linus_*) or finder (finder_*)
        """
        var = locals()
        self._lno = _utlno if _utlno else get_caller_lno()     # caller line number, also used as id
        dict_filters = {x: Funcs.check_regex_list(x, var[x]) for x in var if x in self.set_fields and var[x] is not None}
        super().__init__(dict_to_args(dict_filters))
        Funcs.check_pos_args(None, dummyarg, self.__class__.__name__, self._caller_info,
                             suggestion="See QueryTid() usage. positional args is not used")
        self._check_filters(dict_filters, inherit)
        self._set_vault_linus_filters(dict_filters)
        self._set_finder_filters(dict_filters)
        self._dict_filters = dict_filters       # used in inheritance
        self.add_trctag_linus_name = Funcs.check_bool('add_trctag_linus_name', add_trctag_linus_name)
        self.repeat = Funcs.check_int('repeat', repeat)
        self.ordertop = QueryTid._check_order('ordertop', ordertop, self.__class__.__name__, self._caller_info, qbox.default_vault_field)
        self.orderbottom = QueryTid._check_order('orderbottom', orderbottom, self.__class__.__name__, self._caller_info, qbox.default_vault_field)
        self.latesttestname = Funcs.check_bool('latesttestname', latesttestname)
        self.debugexpect = Funcs.check_string('debugexpect', debugexpect)
        self.debugexpect = self.debugexpect.zfill(7) if self.debugexpect else None
        self._get_grp = {}                      # for get_groups()

        # check invalid args
        msg = ('Invalid args [%s]. See valid args in: https://wiki.ith.intel.com/x/qvfxRw'
               '' % ','.join(kwargs))
        assert not kwargs, msg

        self._process_common()

        # default True
        self.add_trctag_linus_name = True if self.add_trctag_linus_name is None else self.add_trctag_linus_name

        # other attributes
        self._linus_name = self._dict_filters.get('linus_name', None) if self.add_trctag_linus_name else None   # used in Pats() object to add finder tag LI_ in trctag

    @classmethod
    def set_common(cls,
                   dummyarg=None,         # Check only, if user accidentally use positional args
                   attributes=None,
                   directives=None,
                   intent=None,
                   module=None,
                   owner=None,
                   path=None,
                   plist_directives=None,
                   product=None,
                   purpose=None,
                   run_args=None,
                   status=None,
                   step=None,
                   tag=None,
                   test_id=None,
                   testname=None,          # derived from vault path and directives TEST_NAME
                   testtype=None,
                   linus_name=None,        # query linus lineitem name
                   linus_owner=None,       # query linus owner
                   linus_producttag=None,  # query linus producttag
                   finder_tag=None,        # query finder tag
                   finder_testname=None,   # query finder testname
                   finder_regex=None,      # query finder using any regex on tracename
                   # non-field-name keywords below
                   add_trctag_linus_name=None,
                   ordertop=None,                # ordered list -> put on top
                   orderbottom=None,             # ordered list -> put on bottom
                   latesttestname=None,          # return tid with latest testname only
                   debugexpect=None,             # Display debug info given this tid number
                   ):
        """
        Set common QueryTid() attributes

        Strategy:
        1. Use _set_common_vault() for vault fields. This has performance improvement since it reduces vault
           records
        2. Use *inherit* feature of QueryTid() for non-vault fields
        3. Use cls.common dictionary for non-field-name keywords

        :return: Nothing
        """
        # Below will get all the function arguments in to args dictionary
        var = locals()
        args = {x: var[x] for x in var if var[x] is not None and x not in ('cls', 'var')}

        # make sure it is called once and no other QueryTid() are registered
        caller_info = Funcs.caller_info()
        Funcs.check_pos_args(None, dummyarg, cls.__name__, caller_info,
                             suggestion="Use keyword arguments in set_common()")

        if cls.common:
            raise ErrorInput("QueryTid.set_common() on %s: Cannot call set_common() more than once." % caller_info,
                             "Call set_common() once at top of pcar3 file.")

        for item in qbox.dict_objs:
            if isinstance(qbox.dict_objs[item], QueryTid):
                raise ErrorInput("QueryTid.set_common() on %s: Error: at least one QueryTid() object is registered "
                                 "before set_common() is called." % caller_info,
                                 "Call QueryTid.set_common() once at top of pcar3 file before any "
                                 "QueryTid() call")

        arg_vault = {}
        arg_nonvault = {}
        arg_misc = {}
        for item, value in args.items():
            if item in qbox.default_vault_field:
                arg_vault[item] = value
            elif item in cls.set_fields:
                arg_nonvault[item] = value
            else:
                arg_misc[item] = value

        if arg_vault:
            cls._set_common_vault(**arg_vault)
        if arg_nonvault or arg_misc:
            if arg_nonvault:
                q_args = arg_nonvault
            else:
                q_args = {'tag': '!_notexist_'}    # filter cannot be empty
            q_args.update(arg_misc)

            cls.common['_obj'] = QueryTid(**q_args)

        cls.common.update(arg_misc)
        cls.common['_once'] = True

    def _check_filters(self, dict_filters, input_inherit):
        """
        Check input filters and update dict_filters on inheritance

        :param dict_filters: input filters
        :param input_inherit: QueryTid object to get info from
        """
        inherit = list(to_list(input_inherit))
        if '_obj' in self.common:
            inherit.append(self.common['_obj'])

        for iobj in inherit:
            if iobj is None:    # this is the normal case of no inheritance
                continue

            if isinstance(iobj, (int, str)):
                raise ErrorInput('%s() from %s, has args of %r. This is unexpected.'
                                 '' % (self.__class__.__name__, self._caller_info, iobj),
                                 'Use Tids(%r) instead of QueryTid() for hardcoded TID numbers.' % inherit)

            if not isinstance(iobj, QueryTid):
                raise ErrorInput('%s() from %s, has inherit=%s'
                                 '' % (self.__class__.__name__, self._caller_info, type(iobj)),
                                 'Expecting QueryTid object.')

            # update dict_filters based on inherit(ance)
            ref = iobj._dict_filters
            for item in ref:
                if item in dict_filters:
                    # append the ref item. Need to convert to list since dict_filters[item] can be tuple or list
                    dict_filters[item] = list(to_list(ref[item])) + list(to_list(dict_filters[item]))
                else:
                    # use ref as-is
                    dict_filters[item] = ref[item]

        # empty is not allowed
        if not dict_filters:
            raise ErrorInput('%s(%s) from %s has empty filter. This is not allowed.'
                             '' % (self.__class__.__name__, self, self._caller_info),
                             'At least one filter is required')

        if 'finder_regex' in dict_filters:
            Funcs.check_regex_str('finder_regex', dict_filters['finder_regex'])

        # These cannot be together
        if 'finder_testname' in dict_filters and 'finder_regex' in dict_filters:
            raise ErrorInput("%s(%s) at %s is invalid. Cannot use finder_testname and finder_regex at the same time."
                             "" % (self.__class__.__name__, self, self._caller_info),
                             "Either use testname or regex, cannot be both")

        # check for | without parenthesis
        for item, value in dict_filters.items():
            if '|' in value and '(' not in value:
                raise ErrorInput("%s(%s) at %s, is invalid for %s=%r"
                                 "" % (self.__class__.__name__, self, self._caller_info, item, value),
                                 "use %s='(%s)', that is, embrace in parenthesis the OR regex."
                                 "" % (item, value))

    @staticmethod
    def _check_order(field, value, cname, caller_info, valid, ratio_check=False):
        """
        Check validity of order

        :param field: fieldname
        :param value: string 'field=value' or list of string
        :param cname: class name
        :param caller_info: callerinfo
        :param valid: valid fields
        :return: list
        """
        if value is None:
            return []

        result = []
        for item in to_list(value):

            if cname == 'QueryTid':
                item = item.lower()    # because vault and linus are case lowered

            res = re.search(r"^(\w+)=(.+)$", item)
            if not res:
                raise ErrorInput("%s() from %s, has %s=%r. Incorrect format."
                                 "" % (cname, caller_info, field, value),
                                 "Expected format: %s='<field>=<value>' or %s=['<field>=<value>']"
                                 "" % (field, field))

            vfield = res.group(1)
            if vfield not in valid:
                raise ErrorInput("%s() from %s, has %s=%r. Field %r is invalid field."
                                 "" % (cname, caller_info, field, value, vfield),
                                 "Valid fields: %s" % ', '.join(valid))

            sfield = res.group(2).split()
            Funcs.check_regex_list(vfield, sfield, quotes=False)    # Make sure it's valid regex
            if len(sfield) == 1:
                result.append(item)
            else:
                for expr in sfield:
                    result.append('%s=%s' % (vfield, expr))

            if ratio_check and (not res.group(2).isalnum()):
                raise ErrorInput("%s() from %s, has %s=%r. Value [%s] is invalid"
                                 "" % (cname, caller_info, field, value, res.group(2)),
                                 "Expecting value to be alpha numeric")

        return result

    def _set_vault_linus_filters(self, dict_filters):
        """
        Set vault and linus dict_csv

        :param dict_filters: input filter dictionary
        """
        # Populate vault_filters and linus_filters
        vault_filters = {}
        linus_filters = {}
        for filter_ in dict_filters:
            if filter_.startswith('linus_'):
                linus_filter = filter_.replace('linus_', '')
                linus_filters[linus_filter] = dict_filters[filter_]
                assert linus_filter in qbox.default_linus_field, "CODE ERROR! Add %r in pcar3:__init__:default_linus_field" % linus_filter
            elif not filter_.startswith('finder_'):
                vault_filters[filter_] = dict_filters[filter_]
                assert filter_ in qbox.default_vault_field, "CODE ERROR! Add %r in pcar3:__init__:default_vault_field" % filter_

        vault_filter_list = self._gen_filter_list(vault_filters)
        linus_filter_list = self._gen_filter_list(linus_filters)

        # Add to the dictionary only if filter exist, for performance reason: since empty filter means get all records
        if vault_filter_list:
            qbox.vault_dict_csv[self.id] = {'filter_vault': vault_filter_list}
        if linus_filter_list:
            qbox.linus_dict_csv[self.id] = {'filter_linus': linus_filter_list}

    def _set_finder_filters(self, dict_filters):
        """
        Set finder dict_csv

        :param dict_filters: dictionary of finder_tag, finder_testname, finder_regex
        :return:  processed dictionary for unittest
        """
        result = {}
        if 'finder_tag' in dict_filters and dict_filters['finder_tag']:
            result['tag'] = dict_filters['finder_tag']

        if 'finder_regex' in dict_filters:
            field = dict_filters['finder_regex']
            if field:
                # take care of NOT first
                if field.startswith('!'):
                    fnot = '!'
                    field = field[1:]
                else:
                    fnot = ''

                # anchor characters
                end = r"\w*"
                if field.endswith('$'):
                    field = field[:-1]
                    end = ''

                start = r"\w*"
                if field.startswith('^'):
                    field = field[1:]
                    start = ''

                result['name'] = '{fnot}{start}{field}{end}'.format(fnot=fnot, start=start, field=field, end=end)

        if 'finder_testname' in dict_filters:
            field = dict_filters['finder_testname']
            if field:
                # take care of NOT first
                if field.startswith('!'):
                    fnot = '!'
                    field = field[1:]
                else:
                    fnot = ''

                # anchor characters
                if field.endswith('$'):
                    field = field[:-1]
                if field.startswith('^'):
                    field = field[1:]

                result['name'] = r"%s\w+_%s" % (fnot, field)     # finder output as extension, anchor on this.

        if result:
            finder_filter_list = self._gen_filter_list(result)
            qbox.finder_dict_csv[self.id] = {'filter_finder': finder_filter_list}

        return result   # for unittest

    def get_groups(self, field, regex, n, check=True):
        """
        Return a set of regex.group(n) based on regex of field filter

        How it works:
        1. Create set_str. This is a set of strings containing "intent" for example.
           first pass: only TID's found by self (aka, QueryTid) are added in set_str
           second pass: accept only items which matches direct_filters.
           direct_filters are earlier elements of 'regex' string, since last element is regex
        2. re.findall() is executed using regex (ie, last element) given set_str.
           set output of re.findall() is returned

        :param field: string, field name to get group on
        :param regex: regex string. If space delimited, only last element is regex. earlier elements are direct string compare.
        :param n: int, which group number to return. It starts with 1.
        :param check: bool, True to check direct_filters if they are regex
        :return: set of strings
        """
        sw = Elapsed()

        # Do some checks
        if field not in qbox.default_vault_field:
            raise ErrorInput("QueryTid(%s).get_groups(field=%r) is not valid since %r is not a vault field."
                             "" % (self.id, field, field),
                             "get_groups() only work with vault fields.")
        if not regex:
            raise ErrorInput("QueryTid(%s).get_groups(regex=%r) is not valid."
                             "" % (self.id, regex),
                             "regex can't be empty.")

        # get the filters. Only last element is an actual regex. Earlier elements are direct string compares.
        all_filters = Funcs.to_list_split(regex)
        direct_filters = []
        direct_not_filters = []
        if len(all_filters) == 1:
            regex_filter = all_filters[0]
        else:
            # The space is added to avoid partial matches (ambiguous match)
            # '\s' is converted to a real space
            direct_filters = ['%s ' % x.replace(r"\s", ' ') for x in all_filters[:-1] if not x.startswith('!')]
            direct_not_filters = ['%s ' % x[1:].replace(r"\s", ' ') for x in all_filters[:-1] if x.startswith('!')]
            regex_filter = all_filters[-1]

        # make sure it is a valid regex string
        Funcs.check_regex_str('regex', regex_filter)

        # check direct filters if they are regex
        for item in direct_filters + direct_not_filters:
            if check and ('*' in item or '\\' in item or '|' in item):
                raise ErrorInput("QueryTid(%s).get_groups(regex=%r). %r seems to be regex."
                                 "" % (self.id, regex, item),
                                 "Only last element (ie, %r) can be regex. Other elements "
                                 "(ie, %r) must be direct string compare. If you think this "
                                 "is correct and really wanted to use direct string compare on "
                                 "%r, then add check=False in get_groups()"
                                 "" % (regex_filter, item, item))

        # Do the one-time (expensive) processing
        if '_result' not in self._get_grp:
            qbox.process(self)
            self._get_grp['_result'] = self.result()

        # create the large string
        if field not in self._get_grp:
            dv = qbox.dict_vault
            set_str = {' %s ' % dv[tid][field] for tid in self._get_grp['_result'] if tid in dv}    # first pass; space is intentionally added before and after as start and end markers
            self._get_grp[field] = set_str

        # do direct_filters (second pass)
        set_str = self._get_grp[field]
        for filter_ in direct_filters:
            set_str = {x for x in set_str if filter_ in x}
        for filter_ in direct_not_filters:
            set_str = {x for x in set_str if filter_ not in x}

        result = {x if isinstance(x, str) else x[n] for x in re.findall(regex_filter, '\n'.join(set_str))}

        # debug and benchmark
        debug_data = dict(bl=len(self._get_grp[field]), rl=len(result), sl=len(set_str), regex=regex, field=field, sw=sw)
        log.dev("get_groups({field}): {sw} result_len={rl} search_lines={sl} base_n_lines={bl} {regex}".format(**debug_data))
        return result

    @classmethod
    def _set_common_vault(cls, **kwargs):
        """
        Reduce the tid set of Vault records for faster processing.
        Instead of processing 60K (for example) records all the time, reduce this set of records to what
        matters only for this config

        Performance:
        # no common_vault: -i- filter_vault, unique expr=113, Elapsed 12.104 Secs (65282 tid)
        # w/ common_vault: -i- filter_vault, unique expr=113, Elapsed 3.118 Secs  (8731 tid)

        :return: nothing
        """
        # check first if common_vault is already run
        msg = ("QueryTid.common_vault() is already applied. Cannot use common_vault() more than once.",
               "Call common_vault() once at the top of your .pcar3 file. common_vault() will be "
               "applied to all QueryTid() in the .pcar3 file.")
        assert not qbox.orig_dict_vault, msg

        # check for valid args
        invalid = set(kwargs) - qbox.default_vault_field
        assert not invalid, ("The following are non-vault fields: %s" % ','.join(invalid),
                             "Only vault fields are allowed in common_vault()")

        obj = QueryTid(**kwargs)
        qbox.process(obj)
        res = obj.result()
        log.info("-i- common_vault() is set to %s vault records. original vault records: %s"
                 "" % (len(qbox.dict_vault), len(res)))
        qbox.orig_dict_vault = qbox.dict_vault     # save original
        qbox.dict_vault = {x: v for x, v in qbox.dict_vault.items() if x in res}
        qbox.preview.fastlookup.faststr.pop('filter_vault', None)    # remove this key from dict cache (will not error if key does not exist)

    def _process_common(self):
        """
        Assign the common args to the class

        :return: Nothing
        """
        for item in self.common:
            if item.startswith('_'):
                continue     # do nothing

            if item == 'ordertop' and self.ordertop is not None:
                self.ordertop.extend(self.common['_obj'].ordertop)
                continue

            if item == 'orderbottom' and self.orderbottom is not None:
                self.orderbottom.extend(self.common['_obj'].orderbottom)
                continue

            # all other attributes - simple assign
            if getattr(self, item) is None:
                setattr(self, item, self.common[item])


class Preview:
    """
    Compas Preview Class.
    """
    filter_keywords = {'filter_linus', 'filter_vault', 'filter_finder'}

    def __init__(self):
        # These are truly populated in main()
        self.prod = None
        self.step = None
        self.igrp = InvalidGroup(is_error=True)

        # Other initializations
        self.outdir = None
        self.age_cache = 4 * 3600    # number of seconds before cached file is considered stale
        self.sw = Elapsed()

        # list of fields
        self.enum = {'attributes', 'tag', 'testtype', 'producttag'}  # enumerated vault/linus fields. They are processed a little differently
        self.fields_vault_only = {'attributes', 'tag', 'testtype'}

        # Below are special linus fields which need table name
        self.special = {}
        for item in ("product.tag", "product.name"):
            self.special[item.replace('.', '')] = item

        # Valid team names
        self.valid_teams = set("scan func ftw array reset dft tpi fuse sio mio clk ptc fivr power thermal".split())

        # Which algo to use
        self.fastlookup = FastLookup()

    def run_vault(self, more_fields=set()):
        """
        Call vault
        :return: dictionary with the following format
        {'994158': {'attributes': 'targ_de',
                    'directives': 'PAT_NAME=ccf_cbb_byp_sa_mNm_phase0 NUM_CHUNKS=200',
                    'tag': 'unassigned',
                    'testtype': 'iscan_de_diag'},
        }
        """
        default_fields = set('test_id tag testtype attributes directives intent'.split())
        vault_fields = Func.order_fields(default_fields | more_fields, 'test_id')
        vault_cmd = 'vaultmgr -proj %s_%s -pr %s -pr- -nolog' % (self.prod, self.step, vault_fields)
        result = self._call_vault(vault_cmd)
        sw = Elapsed()
        key = None
        dict_vault = defaultdict(dict)
        robj = re.compile(r"^(\w+)\s+\S+\s+(.*)$")
        all_fields = set()
        for line in result.split('\n'):
            line = line.strip().replace(self.fastlookup.special_char, '@')    # replace special char to avoid incorrect queries
            if line.startswith('|--------'):
                key = None
            if line.startswith('test_id'):    # marker
                key = line.split()[2].zfill(7)
                continue
            if key:
                res = robj.search(line)
                if res:
                    field = res.group(1)
                    value = res.group(2)
                else:
                    field = line.split()[0]
                    value = ""

                # add the key so it can be queried
                if key not in dict_vault:
                    dict_vault[key]['test_id'] = key
                    all_fields.add('test_id')

                # add to dictionary
                field = field.lower()
                dict_vault[key][field] = value.lower()
                all_fields.add(field)

        # make sure more_fields exist. If not, then cache is not ok.
        dict_vault.default_factory = None    # turn off defaultdict
        self._check_all_fields(more_fields, all_fields, 'vault')
        self._add_testname_vault(dict_vault)
        log.info("-i- run_vault(): total tids: %s, %s" % (len(dict_vault), sw))
        return dict_vault

    def run_linus(self, more_fields=set(), prod_tag=''):
        """
        Call linus
        :param more_fields:
        :param prod_tag:    Optional string to add to linus query, e.g. 'product.tag=lcc'
        :return: dictionary with the following format
        { 'Burnin_Hvm_Core_Tap0': {'tag': 'targ_de',
                                   'testtype': 'iscan_de_diag'},
        }
        """
        default_fields = set('name tag attributes testtype stepping owner production'.split())

        # replace 'producttag' -> 'product.tag', as defined in self.special
        all_fields = {self.special.get(item, item) for item in (default_fields | more_fields)}

        linus_fields = Func.order_fields(all_fields, 'name')
        linus_cmd = ('linus_qry -q product.name=%s stepping=%s %s enabled=1 -q- -pr %s -pr- -nolog'
                     '' % (self.prod, self.step, prod_tag, linus_fields))
        result = self._call_linus(linus_cmd, prod_tag)
        sw = Elapsed()
        key = None
        dict_linus = defaultdict(dict)
        robj = re.compile(r"^(\S+)\s+\S+\s+(.*)$")
        all_fields = set()
        for line in result.split('\n'):
            line = line.strip().replace(self.fastlookup.special_char, '@')    # replace special char to avoid incorrect queries
            if line.startswith('======'):
                key = None
            if line.startswith('Lineitem.Name'):    # marker
                key = line.split()[2]
                continue
            if key:
                res = robj.search(line)
                if res:
                    field = res.group(1)
                    value = res.group(2)
                else:
                    field = line.split()[0]
                    value = ""

                if '.' in field:
                    if field.lower() in self.special.values():
                        field = field.replace('.', '')
                    else:
                        field = field.split('.')[1]

                field = field.lower()
                if field in dict_linus[key.lower()] and dict_linus[key.lower()][field] != value.lower():
                    dict_linus[key.lower()][field] = "%s,%s" % (dict_linus[key.lower()][field], value.lower())
                else:
                    dict_linus[key.lower()][field] = value.lower()
                all_fields.add(field)

        dict_linus.default_factory = None    # turn off defaultdict
        self._check_all_fields(more_fields, all_fields, 'linus')
        log.info("-i- run_linus(): total LI: %s, %s" % (len(dict_linus), sw))
        return dict_linus

    def run_finder_pcar3(self):
        """
        Execute finder and return data structure.
        Logic here is to avoid disassemble for performance.
        Only three fields are allowed: tag, testname and any name regex

        :return: dict_tid, dict_tup
        dict_tid: {tid: <set_of_tuple#>}
        dict_tup: {tup: {'name': name, 'tid': tid, 'tag': tag}}
        """
        cmd = 'finder.py -local -linus_prod %s_%s' % (self.prod, self.step)
        result = self._call_finder(cmd)
        dict_tid = defaultdict(set)
        dict_tup_field = {}
        result = result.split('\n')
        p3_trctag = set()     # set(OPT.p3_trctag) if OPT.p3_trctag else set()

        log.info("-i- Processing %s finder entries" % len(result))
        sw = Elapsed()
        for line in result:
            res = line.split()
            if len(res) != 3:
                continue

            path, _, tags = res
            name = basename(path)
            if name[0] == "i":  # ipples are not used by vcf. Don't load this.
                continue
            tags = tags[1:-1]
            tid = name[9:16]
            tup = name[1:8]

            if p3_trctag:
                if p3_trctag - set(tags.split(',')):    # return {} if match tags
                    continue

            dict_tid[tid].add(tup)
            dict_tup_field[tup] = {'tid': tid, 'tag': tags, 'name': name}

        dict_tid.default_factory = None    # turn off defaultdict
        log.info("-i- finder entries completed in %s. tid count: %s" % (sw, len(dict_tup_field)))
        return dict_tid, dict_tup_field

    def filter_finder_pcar3(self, dict_csv, dict_finder):
        """
        Get all TIDs for each group.
        This is the same *filter_vault* version for finder.

        :param dict_csv: dictionary from input csv
        :param dict_finder: This is the expanded dictionary
        :return: dictionary: {group: set_of_tuples}
        """
        return self.fastlookup.filter(dict_csv, dict_finder, 'filter_finder', r"(\d+)", enum={'tag'}, lower=False, pcar3=True)

    def _get_product_tags(self, dict_csv):
        """
        Determine product tags per group. Empty string for no product tags.
        :param dict_csv: dictionary of {group: {filter_linus: []} }
        :return: dictionary of {group: <product_tag>}
        """
        r_tag = re.compile(r"producttag\s*=\s*(\S+)")
        result = {}
        for group in dict_csv:
            prod_tag = ""    # default
            for item in dict_csv[group].get('filter_linus', []):
                reobj = r_tag.search(item)
                if reobj:
                    prod_tag = reobj.group(1)
            result[group] = prod_tag
        return result

    def _check_all_fields(self, more_fields, all_fields, area):
        """
        Make sure fields exist in dictionary
        :param more_fields: expected fields
        :param all_fields: fields found
        :param area: area
        :return: Nothing
        """
        for field in sorted(more_fields):
            if field.lower() == 'name' and area == 'linus':
                continue    # name is already added in _gen_fast_string

            if area == 'linus' and field.lower() == 'owner' and field.lower() not in all_fields:
                raise ErrorUser("linus output is empty. Check cached file above or the linus command above.",
                                "Do you have correct product and stepping?")

            if field.lower() not in all_fields:
                raise ErrorUser("[%s] is requested field but it's not in %s output"
                                "" % (self.special.get(field, field), area),
                                "If [%s_%s.%s] exist, then delete this file so cache is refreshed. "
                                "If this error keeps showing up, maybe this field is not a valid one?"
                                "" % (self.prod, self.step, area))

    def _call(self, cmd, area, force_refresh=False):
        """
        Do the system call with smart cache
        :param cmd: Actual system command
        :param area: short string on which area is this
        :param force_refresh: Set to True to force refresh
        :return: stdout+stderr of command
        """
        fname = join(self.outdir, "%s_%s.%s" % (self.prod, self.step, area))
        fobj = File(fname)
        is_refresh = False
        if fobj.exists():
            if True:    # read only
                Func.log_info_once("-i- On %s, reusing cached [%s]. Add -p3_refresh to force refresh." % (area, fname))
                return fobj.read()

        raise ErrorCockpit("QBox() is readonly! Not exist: [%s]" % fname)

        log.info("-i- Running CMD: %s" % cmd)

    def _call_vault(self, cmd):
        """Call Vault as a systemcall, unittest friendly"""
        return self._call(cmd, 'vault')

    def _call_linus(self, cmd, prod_tag=''):
        """Call linus as a systemcall, unittest friendly"""
        if prod_tag:
            area = 'linus.%s' % prod_tag
        else:
            area = 'linus'
        return self._call(cmd, area)

    def _call_finder(self, cmd):
        """Call finder as a systemcall, unittest friendly"""
        return self._call(cmd, 'finder')

    def filter_vault(self, dict_csv, dict_vault, pcar3=False):
        """
        Get all TIDs for each group
        :param dict_csv: dictionary from input csv
        :param dict_vault: This is the expanded dictionary
        :param pcar3: bool, True if pcar3 usage (no regex translation)
        :return: dictionary: {group: set_of_tid}
        """
        return self.fastlookup.filter(dict_csv, dict_vault, 'filter_vault', r"(\d+)", enum=self.enum,
                                      pcar3=pcar3)

    def filter_linus(self, dict_csv, dict_linus, dict_tlg, pcar3=False, refresh=False):
        """
        Get all TIDs for each group
        :param dict_csv: dictionary from input csv
        :param dict_linus: Linus dictionary
        :param dict_tlg: TestListGen dictionary
        :param pcar3: bool, True if pcar3 usage (no regex translation)
        :return: dictionary: {group: set_of_tid}
        """
        result = self.fastlookup.filter(dict_csv, dict_linus, 'filter_linus', r"(\w+)", name_add=True,
                                        enum=self.enum, pcar3=pcar3, refresh=refresh)

        # get all tids for all valid line items
        cache = {}
        tids = {x: set() for x in dict_csv}    # initialize to empty sets
        for group in result:
            key = ':'.join(sorted(result[group]))
            if key not in cache:
                stid = set()
                for lineitem in result[group]:
                    prod_tag = dict_tlg['_MAP'][group]
                    stid.update(dict_tlg[prod_tag].get(lineitem, []))
                cache[key] = stid

            tids[group] = cache[key]
            log.dev("filter_linus: %s: %s" % (group, Func.disp_set_debug(tids[group])))

        return tids

    def expand_dict(self, dict_csv, is_error=True):
        """
        Expand dict_csv and do error checks
        :param dict_csv: dictionary from input csv
        :param is_error: True for Raise Exception (interactive)
        :return: True if dict is modified
        """
        self.igrp.clear()

        # remove the spaces
        modified = False
        robj_spc = re.compile(r"^\s*(\S+)\s*(=|!\s*=)\s*(\S.*)$")
        for group, filtr in Func.iter_group_filter(dict_csv):
            items = []
            for item in dict_csv[group][filtr]:

                # Check if there are not in value. This is not supported
                res = robj_spc.search(item)
                if res:
                    newitem = "%s%s%s" % (res.group(1), res.group(2).replace(' ', ''), res.group(3))
                    newitem = newitem.strip()
                    if newitem != item:
                        items.append(newitem)
                    else:
                        items.append(item)
                else:
                    items.append(item)

            dict_csv[group][filtr] = items

        # remove the "Lineitem."
        robj_dot = re.compile(r"^\w+\.(\w+)(=|!=)(\S.*)$")
        for group, filtr in Func.iter_group_filter(dict_csv):
            items = []
            for item in dict_csv[group][filtr]:
                res = robj_dot.search(item)

                if res:

                    # special case
                    for sp_k, sp_v in self.special.items():   # sp_k=producttag, sp_v=product.tag
                        if item.lower().startswith(sp_v) and filtr == 'filter_linus':
                            items.append('%s%s%s' % (sp_k, res.group(2), res.group(3)))
                            break
                    else:
                        # normal case
                        items.append('%s%s%s' % (res.group(1), res.group(2), res.group(3)))

                else:
                    items.append(item)
            dict_csv[group][filtr] = items

        # lowercase the field
        robj_lc = re.compile(r"^(\w+)(=|!=)(\S.*)$")
        for group, filtr in Func.iter_group_filter(dict_csv):
            if filtr not in self.filter_keywords:
                continue
            items = []
            for item in dict_csv[group][filtr]:
                res = robj_lc.search(item)
                if not res:
                    self.igrp.error_user(group,
                                         "group=[%s] on %s has [%s]. Invalid expression"
                                         "" % (group, filtr, item),
                                         "Expected expression is '<field>(=|!=)<expression'")
                    break

                field = res.group(1).lower()
                expr = res.group(3)
                if field == 'test_id' and filtr == 'filter_vault':
                    if expr.isdigit():
                        expr = expr.zfill(7)

                items.append('%s%s%s' % (field, res.group(2), expr))

            dict_csv[group][filtr] = items

        # Expand the enumerated tags with comma. This assumes no spaces.
        robj_exp = re.compile('^(%s)(=|!=)(.*,.*)$' % '|'.join(self.enum))
        for filtr in self.filter_keywords:
            for group in dict_csv:
                if filtr not in dict_csv[group]:
                    continue

                allitems = []
                for item in list(dict_csv[group][filtr]):

                    # Do the expansion on enumerated fields
                    res = robj_exp.search(item)
                    if res:
                        field, op, value = res.groups()
                        mod_item = ['%s%s%s' % (field, op, x) for x in value.split(',')]
                        allitems.extend(mod_item)
                        modified = True
                        dict_csv[group][Func.get_mod_field(dict_csv[group], group)] = ['update']
                    else:
                        allitems.append(item)
                dict_csv[group][filtr] = allitems

        # Check for not and special characters. This is expanded
        robj_not = re.compile(r"^(\w+)(=|!=)(!.*)$")
        for group, filtr in Func.iter_group_filter(dict_csv):
            for item in dict_csv[group][filtr]:

                # Check if there are not in value. This is not supported
                res = robj_not.search(item)
                if res:
                    self.igrp.error_user(group,
                                         "group=[%s] on %s has [%s]. ! is not supported in value."
                                         "" % (group, filtr, item),
                                         "Use '%s!=<value>' instead" % res.group(1))
                    break

                # check for special char
                if self.fastlookup.special_char in item:
                    self.igrp.error_user(group,
                                         "group=[%s] on %s has [%s]. It contain special char '%s'"
                                         "" % (group, filtr, item, self.fastlookup.special_char),
                                         "Do not use the special character")
                    break    # pragma: no cover - Cannot easily test since json is erroring out on integration

        # check for valid teams
        for group in dict_csv:
            if 'team_name' in dict_csv[group]:
                name = dict_csv[group]['team_name'][0]
                if name.lower() not in self.valid_teams and is_error:
                    raise ErrorUser("group=[%s] has team_name=[%s]. This is invalid." % (group, name),
                                    "List of valid team_name: %s" % ', '.join(sorted(self.valid_teams)))

        self.igrp.remove_groups(dict_csv)

        return modified

    def _add_testname_vault(self, dict_vault):
        """
        Applies Vault directive TEST_RENAME (append, rename, prepend) to test name if applicable.
        'path' and 'directives' will always exist, although 'directives' may be an empty string.

        dict_vault has the following format:
                {'994158': {'attributes': 'targ_de',
                    'directives': 'PAT_NAME=ccf_cbb_byp_sa_mNm_phase0 TEST_RENAME=<replace|append|prepend>:<new_name_str>',
                    'path' : '/tests/kbl_g0/scan/my_test/my_test.cfg',
                    'tag': 'unassigned',
                    'testtype': 'iscan_de_diag'},
                }
        """
        robj = re.compile(r'\bTEST_NAME=(\w+):(\w+)')
        for tid in dict_vault:
            if 'path' not in dict_vault[tid]:  # JDR said add this line for minimal impact to existing unit tests
                continue

            testname = basename_delext(dict_vault[tid]['path'])
            result = robj.search(dict_vault[tid]['directives'])
            if result:
                keyword = result.group(1)
                namestr = result.group(2)

                if keyword == 'replace':
                    testname = namestr
                elif keyword == 'append':
                    testname = testname + namestr
                elif keyword == 'prepend':
                    testname = namestr + testname

            dict_vault[tid]['testname'] = testname


class Funcs(object):
    """
    These are pcar3 helper functions used thoughout objects which are not directly related to any object
    """
    _valid_pat_fields = set()    # cache - set of valid pattern name fields. Assigned once only.

    @staticmethod
    def log_max(obj_list, max_tid_log=5):
        """
        Returns a string for log purposes, truncated depending on self.max_tid_log

        :param obj_list: some list
        :param max_tid_log: maximum number of tid or tuple to display
        :return: string
        """
        if len(obj_list) > max_tid_log:
            return "[%s, ...]" % ', '.join('%r' % item for item in obj_list[:max_tid_log])
        else:
            return str(obj_list)

    @staticmethod
    def caller_info(filepath=False):
        """
        Return the caller file and line number
        This must be called from __init__() of class, which is called from pcar config .py.

        :param filepath: Set to True to return pcar3 filepath only
        :return: string
        """
        tb = traceback.extract_stack()
        for x in range(1, len(tb) + 1):
            target = tb[-1 * x]
            if 'mod/querytid.py' not in target[0]:    # unittest will fail if the python file got renamed
                if filepath:
                    return target[0]
                else:
                    return "%s, line %d" % (basename(target[0]), target[1])

        return "<pcar3_core_file_tvpvhelp>"      # pragma: no cover - should not happen - cant test without Mock

    @staticmethod
    def to_list_split(obj):
        """
        Return list of obj splitted by space

        :param obj: either str or list
        :return: list
        """
        if isinstance(obj, str):
            return obj.split()
        else:
            return to_list(obj)   # return a list

    @staticmethod
    def indent_list(n, input):
        """
        Indent the input list by n characters

        :param n: number of chars of indent
        :param input: list of strings
        :return: new list of strings indented
        """
        result = []
        ind = ("%{n}s".format(n=n)) % " "
        for line in input:
            result.append("%s%s" % (ind, line))
        return result

    @staticmethod
    def check_int(field, value, noneok=False):
        """
        check value if int. Used with param checking

        :param field: fieldname
        :param value: value
        :return: value
        """
        if noneok and value is None:
            return value
        if not isinstance(value, int):
            raise ErrorInput("On %s=%r, %s is expecting an integer."
                             "" % (field, value, field),
                             "Pls fix value of %s" % field)
        return value

    @staticmethod
    def check_string(field, value, valid=None):
        """
        check value if str or None. Used with param checking

        :param field: fieldname
        :param value: value
        :param valid: valid regex
        :return: value
        """
        if value is None:
            return value

        if not isinstance(value, str):
            raise ErrorInput("On %s=%r, %s is expecting a string."
                             "" % (field, value, field),
                             "Pls fix value of %s" % field)
        if valid:
            if not re.search(valid, value):
                raise ErrorInput("%r is invalid for %s."
                                 "" % (value, field),
                                 "Expected valid value is this regex: %r" % valid)

        return value

    @staticmethod
    def check_all_string(field, value):
        """
        check value if str or None. Used with param checking

        :param field: fieldname
        :param value: value (which is a list)
        :return: value
        """
        if value[0] is None:
            return []

        for item in value:
            if not isinstance(item, str):
                raise ErrorInput("On %s=%r, %s is expecting a string."
                                 "" % (field, item, field),
                                 "Pls fix value of %s" % field)
        return value

    @staticmethod
    def check_regex_list(field, value, quotes=True):
        """
        check value if str, list of str or None. If str, must be valid regex.
        Used with param checking

        :param field: fieldname
        :param value: value
        :param quotes: True to display quotes, False otherwise
        :return: value
        """
        for item in to_list(value):
            if not isinstance(item, str):
                raise ErrorInput("On %s=%r, %s is expecting a string."
                                 "" % (field, item, field),
                                 "Pls fix value of %s" % field)
            try:
                _ = re.compile(item)
            except Exception as e:
                if quotes:
                    msg = ("On %s=%r, value is an invalid regex. Error: %s" % (field, item, e))
                else:
                    msg = ("On %s=%s, value is an invalid regex. Error: %s" % (field, item, e))
                raise ErrorInput(msg, "Fix %r so it's a valid regex" % item)
        return value

    @staticmethod
    def check_regex_str(field, value, pseudo=False):
        """
        check value if str is a valid regex.
        Used with param checking

        :param field: fieldname
        :param value: value
        :param pseudo: Set to True for pseudo regex
        :return: value
        """
        if value is None:
            return value
        if not isinstance(value, str):
            raise ErrorInput("On %s=%r, %s is expecting a string."
                             "" % (field, value, field),
                             "Pls fix value of %s" % field)
        try:
            if pseudo:
                _ = re.compile(to_regex(value))
            else:
                _ = re.compile(value)
        except Exception as e:
            raise ErrorInput("On %s=%r, value is an invalid regex. Error: %s"
                             "" % (field, value, e),
                             "Fix %r so it's a valid regex" % value)
        return value

    @staticmethod
    def check_bool(field, value):
        """
        check value if bool. Used with param checking

        :param field: fieldname
        :param value: value
        :return: value
        """
        if value is None:
            return value
        if str(value).lower() == 'true':
            return True
        if str(value).lower() == 'false':
            return False
        if not isinstance(value, bool):
            raise ErrorInput("On %s=%r, %s is expecting True or False."
                             "" % (field, value, field),
                             "Pls fix value of %s" % field)
        return value

    @staticmethod
    def check_pos_args(obj, dummyarg, class_name, caller_info, suggestion="See wiki for usage."):
        """
        Check if positional args is accidentally used (user things it is a list of tuple, as example)

        :param obj: First arg
        :param dummyarg: Input arg
        :param class_name: name of class
        :param caller_info: callerinfo
        :param suggestion: suggestion message
        :return: Nothing
        """
        if dummyarg is not None:
            if obj is not None:
                suggestion = ("Only first argument can be positional arg. First arg can be a list. "
                              "Do you mean to put this as a list, example %s([%r, %r, etc])"
                              "" % (class_name, obj, dummyarg))

            raise ErrorInput("%s() on %s: invalid positional args: %r" % (class_name, caller_info, dummyarg),
                             suggestion)

    @staticmethod
    def copy_to_rundir(ff, ext):
        """
        Copy file to rundir

        :param ff: full path to file
        :param ext: '.tidfile' or '.tuplefile'
        :return: Nothing
        """
        raise Exception("Remove this")


class Func(object):
    """
    Generic Helper functions originally from compas_query
    """
    _cache_log = set()     # cache of log_info_once

    @staticmethod
    def order_fields(fields, mainkey):
        """
        Return a string with mainkey as first element and the rest of the fields concatenated with space
        :param fields: set of keys
        :param mainkey: first key to show up
        :return: string
        """
        return "%s %s" % (mainkey, ' '.join(x for x in sorted(fields - {mainkey})))

    @staticmethod
    def iter_group_filter(dict_csv):
        """
        Iterator on dict_csv. Exclude '_order'
        :param dict_csv:
        :return: group, filter
        """
        for group in list(dict_csv):
            for filtr in list(dict_csv[group]):
                if filtr in ('_order',):
                    continue    # these are non-string
                yield group, filtr

    @staticmethod
    def disp_set_debug(some_set):
        """
        Return the first n value of set (-n <first_value>), if -devdebug

        :param some_set: set
        :return: first N value of set
        """
        if not OPT.devdebug:
            return ""

        result = []
        for n, value in enumerate(sorted(some_set)):
            if n == OPT.n:
                break
            result.append(value)
        result.append('TOTAL=%s' % len(some_set))
        return ' '.join(result)

    @staticmethod
    def get_mod_field(subdict, group):
        """
        Get the field name for row modification
        :param subdict: dictionary of a particular group: {<field>: <value>}
        :param group: group_name
        :return: field name
        """
        for item in subdict:
            if item.startswith('group_action'):
                return item
        else:
            raise ErrorUser("group=[%s] does not have 'group_action' column" % group,
                            "Check csv file and make sure it has group_action header.")

    @staticmethod
    def log_info_once(txt):
        """
        log txt once only for the entire process. (reduce unnecessary logs)

        :param txt:
        :return: None
        """
        if txt not in Func._cache_log:
            log.info(txt)
            Func._cache_log.add(txt)


class InvalidGroup(object):
    """
    Invalid group accumulator.

    Depending on usage:
    1. interactive -> raise exception
    -vs-
    2. compas-json-call -> accumulate invalid groups then remove those groups.

    Usage:
    obj = InvalidGroup()
    obj.error_user(<args>)
    obj.error_user(<args>)
    obj.remove_groups(dict_csv)
    """

    def __init__(self, is_error):
        """
        :param is_error: Set to True for interactive (aka, will raise exception)
        """
        self.invalid_group = set()
        self.is_error = is_error
        self.errors = {}

    def clear(self):
        """
        Clear the invalid groups
        :return: Nothing
        """
        self.invalid_group = set()

    def set_no_error(self):
        """
        Set is_error to False. used by compas
        :return: Nothing
        """
        self.is_error = False

    def error_user(self, group, message, suggestion):
        """
        raise ErrorUser if self.is_error, do nothing otherwise

        :param group: group name
        :param message: string message
        :param suggestion: string suggestion
        :return: nothing
        """
        self.invalid_group.add(group)

        if self.is_error:
            raise ErrorUser(message, suggestion)
        else:
            txt = "%s; %s" % (message, suggestion)
            log.info('Error: %s' % txt)
            self.errors[group] = txt

    def remove_groups(self, dict_csv):
        """
        Remove invalid groups in dict_csv

        :param dict_csv: dictionary, will be modified
        :return: nothing
        """
        for group in self.invalid_group:
            del dict_csv[group]


class SuperTLG:
    """
    TestListGen replacement by deriving it from Vault and Linus data
    This class is instantiated once only
    """

    def __init__(self):
        self.last_prod_tag = None

    def check_cache(self, prod_tag):
        """
        Check if prod_tag is cached, based on age of file

        :param prod_tag: product tag (hcc, lcc, '' for head)
        :return: cache_file, cached data or None
        """
        prodstep = "%s/%s_%s" % (qbox.root, qbox.preview.prod, qbox.preview.step)
        cache_file = '%s.super_tlg.pkl.%s' % (prodstep, prod_tag)

        age1 = File('%s.vault' % prodstep).age(error=False)
        if prod_tag:
            age2 = File('%s.linus.%s' % (prodstep, prod_tag)).age(error=False)
        else:
            age2 = File('%s.linus' % prodstep).age(error=False)

        ageref = File(cache_file).age(error=False)

        # any of the files does not exist
        if age1 == -1 or age2 == -1 or ageref == -1:
            # print "DEBUG1", cache_file, age1, age2, ageref
            return cache_file, 0

        # any of the files is newer than cache file
        if ageref > age1 or ageref > age2:
            # print "DEBUG2", cache_file, age1, age2, ageref
            return cache_file, ""

        # cache is valid
        log.info('-i- On super-testlistgen, reusing cached [%s]' % cache_file)
        return cache_file, pickle.load(open(cache_file, 'rb'))

    def super_tlg(self, linus_data, vault_data, prod_tag):
        """
        This routine replaces the functionality of the 'testlistgen' command line.
        This is called once per product tag

        :param linus_data: dictionary where key is line item, value is dictionary containing testtype, tag, attr, etc
        :param vault_data: same as linus data except key is tid
        :param prod_tag: product tag (hcc, lcc, head)
        :return: dictionary where key = line item name, value = list of matching tids
        """
        cache_file, cached_data = self.check_cache(prod_tag)
        if cached_data:
            return cached_data

        line_item_dict = {}     # key = line item name, value = vault fields to match

        for line_item in linus_data:

            flist = ['tag=%s' % linus_data[line_item]['tag'],
                     'testtype=%s' % linus_data[line_item]['testtype']]

            for ll in linus_data[line_item]['attributes'].split(','):
                # check for not filters in attributes
                if '!' in ll:
                    flist.append('attributes!=%s' % ll.replace('!', ''))
                else:
                    flist.append('attributes=%s' % ll)

            line_item_dict[line_item] = {'filter_vault': flist}

        # line item name = group name (for the call below)
        output = qbox.preview.filter_vault(line_item_dict, vault_data)

        # remove any empty sets from the output
        for key in list(output.keys()):
            if len(output[key]) == 0:
                del output[key]

        # save to cache file (cache_file is None during some unittest)
        if cache_file:
            wip = '%s.wip.%s' % (cache_file, USERNAME)
            pickle.dump(output, open(wip, 'wb'))
            File(wip).chmod("0660", ignoreError=True)
            File(cache_file).unlink()
            File(wip).rename(basename(cache_file))
            log.info('-i- On super-testlistgen, created cache [%s]' % cache_file)

        return output

    def build_prod_dict_tstlg(self, prod, all_prod_tags):
        """
        Build the _MAP key in dict_tstlg to only contain ids of the given prod

        :param prod: hcc/lcc/'' (for head)
        :param all_prod_tags: dictionary
        :return: dict_tstlg dictionary
        """
        dict_tstlg = {'_MAP': {}}
        for id in all_prod_tags:
            if all_prod_tags[id] == prod:
                dict_tstlg['_MAP'][id] = prod
        return dict_tstlg

    def get_prod_linus_csv(self, dict_tstlg, global_linus_dict_csv):
        """
        Build a linus_dict_csv (from the global one) that contains only ids in the current product

        :param dict_tstlg:
        :param global_linus_dict_csv:
        :return: linus_csv dictionary per prodtag (hcc/lcc/'')
        """
        prod_linus_csv = {}
        for id in dict_tstlg['_MAP']:
            prod_linus_csv[id] = global_linus_dict_csv[id]

        return prod_linus_csv

    def check_last_prod_tag(self, prod):
        """
        This tracks the last product tag run through filter_linus
        If the product tag changes, the compas faststr cache needs to be updated (return True)
        If the product tag does not change, return False (compas will keep the same cache)

        :param prod: hcc/lcc/'' (for head)
        :return: True if refresh is needed
        """
        refresh = bool(self.last_prod_tag != prod)      # set to True when the prod changes
        self.last_prod_tag = prod
        return refresh

    def execute_linus(self, linus_dict_csv, dict_linus):
        """
        Execute linus and testlistgen (for all prodtags)

        :param linus_dict_csv: input linus dict_csv
        :param dict_linus: dictionary - this is populated in this routine

        :return: result_linus, linus_info and dict_tstlg
        """
        result_linus = {}        # {<group_id>: [<tids>]}
        linus_info = {}          # {<group_id>: {<lineitems>: <linus_field_values>}
        dict_tstlg = {}          # {<lineitem>: <tids>}

        all_prod_tags = qbox.preview._get_product_tags(linus_dict_csv)
        for prod in set(all_prod_tags.values()):
            # execute linus
            prod_tag = ''
            if prod:
                prod_tag = 'product.tag=%s' % prod
            if prod not in dict_linus:
                dict_linus[prod] = qbox.preview.run_linus(qbox.default_linus_field, prod_tag)

            tmpdict_tstlg = self.build_prod_dict_tstlg(prod, all_prod_tags)
            tmpdict_tstlg[prod] = self.super_tlg(dict_linus[prod], qbox.dict_vault, prod_tag)
            dict_tstlg[prod] = tmpdict_tstlg[prod]

            refresh_linus = self.check_last_prod_tag(prod)
            linus_dict_csv_prod = self.get_prod_linus_csv(tmpdict_tstlg, linus_dict_csv)
            result_linus_prod = qbox.preview.filter_linus(linus_dict_csv_prod, dict_linus[prod], tmpdict_tstlg,
                                                          pcar3=True, refresh=refresh_linus)

            # save the linus result for ids in this product, need for additional filtering since only relevant ids are in linus_dict_csv_prod
            for strid in result_linus_prod.keys():
                result_linus[strid] = result_linus_prod[strid]
                linus_info[strid] = dict_linus[prod]

        return result_linus, linus_info, dict_tstlg


class _TidOperationBase(_TidQueryBase):
    """
    Base Class for TID operations (OR, AND, CONCAT, etc)
    """

    def __init__(self, query_obj1, query_obj2, *query_objn):
        """
        :param query_obj1: first query object
        :param query_obj2: second query object
        :param query_objn: N query objects (list)
        """
        self._lno = get_caller_lno()     # caller line number, also used as id
        q_all = [query_obj1, query_obj2] + list(query_objn)
        super().__init__("%s(%s)" % (self.__class__.__name__, ', '.join(str(x) for x in q_all)))

        self._check_type(query_obj1)
        self._check_type(query_obj2)
        for item in query_objn:
            self._check_type(item)

        self.query_obj1 = query_obj1
        self.query_obj2 = query_obj2
        self.query_objn = query_objn
        self._is_tid = self.query_obj1._is_tid     # Follow the type of first object

        # derive ordering
        self.ordertop = self._get_attr_from_1st(query_obj1, 'ordertop', [])
        self.orderbottom = self._get_attr_from_1st(query_obj1, 'orderbottom', [])

    def _get_attr_from_1st(self, obj, attr, default):
        """
        Recursively get attr from obj on first occurrence

        :param obj: Object to derive attr from
        :param attr: attribute name
        :param default: value if attribute is not found
        :return: attribute value
        """
        if isinstance(obj, _TidOperationBase):
            return obj._get_attr_from_1st(obj.query_obj1, attr, default)
        return getattr(obj, attr, default)


class OR(_TidOperationBase):
    """
    OR/union of two Query objects. Order is resorted
    example: OR([1, 2, 3], [2, 3, 4]) == [1, 2, 3, 4]
    """

    def result(self):
        """
        Returns the OR result

        :return: list
        """
        result = set(self.query_obj1.result()) | set(self.query_obj2.result())
        for item in self.query_objn:
            result |= set(item.result())
        self._tidlist = self._sort(result)
        return self._tidlist


class AND(_TidOperationBase):
    """
    AND/intersection of two Query objects. Order is resorted
    example: AND([1, 2, 3], [2, 3, 4]) == [2, 3]
    """

    def result(self):
        """
        Returns the AND result

        :return: list
        """
        result = set(self.query_obj1.result()) & set(self.query_obj2.result())
        for item in self.query_objn:
            result &= set(item.result())
        self._tidlist = self._sort(result)
        return self._tidlist


class CONCAT(_TidOperationBase):
    """
    CONCAT/ADD of two Query objects. Order is preserved
    example: CONCAT([1, 2, 3], [2, 3, 4]) == [1, 2, 3, 2, 3, 4]
    """

    def result(self):
        """
        Returns the CONCAT result

        :return: list
        """
        self._tidlist = self.query_obj1.result() + self.query_obj2.result()
        for item in self.query_objn:
            self._tidlist += item.result()
        return self._tidlist


class SUBTRACT(_TidOperationBase):
    """
    REMOVE/SUBTRACT of two Query objects. Order is resorted
    example: SUBTRACT([1, 2, 3], [2, 3, 4]) == [1]
    """

    def __init__(self, query_obj1, query_obj2):
        """
        :param query_obj1: first query object
        :param query_obj2: second query object
        """
        super().__init__(query_obj1, query_obj2)

    def result(self):
        """
        Returns the SUBTRACTED result

        :return: list
        """
        self._tidlist = self._sort(set(self.query_obj1.result()) - set(self.query_obj2.result()))
        return self._tidlist


qbox = QBox()     # singleton, equivalent of pcar


if __name__ == '__main__':  # pragma: no cover
    # obj = QueryTid(testtype='sbft_mlc', attributes='core')
    obj = QueryTid(linus_name='clk_cpu_lr_phase2')
    qbox.process()
    print(f'Result: {len(obj.result())}')
