#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
pingroups.py - pingroup management

# Create a new pingroup
CMD> pingroup.py <prodname> -name <pingroup_name> -new <file_pin_list> -why <reason_for_pingroup>

# Remove a pin from pingroup
CMD> pingroup.py <prodname> -name <pingroup_name> -deletepin <pinname>

# Update the pingroup
Step1: dump the contents of pingroup to a file
CMD> pingroup.py <prodname> -name <pingroup_name> -dump <out_file>
Step2: edit <out_file>
Step3: Confirm your edits are ok
CMD> pingroup.py <prodname> -name <pingroup_name> -modify <out_file> -diff
Step4: update it
CMD> pingroup.py <prodname> -name <pingroup_name> -modify <out_file> -why <reason_for_change>

# Initial creation of product
CMD> pingroups.py <prodname> -set_pins <pin_list.txt> -i_am_tpi
CMD> pingroups.py <prodname> -upload_pingroup <pingroup_tab.csv>

"""
import setenv      # must be first in the imports
from gadget.vepargs import Args
from gadget.vepargs import TA_All, TA_StoreFile, TA_Store, TA_StoreTrue, TA_AppendSC
from gadget.errors import ErrorInput, ErrorUser, ErrorVepBase
from gadget.pylog import log
from gadget.helperclass import OPT
from gadget.dictmore import DictDot
from gadget.sepshelve import SqlDict
from gadget.files import File, TempDir
from gadget.shell import USERNAME, SystemCall, fullcmdline, HOSTNAME
from gadget.strmore import curtime, to_ascii, indent, sha1, cjoin
from gadget.printmore import PrintAlign, Dumper
from gadget.helperclass import IS_UT
from gadget.disk import mkdirs
from gadget.gizmo import Elapsed, MockVar
from unittest.mock import Mock
from os.path import join, dirname, exists
from mod.setting import cfg
import csv
import os
import re
import sys
import time


class ErrorCheck(ErrorUser):
    """Error class for caught checks"""
    pass


class PinGroups(object):
    """
    pg = PinGroups('mtl_class_p')

    pingroups = pg.get_pingroups()
    pinlist = pg.get_pinlist(group_name)
    all_pins_set = pg.get_all_pins()
    """

    def __init__(self, prodname, readonly=False, dupcheck=True):
        self.dupcheck = dupcheck
        self.prodname = prodname
        self.dbfile = f'{cfg.pingroup}/{prodname}.sqlite'
        if not exists(self.dbfile) and (not OPT.i_am_tpi):
            valid = [x.replace('.sqlite', '') for x in os.listdir(dirname(self.dbfile)) if not x.startswith('READ') and '.sqlite' in x]
            raise ErrorInput("%s is not valid product. Valid products are %s" % (prodname, valid),
                             "Pls update your command")

        if readonly:
            # put everything in memory - fast access
            self.db = {x[0]: x[1] for x in SqlDict(self.dbfile).items()}
        else:
            # normal
            self.db = SqlDict(self.dbfile)
        self.ipmap = self.read_pin_ip()    # {pin: IP_CPU|IP_PCH|None}

    def _read_file(self, filename, all_pins, valid_groups, pingroup, resource, dupok=False):
        """
        Read filename and return list of pins

        :param filename: filename_path
        :param all_pins: set of all_pins from db (with or without scope)
        :param valid_groups: set of valid groups
        :param pingroup: pingroup name
        :param resource: resource name
        :param dupok: Set to True to accept duplicate pin
        :return: list of pins
        """
        pins = []
        valid_pins = {self.get_pin_only(x) for x in all_pins}
        for line in File(filename).chomp(strip=True):
            if not line:
                continue
            for pin in line.replace('+', ' ').replace('-', ' ').split(' '):      # can be group1-group2+group3
                if not pin:
                    continue

                # need to check if all pins are valid
                pinonly = self.get_pin_only(pin)
                if pinonly not in valid_pins and pin not in valid_groups:
                    raise ErrorCheck("Provided pin/pingroup [%s] is not valid." % pin,
                                     "Run the following to get valid pins: "
                                     "pingroups.py -pinlist")

                # check if scoping is not correct
                iponly = self.get_ip_only(pin)
                if self.ipmap.get(pinonly) and iponly and self.ipmap[pinonly] != iponly:
                    raise ErrorCheck("Provided pin [%s] has incorrect scoping: %s"
                                     "" % (pin, iponly),
                                     "Expected scope: %s. Pls fix your pingroup" % self.ipmap[pinonly])

            if line in pins and (not dupok):
                raise ErrorCheck("pin %s is duplicated in %s" % (pin, pingroup),
                                 "Remove duplicate pin.")
            pins.append(line)

        # Do the checks
        if resource != 'DOMAIN':
            # self.check_scoping(pins, pingroup)     # Mixed scoping is not allowed
            self.check_lowercase(pingroup, pins)
            self.check_dieletname(pingroup, pins)
            self.check_unscoped(pingroup, pins)
            self.check_belong(pingroup, pins)
            self.check_pkg_but_iponly(pingroup, pins)
            self.check_duplicate_content(pingroup, pins)

        return pins

    def check_duplicate_content(self, pingroup, pins):
        """
        Check if pingroup is duplicate
        If intended, then add '_dup' in name

        :param pingroup: pingroup name
        :param pins: list of pins
        :return: None
        """
        if not self.dupcheck:
            return

        if len(pins) == 1:
            return    # alias is ok

        if OPT.force == self.code(pingroup):
            return

        dbcopy = {x[0]: x[1] for x in self.db.items()}   # cannot move this out of this routine!
        for name in sorted(self.get_pingroups(dbcopy)):
            data = dbcopy[dbcopy[name]]
            if set(data['pinlist']) == set(pins) and name != pingroup:
                raise ErrorCheck("pingroup [%s] has exact pin content as [%s]." % (pingroup, name),
                                 "If you still want your own pingroup, add [-force %s] "
                                 "to bypass this duplicate pingroup check." % self.code(pingroup))

    def check_pkg_but_iponly(self, pingroup, pins):
        """
        Check if pkg pingroup but 100% ip

        :param pingroup: pingroup name
        :param pins: list of pins
        :return: None
        """
        no_check = set('''ut_except
        pkg_enclk_all pkg_hpclk_all
        '''.split())
        dielet = pingroup.split('_')[0]
        if pingroup in no_check:
            return
        if dielet != 'pkg':   # This check is only for pkg pingroup
            return

        prev = None
        for pin in pins:
            ip = self.ipmap.get(pin, 'unscoped')
            if prev is None:
                prev = ip
            else:
                if prev != ip:
                    return   # Success, mixed ip

        if prev in ('IP_CPU', 'IP_PCH'):
            raise ErrorCheck("pingroup [%s] is pkg, but pins is 100%% %s" % (pingroup, prev),
                             "Do you really mean to use pkg?")

    def check_belong(self, pingroup, pins):
        """
        Check if pins belong to correct dielet

        :param pingroup: pingroup name
        :param pins: list of pins
        :return: None
        """
        no_check = set('''ut_except
        '''.split())
        md = {'cpu': 'IP_CPU'}
        dielet = pingroup.split('_')[0]
        if IS_UT:    # unittests does not have dieletname
            return
        if pingroup in no_check:
            return
        if dielet in ('pkg', 'soc'):
            return    # no checking necessary
        if self.is_pin_wrapper(pingroup, pins):    # no need to check
            return

        for pin in pins:
            ip = self.ipmap.get(pin)
            if ip == 'IP_CPU' and dielet in ('cpu', 'mpkg', 'ppkg'):
                continue
            if ip == 'IP_PCH' and dielet in ('gcd', 'ioe', 'ioem', 'ioep', 'adm', 'mpkg', 'ppkg'):
                continue
            if ip is None:
                continue

            raise ErrorCheck('Error: pin [%s] has scoping [%s] in pingroup=%s'
                             '' % (pin, ip, pingroup),
                             '[%s] should only contain %s' % (dielet, md.get(dielet, 'IP_PCH')))

    def check_unscoped(self, pingroup, pins):
        """
        Check if pins have scoping. There should be none, except for pinwrappers

        :param pingroup: pingroup name
        :param pins: list of pins
        :return: None
        """
        no_check = set('''ut_except
        cpu_all cpu_fab_all cpu_tap_all
        gcd_all gcd_fab_all gcd_tap_all
        ioem_all ioem_fab_all ioem_tap_all
        ioep_all ioep_fab_all ioep_tap_all
        pkg_all pkg_fab_all pkg_tap_all
        mpkg_all ppkg_all
        soc_all soc_fab_all soc_tap_all
        all_clk_pin_mtl all_dpin_mtl all_hpc_pin_mtl
        ioe_allwoec_lvl
        pkg_all_hcdps pkg_fab_in_timing pkg_all_lcdps pkg_fab_in_timing pkg_tap_out_timing
        soc_allwoec_lvl soc_dielet_dpins
        '''.split())
        if pingroup in no_check:
            return
        if self.is_pin_wrapper(pingroup, pins):    # no need to check
            return
        for pin in pins:
            if ':' in pin:
                raise ErrorCheck('pin [%s] has scoping in pingroup=%s'
                                 '' % (pin, pingroup),
                                 'There should be no scoping inside pingroup.')

    def check_dieletname(self, pingroup, pins):
        """
        Check if first element is dielet name

        :param pingroup: pingroup name
        :param pins: list of pins
        :return: None
        """
        dielets = set('cpu gcd ioe ioem ioep soc adm pkg mpkg ppkg'.split())

        no_check = set('''ut_except
        all_dpin_domainless_pins all_dpin_pins all_edm all_fab_dpin all_hcdps all_lcdps all_tap_dpin dftring_in dftring_out hvm_init_pins misc_tap tap_all_jtag tap_in view_analog
        jtag_aux_pins lya_pins mtl68_cores stf_in stf_out surgeon_alllc_1p0_group surgeon_alllc_1p8_group viewana_pins viewdig_pins
        all_clk_pin_mtl all_dpin_mtl all_hpc_pin_mtl
        '''.split())

        if IS_UT:    # unittests does not have dieletname
            return
        if pingroup in no_check:
            return
        if self.is_pin_wrapper(pingroup, pins):    # no need to check
            return
        dielet = pingroup.split('_')[0]    # lower() is for domain names
        if dielet in dielets:
            return
        if len(pins) == 1:
            return     # pin wrappers are accepted

        raise ErrorCheck('Expecting <dielet> in [%s]. Naming convention is "<dielet>_<pingroupname>"'
                         '' % pingroup,
                         'List of dielet is: %s' % ', '.join(dielets))

    def check_lowercase(self, pingroup, pins):
        """
        Check if pingroup name is all lowercase

        :param pingroup: pingroup name
        :param pins: list of pins
        :param resource: dpin or DOMAIN
        :return: None
        """
        if pingroup.islower():
            return
        if self.is_pin_wrapper(pingroup, pins):    # no need to check
            return

        raise ErrorCheck('pingroup name [%s] has uppercase chars.' % pingroup,
                         'This is not allowed. pingroup name should be lowercase only')

    def check_scoping(self, pins, pingroup):
        """
        THIS CHECK IS OBSOLETE

        Make sure scoping is correct: unscoped mixed pin in not allowed
        It does not look at pins inside a pingroup.
        Need a separate routine that will look at all pingroups and flatten them out.

        :param pins: list of pins
        :param pingroup: name of pingroup

        :return: None
        """
        # see if pins are mixed
        ip_set = {self.ipmap.get(self.get_pin_only(pin), 'NA') for pin in pins}
        ip_set.discard('NA')

        # if > 1, then make sure IP_CPU or IP_PCH is scoped
        if len(ip_set) > 1:
            for pin in pins:
                pinonly = self.get_pin_only(pin)
                iponly = self.get_ip_only(pin)

                not_scoped = bool(not iponly)
                cpu_or_pch = bool(self.ipmap.get(pinonly))
                if cpu_or_pch and not_scoped:
                    raise ErrorCheck("group %s has mixed scope. %s must be scoped" % (pingroup, pin),
                                     "Pls fix input. Put scope in %s" % pin)

    def is_pin_wrapper(self, pingroup, pins):
        """
        Returns True if pingroup is a pin wrapper

        :param pingroup: pingroup name
        :param pins: list of pins
        :return: bool
        """
        if len(pins) != 1:
            return False
        return bool(pingroup == self.get_pin_only(pins[0]))

    def read_pin_ip(self):
        """
        Read pins and create dictionary of mapping

        :return: dict {pin: IP_CPU|IP_PCH|None}
        """
        if '_all_pins' not in self.db:
            return

        dbcopy = {x[0]: x[1] for x in self.db.items()}
        valid_pins = dbcopy['_all_pins']
        ipmap = {self.get_pin_only(pin): self.get_ip_only(pin) for pin in valid_pins}

        # iterate to all pingroups to get all ip's
        for name in sorted(self.get_pingroups(dbcopy)):
            pinlist = dbcopy[dbcopy[name]]['pinlist']
            for pin in pinlist:
                pinonly = self.get_pin_only(pin)
                iponly = self.get_ip_only(pin)
                if pinonly not in ipmap:
                    continue   # this is a pingroup
                if iponly:
                    if ipmap[pinonly] and ipmap[pinonly] != iponly:
                        raise ErrorCheck("Error: group[%s] pin[%s] has %s, however it is already %s"
                                         "" % (name, pinonly, iponly, ipmap[pinonly]))
                    ipmap[pinonly] = iponly

        return ipmap

    def get_pin_only(self, pin):
        """Return pin only portion of pinnname"""
        if ':' in pin:
            return pin.split(':')[2]
        else:
            return pin

    def get_ip_only(self, pin):
        """Return pin only portion of pinnname"""
        if ':' in pin:
            return pin.split(':')[0]
        else:
            return None

    def new(self, groupname, resource, filename, why, pingroups=None, checkonly=False, dupok=False):
        """
        Create a new pingroup

        :param groupname: name of pingroup
        :param resource: resource name
        :param filename: filename to list of pins
        :param why: user comment string
        :param pingroups: set of pingroups
        :param checkonly: True for checkonly
        :return: Nothing
        """
        # read the file, put it in list
        all_pins = self.db['_all_pins']

        if pingroups is None:
            valid_groups = self.db
        else:
            valid_groups = pingroups

        pins = self._read_file(filename, all_pins, valid_groups, groupname, resource, dupok=dupok)

        if not pins:
            log.info("-WARNING- %s is ignored. EMPTY." % groupname)
            return

        if checkonly:
            return

        # check if this pingroup already exist
        if groupname in self.db:
            raise ErrorCheck("Provided group [%s] already exist in %s" % (groupname, self.prodname),
                             "Use -update to update pingroup or use a different group name. "
                             "Use -view to display contents of existing pingroup")

        # get the last id and increment
        id = self.new_id()
        self.db[groupname] = id
        self.db[id] = {'name': groupname,
                       'resource': resource,
                       'pinlist': pins,
                       'user': USERNAME,
                       'date': curtime(),
                       'comment': why}

        log.info("%s is created, receipt id %s" % (groupname, id))

    def new_id(self):
        """
        Get a new id

        :return: integer
        """
        new_id = str(int(self.db.get('_last_id_no', 0)) + 1)
        self.db['_last_id_no'] = int(new_id)        # save the new id
        return new_id

    def upload(self, fname, recheck=False):
        """
        Upload the pingroup csv file
        This will only create new pingroups.
        It will error if pingroup is already in db
        This means, upload is only used once!

        :param fname: filename
        :param recheck: Set to true for recheck
        :return: Nothing
        """
        with TempDir(name=True) as tdir:
            cleanup = join(tdir, 'cleanup')
            File(cleanup).write(self.cleanup(fname))
            result = self.read_csv(cleanup)

        # do not add this special row in .csv
        if 'PINGROUP' in result:
            del result['PINGROUP']

        # check first that all group_names are NEW
        for group_name in result:
            if group_name in self.db and (not recheck):
                raise ErrorUser("Group name [%s] already in database." % group_name,
                                "-upload is meant to be one-time upload on a new product.")

        with TempDir(name=True) as tdir:
            # check first
            err = []
            for group_name in sorted(result):
                log.info("Checking %s group" % group_name)
                resource, list_pins = result[group_name]
                fname = join(tdir, group_name)
                File(fname).write('\n'.join(list_pins))
                try:
                    self.new(group_name, resource, fname, 'initial upload', pingroups=result, checkonly=True, dupok=True)
                except ErrorVepBase as e:
                    err.append('%-20s - %s' % (group_name, ErrorVepBase.get_main_error(e)))

            if err:
                log.info('')
                log.info("Summary of errors:")
                for line in err:
                    log.info("   %s" % line)
                log.info('')

                raise ErrorCheck("Fail! Total of %s errors" % len(err),
                                 "See above")

            if recheck:
                self.read_pin_ip()
                return

            # upload it
            for group_name in result:
                log.info("Uploading %s group" % group_name)
                resource, list_pins = result[group_name]
                fname = join(tdir, group_name)
                File(fname).write('\n'.join(list_pins))
                self.new(group_name, resource, fname, 'initial upload', pingroups=result, dupok=True)

        # Confirm pin_ip is passing
        self.read_pin_ip()

    @classmethod
    def read_csv(cls, fname):
        """
        Read the csv

        :param fname: path to fname
        :return: dictionary of {pingroup: (resource, list_of_pins)}
        """
        final = {}
        domain_area = False
        with open(fname, 'r', newline='') as fh:
            reader = csv.reader(fh, dialect=csv.excel_tab)
            for lineno, row in enumerate(reader):

                if not row:   # ignore empty
                    continue
                line = row[0]
                result = line.replace('"', '').split(',')
                name = result[0]
                resource = result[1]
                pins = [x for x in result[3:] if x]

                if name == 'Domain Definitions':
                    domain_area = True
                    continue

                # change the resource if domain area
                if domain_area:
                    resource = "DOMAIN"

                if name.startswith('#'):
                    continue
                if name:
                    final[name] = (resource, pins)

        return final

    @classmethod
    def cleanup(cls, fname):
        """
        Cleanup the csv for new lines

        :param fname: input
        :return: cleanup string
        """
        result = []
        incomplete = False
        for line in File(fname).chomp():
            line = to_ascii(line).strip()
            if incomplete:
                partial = '%s%s' % (partial, line)
                if '"' in line:
                    incomplete = False
                    result.append(partial)
                continue       # pragma: no cover:  peephole optimization

            if re.search('^[^\"]+\"[^\"]*$', line):
                incomplete = True
                partial = line
                continue

            result.append(line)
        return '\n'.join(result)

    def set_pins(self, fname):
        """
        Update the _all_pins (master list of pins)

        4 things can happen when new set of pins is uploaded (rev1)
        1. same name (do nothing)
        2. new name (do nothing)
        3. renamed (delete old name from pingroups) -> Process is: let owner update their pingroup
        4. deleted (delete from pingroups)

        :param fname: list of pins
        :return:
        """

        # read the file
        list_pins = set()
        for line in File(fname).chomp(comment='#'):
            line = to_ascii(line).strip()
            parsed = line.split(',')
            if len(parsed) == 2:
                list_pins.add(parsed[0].strip())
                if parsed[1] != '-' and parsed[1]:
                    list_pins.add('%s::%s' % (parsed[1].strip(), parsed[0].strip()))
            else:
                list_pins.add(line)

        self.db['_all_pins'] = list_pins
        log.info("Added %s pins" % len(list_pins))

        self.update_all_pingroups()

    def get_pingroups(self, dbinput=None) -> set:
        """
        Return all valid pingroups in db

        :return: set
        """
        if dbinput:
            db = dbinput
        else:
            db = self.db
        valid = set()
        for groups in list(db):
            if groups.startswith('_'):
                continue   # ignore this, special
            if groups.isdigit():
                continue   # ignore the numeric keys
            if groups.startswith('snapshot:'):
                continue   # not a valid group
            valid.add(groups)
        return valid

    def dump(self, name, outfile):
        """
        Dump contents of groupname to a file

        :para name: groupname
        :param outfile: output file
        :return:
        """
        id = self.db[name]
        data = self.db[id]
        pinlist = data['pinlist']
        File(outfile).write('\n'.join(pinlist))
        log.info("File %s is written containing %s" % (outfile, name))

    def disp(self, name):
        """
        Display contents of pingroup to screen

        :para name: groupname
        :return:
        """
        log.info('\n'.join(self.get_pinlist(name)))

    def get_pinlist(self, name) -> list:
        """Return pinlist given pingroup"""
        idn = self.db[name]
        data = self.db[idn]
        return data['pinlist']

    def get_all_pins(self) -> set:
        """Return all pins"""
        return self.db['_all_pins']

    def modify(self, name, filename, why, is_diff):
        """
        Update the pingroup

        :param name: pingroup name
        :param filename: filename
        :param why: reason
        :param is_diff: True if diff
        :return:
        """
        # check first if pin list is valid
        valid_groups = self.db
        all_pins = self.get_all_pins()

        id = self.db[name]
        data = self.db[id]
        pins = self._read_file(filename, all_pins, valid_groups, name, data['resource'])

        if is_diff:
            with TempDir(name=True) as tdir:
                first = join(tdir, 'first')
                File(first).write('%s\n' % '\n'.join(data['pinlist']))
                SystemCall('meld %s %s' % (first, filename)).run_outtxt()
                log.info("Note: pingroup is not modified (diff only)!")
                return   # do not save to db

        # update db
        data['user'] = USERNAME
        data['comment'] = why
        data['date'] = curtime()
        data['pinlist'] = pins
        newid = self.new_id()
        self.db[newid] = data
        self.db[name] = newid

        log.info("%s is modified. Your receipt id %s" % (name, newid))

    def deletegroup(self, name, why):
        """
        Delete a pingroup from db

        :param name: pingroup name
        :param why: reason
        :return:
        """
        # delete the record
        del self.db[name]

        # create a history
        data = {}
        data['name'] = name
        data['user'] = USERNAME
        data['comment'] = why
        data['date'] = curtime()
        data['pinlist'] = []      # empty list means pingroup is deleted
        newid = self.new_id()
        self.db[newid] = data

        log.info("%s is deleted. Record id is %s" % (name, newid))

    def deletepin(self, name, pinstodelete, why, is_diff):
        """
        Delete a pin from pingroup

        :para name: groupname
        :param pinstodelete: list of pins
        :param why: reason
        :param is_diff: True for isdiff
        :return:
        """
        # check first if pinlist is part of the pingroup
        id = self.db[name]
        data = self.db[id]
        orig_pinlist = list(data['pinlist'])
        for pin in pinstodelete:
            if pin not in orig_pinlist:
                raise ErrorCheck("pingroup %s does not have %s pin. Can only delete existing pins." % (name, pin),
                                 "To display contents of pingroup: pingroups.py %s -name %s -view"
                                 "" % (self.prodname, name))

        # delete it
        for pin in pinstodelete:
            data['pinlist'].remove(pin)

        if is_diff:
            with TempDir(name=True) as tdir:
                first = join(tdir, 'first')
                second = join(tdir, 'second')
                File(first).write('%s\n' % '\n'.join(orig_pinlist))
                File(second).write('%s\n' % '\n'.join(data['pinlist']))
                SystemCall('meld %s %s' % (first, second)).run_outtxt()
                log.info("Note: pingroup is not modified (diff only)!")
                return   # do not save to db

        # save it
        data['user'] = USERNAME
        data['comment'] = why
        data['date'] = curtime()
        newid = self.new_id()
        self.db[newid] = data
        self.db[name] = newid
        log.info("Deleted %s in %s. Your receipt id %s" % (pinstodelete, name, newid))

    def update_all_pingroups(self):
        """
        iterate to all the groups and remove invalid pins
        """
        valid_pins = self.db['_all_pins']
        valid_pins = valid_pins | self.get_pingroups()

        # iterate to all the group names and remove invalid pins
        for groups in list(self.db):
            if groups.startswith('_'):
                continue   # ignore this, special
            if groups.isdigit():
                continue   # ignore the numeric keys

            id = self.db[groups]
            data = self.db[id]
            pins = data['pinlist']
            modified = False
            for pin in pins:
                if pin not in valid_pins:
                    log.info("Group %s is modified bec of %s. Contact: %s" % (groups, pin, data['user']))
                    pins.remove(pin)
                    modified = True

            if modified:
                data['pinlist'] = pins
                new_id = self.new_id()
                self.db[groups] = new_id
                self.db[new_id] = data

    def snapshot(self, is_list):
        """
        Create a snapshot (or display them)

        :param is_list: boolean, display all snapshots
        :return:
        """
        if is_list:
            snaps = [snapshot for snapshot in self.db.query_startswith('snapshot:')]
            for snapshot in sorted(snaps):
                log.info("%s %s" % (snapshot, self.db[snapshot][0]))
            return

        # create the snapshot
        set_id = {self.db[x] for x in self.get_pingroups()}
        new_id = self.new_id().zfill(5)
        self.db['snapshot:%s' % new_id] = (curtime(), set_id)
        log.info("Snapshot created: snapshot:%s" % new_id)

    def history(self, name):
        """
        Print the history of this pingroup

        :param name: pingroup name
        :return:
        """
        for id in sorted(self.db):
            if id.isdigit():
                data = self.db[id]
                if data['name'] == name:
                    log.info("%s %s %s" % (id, data['user'], data['comment']))

    def detail(self, old_rev, new_rev):
        """
        Generate a diff of old_rev vs new_rev
        :param old_rev: number
        :param new_rev: number
        :return:
        """
        # make sure number exist first
        for id in (old_rev, new_rev):
            if id not in self.db:
                raise ErrorInput("[%s] does not exist" % id,
                                 "Pls run [pingroups.py <product> -name <pingroupname> -history] first")

        old_list = self.db[old_rev]['pinlist']
        new_list = self.db[new_rev]['pinlist']
        with TempDir(name=True) as tdir:
            first = join(tdir, 'first')
            File(first).write('%s\n' % '\n'.join(old_list))
            second = join(tdir, 'second')
            File(second).write('%s\n' % '\n'.join(new_list))

            log.info("See Diff of %s" % self.db[old_rev]['name'])
            SystemCall('meld %s %s' % (first, second)).run_outtxt()

    def xls(self, snapshot, outfile):
        """
        Create the xls
        :param snapshot: no
        :param outfile: output csv file
        :return:
        """
        key = 'snapshot:%s' % snapshot.zfill(5)
        if key not in self.db:
            raise ErrorInput("Provided snapshot [%s] does not exist" % key,
                             "Run pingroups.py -snapshot -list to display all.")
        list_of_id = self.db[key][1]

        domains = []      # these is a list of domain pingroups
        with open(outfile, 'w', newline='') as fh:
            csv_fh = csv.writer(fh, dialect='excel')
            # write header
            csv_fh.writerow(['PINGROUP'])

            # print the pingroups
            for id in list_of_id:
                record = self.db[id]
                if record['resource'] == 'DOMAIN':
                    domains.append(record)
                    continue
                pinlist = record['pinlist']
                data = [record['name'], record['resource'], '=', ', '.join(pinlist)]
                csv_fh.writerow(data)

            # print the domains
            csv_fh.writerow(['Domain Definitions'])
            for record in domains:
                pinlist = record['pinlist']
                data = [record['name'], record['resource'], '=', ', '.join(pinlist)]
                csv_fh.writerow(data)

        log.info("%s is written" % outfile)

    def report(self, old_snapshot, new_snapshot):
        """
        Generate a display of which pingroups have changed between old_snapshot and new_snapshot

        :param old_snapshot: number
        :param new_snapshot: number or 0 (for latest
        :return:
        """
        # get first snapshot
        old_key = 'snapshot:%s' % old_snapshot.zfill(5)
        if old_key not in self.db:
            raise ErrorInput("Provided snapshot [%s] does not exist" % old_key,
                             "Run pingroups.py -snapshot -list to display all.")
        list_of_old_id = self.db[old_key][1]

        # get second snapshot
        if new_snapshot == '0':
            list_of_new_id = [self.db[x] for x in self.get_pingroups()]
            # latest in db
        else:
            new_key = 'snapshot:%s' % new_snapshot.zfill(5)
            if new_key not in self.db:
                raise ErrorInput("Provided snapshot [%s] does not exist" % new_key,
                                 "Run pingroups.py -snapshot -list to display all.")
            list_of_new_id = self.db[new_key][1]

        # data structure: old[group_name] = <list_of_pins>
        old = {}
        for id in list_of_old_id:
            record = self.db[id]
            old[record['name']] = record['pinlist']

        new = {}
        for id in list_of_new_id:
            record = self.db[id]
            new[record['name']] = record['pinlist']

        # we compare, use old first
        for group in sorted(old):
            if group in new:
                if old[group] == new[group]:
                    # pinlist is the same
                    pass    # do nothing
                else:
                    log.info("%s has changed" % group)
            else:
                log.info("%s is removed" % group)

        for group in new:
            if group not in old:
                log.info("%s is new" % group)

    def list(self):
        """Display pingroups"""
        log.info("List of pingroup names:")
        pa = PrintAlign(rjust=False)
        for name in sorted(self.get_pingroups()):
            data = self.db[self.db[name]]
            pa(name,
               '%3d pins' % len(data['pinlist']),
               'by %s' % data['user'],
               'last update: %s' % data['date']
               )
        pa.disp()

    def recheck(self):
        """Recheck all valid pingroups in db"""
        # create the csv first
        lines = []
        for name in sorted(self.get_pingroups()):
            data = self.db[self.db[name]]
            lines.append('%s,%s,=,"%s"' % (name, data['resource'], ','.join(data['pinlist'])))

        with TempDir(name=True) as tdir:
            csv = join(tdir, 'a.csv')
            File(csv).touch('\n'.join(lines))
            self.upload(csv, recheck=True)

    def pinlist(self):
        """Display pinlist"""
        log.info("# List of defined names:")
        valid_pins = self.db['_all_pins']
        for name in sorted(valid_pins):
            log.info(name)

    def disp_receipt(self, id):
        """
        Display details of this id
        :param id: id number
        :return:
        """
        if not id.isdigit():
            raise ErrorInput("Error: [%s] must be digit." % id,
                             "Pls specify valid receipt id.")

        if id not in self.db:
            raise ErrorInput("Error: %s is not a valid receipt id" % id,
                             "Pls specify valid receipt id.")
        data = self.db[id]
        log.info("%-10s: %s" % ('id', id))
        for item in 'name resource comment user date pinlist'.split():
            if item == 'pinlist':
                log.info('pinlist: %s\n%s' % (len(data['pinlist']), indent(3, data['pinlist'])))
            else:
                log.info("%-10s: %s" % (item, data[item]))

    def flatten(self, pingroup):
        """
        Flatten a pingroup recursively

        :param pingroup: pingroup, pin or list of pins
        :return: list of pins only
        """
        if isinstance(pingroup, str):
            # check first if it is a pin
            if self.get_pin_only(pingroup) in self.ipmap:
                return {pingroup}

            # check if pingroup is valid
            if pingroup not in self.db:
                self.list()
                raise ErrorInput("Error: %s is not a valid pingroup" % pingroup,
                                 "Pls select valid pingroups from above.")

            # assumed valid pingroup at this point
            id = self.db[pingroup]
            data = self.db[id]
            pinlist = data['pinlist']
        else:
            pinlist = pingroup

        result = set()
        for pin in pinlist:
            result.update(self.flatten(pin))
        return result

    @staticmethod
    def code(pingroup):
        """
        Returns a unique code given pingroup and the date.
        This code is only valid for the day and this pingroup
        """
        return sha1('%s %s' % (pingroup, curtime()[:10]))[:6]


class PinGroupsArgs(Args):   # parent: ArgsBase
    """
    Simple calculator (add and subtract)
    Demonstration Usage of Args() class.
    """

    def config(self):
        """
        Define the arguments for the script.
        The order below will matter, it is the order of display during help.
        """
        valid_resource = ('HPCC.EnabledClock HPCC.dpin HDDPS.HC HDDPS.LC HDDPS.VLC '
                          'DOMAIN HighPurityClock EnabledClock DPin').split()

        cfg = DictDot()
        cfg.resource = TA_Store('Specify the resource name', choices=valid_resource)
        cfg.all = TA_All('prodname')
        cfg.name = TA_Store('Specify pingroup name', metavar='pingroup_name')
        cfg.why = TA_Store('Reason why new or update the pingroup', metavar='reason')
        cfg.i_am_tpi = TA_StoreTrue("Used for TP integrator to create db")
        cfg.diff = TA_StoreTrue("Display diff during -modify or -deletepin (changes will not save to db)")
        cfg.force = TA_Store('Specify unique code', metavar='<code>')

        # Below are commands
        cfg.set_pins = TA_StoreFile('CMD: Initial pinlist upload. csv must be two column, 2nd column is IP_PCH|IP_CPU',
                                    metavar='pin_list.csv')
        cfg.upload_pingroup = TA_StoreFile('CMD: Upload (initial) pingroup tab csv', metavar='pingroup_tab.csv')
        cfg.new = TA_StoreFile('CMD: Create a new pingroup given a file list of pins', metavar='file_pin_list')
        cfg.modify = TA_StoreFile('CMD: Update a new pingroup given a file list of pins', metavar='out_file')
        cfg.snapshot = TA_StoreTrue("CMD: Create a snapshot of all pingroups")
        cfg.list = TA_StoreTrue("CMD: Display pingroup list; display snapshot versions for -snapshot")
        cfg.pinlist = TA_StoreTrue("CMD: Display all valid pins")
        cfg.deletepin = TA_AppendSC('CMD: Delete this pin from a given pingroup', metavar='pinname')
        cfg.deletegroup = TA_StoreTrue('CMD: Delete this pingroup')
        cfg.dump = TA_Store('CMD: Write out the contents of a given pingroup to a outfile', metavar='outfile')
        cfg.report = TA_Store('CMD: Snapshot diff report. use 0 for latest', metavar='new_snapshot_number')
        cfg.history = TA_StoreTrue("CMD: Display history of a pingroup")
        cfg.detail = TA_Store('CMD: Show diff of two pingroup id', metavar='id_new')
        cfg.xls = TA_Store('CMD: Save a snapshot to a file.csv', metavar='outfile.csv')
        cfg.receipt = TA_Store('CMD: Display contents of this specific id', metavar='id')
        cfg.disp = TA_StoreTrue('CMD: Display contents of this pingroup')
        cfg.recheck = TA_StoreTrue('CMD: Recheck all pingroups in db if all are passing checks')
        cfg.check = TA_StoreFile('CMD: Check pinlist (argument1) and pingroup files', metavar='pingroup.csv')
        cfg.merge = TA_StoreTrue('CMD: Merge two products together to form a superset')
        return cfg

    def main(self):
        """
        Main entry point of executable
        -h will not reach this method, since that is taken cared of in Args Base class
        """
        if len(sys.argv) == 1:
            self.print_help()

        if len(OPT.all) == 0:
            raise ErrorUser("first argument must be product name",
                            "Fix the inputs")

        self.setup_logger()

        # list of arg commands (will be translated to do_<argument>()
        self.call_methods(['set_pins',         # call do_set_pins(), if -set_pins argument is specified
                           'upload_pingroup',  # call do_upload_pingroup(), if -upload_pingroup
                           'new',              # call do_new(), if -new
                           'modify',           # call do_modify(), if -modify
                           'deletepin',        # call do_deletepin(), if -deletepin
                           'deletegroup',      # call do_deletegroup(), if -deletegroup
                           'dump',             # call do_dump(), if -dump
                           'snapshot',         # call do_snapshot(), if -snapshot
                           'list',             # call do_list(), if -list
                           'report',           # call do_report(), if -report
                           'history',          # call do_history(), if -history
                           'detail',           # call do_detail(), if -detail
                           'xls',              # call do_xls(), if -xls
                           'pinlist',          # call do_pinlist(), if -pinlist
                           'receipt',          # call do_receipt(), if -receipt
                           'disp',             # call do_disp(), if -disp
                           'recheck',          # call do_recheck(), if -recheck
                           'check',            # call do_check(), if -check
                           'merge',            # call do_merge(), if -merge
                           ])           # do_else() is called if no argument command is processed

    def setup_logger(self):     # pragma: no cover
        """
        Setup logging

        :return:
        """
        if IS_UT:
            return

        root = f'{cfg.log_dir}/tp_pingroups/{curtime()[:10]}'    # date
        mkdirs(root, mode='02770')
        log_filename = "%s_%s_%s.log" % (USERNAME, HOSTNAME, int(time.time()))
        log.filemixed(os.path.join(root, log_filename))
        log.debug("FULL CMD: %s" % fullcmdline(with_exec=True))

    # --- commands below ---

    def do_list(self):
        """list all pingroups"""
        pingroup = PinGroups(OPT.all[0])
        pingroup.list()

    def do_pinlist(self):
        """list all pingroups"""
        pingroup = PinGroups(OPT.all[0])
        pingroup.pinlist()

    def do_recheck(self):
        """recheck all pingroups in db"""
        pingroup = PinGroups(OPT.all[0], readonly=True, dupcheck=False)
        pingroup.recheck()

    def do_check(self):
        """check input pinlist and pingroup"""
        if not exists(OPT.all[0]):
            raise ErrorUser("Input [%s] does not exist. This must be a valid pinlist.csv file"
                            "" % OPT.all[0],
                            "Usage: pingroups.py <pinlist.csv> -check <pingroup.csv>")

        pinlist_file = OPT.all[0]
        pingroup_file = OPT.check

        with TempDir(name=True) as tdir,\
                MockVar(cfg, "pingroup", tdir):

            cmd = "pingroups.py check -set_pin %s -i_am_tpi" % pinlist_file
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

            cmd = "pingroups.py check -upload %s" % pingroup_file
            with MockVar(sys, "argv", cmd.split()):
                PinGroupsArgs().main()

    def do_report(self):
        """snapshot diff report"""
        pingroup = PinGroups(OPT.all[0])
        if len(OPT.all) != 2:
            raise ErrorInput("old_snapshot_no is not specified",
                             "Usage: pingroups.py <product> <old_snapshot_no> -report <new_snapshot_no>; "
                             "use 0 for <new_shapshot_no> for latest data")
        pingroup.report(OPT.all[1], OPT.report)

    def do_xls(self):
        """snapshot diff report"""
        pingroup = PinGroups(OPT.all[0])
        if len(OPT.all) != 2:
            raise ErrorInput("snapshot_no is not specified",
                             "Usage: pingroups.py <product> <snapshot_no> -xls <outfile.csv>")
        pingroup.xls(OPT.all[1], OPT.xls)

    def do_detail(self):
        """snapshot diff report"""
        pingroup = PinGroups(OPT.all[0])
        if len(OPT.all) != 2:
            raise ErrorInput("old_rev is not specified",
                             "Usage: pingroups.py <product> <old_rev_no> -detail <new_rev_no>")
        pingroup.detail(OPT.all[1], OPT.detail)

    def do_new(self):
        """new pingroup"""
        self.check_why()
        self.check_name()
        pingroup = PinGroups(OPT.all[0])
        pingroup.new(OPT.name, OPT.resource, OPT.new, OPT.why)

    def do_upload_pingroup(self):
        """Upload initial pingroup csv"""
        pingroup = PinGroups(OPT.all[0], dupcheck=False)
        pingroup.upload(OPT.upload_pingroup)

    def do_dump(self):
        """Dump pingroup to a file"""
        self.check_name()
        pingroup = PinGroups(OPT.all[0])
        self.check_name_exist(pingroup, OPT.name)
        pingroup.dump(OPT.name, OPT.dump)

    def do_disp(self):
        """Disp pingroup to screen"""
        self.check_name()
        pingroup = PinGroups(OPT.all[0])
        self.check_name_exist(pingroup, OPT.name)
        pingroup.disp(OPT.name)

    def do_set_pins(self):
        """set the initial pins"""
        pingroup = PinGroups(OPT.all[0])
        pingroup.set_pins(OPT.set_pins)

    def do_snapshot(self):
        """set the initial pins"""
        pingroup = PinGroups(OPT.all[0])
        pingroup.snapshot(OPT.list)

    def do_deletepin(self):
        """delete a pin from a pingroup"""
        self.check_why()
        self.check_name()
        pingroup = PinGroups(OPT.all[0])
        self.check_name_exist(pingroup, OPT.name)
        pingroup.deletepin(OPT.name, OPT.deletepin, OPT.why, OPT.diff)

    def do_deletegroup(self):
        """delete a pingroup"""
        self.check_why()
        self.check_name()
        pingroup = PinGroups(OPT.all[0])
        self.check_name_exist(pingroup, OPT.name)
        pingroup.deletegroup(OPT.name, OPT.why)

    def do_history(self):
        """display history of a pingroup"""
        self.check_name()
        pingroup = PinGroups(OPT.all[0])
        self.check_name_exist(pingroup, OPT.name)
        pingroup.history(OPT.name)

    def do_modify(self):
        """Update pingroup"""
        self.check_why()
        self.check_name()
        pingroup = PinGroups(OPT.all[0])
        self.check_name_exist(pingroup, OPT.name)
        pingroup.modify(OPT.name, OPT.modify, OPT.why, OPT.diff)

    def do_receipt(self):
        """display this receipt id"""
        pingroup = PinGroups(OPT.all[0])
        pingroup.disp_receipt(OPT.receipt)

    def check_why(self):
        """-why cannot be empty"""
        if OPT.diff:   # reason is not needed for -diff
            return

        if not OPT.why:
            raise ErrorUser("-why is not provided.",
                            "Pls add -why '<reason why you are doing this action>'")

    def check_name(self):
        """-name cannot be empty"""
        if not OPT.name:
            raise ErrorUser("-name is not provided. This is the groupname you want to operate on.",
                            "Pls add -name <groupname>")

    def check_name_exist(self, pingroup, name):
        """
        Check if groupname exist
        :param pingroup: pingroup object
        :param name: pingroup name
        """
        # check first if pingroup exist
        if name not in pingroup.db:
            raise ErrorUser(f"pingroup {name} does not exist",
                            f"To list all known pingroups: pingroups.py {OPT.all[0]} -list")

    def do_else(self):
        """
        Execute this if no valid command is specified
        do_else() in base class will just print the help message
        """
        print("Nothing to do")

    def _renamed(self):
        info = '''IO_RLY_03,Removed
IO_RLY_04,Removed
IO_RLY_05,Removed
IO_RLY_06,Removed
IO_RLY_07,Removed
IO_RLY_08,Removed
IO_RLY_09,Removed
IP_CPU::VCCLOAD_ATOM_0_LC,Removed
IP_CPU::VCCLOAD_ATOM_1_LC,Removed
IP_CPU::VCCLOAD_CORE_0_LC,Removed
IP_CPU::VCCLOAD_CORE_1_LC,Removed
IP_CPU::VCCLOAD_CORE_2_LC,Removed
IP_CPU::VCCLOAD_CORE_3_LC,Removed
IP_CPU::VCCLOAD_CORE_4_LC,Removed
IP_CPU::VCCLOAD_CORE_5_LC,Removed
IP_CPU::VCCLOAD_LLC_LC,Removed
IP_CPU::XX_CORE_DLVR_VIEWANA0,IP_CPU::XX_CORE_DLVR_VIEWANA_0
IP_CPU::XX_CORE_DLVR_VIEWANA1,IP_CPU::XX_CORE_DLVR_VIEWANA_1
IP_CPU::XX_CORE_DLVR_VIEWDIG0,IP_CPU::XX_CORE_DLVR_VIEWDIG_0
IP_CPU::XX_CORE_DLVR_VIEWDIG1,IP_CPU::XX_CORE_DLVR_VIEWDIG_1
IP_CPU::XX_CORE_VIEWDIGANA0,IP_CPU::XX_CORE_VIEWDIGANA_0
IP_CPU::XX_CORE_VIEWDIGANA1,IP_CPU::XX_CORE_VIEWDIGANA_1
IP_CPU::XX_CORE_VIEWLYA0,IP_CPU::XX_CORE_VIEW_LYA_0
IP_CPU::XX_CORE_VIEWLYA1,IP_CPU::XX_CORE_VIEW_LYA_1
IP_PCH::XX_GCD_VIEWANA0,IP_PCH::XX_GCD_VIEWANA_0
IP_PCH::XX_GCD_VIEWANA1,IP_PCH::XX_GCD_VIEWANA_1
VCCLOAD_ATOM_0_LC,Removed
VCCLOAD_ATOM_1_LC,Removed
VCCLOAD_CORE_0_LC,Removed
VCCLOAD_CORE_1_LC,Removed
VCCLOAD_CORE_2_LC,Removed
VCCLOAD_CORE_3_LC,Removed
VCCLOAD_CORE_4_LC,Removed
VCCLOAD_CORE_5_LC,Removed
VCCLOAD_LLC_LC,Removed
XXEDM_BASE,Removed
XXEDM_CORE,XX_EDM_CORE
XXEDM_GCD,XX_EDM_GCD
XXEDM_GND,XX_EDM_GND
XXEDM_IOE,XX_EDM_IOE
XXEDM_SOC,XX_EDM_SOC
XX_CORE_DLVR_VIEWANA0,XX_CORE_DLVR_VIEWANA_0
XX_CORE_DLVR_VIEWANA1,XX_CORE_DLVR_VIEWANA_1
XX_CORE_DLVR_VIEWDIG0,XX_CORE_DLVR_VIEWDIG_0
XX_CORE_DLVR_VIEWDIG1,XX_CORE_DLVR_VIEWDIG_1
XX_CORE_VIEWDIGANA0,XX_CORE_VIEWDIGANA_0
XX_CORE_VIEWDIGANA1,XX_CORE_VIEWDIGANA_1
XX_CORE_VIEWLYA0,XX_CORE_VIEW_LYA_0
XX_CORE_VIEWLYA1,XX_CORE_VIEW_LYA_1
XX_GCD_VIEWANA0,XX_GCD_VIEWANA_0
XX_GCD_VIEWANA1,XX_GCD_VIEWANA_1'''
        result = {}
        for line in info.split('\n'):
            old, new = line.split(',')
            if new == "Removed":
                result[old] = None
            else:
                result[old] = new
        return result

    def do_merge(self):    # pragma: no cover
        """mtl-m and mtl-p merge"""
        mtlm = PinGroups('mtl_class_m', readonly=True)
        mtlp = PinGroups('mtl_class_p', readonly=True)
        mtlu = PinGroups('mtl_class_unified', readonly=True)
        mtlu_all = mtlu.get_pingroups()
        renamed = self._renamed()

        # print("Unique pins in mtl-m:")
        # # print('\n'.join(sorted(mtlm.get_all_pins() - mtlu.get_all_pins())))
        # mu = mtlm.get_all_pins() - mtlu.get_all_pins()
        # pu = mtlp.get_all_pins() - mtlu.get_all_pins()
        # print('\n'.join(sorted(mu - pu)))

        # print("Unique pingroups in mtl-m:")
        # for grp in sorted(mtlm.get_pingroups() - mtlp.get_pingroups()):
        #     if len(mtlm.get_pinlist(grp)) == 1:
        #        continue
        #     if grp in mtlu_all:
        #         print(f"Exist: {grp}: {cjoin(set(mtlm.get_pinlist(grp))-set(mtlu.get_pinlist(grp)))}")
        #         continue
        #     resource = mtlm.db[mtlm.db[grp]]['resource']
        #
        #     # See if any of them are renamed
        #     for pin in mtlm.get_pinlist(grp):
        #         if pin in renamed:
        #             print(f'RENAMED: {grp} {renamed[pin]}')
        #
        #     print(f"Inserting {grp}")
        #     with TempDir(name=True) as tdir:
        #         fname = f'{tdir}/pins'
        #         File(fname).touch('\n'.join(mtlm.get_pinlist(grp)))
        #         mtlu.new(grp, resource, fname, 'port from mtl_class_p')

        # print("pingroup diff, but superset")
        # for grp in sorted(mtlp.get_pingroups() & mtlm.get_pingroups()):
        #     if len(mtlp.get_pinlist(grp)) == 1:
        #         continue
        #     if mtlp.get_pinlist(grp) != mtlm.get_pinlist(grp):
        #         if len(set(mtlm.get_pinlist(grp)) - set(mtlp.get_pinlist(grp))) == 0:
        #             print(grp)

        # print("unified vs mtlp diff:")
        # for grp in sorted(mtlu.get_pingroups() & mtlp.get_pingroups()):
        #     result = set(mtlp.get_pinlist(grp)) - set(mtlu.get_pinlist(grp))
        #     if result:
        #         print("Diff: %-20s: count: %s, first 4: %s" % (grp, len(result), sorted(result)[:4]))

        # print("pingroup diff, but not superset")
        # for grp in sorted(mtlp.get_pingroups() & mtlm.get_pingroups()):
        #     if len(mtlp.get_pinlist(grp)) == 1:
        #         continue
        #     if len(set(mtlm.get_pinlist(grp)) - set(mtlp.get_pinlist(grp))) > 0:
        #
        #         res = set(mtlm.get_pinlist(grp)) - set(mtlp.get_pinlist(grp))
        #         if len(res) > 0:
        #             print("%-20s mtl-m unique: %s" % (grp, ','.join(sorted(res))))
        #
        #         res = set(mtlp.get_pinlist(grp)) - set(mtlm.get_pinlist(grp))
        #         if len(res) > 0 and len(res) < 10:
        #             print("%-20s mtl-p unique: %s" % (grp, ','.join(sorted(res))))
        #         if len(res) > 0 and len(res) >= 10:
        #             print("%-20s mtl-p unique: %s pins" % (grp, len(res)))

        print("pingroup diff, but not superset")
        for grp in sorted(mtlp.get_pingroups() & mtlm.get_pingroups()):
            if len(mtlp.get_pinlist(grp)) == 1:
                continue
            if grp in 'pkg_all pkg_all_lcdps pkg_fab_all pkg_tap_all'.split():
                continue
            m_unique = set(mtlm.get_pinlist(grp)) - set(mtlp.get_pinlist(grp))
            if len(m_unique) > 0:
                current = mtlu.get_pinlist(grp)
                toadd = set()
                for pin in m_unique:
                    if pin in renamed:
                        print(f'RENAMED: {grp} {renamed[pin]}')
                    if pin not in current:
                        toadd.add(pin)
                        # print(f'To add: {grp}: {pin}')
                print(f'{grp:20}: To add: {cjoin(sorted(toadd))}')

        exit(0)


if __name__ == '__main__':  # pragma: no cover
    PinGroupsArgs(desc=__doc__).main()
