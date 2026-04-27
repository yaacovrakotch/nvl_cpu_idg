#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
pinname mapping Tool
The tool will try to map rtlname (from connectivity.csv) to pinname (from pindef.xls)
Once the pin name are mapped, then ballname is compared as well.

connectivity.csv (via -c) columns:
    ballname,rtlname,<extra_fields_ignored>
pindef.csv (via -p) columns:
    pinname,channel_no,ballname

"""
import setenv      # must be first in the imports
from gadget.files import File
from gadget.vepargs import Args, TA_All, TA_StoreFile
from gadget.helperclass import OPT
from gadget.dictmore import DictDot
from gadget.printmore import PrintAlign
from collections import defaultdict
from itertools import zip_longest
from os.path import basename
import difflib
import re


class MainArg(Args):   # parent: ArgsBase
    """
    Main wrap
    """

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        cfg = DictDot()
        cfg.c = TA_StoreFile('Connectivity File')
        cfg.p = TA_StoreFile('Pindef File')
        return cfg

    def main(self):
        """
        Main entry point
        """
        if not (OPT.c and OPT.p):
            self.do_else()

        MapIt(OPT.p, OPT.c).main()


class MapIt:

    def __init__(self, pinfile, connectfile):
        self.pinfile = pinfile
        self.connectfile = connectfile
        self.r2b = None       # {rtl_pin: ballname}, from connectivity.csv
        self.pindef = None    # {pin: ballname}, from pindef .xls
        self.final = None     # {pin: ballname}, final mapped dictionary
        self.search = None    # {set_of_pins}   # pins in self.r2b to search from

    # def read_ballmap(self):
    #     # read ballmap (official copy)
    #     r2b = defaultdict(set)
    #     b2r = defaultdict(set)
    #     with File('mtl_ballmap.csv') as fh:
    #         for lno, line in enumerate(fh.chomp()):
    #             if lno == 0:   # throw away header
    #                 continue
    #             rtl, ball = line.split(',')
    #             r2b[rtl].add(ball)
    #             b2r[ball].add(rtl)
    #
    #     # convert to plain dict
    #     r2b = {k: v.pop() if len(v) == 1 else v for k, v in r2b.items()}
    #     b2r = {k: v.pop() if len(v) == 1 else v for k, v in b2r.items()}

    def read_connectivity(self):
        """
        Read Connectivity matrix file

        :return: dict: {rtlname: ball}
        """
        r2b = {}
        with File(self.connectfile) as fh:
            for lno, line in enumerate(fh.chomp()):
                if lno == 0:   # throw away header
                    continue
                elems = line.split(',')
                ball = elems[0]
                rtl = elems[1]
                if not rtl:
                    rtl = ball
                    print(f'-w- ball={ball} has rtl empty, so assigning rtl=ball')

                # remove brackets and underscores
                rtl = rtl.replace('[', '').replace(']', '')
                r2b[rtl] = ball.replace('[', '').replace(']', '')

        return r2b

    def read_pindef(self):
        """
        Read the pindef file

        :return: dict: {pin: ballname}
        """
        # read pindef
        pindef = {}
        ignore_set = set('PINDEF CHANNEL_CONFIGS BASE_CONFIG_NAME SITE_DEF_NUMBER PINNAME'.split())
        with File(self.pinfile) as fh:
            for lno, line in enumerate(fh.chomp()):
                if lno == 0:    # throw away header
                    continue

                if line.startswith('#'):
                    continue

                pin, ch, ball = line.split(',', 2)
                if pin in ignore_set:   # Ignore these pins
                    continue
                pindef[pin] = ball

        return pindef

    def remove_ec_hpc(self):
        """remove ec and hpc duplicate pins. These are physically duplicate pins in tester."""
        robj = re.compile('^(.*)(_ec|_hpc)$')
        print()
        print("-i- Removing tester pin duplicate (_ep/_hpc):")
        for pin in list(self.pindef):
            res = robj.search(pin)
            if res:
                rpin = res.group(1)
                if rpin in self.pindef:
                    del self.pindef[pin]
                    print(f"Removing _ec/_hpc: {pin}")

    # def find2(self, search, pin):
    #     """Return the pin closest match based on number of characters matching"""
    #     pin_set = self.toset(pin)
    #     match = {}
    #     mismatch = {}
    #     for target in search:
    #         target_set = self.toset(target)
    #         match[target] = len(pin_set & target_set)
    #         mismatch[target] = len(target_set - pin_set)
    #
    #     sorted_list = sorted(match, key=match.get, reverse=True)
    #     sorted_list.sort(key=mismatch.get)
    #     print(f'pin={pin}')
    #     print('\n'.join(f'{x} {match[x]} {mismatch[x]}' for x in sorted_list))
    #     if dd[sorted_list[0]] == dd[sorted_list[1]]:
    #         raise Exception(f'pin={pin}, cannot select between [{sorted_list[0]}] vs [{sorted_list[1]}]')
    #     return dd[sorted_list[0]]
    #
    # @staticmethod
    # def toset(pin):
    #     """Convert pin, a string to a set"""
    #     result = set()
    #     for char in pin:
    #         for idx in range(100):
    #             key = f'{char}{idx}'
    #             if key in result:
    #                 continue
    #             result.add(key)
    #             break
    #     return result

    def find(self, pin, search_list, cutoff=0.6):
        """
        Given pin, find the closes match from the search_ list

        :param pin: input pin name
        :param search_list: list of pins to search from
        :param cutoff: number from 0 to 1
        :return: found pin, or None
        """

        result = difflib.get_close_matches(pin, search_list, cutoff=cutoff)
        if result:
            return result[0]

        # print(f'pin={pin}')
        # for trial in (0.6, 0.5, 0.4, 0.3, 0.2, 0.1):
        #     result = difflib.get_close_matches(pin, search, cutoff=trial)
        #     if result:
        #         print(f'at {trial}')
        #         pprint(result)
        #         exit(0)
        # exit(0)

        return None

    def map_pin_to_rtl(self):
        """
        Do the pindef to rtlname mapping
        """
        final = {}                          # {pin: ball} mapping, final
        search = {x for x in self.r2b}      # set of pins to search

        # exact match first
        for pin in sorted(self.pindef):
            if pin in self.r2b:
                search.discard(pin)
                final[pin] = self.r2b[pin]

        print()
        print(f'-i- Exact match found: {len(final)} of {len(self.pindef)}')

        # exact match first - no underscores
        r2bnu = {k.replace('_', ''): k for k, v in self.r2b.items()}
        count = 0
        for pin in sorted(self.pindef.keys() - final.keys()):
            _pin = pin.replace('_', '')

            if _pin in r2bnu:
                print(f"_NU: pin=[{pin}] _pin=[{_pin}]")
                search.discard(r2bnu[_pin])
                final[pin] = self.r2b[r2bnu[_pin]]
                count += 1

        # No _HC
        for pin in sorted(self.pindef.keys() - final.keys()):
            _pin = pin.replace('_HC', '')

            if _pin in self.r2b:
                print(f"_HC: pin=[{pin}] _pin=[{_pin}]")
                search.discard(_pin)
                final[pin] = self.r2b[_pin]
                count += 1

        print()
        print(f'-i- w/o underscore: {count}, Total exact match found: {len(final)} of {len(self.pindef)}')

        # Iterate to different cutoff
        print()
        print('-i- Start of get_close_match():')
        for cutoff in (0.9, 0.8, 0.7):
            for pin in sorted(self.pindef.keys() - final.keys()):
                _pin = pin

                # try to find this pin
                foundpin = self.find(_pin, search, cutoff=cutoff)
                if foundpin:
                    final[pin] = self.r2b[foundpin]
                    search.discard(foundpin)
                    print(f"Found-P at {cutoff}: {_pin}: {foundpin}")
                    continue

                # try the ballmap
                bm = {self.r2b[k] for k in search}
                foundball = self.find(_pin, bm, cutoff=cutoff)
                if foundball:
                    foundpin = [k for k, v in self.r2b.items() if v == foundball][0]
                    final[pin] = self.r2b[foundpin]
                    search.discard(foundpin)
                    print(f"Found-B at {cutoff}: {_pin}: [{foundpin}], foundball=[{foundball}]")

        self.final = final
        self.search = search

    def missing(self):
        # display not found
        print()
        print(f'-i- counts pindef={len(self.pindef)}, final={len(self.final)}')
        print()
        print("-i- TABLE: Not found in pindef vs connectivity:")
        pa = PrintAlign(rjust=False, col_header=True)
        pa(f'pindef:{basename(self.pinfile)}',
           f'pindef ball name',
           f'connectivity:{basename(self.connectfile)}',
           f'connect ball name')
        for a, b in zip_longest(sorted(self.pindef.keys() - self.final.keys()), sorted(self.search)):
            pa(a, self.pindef.get(a, ''), b, self.r2b.get(b, ''))
        pa.disp()

        print()
        print("-i- pindef mapping, which is not mapped to connectivity csv:")
        print('%-30s %s' % ('PIN:', 'BALL:'))
        for pin in sorted(self.pindef.keys() - self.final.keys()):
            print('%-30s %s' % (pin, self.pindef[pin]))

        print()
        print("-i- connectivity mapping: not mapped to pindef:")
        print('%-30s %s' % ('PIN:', 'BALL:'))
        for pin in sorted(self.search):
            print('%-30s %s' % (pin, self.r2b[pin]))

    def ball_compare(self):
        """Do the ball compare"""
        print()
        print("Ballmap compare report:")
        for pin in sorted(self.pindef):
            if pin not in self.final:
                continue     # cannot compare

            ball = self.pindef[pin]
            _ball = ball.split(':')[1] if ':' in ball else ball
            _ball = _ball.strip().split()[0] if _ball else _ball      # remove space

            if _ball == self.final[pin]:
                continue    # exact match

            if _ball == self.final[pin].replace('NC_', ''):
                continue    # still the same

            print(f'pindef={pin} ballmap mismatch: [{_ball}] vs connectivity=[{self.final[pin]}]')

    def main(self):
        """Do the mapping - main algo"""
        self.r2b = self.read_connectivity()
        self.pindef = self.read_pindef()
        self.remove_ec_hpc()
        self.map_pin_to_rtl()
        self.ball_compare()
        self.missing()


if __name__ == '__main__':  # pragma: no cover
    MainArg(desc=__doc__).main()
