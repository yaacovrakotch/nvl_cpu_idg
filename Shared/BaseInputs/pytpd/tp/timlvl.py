#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
timlvl module - Timings, Levels and Uservar (includes expression parser)

TimingsSequences.tim (one only) ===================================
Timing A {
   <some text>
}

BaseTiming.tcg or Module.tcg ======================================
SpecificationSet B (D) {
   <type> <var> = <value>
}
TestConditionGroup E {
   SpecificationSet = B
   Timing = A;
}
TestCondition F {
   TestConditionGroup  = E
   Selector = D
}

Usage =================================================
timings = "(BASE|Module)::F"

specset = {B_specset: {'_SELECTOR': ['D']
                        <var>: <value>}

tcg = {E_tcg: (B_specset, A_timing)}
tc_tmp    = {F_tc:  (E_tcg,     D_selector)}
tc_final  = {F_tc:  {'Timing':           A_timing,
                     'SpecificationSet': B_specset,
                     'Selector':         D_selector,
                     'TCG':              E_tcg_name,
                     'Inherit':          A_timing}}
"""

from os.path import exists, basename, dirname, isdir
from gadget.errors import ErrorInput, ErrorCockpit, ErrorUser
from gadget.pylog import log
from gadget.dictmore import keys_atlevel
from gadget.tputil import remove_ip, Units, OtplFile
from gadget.gizmo import Elapsed, count_iter
from gadget.files import File, check_and_del, tempname
from gadget.errors import ErrorCockpit, ErrorInput, ErrorUser, confirm
from collections import OrderedDict, ChainMap
from pprint import pprint
import re
import math


SEP = '_ZQ_'         # '.' replacement separator. If this is not good enough, use _ZQ_
SEPMOD = '_ZQZ_'     # separator for module var. If this is not good qnough, use _ZQZ_


class ErrorTOS(ErrorUser):
    """TOS-specific error raised during expression evaluation or rule processing."""

    pass


class EvalFuncs:
    """Eval related funcs"""

    @staticmethod
    def _toInteger(x):
        """Convert a value or list of values to integer.

        :param x: Value or list of values to convert
        :type x: int, float, str, or list
        :return: Converted integer or list of integers
        :rtype: int or list[int]
        """
        if isinstance(x, list):
            return [int(y) for y in x]
        else:
            return int(x)

    @staticmethod
    def _toDouble(x):
        """Convert a value or list of values to float (double).

        :param x: Value or list of values to convert
        :type x: int, float, str, or list
        :return: Converted float or list of floats
        :rtype: float or list[float]
        """
        if isinstance(x, list):
            return [float(y) for y in x]
        else:
            return float(x)

    @staticmethod
    def _toString(x):
        """Convert a value or list of values to string.

        :param x: Value or list of values to convert
        :type x: int, float, str, or list
        :return: Converted string or list of strings
        :rtype: str or list[str]
        """
        if isinstance(x, list):
            return [str(y) for y in x]
        else:
            return str(x)

    @staticmethod
    def raise_(msg):
        """Raise an ErrorTOS exception with the given message.

        :param msg: Error message describing the failure
        :type msg: str
        :raises ErrorTOS: Always raised with the provided message
        """
        raise ErrorTOS(msg, 'Debug and Fix based on the message above.')

    @staticmethod
    def rule2py(args, var):
        """
        Convert tos rule to python lambda

        From: rule = [expr0, expr1, expr2]
        To:   lambda a0, a1, a2: (a0 if expr0 else (a1 if expr1 else ...))

        :param args: list of expressions from TOS rules. These are already evaluated to either True or False.
        :param var: Name of the rule
        :return: string (python lambda expression)
        """
        result = 'lambda %s:' % ', '.join(f'a{idx}' for idx in range(len(args)))
        for idx, expr in enumerate(args):
            if idx != len(args) - 1:
                result = f'{result} (a{idx} if ({expr}) else'
            else:
                # last
                result = f'{result} (a{idx} if {expr} else EvalFuncs.raise_("{var} outcome conditions are all False"))'

        result = '%s%s' % (result, ')'.join('' for _ in args))
        return result


class TOSVar:
    """Wrapper for TOS variable values supporting string, float, and list types with concatenation."""

    def __init__(self, value):
        """Initialize TOSVar with a value, detecting its type.

        :param value: The value to wrap (string, float, list, or another TOSVar)
        :type value: str, float, list, or TOSVar
        :raises TypeError: If value type is not supported
        """
        if isinstance(value, TOSVar):
            value = value.value
        if isinstance(value, list):
            self.mytype = 'L'
        elif isinstance(value, str):
            self.mytype = 'S'
        elif isinstance(value, float):
            self.mytype = 'F'
        else:
            raise TypeError(f"Invalid type for {value}")
        self.value = value

    def __add__(self, other):
        """Concatenate two TOSVar values, supporting string-list cross-type operations.

        :param other: The other TOSVar to concatenate
        :type other: TOSVar
        :return: New TOSVar with concatenated result
        :rtype: TOSVar
        :raises TypeError: If types are incompatible for concatenation
        """
        if self.mytype != 'L':
            if other.mytype == 'S' or other.mytype == 'F':
                return TOSVar(f'{self.value}{other.value}')
            elif other.mytype == 'L':
                return TOSVar([f'{self.value}{x}' for x in other.value])
            else:
                raise TypeError("oops, type not supported")
        else:
            if other.mytype == 'S' or other.mytype == 'F':
                return TOSVar([f'{x}{other.value}' for x in self.value])
            elif other.mytype == 'L':
                # list + list
                if len(self.value) != len(other.value):
                    raise TypeError(f"Cannot add lists of different lengths: {self.value} and {other.value}")
                return TOSVar([f'{self.value[idx]}{other.value[idx]}' for idx in range(len(self.value))])
            else:
                raise TypeError("oops, type not supported")


class ExprParser:
    """OTPL expression parser/tokenizer, to convert to python expression"""

    # The following are the token types
    WORD = 'W'
    QUOTE = 'Q'
    OP = 'O'
    PAREN = 'P'
    COMMA = 'C'
    EXPR = 'E'

    # counter for to_py() calls
    ctr = [0]

    # Set of ip domains: IP domains are currently ignored in pytpd. This is cumulative as it's a class method.
    # Two or more TestProgram objects is ok as IP domains dont change much
    IP_DOMAIN = {'__shared__'}        # Populated set_ip_domain(), called from usrv's set_data

    # Performance/benchmark using RPL: 10120 count, 0.315 Secs. This is from Usrv.evaluate(), which includes eval()

    @classmethod
    def _tokenize(cls, expr):
        r"""
        Parse/Tokenize expr
        Parses a string expression into "atomic" elements
        Atomic elements: WORD (\w\.), QUOTE, PAREN, COMMA, EXPR, OP (everything else)
        a) expression inside parenthesis are EXPR
        b) expression inside a function args are EXPR, unless single element
        EXPR must be recursively processed later.

        :param expr: string
        :return: (list_tokenized, list_type)
        """
        tokens = []     # token result
        t_type = []     # type of token

        counter = 0     # parenthesis counter
        inner = []
        inside_func = False
        inside_expr = False
        linesplit = cls._line_split(expr)
        maxlen = len(linesplit) - 1
        for idx, item in enumerate(linesplit):     # split according to quote, word or non-word

            # process open and close paren first
            if item == ')' or item == ']':
                counter -= 1
                assert counter >= 0, f'Mismatched parenthesis: {expr}'
            if item == '(' or item == '[':
                counter += 1

            if inside_expr:
                if counter == 0:
                    # done with this expression
                    tokens.append(''.join(inner))
                    t_type.append(cls.EXPR)
                    inside_expr = False
                    inner = []
                else:
                    inner.append(item)
                continue

            if inside_func:
                if (counter == 1 and item == ',') or (counter == 0 and item == ')'):
                    if len(inner) == 1:
                        tokens.append(inner[0])
                        t_type.append(cls._id_type(inner[0], expr))
                    else:
                        tokens.append(''.join(inner))
                        t_type.append(cls.EXPR)
                    inner = []
                    if item == ')':
                        inside_func = False
                else:
                    inner.append(item)
                    continue

            # func or expression?
            if item == '(' and counter == 1:
                # Is this a function?
                if idx > 0 and linesplit[idx - 1][0].isalnum():
                    inside_func = True
                else:
                    # it is not a function, thus, put it in it's own expression
                    inside_expr = True
                    continue

            # hack: the scientific number expression
            if (item.endswith('e') and (item.startswith(('.', '-')) or item[0].isdigit()) and
                    idx < (maxlen - 1) and
                    linesplit[idx + 1] in ('-', '+') and
                    linesplit[idx + 2][0].isdigit()):
                tokens.append(f'{item}{linesplit[idx + 1]}{linesplit[idx + 2]}')
                t_type.append(cls.WORD)
                linesplit[idx + 1] = ''
                linesplit[idx + 2] = ''
                continue

            # hack: negative number
            if (item.endswith('-') and
                    idx < maxlen and
                    (linesplit[idx + 1][0].startswith('.') or linesplit[idx + 1][0].isdigit())):
                item = item[:-1]
                linesplit[idx] = item
                linesplit[idx + 1] = f'-{linesplit[idx + 1]}'

            # hack: : and ? must be it's own token because of ternary, except ::
            if item.startswith((':', '?')) and len(item) > 1 and (not item.startswith('::')):
                tokens.extend([item[0], item[1:]])
                t_type.extend([cls.OP, cls.OP])
                continue

            if item == '':
                continue   # This happens for numeric expression

            # The rest of the tokens
            tokens.append(item)
            t_type.append(cls._id_type(item, expr))

        # Do some checks
        assert counter == 0, f'Mismatched parenthesis: {expr}'
        assert not inside_func, f'Cockpit error: inside_func is True: {expr}'
        assert not inside_expr, f'Cockpit error: inside_expr is True: {expr}'
        assert len(tokens) == len(t_type), f'Cockpit: length of token vs type is mismatched: {len(tokens)} != {len(t_type)}'
        assert not inner, f'Cockpit error: inner variable is not empty: {inner}, {expr}'

        return tokens, t_type

    @classmethod
    def _id_type(cls, item, expr):
        """
        Return the type of item
        :param item: string
        :param expr: full expr
        :return: type
        """
        if item.startswith(('"', "'")):
            return cls.QUOTE
        elif item[-1].isalnum() or item[-1] == '_':
            return cls.WORD
        elif item == ',':
            return cls.COMMA
        elif item in ('(', ')'):
            return cls.PAREN

        assert not item.isspace(), f'Cockpit error: item is space. This should not happen. Pls debug and add in unittests: {expr}'
        return cls.OP

    @staticmethod
    def _line_split(text, _r=re.compile(r'[^"\'\s\w\.\(\)\[\],]+|,|\(|\)|\[|\]|[\w\.]+|""|\'\'|".+?"|\'.+?\'')) -> list:
        """
        Returns a split of text based on: quotes, (), comma, word, non-word
        """
        result = _r.findall(text)
        final = []

        # for some reason TOS accepts "word. word" - srf testprogram
        skip = False
        for idx in range(len(result)):
            if idx < len(result) - 1 and result[idx + 1][0].isalpha() and result[idx].endswith('.'):
                final.append(f'{result[idx]}{result[idx + 1]}')
                skip = True
            elif idx < len(result) - 1 and result[idx + 1][0] == '.' and result[idx][-1].isalnum():
                final.append(f'{result[idx]}{result[idx + 1]}')
                skip = True
            else:
                if skip:
                    skip = False
                    continue
                final.append(result[idx])

        return final

    @classmethod
    def _ternary2py(cls, elist, tlist):
        """
        Convert ternary expression to python
        From: a ? b : c
        To:   b if a else c
        """
        result = elist
        r_type = tlist
        if '?' in result and ':' in result:
            idx_q = result.index('?')   # first occurrence
            idx_c = result.index(':')   # first occurrence
            expr_a = result[:idx_q]
            type_a = r_type[:idx_q]
            expr_b = result[idx_q + 1:idx_c]
            type_b = r_type[idx_q + 1:idx_c]
            expr_c = result[idx_c + 1:]

            # convert last element into an expression, since it can have another ternary in there
            result = expr_b + ['if'] + expr_a + ['else'] + [''.join(expr_c)]
            r_type = type_b + [cls.OP] + type_a + [cls.OP] + [cls.EXPR]

        return result, r_type

    @classmethod
    def _regex2py(cls, elist, tlist):
        """
        Convert TOS ~= to python
        From: p a ~= b c
        To:   p re.search(b, a) c
        """
        result = elist
        r_type = tlist
        while '~=' in result:
            idx = result.index('~=')
            expr_p = [] if idx <= 1 else result[:idx - 1]
            type_p = [] if idx <= 1 else r_type[:idx - 1]
            e_expr_a = result[idx - 1]
            e_type_a = r_type[idx - 1]
            e_expr_b = result[idx + 1]
            e_type_b = r_type[idx + 1]
            expr_c = [] if idx + 2 == len(result) else result[idx + 2:]
            type_c = [] if idx + 2 == len(result) else r_type[idx + 2:]
            result = expr_p + ['bool(re.search', '(', e_expr_b, ',', e_expr_a, '))'] + expr_c
            r_type = type_p + [cls.OP, cls.PAREN, e_type_b, cls.COMMA, e_type_a, cls.PAREN] + type_c

        assert len(result) == len(r_type)
        return result, r_type

    @classmethod
    def _removedot(cls, elist, tlist):      # template to use for future routines
        """
        Replace the dot and remove scoping so that python evaluate will work

        :param elist: list of expressions
        :param tlist: list of expression types
        :return: None
        """
        maxlen = len(elist) - 1
        result = []
        r_type = []
        for idx, item in enumerate(elist):

            if tlist[idx] == 'SKIP':
                continue

            # convert dot to underscore
            if tlist[idx] == cls.WORD:
                if item[0].isalpha() or item[0] == '_':
                    elist[idx] = item.replace('_UserVars.', '').replace('.', SEP)

            # scoping
            if idx < (maxlen - 1) and elist[idx + 1] == '::' and tlist[idx] == cls.WORD and tlist[idx + 2] == cls.WORD:
                # remove ip_scoping
                if elist[idx] in cls.IP_DOMAIN:
                    tlist[idx + 1] = 'SKIP'    # skip next element
                    continue                   # skip this element

                # combine normal module scope
                varname = f'{elist[idx]}{SEPMOD}{elist[idx + 2]}'.replace('.', SEP)
                result.append(varname)
                r_type.append(tlist[idx])
                tlist[idx + 1] = 'SKIP'    # skip next element
                tlist[idx + 2] = 'SKIP'    # skip the other element
                continue                   # skip this element

            result.append(elist[idx])
            r_type.append(tlist[idx])

        return result, r_type

    @classmethod
    def _set_mtt(cls, elist, tlist):
        """
        Mtt expression: wrap WORD or expr with _MTT()

        :param elist: list of expressions
        :param tlist: list of expression types
        :return: None
        """
        maxlen = len(elist) - 1
        for idx, item in enumerate(elist):

            if tlist[idx] == cls.WORD:
                if idx < (maxlen - 1) and elist[idx + 1] == '(':
                    continue   # Do nothing for func names
                elist[idx] = f'_MTT({elist[idx]})'

        return elist, tlist

    @classmethod
    def split(cls, expr, char=','):
        """
        Split expr according to char

        :param expr: string
        :param char: split char
        :return: list
        """
        final = []
        counter = 0
        result, _ = cls._tokenize(expr)
        tmp = []
        for item in result:
            # process paren first
            if item == ')':
                counter -= 1
                assert counter >= 0, f'Mismatched parenthesis: {expr}'
            if item == '(':
                counter += 1

            if counter == 0 and item == char:
                final.append(''.join(tmp))
                tmp = []
                continue

            tmp.append(item)

        final.append(''.join(tmp))
        assert counter == 0, f'Mismatched parenthesis: {expr}'
        return final

    TOS2PY = {'||': 'or',
              '&&': 'and',
              '^': '**',
              '!': 'not',
              '&&!': 'and not',
              '||!': 'or not'}

    @classmethod
    def to_mtt(cls, expr, start=True):
        """
        Convert TOS expr to TOS mtt. Recursive function.
        Reason: mtt expressions has mix of string and arrays. For pytpd perspective, just get the first element.

        :param expr: string: TOS expression
        :param start: True for initial run and False for "recursive runs"
        :return: string: python expression
        """

        # one-time stuff
        if start:
            # corner case - empty expr
            if expr == '':
                return expr    # as-is

            # Convert backslashed quote so it remains a quote
            if r'\\' in expr:
                expr = expr.replace(r'\\', '~!%')
            if r'\"' in expr:
                expr = expr.replace(r'\"', '~`%')

        # tokenize first
        tokens = cls._tokenize(expr)          # tokens here are atomic level

        # Start of convert for this expression
        tokens = cls._set_mtt(*tokens)

        result, r_type = tokens

        # last - recursively do all expressions
        for idx in range(len(result)):
            if r_type[idx] == cls.EXPR:
                result[idx] = cls.to_mtt(result[idx], start=False)       # call itself for each expr

        final = '(%s)' % ' '.join(result)
        if start and '~`%' in final:
            final = final.replace('~`%', r'\"')
        if start and '~!%' in final:
            final = final.replace('~!%', r'\\')
        return final

    @classmethod
    def to_py(cls, expr, start=True):
        """
        Convert TOS expr to python. Recursive function.

        :param expr: string: TOS expression
        :param start: True for initial run and False for "recursive runs"
        :return: string: python expression
        """
        cls.ctr[0] += 1

        # one-time stuff
        if start:
            # corner case - empty expr
            if expr == '':
                return '""'

            # Convert backslashed quote so it remains a quote
            if r'\\' in expr:
                expr = expr.replace(r'\\', '~!%')
            if r'\"' in expr:
                expr = expr.replace(r'\"', '~`%')

        # tokenize first
        tokens = cls._tokenize(expr)          # tokens here are atomic level

        # Start of convert for this expression
        tokens = cls._removedot(*tokens)
        tokens = cls._ternary2py(*tokens)
        tokens = cls._regex2py(*tokens)

        result, r_type = tokens

        # Math expressions
        result = [Units.math_units(x) for x in result]

        # Simple replace
        to_rep = set(result) & cls.TOS2PY.keys()
        for item in to_rep:
            while item in result:
                idx = result.index(item)
                result[idx] = cls.TOS2PY[item]     # replacement

        # last - recursively do all expressions
        for idx in range(len(result)):
            if r_type[idx] == cls.EXPR:
                result[idx] = cls.to_py(result[idx], start=False)       # call itself for each expr

        final = '(%s)' % ' '.join(result)
        if start and '~`%' in final:
            final = final.replace('~`%', r'\"')
        if start and '~!%' in final:
            final = final.replace('~!%', r'\\')
        return final

    @classmethod
    def set_ip_domain(cls, stplfile):
        """Populates IP_DOMAIN given stplfile"""
        for _, line in OtplFile(stplfile).readline():
            if line.startswith('IPName'):
                elems = line.split()
                cls.IP_DOMAIN.add(elems[1])


class BaseTimingLevel:
    """Common routines for both Timing and Levels"""

    def __init__(self, tpobj):
        """Initialize base timing/level data structures.

        :param tpobj: TestProgram object providing TP context
        :type tpobj: tp.testprogram.TestProgram
        """
        # {'BASE::F_tc':  {'Timing':           '__main__::A_timing',
        #                  'SpecificationSet': 'BASE::B_specset',
        #                  'Selector':         'D_selector',
        #                  'TCG':              'E_tcg_name),
        #                  'Inherit':          'BASE::A_timing'}
        self._tc = None
        self._specset = None         # {'BASE::B_specset': {'_SELECTOR': ['D'], <var>: <value>}}
        self._thermalcontrol = None  # {'BASE::name}: [lines]}
        self._ss_eval = None         # {'BASE::B_specset': {selector: {<var>: <value>}}}
        self._ss_order = None        # {'BASE::B_specset': [list of vars]}
        self._tc_concat = None       # large concatenated string
        self.tpobj = tpobj

    def evaluate(self):
        """
        Evaluate all specsets
        """
        # Performance: as of 5/25 non-profile
        # -i- Completed equations evaluations. selectors=155 params=54228 Elapsed=0.616 Secs
        # CMD> main/tp_info.py /intel/hdmxprogs/tgl/TGLXXXXRXH35H00S025/TPL/EnvironmentFile.env -tim_list p_bclkper_spec

        sw = Elapsed()
        log.info(f'-i- Starting evaluation of {len(self._specset)} SpecificationSets')

        # Evaluate each selector
        self._ss_eval = {}
        for ss in self._specset:
            testplan = self.tpobj.testplan_base
            if '::' in ss:
                testplan = ss.split('::')[-2]
            self._ss_eval[ss] = {}
            for selector in self._specset[ss]['_SELECTOR']:
                self._ss_eval[ss][selector] = {}
                self._evaluate_selector(ss,
                                        selector,
                                        self._ss_eval[ss][selector],
                                        self.tpobj.usrv.uflat,
                                        usrv_local=self.tpobj.usrv.userv_local(testplan))

        log.info('-i- Completed %s equations evaluations. selectors=%s params=%s Elapsed=%s'
                 '' % (self.__class__.__name__,
                       count_iter(keys_atlevel(self._ss_eval, 1)),
                       count_iter(keys_atlevel(self._ss_eval, 2)),
                       sw))

    def _evaluate_selector(self, ss, selector, result, usrv_nd, usrv_local={}):
        """
        Evaluate one selector

        :param ss: specificationset
        :param selector: selector
        :param result: dictionary. Results are updated here
        :param usrv_nd: dictionary: uservar with no dot
        :param usrv_local: dictionary: local variables
        :return: None
        """
        index = self._specset[ss]['_SELECTOR'].index(selector)

        # expand first, convert non-expression into number
        data = {}  # values that is string
        fin = {}   # finished values
        for item, val in self._specset[ss].items():
            if item == '_SELECTOR':
                continue

            if isinstance(val, list):
                if index >= len(val):
                    raise ErrorInput(f'Error on [{item}] for [{ss}] selector={selector}, index={index} is not defined',
                                     f'Fix: {item}={val}')
                else:
                    value = val[index]
            else:
                value = val

            # convert simple values.
            res = Units.to_number(value)
            if res is None:
                data[item] = value
            else:
                fin[item] = res

        # do some processing of data
        for var, orig in data.items():
            # convert to python
            data[var] = ExprParser.to_py(orig)

        # Evaluate all variables in order
        for var in self._ss_order[ss]:
            if var not in data:
                continue

            val = data[var]
            try:
                fin[var] = eval(val, usrv_nd, ChainMap(fin, usrv_local))
            except Exception as e:
                self.tpobj.usrv.print_usrv()
                msg = (f'   original {var} = {self._specset[ss][var]}\n'
                       f'   python   {var} = {val}\n'
                       f'   Error: {e}')
                raise ErrorInput("Failed to evaluate for SpecificationSet=%s selector=%s\n%s" % (ss, selector, msg),
                                 f"Check .tcg file for [{var}]. Is the expression valid?")

        # Do check
        orig_ref = set(self._specset[ss])
        orig_ref.discard('_SELECTOR')
        assert orig_ref == fin.keys(), f"{len(orig_ref)}!={len(fin.keys())}: Logic error! Some variable is missing or extra. Pls debug."

        result.update(fin)

    def _read_tcg_file(self, fname, tcgtype):
        """
        Populate self._tc and self.specset

        :param fname: tcg file
        :param tcgtype: 'Timing' or 'Level'
        :return: None
        """
        ss_name = None
        tcg_name = None
        tc_name = None
        thermalcontrol = None
        tc_data = {}
        tcg_data = {}
        ss_data = {}
        ss_order = {}
        ss_inherit = {}
        r_ss = re.compile(r'^SpecificationSet\s+(\w+)\s*\(([^\)]+)\)')
        r_inherit = re.compile(r'Inherits\s+(\S+)')
        r_keyval1 = re.compile(r'^(\w+)\s*=\s*(\S+)\s*;')
        r_keyval2 = re.compile(r'^\w+\s+(\w+)\s*=\s*(\S.*);')
        data = None
        order = None
        i_key = None
        nest = 0
        scope = self.tpobj.get_scope(fname, "BASE")

        for lno, line in OtplFile(fname).readline():

            # Ignore these
            if line.startswith(('Version', 'Import')):
                continue

            if line == '{':
                nest += 1
                continue

            # closure
            if line == '}':
                nest -= 1
                assert nest >= 0, f"Error: Unbalanced close bracket detected line#{lno} of {fname}"

                if thermalcontrol:
                    if nest == 0:
                        self._thermalcontrol[thermalcontrol] = data
                        data = None
                        thermalcontrol = None
                    else:
                        data.append(line)
                    continue

                assert nest == 0, f'Error: close bracket unexpected in line#{lno} of {fname}'
                if ss_name:
                    key = f'{scope}::{ss_name}'
                    ss_data[key] = data
                    ss_order[key] = order
                    ss_inherit[key] = i_key
                    ss_name = None

                if tcg_name:
                    tcg_data[tcg_name] = data
                    tcg_name = None

                    # Check if this is Level or Timing
                    for item in tcg_data:
                        if tcgtype not in tcg_data[item]:
                            return     # Do nothing for this file

                if tc_name:
                    tc_data[tc_name] = data
                    tc_name = None

                data = None
                order = None
                i_key = None
                continue

            # everything inside thermalcontrol
            if thermalcontrol:
                data.append(line)
                continue

            # (\w+) = (\w+)
            res = r_keyval1.search(line)
            if res:
                data[res.group(1)] = res.group(2)
                continue

            # \w+ (\w+) = (\w+)
            res = r_keyval2.search(line)
            if res:
                val = res.group(2)
                split_val = ExprParser.split(val)
                data[res.group(1)] = split_val[0] if len(split_val) == 1 else split_val
                if res.group(1) not in order:     # add once, because of inherit
                    order.append(res.group(1))
                _ = None    # coverage only
                continue

            # Block headers
            res = r_ss.search(line)  # SpecificationSet
            if res:
                ss_name = res.group(1)
                selector = res.group(2)
                data = {'_SELECTOR': [x.strip() for x in selector.split(',')]}
                order = []

                # Do the inherit
                i_res = r_inherit.search(line)
                if i_res:
                    i_key = i_res.group(1).replace('__main__', 'BASE')
                    if i_key in self._specset:
                        for k, v in self._specset[i_key].items():
                            if k == '_SELECTOR':
                                continue
                            data[k] = v
                        order = list(self._ss_order[i_key])
                _ = None    # coverage only
                continue

            if line.startswith('TestConditionGroup '):
                tcg_name = line.split()[1]
                data = {}
                continue

            if line.startswith('TestCondition '):
                tc_name = line.split()[1]
                data = {}
                continue

            if line.startswith('ThermalControl '):
                thermalcontrol = f'{scope}::{line.split()[1]}'
                data = []
                continue

            raise ErrorCockpit(f"Unknown tcg line: [{line}] on {fname}")

        self._specset.update(ss_data)
        self._ss_order.update(ss_order)

        # consolidate
        for item, value in tc_data.items():
            # print("item=%s tcg=%s selector=%r" % (item, value['TestConditionGroup'], value['Selector']))
            # Dumper(tcg_data[tcg])
            tcg = value['TestConditionGroup']
            ss = '%s::%s' % (scope, tcg_data[tcg]['SpecificationSet'])
            data = {tcgtype: tcg_data[tcg][tcgtype],
                    'SpecificationSet': ss,
                    'Selector': value['Selector'],
                    'TCG': tcg,
                    'Inherit': ss_inherit.get(ss)}
            self._tc['%s::%s' % (scope, item)] = data

    def iter_tc(self):
        """
        Iterate on all testconditions
        :return: testcondition
        """
        self.set_data()
        for tc in self._tc:
            yield tc

    def get_tc_dict(self):
        """
        Returns the tc dictionary
        :return: dict
        """
        self.set_data()
        return self._tc

    def get_tc_value(self, testcondition, param):
        """
        Return specific param given testcondition

        :param testcondition: testcondition
        :param param: specific parameter
        :return: value of specific param
        """
        self.set_data()

        assert testcondition in self._tc, f'input [{testcondition}] not found in any TestCondition'
        ss = self._tc[testcondition]['SpecificationSet']
        selector = self._tc[testcondition]['Selector']

        assert param in self._ss_eval[ss][selector], f'param [{param}] not found in [{ss}] SpecificationSet'
        return self._ss_eval[ss][selector][param]

    def set_param(self, testcondition, param, val):
        """
        Set param value. Iterator

        Called by glx express (or future testprogram setters)

        :param testcondition: testcondition
        :param param: variable name
        :param val: value
        :return old value or None if no change
        """
        # parse input first
        testcondition = remove_ip(testcondition)
        if '::' not in testcondition:
            testcondition = 'BASE::' + testcondition     # scope is always required

        # consider regex
        if '*' in testcondition:
            if not self._tc_concat:
                self._tc_concat = '\n'.join(self._tc)

            for found in re.findall(testcondition.replace('*', '.*'), self._tc_concat, re.MULTILINE):
                if found in self._tc:
                    for item in self.set_param(found, param, val):
                        yield item

            return   # Done

        orig = self.get_tc_param(testcondition, param)
        if orig == val:
            yield None, testcondition
            return

        # at this point, need to set the value
        ss = self._tc[testcondition]['SpecificationSet']
        param_value = self._specset[ss][param]
        if isinstance(param_value, list):
            selector = self._tc[testcondition]['Selector']
            index = self._specset[ss]['_SELECTOR'].index(selector)
            param_value[index] = val           # This is string. Evaluated value is in _ss_eval
        else:
            self._specset[ss][param] = val     # Note: It will not convert to list. It will change it.

        yield orig, testcondition

    def get_tc_param(self, testcondition, param):
        """
        Return specific param given testcondition

        :param testcondition: testcondition
        :param param: specific parameter
        :return: value of specific param
        """
        self.set_data()
        assert testcondition in self._tc, f"input [{testcondition}] not found in any TestCondition"

        ss = self._tc[testcondition]['SpecificationSet']
        assert param in self._specset[ss], f"param [{param}] not found in [{ss}] SpecificationSet"

        param_value = self._specset[ss][param]
        if isinstance(param_value, list):
            selector = self._tc[testcondition]['Selector']
            index = self._specset[ss]['_SELECTOR'].index(selector)
            return param_value[index]
        else:
            return param_value

    def iter_params(self, testcondition, isvalue=False):
        """
        Iterate all params, in specific order

        :param testcondition: string
        :param isvalue: Set to True to return evaluated value
        :return: param, value
        :rtype: (str, str)
        """
        self.set_data()
        assert testcondition in self._tc, f"input [{testcondition}] not found in any TestCondition"
        ss = self._tc[testcondition]['SpecificationSet']
        for param in self._ss_order[ss]:
            if isvalue:
                yield param, self.get_tc_value(testcondition, param)
            else:
                yield param, self.get_tc_param(testcondition, param)


class Timing(BaseTimingLevel):
    """
    storage of tim data
    parser of tim and tcg files
    Design: one Timing() instance for entire TP
    """

    def __init__(self, tpobj):
        """
        :param tpobj: path to TP env file
        :type tpobj: tp.testprogram.TestProgram
        """
        self._timing = None     # {'__main__::A_timing': {domain: {pin: {key: value }}}}
        super().__init__(tpobj)

    def set_data(self, evaluate=True):
        """
        Populate the timing data structures
        """
        if self._timing:
            return    # Do nothing, since it is already populated.

        self._timing = {}
        self._specset = {}
        self._tc = {}
        self._ss_order = {}
        self._thermalcontrol = {}

        for ff in self.tpobj.get_import_files('tim'):
            self._read_tim_file(ff)

        for ff in self.tpobj.get_import_files('tcg'):
            self._read_tcg_file(ff, 'Timing')

        if evaluate:
            self.tpobj.usrv.set_data()
            self.evaluate()

    def _read_tim_file(self, fname):
        """
        Populate self._timing
        :param fname: timing file
        :return: None
        """
        scope = self.tpobj.get_scope(fname, "__main__")
        name = None
        domain = None
        pin = None
        r_val = re.compile(r'^(\w+)\s*=\s*([^;]+);')

        # self._timing = {timing: {domain: {pin: {key: value }}}}
        for lno, line in OtplFile(fname).readline():
            if line.startswith(('{', 'Version', 'Import')):
                continue

            # closure
            if line == '}':
                if pin:
                    pin = None
                    continue

                if domain:
                    domain = None
                    continue

                if name:
                    name = None
                    continue

                raise ErrorInput(f"Mismatched closed parenthesis in line {lno} at {fname}")

            if line.startswith('Timing '):
                assert not name, f"Timing {name} is already defined in line#{lno} at {fname}"
                name = f'{scope}::{line.split()[1]}'
                assert name not in self._timing, f"Name {name} is defined twice, 2nd occurrence in line#{lno} at {fname}"
                self._timing[name] = {}
                continue

            if line.startswith('Domain '):
                assert name, f"No name found but Domain is set in line#{lno} at {fname}"
                domain = line.split()[1]
                assert domain not in self._timing[name], f"Domain {domain} is defined twice, 2nd occurrence in line#{lno} at {fname}"
                self._timing[name][domain] = {}
                continue

            if len(line.split()) == 1 and name and domain and not pin:
                pin = line
                self._timing[name][domain][pin] = {}
                continue

            if name and domain and pin:
                res = r_val.search(line)
                if res:
                    self._timing[name][domain][pin][res.group(1)] = res.group(2)
                    continue

            raise ErrorCockpit(f"Unknown tim line: [{line}] at line#{lno} at {fname}")

    def get_period_param(self, testcondition) -> dict:
        """
        Return the period param value of this testcondition
        :param testcondition: testcondition
        :return: dict of period params (unique) and it's value
        """
        self.set_data()
        assert testcondition in self._tc, 'input [%s] not found in any TestCondition' % testcondition

        tim = self._tc[testcondition]['Timing']
        result = {}
        for dom in self._timing[tim]:
            param = self._timing[tim][dom]['PeriodTable']['Period']
            result[param] = self.get_tc_value(testcondition, param)
        return result

    def get_timings(self) -> set:
        """
        :return: set of all timings
        """
        self.set_data()
        return self._timing.keys()

    def get_pingrps(self, timname) -> dict:
        """
        Return dict of pingroups given timing across all domains
        :param timname: timing name
        :return: dict {pingrp: domain}
        """
        self.set_data()
        assert timname in self._timing, f'[{timname}] is not a valid timing name.'
        result = {}
        for dom in self._timing[timname]:
            for pingrp in self._timing[timname][dom]:
                assert pingrp not in result, f'[{pingrp}] is defined twice in {timname}'
                if pingrp == 'PeriodTable':
                    continue    # ignore
                result[pingrp] = dom
        return result


class Levels(BaseTimingLevel):
    """
    storage of lvl data
    parser of lvl and tcg files
    Design: one Levels() instance for entire TP
    """

    def __init__(self, tpobj):
        """Initialize Levels with level-specific data structures.

        :param tpobj: TestProgram object providing TP context
        :type tpobj: tp.testprogram.TestProgram
        """
        self._levels = None     # {'__main__::A_level': {pin: {key: value}}}
        super().__init__(tpobj)

    def set_data(self, evaluate=True):
        """
        Populate the levels data structures
        """
        if self._levels:
            return    # Do nothing, since it is already populated.

        self._levels = {}
        self._specset = {}
        self._tc = {}
        self._ss_order = {}
        self._thermalcontrol = {}

        for ff in self.tpobj.get_import_files('lvl'):
            self._read_lvl(ff)

        for ff in self.tpobj.get_import_files('tcg'):
            self._read_tcg_file(ff, 'Level')

        if evaluate:
            self.tpobj.usrv.set_data()
            self.evaluate()

    def _read_lvl(self, fname):
        """
        Read one lvl file

        :param fname: full path to fname
        :return: None
        """
        name = None
        pinname = None
        data = None
        _unit = '|'.join(Units.UNITMAP)
        r_lvl = re.compile(r'^(DynamicGangControlTestCondition|Levels|LevelsTestCondition)\s+(\w+)$')
        r_pin = re.compile(r'^([\w:]+)$')
        r_kv = re.compile(r'^(\w+)\s*=\s*([^;]+);')
        scope = self.tpobj.get_scope(fname, "__main__")

        for lno, line in OtplFile(fname).readline():

            # Ignore these
            if line.startswith(('{', 'Version', 'Import', 'SequenceBreak')):   # startswith is 1.6s -vs- re.search is 3.0 for 4M matches
                continue

            # closure
            if line == '}':
                if pinname:
                    self._levels[name][pinname] = data
                    pinname = None
                    data = None
                    continue
                if name:
                    name = None
                    continue
                raise ErrorCockpit("Invalid line in line#%s of %s" % (lno, fname),
                                   "No pinname or levels name found. Pls check.")

            # ^(\w+)\s*=\s*([^;]+);
            res = r_kv.search(line)
            if res:
                assert name and pinname, "Error: Either pinname or levels name is not defined. line=%r" % line
                data[res.group(1)] = res.group(2)
                continue

            # ^(\w+)$
            if r_pin.search(line):
                assert name is not None, "Error: name is not initialized, line=%r" % line
                pinname = line
                data = {}
                continue

            # ^Levels\s+(\w+)
            res = r_lvl.search(line)
            if res:
                assert name is None, "Error: name [%s] is already initialized, line=%r!" % (name, line)
                name = '%s::%s' % (scope, res.group(2))
                self._levels[name] = {}
                continue

            raise ErrorCockpit("Unknown levels line in line#%s: [%s]" % (lno, line))

    def get_lvl_param(self, testcondition, display=False) -> dict:
        """
        Get params used for powersupplies, return value

        :param testcondition: TestCondition
        :param display: Set to True to display values
        :return: dict of level params used in powersupplies and it's value
        """
        self.set_data()
        assert testcondition in self._tc, f"input [{testcondition}] not found in any TestCondition"

        lvl = self._tc[testcondition]['Level']
        ss = self._tc[testcondition]['SpecificationSet']
        params = set()
        for pin in self._levels[lvl]:
            if 'VForce' in self._levels[lvl][pin]:
                val = self._levels[lvl][pin]['VForce']
                if val in self._specset[ss]:
                    if display:
                        print(f'pin=%-22s param=%-30s val=%0.3fV eqn=%s'
                              '' % (pin,
                                    val,
                                    self.get_tc_value(testcondition, val),
                                    self.get_tc_param(testcondition, val)))
                    params.add(val)

        return {x: self.get_tc_value(testcondition, x) for x in sorted(params)}

    def get_lvl_pin_val(self, testcondition, attrib) -> dict:
        """
        Get pinvalue of levels

        :param testcondition: TestCondition
        :param attrib: Which attribute: VForce, VIH, VIL, VOX, etc
        :return: dict {pin: (value_or_variable, value, eqn)}
        """
        self.set_data()
        assert testcondition in self._tc, f"input [{testcondition}] not found in any TestCondition"

        lvl = self._tc[testcondition]['Level']
        ss = self._tc[testcondition]['SpecificationSet']
        result = {}
        for pin in self._levels[lvl]:
            if attrib in self._levels[lvl][pin]:
                val = self._levels[lvl][pin][attrib]
                if val in self._specset[ss]:
                    result[pin] = (val, self.get_tc_value(testcondition, val), self.get_tc_param(testcondition, val))
                else:
                    result[pin] = (val, '', '')

        return result


class Usrv:
    """storage of usrv data"""

    def __init__(self, tpobj):
        """Initialize Usrv with uservar data structures.

        :param tpobj: TestProgram object providing TP context
        :type tpobj: tp.testprogram.TestProgram
        """
        self.tpobj = tpobj
        self.testplan_base = tpobj.testplan_base

        # used for eval: scoped
        self.uflat = None         # {'MODULE___NAME__var': value}

        # used for eval: non-scoped   (uflat and ulocal are equivalent)
        self.ulocal = None        # {module: {'NAME__var': value}}

        # raw userv values scalar (unevaluated)
        self._userv = None        # {module: {'NAME.var': value}}

        # raw userv values expression (unevaluated)
        self._userv_orig = None   # {module: {'NAME.var': (value, var_type)}

        # intermediate tosrules
        self._src = None          # {module: {'NAME.var': [bool, bool, bool]}}     # SelectorRuleCollection

        # raw/original tosrules
        self._src_orig = None     # {module: {'NAME.var': [expr, expr, '']}}       # SelectorRuleCollection

        # evaluated tosrules (both scoped and non-scoped)
        self._src_eval = {}       # {module: {'NAME__var': lambda}, 'MODULE___NAME__var': lambda}

        # cache for rules2py
        self._cache_rule = {}
        self._func_dict = {}      # Static funcs

    def clear_cache(self):
        """
        Clear the uservar dict (mainly because it can't be pickled)
        """
        self._src_eval = {}       # evaluated src
        self._cache_rule = {}
        self._func_dict = {}

    @classmethod
    def update_usrv(cls, usrv_path, usrv_name, usrv_value):
        """
        Modify any uservar in TP to a desied value.
        """
        # User Input param example below
        # usrv_path = 'Shared/BaseInputs/Common/Common_Files/common.usrv'
        # usrv_name = 'DIELET_INDICATOR'
        # usrv_value = 'CPU,GCD,HUB,PCD'
        # Check usrv path. Proceed only if these files exist

        if usrv_value is None:
            log.info(f'-i- Change to {usrv_name} is skipped due to no value')
            return 1

        confirm(exists(usrv_path), f'Error: {usrv_path} not exist.', 'This is required file')

        data = File(usrv_path).raw()
        updated_lines = []
        robj = re.compile(rf'\s+\b{usrv_name}\s*=\s*"([^"]*)";')
        for line in data:
            res = robj.search(line)
            if res:
                line = robj.sub(f' {usrv_name} = "{usrv_value}";', line)
            updated_lines.append(line)

        File(usrv_path).rewrite(''.join(updated_lines), f'Uservar {usrv_name} updated with value {usrv_value}.')

    @classmethod
    def derive_val_folder_name(cls, tpname, isval, ispart):
        """
        Convert the validation folder name with user input tpname
        :param tpname: TP name - 19 char
        :param isval: True for val folder, False for production
        :param ispart: True for partial TP folder, False for full TP
        TP name example below
        FULL:NVLS356A0H01B00S528
        VALL:NVLS3XXXXX01B0ASXXX
        """
        if tpname is None:
            return None

        if isval:
            folder_name = f'{tpname[:3]}XXXXXXX{tpname[10:16]}XXX'

        elif ispart:
            folder_name = f'{tpname[:3]}XXXXXXX{tpname[10:17]}XX'

        else:
            folder_name = f'{tpname[:3]}XXXX{tpname[7:]}'

        return folder_name

    def set_data(self):
        """
        Populate uservar data structures

        :return: None
        """
        self._init_func_dict()
        self._init_uflat()      # So that uflat is initialized after pickle
        self._init_src_eval()   # So that src_eval is initialized after pickle
        if self._userv:
            return

        ExprParser.set_ip_domain(self.tpobj.get_stpl())
        self._userv = {}
        self._userv_orig = OrderedDict()
        self._src = {}
        self._src_orig = OrderedDict()

        # Read the files
        for ff, val in self.tpobj.get_import_files('usrv', withmodule=True).items():
            self._read_usrv(ff, val[0])

        # Assign the user-specified values
        for k, v in self.tpobj.vars.items():
            self.set_var(k, v, 'initial set_data()', as_is=True)

        # Make sure None exist
        self._set_base_key(self._userv)
        self._set_base_key(self._userv_orig)
        self._set_base_key(self._src)
        self._set_base_key(self._src_orig)

        # Evaluate rule first, then usrv (Since rule is used in usrv)
        self.evaluate()

    def evaluate(self):
        """
        Assumption: values don't chnage in the middle of the flow, so we evaluate all at "init" time
        Strategy: "batch" evaluate. It would be slow if we evaluate as we need it.
        """
        # sw = Elapsed()

        self._init_uflat()

        # first pass - Do not error, let all evaluations take place
        self._evaluate_usrv(False)     # first pass
        self._evaluate_rule(False)
        self._evaluate_usrv(False)     # second pass, since there are TOS rules in some user vars
        self._evaluate_rule(False)

        # 3rd pass - final. Error out
        self._evaluate_usrv(True)
        self._evaluate_rule(True)

        # print(f'-i- Usrv evaluate: {ExprParser.ctr[0]} count, {sw}')
        # -i- Usrv evaluate: 7785 count, 27.914 Secs (new)
        # -i- Usrv evaluate: 6543 count, 1.766 Secs (prev)

    def _init_func_dict(self):
        """Populate func_dict"""
        # TODO: What's left: array and toString-two-argument
        self._func_dict = {'toInteger': EvalFuncs._toInteger,
                           'toDouble': EvalFuncs._toDouble,
                           'toString': EvalFuncs._toString,
                           'toBoolean': lambda x: bool(x),

                           # strings
                           'contains': lambda x, y: str(y) in str(x),
                           'startsWith': lambda x, y: str(x).startswith(str(y)),
                           'endsWith': lambda x, y: str(x).endswith(str(y)),
                           'toUpper': lambda x: str(x).upper(),

                           # math
                           'ln': math.log,
                           'exp': math.exp,
                           'log': math.log10,
                           'sqrt': math.sqrt,

                           # true/false combinations
                           'TRUE': True,
                           'true': True,
                           'FALSE': False,
                           'false': False,

                           # Others
                           're': re,             # needed for ~= operation
                           '_MTT': lambda x: x[0] if isinstance(x, list) else x,
                           'GetEnvironmentVariable': lambda x: self.tpobj.env.get_contents(x),
                           'TOSVar': TOSVar
                           }

    def _init_uflat(self):
        """
        Populates uflat and ulocal

        uflat and ulocal is:
            pickled
            acts as cache
            derived from _userv
            global var
            without funcs (tos rules are in src_eval)
            uflat is scoped (MODULE___<name>)
            ulocal is unscoped {MODULE: <name>}
            uflat and ulocal are matched
        """
        if self.uflat:
            return     # Do nothing, it is already initialized
        if not self._userv:
            return     # Do nothing, userv is not yet populated

        ulocal = {}
        res = {}

        # Add _userv, both scoped and unscoped
        for testplan in self._iter_testplan(self._userv, last=True):
            ulocal[testplan] = {}
            for var, val in self._userv[testplan].items():
                varnd = var.replace('.', SEP)
                res[f'{testplan}{SEPMOD}{varnd}'] = val
                res[varnd] = val                      # for evergreen, other module unscoped
                ulocal[testplan][varnd] = val

        self.uflat = res
        self.ulocal = ulocal

    def _init_src_eval(self):
        """Initialize _src_eval"""
        if self._src_eval:
            return    # Do nothing, it is already initialized
        if not self._src:
            return    # Do nothing, _src is not yet populated

        # evaluate tos rules, scoped and unscoped
        # This is only called by pickle, since _src_eval is evaluated under _evaluate_rule
        for testplan in self._iter_testplan(self._src, last=True):
            self._src_eval[testplan] = {}
            for var, args in self._src[testplan].items():
                varnd = var.replace('.', SEP)
                assert not (None in args), f'TosRule has unevaluated param: testplan={testplan}, var={var}, args={args}'

                ckey = f'{testplan}{SEPMOD}{var}'
                self._cache_rule[ckey] = (args, eval(EvalFuncs.rule2py(args, var)))     # cannot create testcase where this will error, without mocking :)
                self._src_eval[testplan][varnd] = self._cache_rule[ckey][1]
                self._src_eval[f'{testplan}{SEPMOD}{varnd}'] = self._src_eval[testplan][varnd]

    def _set_base_key(self, dd):
        """Make sure None key exist in dd"""
        if self.testplan_base not in dd:
            dd[self.testplan_base] = {}

    def _iter_testplan(self, dd, last=False):
        """Return the keys of dd, with None first"""
        if not last:
            if self.testplan_base in dd:
                yield self.testplan_base

        for key in sorted(dd):
            if key == self.testplan_base:
                continue
            yield key

        if last:
            if self.testplan_base in dd:
                yield self.testplan_base

    def _wrap_tosvar(self, expr):
        """
        Remove outer parentheses, split by '+', and wrap each element with TOSVar().
        """
        expr = expr.strip()

        while expr.startswith('(') and expr.endswith(')'):
            expr = expr[1:-1].strip()
        parts = [part.strip() for part in expr.split('+')]
        return ' + '.join([f'TOSVar({part})' for part in parts])

    def _evaluate_usrv(self, is_error):
        """
        Evaluate all uservars

        :param is_error: Set to True to error out
        :return: None
        """
        r_vtype = re.compile(r'(Array\s*<String>|Array\s*<Double>|Array\s*<Integer>)')
        for testplan in self._iter_testplan(self._userv):

            # evaluate all
            for var, (val, vtype) in self._userv_orig[testplan].items():
                varnd = var.replace('.', SEP)

                # create a local dict, with no scoping for local scope variables
                local = {}
                if '.' in var:
                    # ulocal
                    scope = f"{var.split('.')[0]}{SEP}"
                    local = {x.split(SEP)[1]: y for x, y in self.ulocal.get(testplan, {}).items() if x.startswith(scope)}

                # parse
                expr = ExprParser.to_py(val)

                # eval
                try:
                    result = eval(expr, self.uflat, self.userv_local(testplan, local))
                except Exception as e:
                    res = r_vtype.search(vtype)
                    if res:
                        # wrap val if vtype is Array<> and try eval again
                        expr = self._wrap_tosvar(expr)
                        try:
                            result = eval(expr, self.uflat, self.userv_local(testplan, local)).value
                        except Exception as e_res:
                            if not is_error:
                                continue     # goto next var
                            self.print_usrv()
                            msg = (f'   original {var} = {val}\n'
                                   f'   python   {var} = {expr}\n'
                                   f'   Error: {e_res}')
                            raise ErrorInput(f"Failed to evaluate Array<> uservar: {var}\n{msg}",
                                             f"Check [{var}] in .usrv file. Is the expression valid?")
                    else:
                        if not is_error:
                            continue     # goto next var
                        self.print_usrv()
                        msg = (f'   original {var} = {val}\n'
                               f'   python   {var} = {expr}\n'
                               f'   Error: {e}')
                        raise ErrorInput(f"Failed to evaluate: {var}\n{msg}",
                                         f"Check [{var}] in .usrv file. Is the expression valid?")

                # get correct type
                if vtype in ('Voltage', 'Current', 'Double', 'Time'):
                    final = float(result)
                elif vtype == 'Integer':
                    final = int(result)
                elif vtype == 'Boolean':
                    final = bool(result)
                else:   # bool/string/etc
                    final = result

                # assign it
                self.ulocal[testplan][varnd] = final
                self.uflat[f'{testplan}{SEPMOD}{varnd}'] = final

                # for evergreen - put module scope into non-scoped global
                if testplan == self.testplan_base or varnd not in self.ulocal[self.testplan_base]:
                    self.uflat[varnd] = final

    def _evaluate_rule(self, is_error):
        """
        Evaluate all SelectorRuleCollection

        :param is_error: Set to True to error out
        :return: None
        """
        for testplan in self._iter_testplan(self._userv):
            if testplan not in self._src:
                self._src[testplan] = OrderedDict()
            if testplan not in self._src_eval:
                self._src_eval[testplan] = {}

            # evaluate all
            for var in self._src_orig[testplan]:

                self._src[testplan][var] = [None for _ in self._src_orig[testplan][var]]
                for idx, val in enumerate(self._src_orig[testplan][var]):
                    if val == '':
                        self._src[testplan][var][idx] = True
                        continue

                    # if var == 'FlowMatrixRule.BomGroupRule':
                    #     print('=============', var, idx, expr)
                    #     pprint(ud)

                    expr = ExprParser.to_py(val)

                    # eval
                    try:
                        result = eval(expr, self.uflat, self.userv_local(testplan))
                    except Exception as e:
                        if not is_error:
                            continue    # to next var
                        self.print_usrv()
                        msg = (f'   original {var} = {val}\n'
                               f'   python   {var} = {expr}\n'
                               f'   Error: {e}')
                        raise ErrorInput(f"Failed to evaluate SelectorRuleCollection: arg#{idx} for [{var}]\n{msg}",
                                         f"Check [{var}] in .usrv file. Is the expression valid?")

                    # assign it
                    self._src[testplan][var][idx] = bool(result)

                # evaluate it ==============
                varnd = var.replace('.', SEP)
                args = self._src[testplan][var]
                if None in args:
                    # do not cache yet
                    self._src_eval[testplan][varnd] = eval(EvalFuncs.rule2py(args, var))
                else:
                    ckey = f'{testplan}{SEPMOD}{var}'
                    if ckey not in self._cache_rule or self._cache_rule[ckey][0] != args:
                        self._cache_rule[ckey] = (args, eval(EvalFuncs.rule2py(args, var)))     # cannot create testcase where this will error, without mocking :)
                    self._src_eval[testplan][varnd] = self._cache_rule[ckey][1]

                self._src_eval[f'{testplan}{SEPMOD}{varnd}'] = self._src_eval[testplan][varnd]

    def _read_usrv(self, fname, testplan):
        """
        Read one usrv file

        :param fname: full path to fname
        :param testplan: TestPlan name
        :return: None
        """
        name = None
        src_name = None
        rc_name = None
        rc_args = None
        data = OrderedDict()
        src = OrderedDict()       # SelectorRuleCollection
        sharedline = False
        _unit = '|'.join(Units.UNITMAP)
        r_src = re.compile(r'^SelectorRuleCollection\s+(\w+)$')
        r_sr = re.compile(r'^SelectorRule\s+(\w+)\s*\(([^\)]+)\)')
        r_uv = re.compile(r'^(TrialVars|UserVars)\s+(\w+)$')
        r_string = re.compile(r'^String\s+(\w+)\s*=\s*\"([^\"]*)\"\s*;')

        # Simple number
        r_int = re.compile(r'^(Integer|Voltage|Current|Double|Time)\s+(\w+)\s*=\s*(-?[\d\.]+)(%s)?;' % _unit, re.IGNORECASE)
        r_int2 = re.compile(r'^(\w+)\s*=\s*(-?\d+);', re.IGNORECASE)

        # expression
        r_expr = re.compile(r'^(Array\s*<String>|Array\s*<Double>|Array\s*<Integer>|String|Boolean|Integer|Voltage|Current|Double|Time)\s+(\w+)\s*=\s*(\S.*);')

        # Boolean and future expressions
        r_bool = re.compile(r'^Boolean\s+(\w+)\s*=\s*(true|false);', re.IGNORECASE)

        if testplan not in self._userv_orig:
            self._userv_orig[testplan] = OrderedDict()

        for lno, line in OtplFile(fname).readline():

            # Special line
            if line.startswith('Default ='):
                line = f'Integer {line}'

            # Ignore these
            if line.startswith(('{', 'Version')):
                continue

            if line == 'Shared':
                sharedline = True
                continue      # Shared is considered do-nothing for pytpd

            # const
            if line.startswith('Const'):
                line = line[5:].strip()

            # closure
            if line == '}':
                if name is not None:
                    name = None
                    continue
                if rc_name:
                    # make sure all outcomes are set
                    for idx, val in enumerate(src[rc_name]):
                        assert val is not None, f'[{rc_args[idx]}] is not defined: line#[{lno}] of [{fname}]'
                    rc_name = None
                    continue
                if src_name:
                    src_name = None
                    continue
                if sharedline:
                    sharedline = False
                    continue

                raise ErrorUser(f'Close bracket found in [{lno}] of [{fname}], but no block found')

            if line == 'UserVars':
                name = ''
                continue

            # SelectorRuleCollection\s+(\w+)
            res = r_src.search(line)
            if res:
                src_name = res.group(1)
                continue

            # SelectorRule
            res = r_sr.search(line)
            if res:
                assert src_name, "Error: SelectorRuleCollection is not initialized!"
                rc_name = f'{src_name}.{res.group(1)}'
                rc_args = [x.strip() for x in res.group(2).split(',')]
                assert rc_name not in src, f"Error: [{rc_name}] is already defined: line#{lno} of [{fname}]"
                src[rc_name] = [None for _ in rc_args]
                continue

            # inside selector rule
            if rc_name:
                assert line[-1] == ';', f'Expecting semicolon at end of line: line#{lno} of [{fname}]: {line}'
                line = line[:-1]     # remove semicolon
                if '=>' in line:
                    val = line.split('=>')
                    assert val[0].strip() in rc_args, f'Error: [{val[0].strip()}] is not part of args. line#{lno} of [{fname}]'
                    idx = rc_args.index(val[0].strip())
                    src[rc_name][idx] = val[1].strip()
                else:
                    idx = rc_args.index(line.strip())
                    src[rc_name][idx] = ''
                continue

            # UserVars\s+(\w+)
            res = r_uv.search(line)
            if res:
                name = res.group(2) + '.'
                continue

            # String
            res = r_string.search(line)
            if res:
                data[name + res.group(1)] = res.group(2)
                continue

            # Integer|Voltage|Current|Double|Time - simple
            res = r_int.search(line)
            if res:
                if res.group(4):
                    mult = Units.UNITMAP[res.group(4).lower()]
                else:
                    mult = 1

                data[name + res.group(2)] = float(res.group(3)) * mult
                if res.group(1) == 'Integer':
                    data[name + res.group(2)] = int(data[name + res.group(2)])
                else:
                    _dummy = 0    # for coverage
                continue

            # integer without type
            res = r_int2.search(line)
            if res:
                data[name + res.group(1)] = int(res.group(2))
                continue

            # Boolean
            res = r_bool.search(line)
            if res:
                val = res.group(2)
                data[name + res.group(1)] = bool(val.lower() == 'true')
                continue

            # Expression - to evaluate later
            res = r_expr.search(line)
            if res:
                self._userv_orig[testplan][name + res.group(2)] = (res.group(3), res.group(1))
                continue

            raise ErrorCockpit(f"Unknown usrv line: [{line}] at [{lno}] of [{fname}]")

        if testplan not in self._userv:
            self._userv[testplan] = OrderedDict()
        self._userv[testplan].update(data)

        if testplan not in self._src_orig:
            self._src_orig[testplan] = OrderedDict()
        self._src_orig[testplan].update(src)

    def userv_local(self, testplan, local={}):
        """
        Returns the local user varaibles for eval

        Performance: 500K eval() local dict:
        Chain eval 39.064 Secs: eval(expr, {}, chainmap(<dicts>))
        Dict  eval 20.744 Secs: eval(expr, {}, <dict>)

        Performance: 500K eval():
        eval 18.956 Secs: eval('a+b+c+d+e+f+g+h+i+j', comb, ChainMap(func, qq, loc))
        eval 16.974 Secs: eval('a+b+c+d+e+f+g+h+i+j', combfunc, ChainMap(qq, loc))
        """
        return ChainMap(local,
                        self.ulocal.get(testplan, {}),
                        self.ulocal.get(self.testplan_base, {}),
                        self._src_eval.get(testplan, {}),
                        self._src_eval.get(self.testplan_base, {}),
                        self._src_eval,
                        self._func_dict)

    def eval_param(self, param, testplan, info='not specified', is_print=True):
        """
        Evaluate a single expression string (param)

        :param param: string expression
        :param testplan: which testplan
        :param info: variable name, for debug
        :param is_number: Set to True ifnumber
        :return: evaluated value
        """
        self.set_data()

        # evaluate all
        expr = ExprParser.to_py(param)

        # eval
        try:
            result = eval(expr, self.uflat, self.userv_local(testplan))
        except Exception as e:
            expr = self._wrap_tosvar(expr)
            # Try again in wrapping expression with TOSVar
            try:
                result = eval(expr, self.uflat, self.userv_local(testplan)).value
            except Exception as e:
                if is_print:
                    self.print_usrv()
                msg = (f'   original {info} = {param}\n'
                       f'   python   {info} = {expr}\n'
                       f'   Error: {e}')
                raise ErrorInput(f"Failed to evaluate: {info}\n{msg}",
                                 f"Check {info}. Is the expression valid?")
        return result

    def get_usrv_map(self):
        """
        Returns a copy of usrv dictionary, mainly used for diffing. Do not use this for eval.

        :return: dict
        """
        self.set_data()
        dd = {}
        for testplan in self._iter_testplan(self.ulocal, last=True):
            dd.update({x.replace(SEP, '.'): y for x, y in self.ulocal[testplan].items()})
        return dd

    def get_rule_map(self, flat=True):
        """
        Returns the rule dictionary
        :param flat: Set to False to return map as-is
        :return: dict
        """
        if flat:
            # This is used for diffs
            final = {}
            for testplan in self._src:
                final.update(self._src[testplan])
            return final
        else:
            return self._src

    def print_usrv(self):
        """Print ulocal and rules dictionary"""
        if not self.ulocal:
            log.info("-w- ulocal is empty!")
            return   # nothing to print

        dd = self.ulocal
        for testplan in self._iter_testplan(dd):
            for varnd in sorted(dd[testplan]):
                var = varnd.replace(SEP, '.')
                log.info(f'-d- usrv [{testplan}] {var} = {dd[testplan][varnd]}')

        dd = self._src
        for testplan in self._iter_testplan(dd):
            for var in sorted(dd[testplan]):
                log.info(f'-d- rule [{testplan}] {var} = {dd[testplan][var]}')

    def get_var(self, var, testplan=None, default=None):
        """
        Returns value of var

        :param var: uservar name
        :param testplan: testplan name
        :param default: Return default value if var is not found, otherwise error out
        :return: value
        """
        if not self._userv:    # for fast access!
            self.set_data()

        if testplan is None:
            testplan = self.testplan_base

        # look at scope
        if '::' in var:
            elems = var.split('::')
            var = elems[-1]
            testplan = elems[-2]

        # special global
        if '.' in var and var.split('.')[0].lower() == '_uservars':
            var = var.split('.')[1]

        varnd = var.replace('.', SEP)

        # try local first
        local_map = self.userv_local(testplan)
        if varnd in local_map:
            return local_map[varnd]

        if varnd in self.uflat:
            return self.uflat[varnd]

        # default
        if default is None:
            raise ErrorInput(f'Error: [{var}] uservar is not defined. module={testplan}')
        else:
            return default

    def set_var(self, var, val, msg, as_is=False, testplan=None):
        """
        Sets val into var

        :param var: variable name
        :param val: value
        :param msg: from where
        :param as_is: Set to True to assign it as-is without eval. This is called before evaluate() is called.
        :param testplan: which testplan
        :return: orig value or None if no change
        """
        if '::' in var:
            elems = var.split('::')
            var = elems[-1]
            testplan = elems[-2]

        var = var.replace('_UserVars.', '')
        varnd = var.replace('.', SEP)

        if testplan is None:
            testplan = self.testplan_base
        origtestplan = testplan

        # If it is not found in local scope, try global scope
        if var in self._userv.get(testplan, {}):
            pass
        elif var in self._userv_orig.get(testplan, {}):
            pass
        else:
            testplan = self.testplan_base

        # make sure it exist
        if var in self._userv.get(testplan, {}):
            orig = self._userv[testplan][var]
        elif var in self._userv_orig.get(testplan, {}):
            if not self.ulocal:
                orig = "___SOMEVALUE___"     # this means ulocal is not evaluated yet, during initial setting
            else:
                orig = self.ulocal[testplan][varnd]    # to determine the type
        else:
            raise ErrorInput(f"Error: uservar scope={testplan}|{origtestplan}, [{var}] does not exist. From: {msg}",
                             "Pls check uservar and the expression if it's valid")

        # This is called pre-evaluate. Thus, return as-is (string)
        if as_is:
            newval = val

        # make sure type is followed ==========================================
        # val is a string
        elif isinstance(orig, str) and isinstance(val, str):
            newval = val
        elif isinstance(orig, bool) and isinstance(val, str):
            newval = bool(self.eval_param(val, testplan, var))
        elif isinstance(orig, int) and isinstance(val, str):
            newval = int(self.eval_param(val, testplan, var))
        elif isinstance(orig, float) and isinstance(val, str):
            newval = float(self.eval_param(val, testplan, var))

        # val is not a string
        elif isinstance(orig, str):
            newval = str(val)
        elif isinstance(orig, bool):
            newval = bool(val)
        elif isinstance(orig, int):
            newval = int(val)
        elif isinstance(orig, float):
            newval = float(val)
        else:
            raise TypeError('set_var(%s=%r) error: Unknown type: %s, From: %s' % (var, orig, type(orig), msg))

        # return
        if orig != newval:
            # 1- assign _userv or _userv_orig
            if var in self._userv[testplan]:
                self._userv[testplan][var] = newval
            if var in self._userv_orig[testplan]:
                self._userv_orig[testplan][var] = (newval, self._userv_orig[testplan][var][1])

            # 2- assign uflat+ulocal
            if self.uflat:
                self.uflat[f'{testplan}{SEPMOD}{varnd}'] = newval
                self.ulocal[testplan][varnd] = newval

                # for evergreen - put module scope into non-scoped global
                if testplan == self.testplan_base or varnd not in self.ulocal[self.testplan_base]:
                    self.uflat[varnd] = newval

            return orig
        else:
            return None     # nochange


import tp.testprogram    # used for :type
