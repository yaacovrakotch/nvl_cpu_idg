#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Pin&Soc file module

This module is *independent* from the rest of the TP modules.

Independent Usage:
   pin = PinSoc(None)
   pin.set_data(file.pin)
   pin.<operations>
"""
from gadget.errors import ErrorInput, ErrorCockpit, confirm
from gadget.tputil import remove_ip, ip_tuple, OtplFile
from gadget.strmore import sha1
from collections import defaultdict
from os.path import join, dirname, basename
import re
import glob


class PinSoc:
    """storage of pin data"""

    def __init__(self, tpobj):
        """Initialize PinSoc with empty data structures.

        :param tpobj: TestProgram object providing TP context, or None for standalone use
        :type tpobj: tp.testprogram.TestProgram or None
        """
        self._resource = None    # {resource: [pins]}
        self._groups = None      # {name: [pins]}
        self._domain = None      # {name: [pins]}
        self._pinset = None      # set of all pin resources
        self._pinfiles = None    # set of read pinfiles
        self._soc = {}           # {socfile: <data>}, populated in read_soc()
        self.tpobj = tpobj

    def set_data(self, pinfile=None):
        """
        Populate data structures. This is not called automatically in pickle_init().
        This can be called with a specific pin file for adhoc pin processing
        """
        if pinfile:
            self._resource = None

        if self._resource:
            return    # Do nothing if initialized already

        self._resource = {}
        self._groups = {}
        self._domain = {}
        self._pinset = set()
        self._pinfiles = set()

        if pinfile:
            self._read_pin(pinfile)
        else:
            # Do not load module level .pin
            for ff in (x for x in self.tpobj.get_import_files('pin') if '/Modules/' not in x):
                self._read_pin(ff)

        # derived attributes
        for item in self._resource:
            self._pinset.update(remove_ip(x) for x in self._resource[item])

        # Add group names without scoping for use in local context
        for name in list(self._groups):
            if remove_ip(name) not in self._groups:
                self._groups[remove_ip(name)] = self._groups[name]

        # Do check
        self._check_flat_all()

        for pin in self._pinset:
            # Reason for this check: There is assumption flatten() and get_pin2domain() that raw resource has no scoping
            assert ':' not in pin, f'Error: [{pin}] is a resource. Expecting no scoping.'

    def _check_flat_all(self):
        """
        Check all groups and domains that they can be flattened
        That is, make sure all pins are defined in all pingroups
        """
        total = 0
        cnt = 0
        for pg in self._domain.keys() | self._groups.keys():
            cnt += 1
            total += len(list(self.flatten(pg)))
        return cnt, total

    def _read_pin(self, fname, ip=''):
        """Read the pin file"""
        resource = None
        group = None
        pindesc = None
        domain = None
        domaindef = None

        # Do not re-read already read files
        if fname in self._pinfiles:
            return
        self._pinfiles.add(fname)

        for lno, line in OtplFile(fname).readline():
            if line.startswith(('{', 'Version', 'DefaultPowerDomain')):
                pass  # Do nothing

            # closure
            elif line == '}':
                if group:       # This must be in correct order
                    group = None
                elif resource:
                    resource = None
                elif domain:
                    domain = None
                elif domaindef:
                    domaindef = None
                elif pindesc:
                    pindesc = None
                else:
                    raise ErrorInput(f"Mismatched closed parenthesis in line#{lno} at {fname}")

            elif line == 'PinDescription':
                pindesc = True

            elif line in ('DomainDefinitions', 'PowerDomainDefinitions', 'ThermalDomainDefinitions', 'SerialCaptureDomainDefinitions'):
                domaindef = True

            elif line.startswith('IPPinDescription '):
                _, target_ip, fn = line.replace(';', '').split()
                self._read_pin(join(dirname(fname), fn.replace('"', '')), f'{target_ip}::')

            elif line.startswith('Resource '):
                resource = f'{ip}{line.split()[1]}'
                assert resource not in self._resource, f"Resource {resource} is defined twice, 2nd occurrence in line#{lno} at {fname}"
                self._resource[resource] = []

            elif line.startswith('Group '):
                group = f'{ip}{line.split()[1]}'
                assert group not in self._groups, f"Group {group} is defined twice, 2nd occurrence in line#{lno} at {fname}"
                self._groups[group] = []

            elif line.startswith('SCDomain '):
                domain = f'SCDomain::{ip}{line.split()[1]}'
                assert domain not in self._domain, f"Domain {domain} is defined twice, 2nd occurrence in line#{lno} at {fname}"
                self._domain[domain] = []

            elif line.startswith(('Domain ', 'ThermalDomain ', 'PowerDomain ')):
                domain = f'{ip}{line.split()[1]}'
                assert domain not in self._domain, f"Domain {domain} is defined twice, 2nd occurrence in line#{lno} at {fname}"
                self._domain[domain] = []

            elif domain:
                self._domain[domain].extend([x.strip() for x in line.split(',') if x.strip()])

            elif group:
                self._groups[group].extend([x.strip() for x in line.split(',') if x.strip()])

            elif resource:
                self._resource[resource].extend([x.strip() for x in line.split(';') if x.strip()])

            else:
                raise ErrorCockpit(f"Unknown pin line: [{line}] at line#{lno} at {fname}")

    def get_resource(self, resource):
        """Return the set of pins given the resource name (lowercase)"""
        assert resource == resource.lower(), f'Input resource={resource} must be lowercase'
        result = set()
        for res in self._resource:
            fres = res.split('.')[-1].lower()
            if fres == resource:
                result.update(self._resource[res])
        return result

    def get_resources(self):
        """Return the resource dictionary"""
        return self._resource

    def get_groups(self):
        """Return the groups dictionary"""
        return self._groups

    def get_domains(self):
        """Return the domain dictionary"""
        return self._domain

    def flatten(self, pin_or_group, strip_ip=False):
        """Iterator: yield a list of flattened pins given pin_or_group"""
        found = False
        if remove_ip(pin_or_group) in self._pinset:
            # It is a resource
            found = True
            if strip_ip:
                yield remove_ip(pin_or_group)
            else:
                yield pin_or_group

        else:
            # It is a pingroup
            for dd in (self._groups, self._domain):
                if pin_or_group in dd:
                    for pg in dd[pin_or_group]:
                        for pin in self.flatten(pg, strip_ip):
                            found = True
                            if strip_ip:
                                yield remove_ip(pin)
                            else:
                                yield pin

        if not found:
            raise ErrorInput(f'[{pin_or_group}] is not found in any domain/resource/group')

    def get_pin2domain(self):
        """Return dictionary of {pin: {set_of_domains}} mapping. ip is removed."""
        result = defaultdict(set)
        for domain in self._domain:
            for pg in self._domain[domain]:
                for pin in self.flatten(pg):
                    result[remove_ip(pin)].add(remove_ip(domain))
        return dict(result)     # make it non-default dict so keys error if not found

    def get_pin2ip(self):
        """Return dictionary of {pin: ip} map"""
        result = {}

        # do domain first
        for domain in self._domain:
            for pg in self._domain[domain]:
                for pin in self.flatten(pg):
                    self._assign_ip(result, pin)

        # do resources
        for res in self._resource:
            for pin in self._resource[res]:
                self._assign_ip(result, pin)

        # do groups
        for res in self._groups:
            for pin in self._groups[res]:
                self._assign_ip(result, pin)

        return result

    def _assign_ip(self, result, pin):
        """Assign ip and name into result"""
        ip, name = ip_tuple(pin)
        if name in result:
            is_invalid = bool(ip and result[name] and ip != result[name])
            assert not is_invalid, f'pin {pin} is in two IP: {result[name]} vs {ip}'
        result[name] = ip   # ok to reassign

    def is_resource(self, pin):
        """Returns True if pin is a resource"""
        return remove_ip(pin) in self._pinset

    def get_soc_sha(self):
        """
        Returns 6-digit-sha for use in folder
        Will read all .soc files
        """
        socpath = f'{self.tpobj.tpldir}/Shared*/*/*.soc'
        socfiles = glob.glob(socpath) + glob.glob(f'{self.tpobj.tpldir}/*.soc')
        confirm(len(socfiles), f'No .soc files found: {socpath}', 'Pls check path')
        result = [self.sha_otpl(f) for f in sorted(socfiles, key=lambda x: basename(x))]
        finalsha = sha1('\n'.join(result))
        return finalsha[:6]

    @classmethod
    def sha_otpl(cls, fname):
        """
        Return the sha of cleaned up .soc or any otpl files

        Clean up is:
        1. removal of empty lines
        2. removal of leading and trailing spaces
        3. replacement of 2 or more contiguous spaces to 1
        """
        robj = re.compile(r'\s\s+')
        result = []
        for _, line in OtplFile(fname).readline():    # empty lines is removed here
            line = line.strip()                       # remove both leading and trailing space
            line = robj.sub(' ', line)                # remove extra spaces
            result.append(line)

        finaltext = '\n'.join(result)
        return sha1(finaltext)

    def read_soc(self, fname):
        """
        Read the socket file

        :return: dictionary: {pin_no_ip: {ip: <IP_CPU|IP_PCH>,
                                          u: <bool>,
                                          ch: <channel>,
                                          resource: <resource>,
                                          dut: <dut>}
        """
        socketdef = None
        dut = None
        resource = None
        result = {}
        for lno, line in OtplFile(fname).readline():
            if line.startswith(('{', 'Version', 'PinDescription')):
                pass  # Do nothing

            # closure
            elif line == '}':
                if resource:        # This must be in correct order
                    resource = None
                elif dut:
                    dut = None
                elif socketdef:
                    socketdef = None
                else:
                    raise ErrorInput(f"Mismatched closed parenthesis in line#{lno} at {fname}")

            elif line == 'SocketDef':
                socketdef = True

            elif line.startswith('DUT '):
                dut = line.split()[1]

            elif line.startswith('Resource '):
                resource = line.split()[1]

            elif resource:
                dataline = line.split(';')[0]
                unconnected = bool('[U]' in dataline)
                dataline = dataline.replace('[U]', '')
                pin, channel = dataline.split()
                pin_noip = remove_ip(pin)
                ip = pin.split(':')[0] if ':' in pin else ''
                assert pin_noip not in result, f'[{pin_noip}] is redefined in line#{lno} at {fname}'
                result[pin_noip] = {'ip': ip,
                                    'u': unconnected,
                                    'ch': channel,
                                    'resource': resource,
                                    'dut': dut}

            else:
                raise ErrorCockpit(f"Unknown soc line: [{line}] at line#{lno} at {fname}")

        self._soc[basename(fname)] = result
        return result
