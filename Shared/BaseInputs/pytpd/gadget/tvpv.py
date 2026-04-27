#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
import os
import json
import re
from collections import defaultdict
from os.path import basename, dirname, join, exists, realpath
from time import time, sleep

from .files import File, TempDir
from .helperclass import is_ut
from .pylog import log
# from .shell import SystemCall
from .strmore import Base3844


class TvpvEnv:
    # Below is the mapping of which '<machine>.<site>.intel.com' to the VEP2 site name.
    site_mapping = {'sc': 'SC',
                    'sc1': 'SC1',
                    'sc2': 'SC2',
                    'sc3': 'SC3',
                    'sc4': 'SC4',
                    'sc5': 'SC5',
                    'sc6': 'SC6',
                    'sc7': 'SC7',
                    'sc8': 'SC8',
                    'sc9': 'SC9',
                    'sc10': 'SC10',
                    'sc11': 'SC11',
                    'zsc1': 'SC1',
                    'zsc2': 'SC2',
                    'zsc3': 'SC3',
                    'zsc4': 'SC4',
                    'zsc5': 'SC5',
                    'zsc6': 'SC6',
                    'zsc7': 'SC7',
                    'zsc8': 'SC8',
                    'zsc9': 'SC9',
                    'zsc10': 'SC10',
                    'zsc11': 'SC11',
                    'zsc12': 'SC12',
                    'zsc14': 'SC14',
                    'zsc15': 'SC15',
                    'fm': 'FM',
                    'fc': 'FC',
                    'rr': 'RR',
                    'ra': 'RA',
                    'fedh': 'HD',
                    'hd': 'HD',
                    'pdx': 'JF',
                    'png': 'PG',
                    'iil': 'IDC',
                    'lc': 'IDC',
                    'pt': 'PT',
                    'ch': 'CH',
                    'an': 'AN',
                    'ir': 'IR',
                    'cr': 'CR',
                    'iind': 'BA',
                    'to': 'TO'
                    }

    site2domain = {v.lower(): k for k, v in site_mapping.items()}
    site2domain['idc'] = 'iil'     # special

    idrive_mapping = {'HA': 'IDC',
                      }    # all others are default

    @classmethod
    def site_to_domain(cls, site):
        """
        Given site code, return the domain
        non-case-sensitive
        """
        if not site:
            return 'pdx'   # default if empty

        site_lower = site.lower()
        if site_lower in cls.site_mapping:
            return site_lower
        if site_lower in cls.site2domain:
            return cls.site2domain[site_lower]

        from .errors import ErrorInput
        raise ErrorInput(f'Given site [{site}], does not have mapping in site_to_domain.',
                         'Check logs and seek help.')

    @classmethod
    def get_site(cls):
        """
        Return the site the machine is running from.
        :return: site string
        """
        from .shell import IS_UNIX
        if IS_UNIX:
            return cls._get_site_unix()
        else:    # pragma: no cover
            return cls._get_site_windows()

    @classmethod
    def _get_site_windows(cls):
        r"""
        windows version
        Use I:\ drive mapping to determine site.

        Laptop:            '\\\\amr\\ec\\proj\\mdl\\jf\\intel\\tpvalidation'
        Tester:            '\\\\amr.corp.intel.com\\ec\\proj\\mdl\\jf\\prod\\hdmx_intel\\i\\tpvalidation'
        KM remote desktop: '\\\\gar.corp.intel.com\\ec\\proj\\mdl\\pg\\prod\\tpvalidation'

        :return: site string
        """
        i_path = r'I:\hdmxprogs'
        f_path = realpath(i_path)
        res = re.search(r'[\\]+mdl[\\]+(\w+)', f_path)
        if res:
            site_upper = res.group(1).upper()
            return cls.idrive_mapping.get(site_upper, site_upper)

        from .errors import ErrorInput
        raise ErrorInput(f'Cannot get site from [{f_path}]',
                         'If this is a sort site, Contact jqdelosr for usage as sort is not enabled. '
                         'For class site, Contact jqdelosr to enable this particular site')

    @classmethod
    def _get_site_unix(cls):
        """
        unix version
        Return the site the machine is running from.
        This is the site-auto-detect algo.
        """
        result = {}
        for method in (cls._dns_by_unix,
                       cls._by_eczone,
                       cls._direct_dir):
            try:
                raw = method()
            except BaseException:
                raw = "Exception"

            sitestring = cls._get_sitestring(raw)
            sitestring = cls.get_id_zone(sitestring)
            if sitestring is not None:
                break
            result[method] = raw
        else:
            raise Exception("All methods to determine DNS is exhausted. "
                            "Cannot get DNS name for this machine [%s]. "
                            "Pls copy this info and send to TVPV admin for debug. "
                            "methods: %s" % (os.environ.get('HOST', "None"),
                                             ', '.join("%s:%s" % (x, result[x]) for x in result)))

        # at this point, sitestring is derived
        if sitestring in cls.site_mapping:
            return cls.site_mapping[sitestring]
        else:
            raise EnvironmentError("[%s] is not registered in EnvBase.sites. Pls register." % sitestring)

    @classmethod
    def _get_sitestring(cls, raw):
        """
        Given a raw string (either <machine>.<site>.intel.com or /nfs/<site>/proj),
        return <site>
        """
        if raw in cls.site_mapping:   # provided string is already the site
            return raw

        if raw is None:
            return None

        res = re.search(r'\.(\w+)\.intel\.com', raw.lower())
        if res:
            return res.group(1)

        res = re.search(r'/nfs/(\w+)/proj', raw)
        if res:
            return res.group(1)

        return None

    @classmethod
    def get_id_zone(cls, sitestring):
        """Return raw value of sitestring for SC zones"""

        if sitestring == "sc" and 'EC_ZONE' in os.environ:
            result_sitestring = os.environ['EC_ZONE']      # this identifies the SC zone
            if result_sitestring in cls.site_mapping:
                return result_sitestring

        return sitestring   # original string

    @classmethod
    def _direct_dir(cls):
        """Return the name of directory of caller"""
        name = basename(dirname(dirname(__file__)))
        for sitename, vepname in cls.site_mapping.items():
            if vepname == name:
                return sitename
        return None

    @staticmethod
    def _dns_by_unix():
        """Return result from unix /usr/bin/host"""
        from .shell import HOSTNAME
        if 'HOST' in os.environ:
            return os.popen("/usr/bin/host " + os.environ['HOST']).read().strip()
        else:
            return os.popen("/usr/bin/host " + HOSTNAME).read().strip()

    @staticmethod
    def _by_eczone():
        """Return site via ECZONE"""
        return os.environ.get('EC_ZONE', "")

    @classmethod
    def get_tvpv_prodcode(cls, prod_override=''):

        # Flash does not guarantee that a product will be set.  Allow a user override.
        if prod_override:
            return prod_override

        # unittest mode always returns TST to help when running in a CI/CD pipeline with no VEP/Flash loaded
        if is_ut():
            return 'tst'

        # This will throw an exception if no TVPV env can be found
        env_type = cls._get_flash_or_vep()
        prodcode = ''

        # Check Flash environment to see if we can determine which product to use. This is not guarenteed to be set in
        # Flash, but do the best we can :).
        flash_env_vars = ['FLASH_PROD', 'TCG_PROD']
        if env_type == 'flash':
            for env_var in flash_env_vars:
                if os.getenv(env_var, ''):
                    prodcode = os.getenv(env_var)
        # This is a VEP env, use the 'checkenv.py' utility to get the product code
        elif env_type == 'vep':
            from .shell import SystemCall  # Prevent circular imports
            ecode, stdout = SystemCall('checkenv.py').run_outtxt()
            if not ecode:
                for line in stdout.split('\n'):
                    # Example Line: ('Product:        ', 'TST')
                    m = re.search(r"'Product:\s*',\s*'(\w+)'", line)
                    if m:
                        prodcode = m.group(1).lower()
                        break

        return prodcode

    @staticmethod
    def _is_vep():
        """Is this the VEP environmnet"""
        vep_path = os.getenv('VEP2_ROOT', '')
        return bool(vep_path)

    @staticmethod
    def _is_flash():
        """Is this the Flash environmnet"""
        flash_path = os.getenv('FLASH_INSTALL_DIR', '')
        return bool(flash_path)

    @classmethod
    def _get_flash_or_vep(cls):
        if cls._is_flash():
            return 'flash'
        elif cls._is_vep():
            return 'vep'

        raise EnvironmentError(".env file is not found. "
                               "Trying to find it, but unable to determine VEP vs Flash. "
                               "Please source a valid TVPV ENV.")


class TupleDataError(ValueError):
    pass


def _new_trace_cache():
    """
    Helper for the TraceInfo class because Python didn't like using a staticmethod in class
    parameter definition
    """
    return defaultdict(
        lambda: {
            'tuple_int': 0,
            'tracepath': '',
            'tracename': '',
            'tags': [],
            'lineitem': '',
            'exists': False,
            'valid': False,
            'remote': False,
            'remote_site': '',
            'disassemble_data': {
                'full': {},  # Human readable version of the bit data: module_bit=MFunc
                'bit': {},  # Raw bit value: module_bit=F
            },
        }
    )


class TraceInfo:
    """
    Class to replace VEP & Flash finder/search/name_disassemble. Will get the needed data by running cmdline
    calls and caching the data as it goes. Cmdline calls are required inorder to avoid imports of VEP or Flash
    underlying libraries so that this code can be fully interoperable.

    Finder takes too long to dump the entire DB (90s+ for TGL 1.3M traces), so a new call will happen everytime
    there is a new tuple requested, but previously queried ones will check the cached results.

    The most efficient way of using this class is to query for large volumns of traces at once because finder and
    name_disassemble cmdline calls will be made for each request.  System calls are very slow, so bulk lookups
    should be used.

    Example Code:
        all_my_traces = find_all_traces()  # ['d0012345', 'g0023457', 45678]
        valid_tuples = TraceInfo.is_valid(all_my_traces)  # Will query with finder & disassemble cmdline call
        tups_to_process = [tup for tup in valid_tuples if valid_tuples[tup]]  # Skip items marked PDE_INVALID
        for tup in tups_to_process:
            tracename = TraceInfo.get_info(tup, 'tracename', single_val=True)  # Finder info
            chunknum = TraceInfo.get_bit(tup, 'chunknum', single_val=True)     # Disassemble bit info (human-readable)
            prefix = TraceInfo.get_bit(tup, 'traceprefix', valtype='bit')  # Disassemble bit info - raw bit val
            ...
    """
    # DB calls will happen through the cmdline -- VERY SLOW! -- cache the results here.
    # Key: _datacache[tuple_int]
    _datacache = _new_trace_cache()
    _valid_disassemble_fields = set()
    _flash_prod = ''  # All of the Flash commands need Product set on cmdline

    # If disassemble throws an error on some traces, keep going. This can happen when
    # a few bad traces are mixed in with some good ones.
    _continue_on_error = False

    @classmethod
    def exists(cls, tup_or_list, single_val=False):
        """Tuples exist in DB, could be remote or local, valid or invalid"""
        tups = cls.get_tuple(tup_or_list)
        cls._query_traces(tups)  # Update Cache

        final = {}
        for tup in tups:
            final[tup] = cls._datacache[tup]['exists'] if tup in cls._datacache else False

        if single_val:
            return cls._single_val_from_dict(final, False)

        return final

    @classmethod
    def is_valid(cls, tup_or_list, single_val=False):
        """Tuples are found and not marked PDE_INVALID.  Like Exists, but checks the tags as well"""
        tups = cls.get_tuple(tup_or_list)
        cls._query_traces(tups)  # Update Cache

        final = {}
        for tup in tups:
            if tup in cls._datacache:
                t_exist = cls._datacache[tup]['exists']
                t_valid = cls._datacache[tup]['valid']
                final[tup] = True if tup in cls._datacache and t_exist and t_valid else False
            else:
                final[tup] = False

        if single_val:
            return cls._single_val_from_dict(final, False)

        return final

    @classmethod
    def is_remote(cls, tup_or_list, single_val=False):
        """Tuples do not exist at currenty local site"""
        tups = cls.get_tuple(tup_or_list)
        cls._query_traces(tups)  # Update Cache

        final = {}
        for tup in tups:
            final[tup] = True if tup in cls._datacache and cls._datacache[tup]['remote'] else False

        if single_val:
            return cls._single_val_from_dict(final, False)

        return final

    @classmethod
    def is_tuple(cls, name_or_list, single_val=False):
        """Can a tuple possibly be extracted from these strings. No finder query happens"""
        tup_map = cls.map_tuples(name_or_list)
        result = {tup: bool(tup_int) for tup, tup_int in list(tup_map.items())} if tup_map else {}

        if single_val:
            return cls._single_val_from_dict(result, False)

        return result

    @staticmethod
    def is_valid_info_field(field):
        return field in _new_trace_cache()[0]

    @classmethod
    def get_bit(cls, name_or_list, field, valtype='full', single_val=False):
        """
        Get Name Disassemble bit info for the traces requested
        :param name_or_list: Trace name string or list of strings/tup_ints to get data for
        :param field: tracename field like: traceprefix, tid, chunknum, module. Each product has different options
        :type field: str
        :param valtype: 'bit' or 'full'. bit returns the raw bit value (i.e. 'F'), full returns the human-readable
                        value (i.e. 'MFunc')
        :param single_val: When provided, output a single string value. Useful for just a single input
        :type single_val: bool
        :return: map of tup_int to bit requeseted. Format: data[tup_int] = <field_bit_val>
        :rtype: dict or str
        """

        # It is possible to disassemble sample names that don't actually exist in finder. Use the map_tuple()
        # function to do checks before running the general query
        bit_data = {}
        possible_tups = list(cls.map_tuples(name_or_list).values())
        cls._disassemble_traces(possible_tups)

        # Error checking
        if field not in cls._valid_disassemble_fields:
            raise ValueError("Invalid bit field [%s] requested" % field)

        sample_entry = _new_trace_cache()[0]
        if valtype not in sample_entry['disassemble_data']:
            valid_types = list(sample_entry['disassemble_data'].keys())
            raise ValueError("Invalid bit value type [%s] requested. Valid types: %s"
                             % (valtype, ','.join(valid_types)))

        for tup in possible_tups:
            if tup in cls._datacache:
                # It is possible that with different naming revs some fields don't exist in all tracenames
                if field in cls._datacache[tup]['disassemble_data'][valtype]:
                    bit_data[tup] = cls._datacache[tup]['disassemble_data'][valtype][field]

            # Result was not found for this tupID, give it a valid default value
            if tup not in bit_data:
                bit_data[tup] = ''

        if single_val:
            return cls._single_val_from_dict(bit_data, '')

        return bit_data

    @classmethod
    def get_info(cls, name_or_list, field, include_invalid=False, single_val=False):
        """
        Get Finder info for the traces requested.
        :param name_or_list: Trace name string or list of strings/tup_ints to get data for
        :param field: Finder trace field like: tracename, tracepath, tags, etc
        :type field: str
        :param include_invalid: by default, only lookup values for valid traces.
        :type include_invalid: bool
        :param single_val: When provided, output a single string value. Useful for just a single input
        :type single_val: bool
        :return: map of tup_int to info requeseted. Format: data[tup_int] = <field_val>
        :rtype: dict or str
        """
        result = {}
        valid_tups = cls.is_valid(name_or_list) if not include_invalid else cls.exists(name_or_list)

        if not cls.is_valid_info_field(field):
            raise ValueError("Invalid tuple field [%s] requested" % field)

        for tup in valid_tups:
            result[tup] = cls._datacache[tup][field] if tup in cls._datacache else ''

        if single_val:
            return cls._single_val_from_dict(result, '')

        return result

    @classmethod
    def get_tuple(cls, name_or_list, single_val=False):
        """
        Take in a list of strings and see if they can turned into a tuple number. Does not check if these exist or
        are valid.  Does not preserve mapping, just returns all of the valid tuple_int found
        :return: set of valid tuple_ints
        :rtype: set
        """
        tup_map = cls.map_tuples(name_or_list)
        tups = {tup_int for tup, tup_int in list(tup_map.items()) if tup_int}  # Don't include 0, None, etc vals
        if single_val:
            return list(tups)[0] if len(tups) else ""
        return tups

    @classmethod
    def get_tuples_from_file(cls, filename):
        """
        Read through a file (like a Plist!) and extract all possible tuples that can be found. Query will not be called
        so an exists() check afterwards will be needed.
        :param filename: Fullpath to file to read tuples from
        :type filename: str
        :return: all of the tuples fround in the passed in file.
        :rtype: list
        """
        found = []
        # Loop through each line of the file, return tuple from a valid name or single integer
        for line in File(filename).chomp(comment='#'):
            tup = cls.get_tuple_from_line(line)
            if tup:
                found.append(tup)
        return found

    @classmethod
    def get_tuple_from_line(cls, line):
        """
        Primarily used for parsing Plists or stright trace lists.
        :param line: string line to read
        :type line: str
        :return: Tuple_int if line contains a valid Trace/Tuple, 0 otherwise
        :rtype: int
        """
        line = line.strip()
        # Empty Line
        if not line or line.isspace():
            return 0

        # Comment line
        if line.startswith('#') or line.startswith('//'):
            return 0

        if line.startswith('Pattern'):    # HDMT .plist
            line = line.replace('Pattern', '').strip()
        if line.startswith('Pat'):        # CMT.plist
            line = line.replace('Pat', '').strip()

        # Assume that the trace/tuple would be the first element of a line
        # Can be: 1) tuple_int, 2) trace name, 3) full trace path
        element1 = line.split()[0]
        return cls.int_tup(element1)

    @classmethod
    def get_disassemble_errors(cls):
        """
        Return a list of tuples that did not disassemble properly
        :rtype: list
        """
        return [tup for tup in cls._datacache if not cls._datacache[tup]['disassemble_data']['bit']]

    @classmethod
    def map_tuples(cls, name_or_list):
        """
         Take in a list of strings and see if they can turned into a tuple number. Does not check if these exist or
         are valid. Preserves mapping with the inputs. Invalid tuples/traces are assigned 0 for tuple_int.
         :return: dictionary mapping input to tuple_int
         :rtype: dict
        """
        if isinstance(name_or_list, (int, str)):
            search_list = [name_or_list]
        elif isinstance(name_or_list, (set, list, dict, tuple)):
            search_list = name_or_list
        else:
            raise TypeError("Cannot get tuple for type %s. Expecting int/str or list/set/dict/tuple of int/str"
                            % type(name_or_list))

        final = {}
        for tup in search_list:
            if not tup:
                continue

            final[tup] = cls.int_tup(tup)

        return final

    @classmethod
    def int_tup(cls, tup):
        """
        Convert to the actual tuple number for looking up data in the cache. Input must be a basic type like
        int or str.
        :raises: ValueError if cannot convert to int tuple
        :return: int version of the tuple. Returns 0 if can't be found
        :rtype: int
        """
        # Already an integer
        if isinstance(tup, int):
            return tup
        # Not a string, error
        if not isinstance(tup, str):
            raise TypeError("%s cannot be converted to tuple int. Must provide a string." % type(tup))

        # This will handle multiple sting formats like:
        #  1) 1234567
        #  2) g012345
        #  3) /p/tvpv/vep/prod/disks/d01/d2345677X111111_xo/d2345677_xxxx_xxxx.itpp
        #  4) /p/tvpv/vep/prod/disks/d01/i3456789X111111_xo/<somerandomFile>
        for tup_piece in [tup, basename(tup), basename(dirname(tup))]:
            res = cls._strtoint(tup_piece)
            if res:
                return res

        # Cannot determine any possible tuple ID. Return 0
        return 0

    @classmethod
    def clear_cache(cls):
        """Mostly used for unittests"""
        cls._datacache = _new_trace_cache()
        cls._valid_disassemble_fields = set()

    @classmethod
    def remote_copy(cls, name_or_list):
        """
        Copy Traces from remote sites to the current local site. This function is blocking, it will wait until
        the traces can be successfully queried locally before returning.
        """
        remote_data = cls.is_remote(name_or_list)
        remote_tups = [tup for tup in remote_data if remote_data[tup]]

        if not remote_tups:
            return

        env = cls._get_flash_or_vep()
        if env == 'vep':
            cls._remote_copy_vep(remote_tups)
        else:
            cls._remote_copy_flash(remote_tups)

        cls._wait_to_showup(remote_tups)

    @classmethod
    def _remote_copy_vep(cls, remote_tups):
        """
        Call VEP copy_entity.py to copy the remote traces to the current local site. Return immediately when the
        copy process has complete, don't wait for them to be queriable through Finder.
        :param remote_tups: tuples that should be copied
        :type remote_tups: list
        """
        site_map = cls.get_info(remote_tups, 'remote_site')
        sites = set([site_map[tup] for tup in site_map if site_map[tup]])

        errors = {}
        with TempDir(name=True) as tdir:
            for site in sites:
                site_tups = [str(tup) for tup in site_map if site_map[tup] == site]
                tup_file = join(tdir, 'copy.%s.tuples' % site)
                contents = '\n'.join(site_tups)
                File(tup_file).touch(contents)

                # This will copy traces to the xfer disk, but will not wait for them to show up in finder.
                # that could take 5min or 24hrs depending on xfer daemon load.
                from .shell import SystemCall  # Prevent circular imports
                copy_cmd = "copy_entity.py -save -from %s -tuple_list %s" % (site, tup_file)
                log.debug("Using Remote Copy cmd: %s" % copy_cmd)
                ecode, sout = SystemCall(copy_cmd).run_outtxt()
                if ecode:
                    errors[site] = sout + ". Sample Tuple: %s. Cmd: %s" % (site_tups[0], copy_cmd)
                # Error case for copy_entity where the ecode is not being set.
                elif 'RSYNC failed. Exiting' in sout:
                    errors[site] = sout + ". Sample Tuple: %s. Cmd: %s" % (site_tups[0], copy_cmd)

        if errors:
            raise SystemError("Failed to copy traces from %s sites. Reason: %s"
                              % (len(errors), '\n'.join(["Error %s: %s" % (site, errors[site]) for site in errors])))

    @classmethod
    def _remote_copy_flash(cls, remote_tups):
        """
        Call Flash <UNKNOWN CMD> to copy the remote traces to the current local site. Return immediately when the
        copy process has complete, don't wait for them to be queriable.
        :param remote_tups: tuples that should be copied
        :type remote_tups: list
        """
        pass

    @classmethod
    def _has_disassemble_data(cls, name_or_list):
        """
        Helper function to determine which tuples already have disassemble data filled in and don't need to be
        re-queried. Non-tuple names will be preserved in case the disassemble process can interpret them.
        """
        result = {}
        tup_map = cls.map_tuples(name_or_list)
        for tup_or_name in tup_map:
            tup = tup_map[tup_or_name]
            if tup:
                result[tup] = bool(tup in cls._datacache and len(cls._datacache[tup]['disassemble_data']['bit']))
            # Tuple couldn't be found. But this can be OK when providing "sample" tracenames for disassembly
            else:
                result[tup_or_name] = False
        return result

    @classmethod
    def _disassemble_traces(cls, name_or_list):
        """
        Do a commandline call to get the bit level info for traces.
        """
        is_disassembled = cls._has_disassemble_data(name_or_list)
        tup_map = cls.map_tuples(name_or_list)

        # Don't re-disassemble tuples we already have data for, just the ones we haven't seen yet
        need_data_tups = [x for x in is_disassembled if not is_disassembled[x]]
        known_tracenames = list(cls.get_info(need_data_tups, 'tracename').values())
        unknown_tracenames = [x for x in tup_map if not tup_map[x]]  # Can't determine what to do, VEP/Flash might

        env = cls._get_flash_or_vep()
        if env == 'vep':
            # For VEP, pass in all known/unknown tracenames.  name_disassemble.py won't throw an error.
            new_data = cls._disassemble_vep(set(known_tracenames + unknown_tracenames))
        else:
            # Flash doesn't handle unknown tracenames
            new_data = cls._disassemble_flash(known_tracenames)

        for tup in new_data:
            cls._datacache[tup]['disassemble_data'].update(new_data[tup])

    @classmethod
    def _disassemble_vep(cls, tracenames):
        """
        Call name_disassemble.py on the commandline to get trace-bit data. For bulk lookup, name_disassemble requires
        full tracenames rather than just tuple numbers.
        :param tracenames: collection of string tracenames
        :type tracenames: set
        :return: bit and human-readable data found.
                Format:
                    data[tup_int] = {'bit': {'tuple': '000123', 'traceprefix': 'd', 'module': 'F', ...},
                                    'full': {'tuple': '000123', 'traceprefix': 'Debug', 'module': 'MFunc', ...},
        :rtype: dict
        """
        # Nothing to do, don't run name_disassemble.py
        if not tracenames:
            return {}

        # Write tuples to a file to pass to finder.  This is much safer with large searches to ensure that it
        # doesn't overwhelm the cmdline character count
        with TempDir(name=True) as tdir:
            trace_file = join(tdir, 'disassemble_trace_list.txt')
            contents = '\n'.join(tracenames)
            File(trace_file).touch(contents)
            disassemble_cmd = "name_disassemble.py -list %s -csv" % trace_file

            from .shell import SystemCall  # Prevent circular imports
            ecode, sout = SystemCall(disassemble_cmd).run_outtxt()

        if ecode and not cls._continue_on_error:
            raise SystemError("Unable to call name_disassemble.py. Reason: %s" % sout)

        data = {}
        for line in sout.split('\n'):
            # Skip empty lines
            if not line or line.isspace():  # pragma: no cover
                continue

            # Expected Format:
            # <name>,bit,traceprefix=d,tuple=0041685,testfamily=H,tid=0631170,chunknum=aa
            # <name>,full,traceprefix=Debug,tuple=0041685,testfamily=HSW,tid=0631170,chunknum=aa
            entries = line.split(',')
            if len(entries) > 2:
                tracename = entries[0]
                valtype = entries[1]  # should be 'bit' or 'full'
                tup_int = cls.int_tup(tracename)

                # Initialize data
                if tup_int not in data:
                    data[tup_int] = {}
                data[tup_int][valtype] = {}

                for pair in entries[2:]:
                    if '=' in pair:
                        field, val = pair.strip().split('=')
                        if field == 'chunknum' and valtype == 'full':
                            data[tup_int][valtype][field] = Base3844.decode(val)  # Convert bits like 'aa' to int 100
                        else:
                            data[tup_int][valtype][field] = val
                        cls._valid_disassemble_fields.add(field)  # Record fields seen for future checks

        return data

    @classmethod
    def _disassemble_flash(cls, tracenames):
        """
        Call flash_disassemble on the cmdline to get the trace-bit data. Flash does not handle unknown or sample
        tracenames so only pass in valid tracenames from valid tuples.
        :param tracenames: collection of string tracenames
        :type tracenames:
        :return: bit and human-readable data found.
                Format:
                    data[tup_int] = {'bit': {'tuple': '000123', 'traceprefix': 'd', 'module': 'F', ...},
                                    'full': {'tuple': '000123', 'traceprefix': 'Debug', 'module': 'MFunc', ...},
        :rtype: dict
        """
        if not tracenames:
            return {}

        cls.set_flash_prod()
        prod = cls._flash_prod
        # Write tracenames to a file to pass to Flash.  This is much safer with large searches to ensure that it
        # doesn't overwhelm the cmdline character count
        with TempDir(name=True) as tdir:
            trace_file = join(tdir, 'flash_disassemble_trace_list.txt')
            flash_json = join(tdir, "flash_out.json")
            contents = '\n'.join(tracenames)
            File(trace_file).touch(contents)
            flash_cmd = "flash_name_disassemble --prod %s --name_list %s --out %s" % (prod, trace_file, flash_json)

            from .shell import SystemCall  # Prevent circular imports
            ecode, sout = SystemCall(flash_cmd).run_outtxt()
            if (ecode and not cls._continue_on_error) or not exists(flash_json):
                errors = [x for x in sout.split('\n') if re.search('Error', x, re.IGNORECASE)]
                msg = '\n'.join(errors) if errors else sout
                raise SystemError("Unable to call Flash Disassemble. Reason: %s" % msg)

            with open(flash_json) as fh:
                results = json.load(fh)

        data = {}
        for t_name in results:
            # Flash Error case Json:
            # <tname>: null
            if not results[t_name]:
                continue
            tup_int = int(results[t_name]['tuple']['val'])
            data[tup_int] = {'bit': {}, 'full': {}}
            for field in results[t_name]:
                # Skip the underscore separators
                if 'underscore' in field:
                    continue
                data[tup_int]['bit'][field] = results[t_name][field]['val']
                data[tup_int]['full'][field] = results[t_name][field]['desc']

                # TODO: When FLash makes an update, this will no longer be needed and we can just use 'desc' value
                # and delete this if-block
                if field == 'chunknum':
                    data[tup_int]['full'][field] = Base3844.decode(results[t_name][field]['val'])

                cls._valid_disassemble_fields.add(field)

        return data

    @classmethod
    def _query_traces(cls, tup_list, refresh=False):
        """
        Make a cmdline call to finder or flash_search to get trace info.  Update the _datacache with the results
        :param tup_list: list of tuple_int that have already been converted to IDs
        :param refresh: Query for tuples already in cache as well and update their entries
        :type refresh: bool
        """
        start = time()
        missing = [x for x in tup_list if x not in cls._datacache]
        query_list = tup_list if refresh else missing
        if query_list:
            env = cls._get_flash_or_vep()
            if env == 'vep':
                new_data = cls._query_vep(query_list)
            else:
                new_data = cls._query_flash(query_list)

            # Cache the trace data found so that it won't be looked up in the future
            not_found = [tup for tup in query_list if tup not in new_data]
            cls._update_cache(new_data, not_found)
            query_end_time = time()
            log.dev(" * Trace Query Took: %f s" % (query_end_time - start))

            # Call disassemble to cache that data as well
            cls._disassemble_traces(query_list)
            log.dev(" * Disassemble Took: %f s" % (time() - query_end_time))

    @classmethod
    def _query_flash(cls, tup_list):
        """
        Query tuple data using flash_search in the Flash env.
        :param tup_list: list of tuples to pass to flash_search. Requires tuple ints.
        :type tup_list: list
        :return: finder data for each tuple found.
            Format:
                data[tup_int] = {'tracename': <basename>, 'tracepath': <fullpath>, 'remote': True, tags: []}
        :rtype: dict
        """
        # Nothing to do, don't query finder.
        if not tup_list:
            return {}

        cls.set_flash_prod()
        # Write tuples to a file to pass to finder.  This is much safer with large searches to ensure that it
        # doesn't overwhelm the cmdline character count
        with TempDir(name=True) as tdir:
            tup_file = join(tdir, 'flash_tuple_list.txt')
            flash_json = join(tdir, "flash_out.json")
            contents = '\n'.join([str(tup) for tup in tup_list])
            File(tup_file).touch(contents)
            flash_cmd = "flash_search --prod %s --out %s --verbose trc " \
                        "--search_list %s --search_mode tuple" % (cls._flash_prod, flash_json, tup_file)

            from .shell import SystemCall  # Prevent circular imports
            ecode, sout = SystemCall(flash_cmd).run_outtxt()
            if (ecode and not cls._continue_on_error) or not exists(flash_json):
                errors = [x for x in sout.split('\n') if re.search('Error', x, re.IGNORECASE)]
                msg = '\n'.join(errors) if errors else sout
                raise SystemError("Unable to call Flash Search. Reason: %s" % msg)

            with open(flash_json) as fh:
                results = json.load(fh)

        data = {}
        for row in results:
            tup_int = int(row['tuple'])
            data[tup_int] = {
                'tuple_int': tup_int,
                'tracepath': row['path'],
                'tracename': row['name'],
                'tags': row['tag'],
                'lineitem': row['lineitem'],
                'exists': True,
                'valid': row['valid'],

                # TODO: Fill in Flash remote stuff
                'remote': False,
                # 'remote_site': remote_site,
            }

        return data

    @classmethod
    def _query_vep(cls, tup_list):
        """
        Query tuple data using finder.py in the VEP env.
        :param tup_list: list of tuples to pass to finder. Safest is simply tup_int values.
        :type tup_list: list
        :return: finder data for each tuple found.
            Format:
                data[tup_int] = {'tracename': <basename>, 'tracepath': <fullpath>, 'remote': True, tags: []}
        :rtype: dict
        """
        # Nothing to do, don't query finder.
        if not tup_list:
            return {}

        # Write tuples to a file to pass to finder.  This is much safer with large searches to ensure that it
        # doesn't overwhelm the cmdline character count
        with TempDir(name=True) as tdir:
            tup_file = join(tdir, 'finder_tuple_list.txt')
            contents = '\n'.join([str(tup) for tup in tup_list])
            File(tup_file).touch(contents)
            finder_cmd = "finder.py -list %s -db all" % tup_file

            from .shell import SystemCall  # Prevent circular imports
            ecode, sout = SystemCall(finder_cmd).run_outtxt()

        if ecode:
            # If no traces found, finder.py returns an error code, but this is an OK case. Contains only
            # INFO messages
            errors_found = [x for x in sout.split('\n')
                            if not re.search(r'^\s*$', x) and not re.search(r"\s*INFO:", x)]
            if errors_found:
                raise SystemError("Unable to call finder.py. Reason: %s." % sout)

        remote_site = ''
        data = {}
        for line in sout.split('\n'):
            # Skip empty lines
            if not line or line.isspace():  # pragma: no cover
                continue

            # Grab the remote site name from the INFO messages
            if re.search(r"\s*INFO:", line):
                m = re.search(r"Results from '(\w+)'", line)
                if m:
                    remote_site = m.group(1)
                elif 'Results from local site' in line:
                    remote_site = ''

                # Ignore all other INFO messages
                continue  # pragma: no cover

            # Standard Format: <full trace path> : [tag1,tag2]
            fields = line.split(':')
            if len(fields) == 2:
                t_path = fields[0].strip()
                tags = fields[1].strip().replace('[', '').replace(']', '').split(',')
                int_tup = cls.int_tup(t_path)

                if int_tup:
                    # Keep local data if it has already been seen. Otherwise update with 'latest seen'.
                    if int_tup not in data or data[int_tup]['remote']:
                        lineitem_tags = [x for x in tags if x.startswith('LI_')]
                        lineitem = lineitem_tags[0].replace('LI_', '') if lineitem_tags else ''
                        data[int_tup] = {
                            'tuple_int': int_tup,
                            'tracepath': t_path,
                            'tracename': basename(t_path),
                            'tags': tags,
                            'lineitem': lineitem,
                            'exists': True,
                            'valid': False if 'PDE_INVALID' in tags else True,
                            'remote': bool(remote_site),
                            'remote_site': remote_site,
                        }

        return data

    @classmethod
    def _update_cache(cls, data, not_found):
        """
        Update the class datacache with new data discovered by the VEP/Flash queries.
        :param data: New data rows to update the cache with. Expected format:
                        data[tup_int] = {'path': <fullpath>, 'name': <g000000V111111_cxxxx.itpp>,
                                         'tags': ['PDE_INVALID', 'DRVtag'], remote: True, remote_site: 'SC'
                                         }
        :type data: dict
        :param not_found: Tuple IDs that could not be found in the central DB. Cache so we don't keep querying for them
        :type not_found: list
        """
        for tup in data:
            cls._datacache[tup].update(data[tup])
            cls._datacache[tup]['tuple_int'] = tup
            cls._datacache[tup]['exists'] = True
            if 'valid' not in data[tup]:
                cls._datacache[tup]['valid'] = False if 'PDE_INVALID' in cls._datacache[tup]['tags'] else True
            if 'disassemble_data' in data[tup]:
                for bit_type in data[tup]['disassemble_data']:
                    cls._valid_disassemble_fields.update(list(data[tup]['disassemble_data'][bit_type].keys()))

        for tup in not_found:
            cls._datacache[tup]['tuple_int'] = tup
            cls._datacache[tup]['exists'] = False

    @classmethod
    def _wait_to_showup(cls, name_or_list, timeout=5 * 60, sleep_amt=2.0, report_interval=10):
        """
        Wait (blocking) until request traces so up as local after a copy operation has been initiated. Raise
        an error if not completed by the timeout amount
        :param name_or_list: traces to wait for
        :param timeout: timeout in seconds for when to give up checking for all copies to show up
        :type timeout: float
        :param sleep_amt: number of seconds to sleep between checks
        :type sleep_amt: float
        :param report_interval: number of iterations bewteen log reporting
        :type report_interval: int
        """
        done = False
        start_t = time()
        count = 0
        remote_tups = []
        while not done and (time() - start_t) < timeout:
            count += 1
            cls._query_traces(name_or_list, refresh=True)  # Refresh the Trace data cache
            remote_data = cls.is_remote(name_or_list)
            remote_tups = [tup for tup in remote_data if remote_data[tup]]
            # No valid tuples passed in
            if not remote_data:
                done = True

            if remote_tups:
                # Periodically report out
                if count % report_interval == 0:
                    log.info("TraceInfo: Waiting for %s tuple(s) to show up. Example: %s"
                             % (len(remote_tups), remote_tups[0]))

                sleep(sleep_amt)
            else:
                done = True

        if not done:
            raise SystemError("Error: %s Traces were copied but haven't shown up. Example: %s"
                              % (len(remote_tups), remote_tups[0]))

    @classmethod
    def _is_vep(cls):
        """Is this the VEP environmnet"""
        vep_path = os.getenv('VEP2_ROOT', '')
        return bool(vep_path)

    @classmethod
    def _is_flash(cls):
        """Is this the Flash environmnet"""
        flash_path = os.getenv('FLASH_INSTALL_DIR', '')
        return bool(flash_path)

    @classmethod
    def _get_flash_or_vep(cls):
        if cls._is_flash():
            return 'flash'
        elif cls._is_vep():
            return 'vep'

        raise TupleDataError("Unable to determine VEP vs Flash. Please source a valid product ENV.")

    @classmethod
    def set_continue_on_error(cls, flag):
        """
        If disassemble throws an error on some traces, keep going. This can happen when
        a few bad traces are mixed in with some good ones. Defaults to off so errors stop execution.
        :param flag:
        :type flag: bool
        """
        cls._continue_on_error = bool(flag)

    @classmethod
    def set_flash_prod(cls, prod_override='', refresh=False):
        """
        All Flash commands require a --prod <prd> commandline switch, but there is nothing guarenteed to be in the
        Environment. Search the best we can.
        :param prod_override: Directly provide the prd value that should be used. No searching required
        :type prod_override: str
        :param refresh: Force to requery the Flash product and reset the value
        :type refresh: bool
        """
        env_vars = ['FLASH_PROD', 'TCG_PROD']
        if prod_override:
            cls._flash_prod = prod_override

        # This check ensures future calls don't reset a prod_override
        elif not cls._flash_prod or refresh:
            for env_var in env_vars:
                if os.getenv(env_var, ''):
                    cls._flash_prod = os.getenv(env_var)

        if not cls._flash_prod:
            raise EnvironmentError("Unable to find a Product to use for Flash commands. Please set one of %s "
                                   "environment variables or contact your Flash admins for "
                                   "support." % ','.join(env_vars))

    @staticmethod
    def _strtoint(tupstr):
        """Converts a string tuple to an integer tuple. Copied from VEP TracePathBase"""
        tupstr = tupstr.strip()
        if tupstr.isdigit():
            return int(tupstr)

        # string - with character
        if tupstr[1:].isdigit():
            return int(tupstr[1:])

        # string - full name
        if tupstr[1:8].isdigit():
            return int(tupstr[1:8])

        return None

    @staticmethod
    def _single_val_from_dict(dd, default=None):
        """Simple helper function to make returning a single value easier for get_* functions"""
        return dd[list(dd.keys())[0]] if dd else default
