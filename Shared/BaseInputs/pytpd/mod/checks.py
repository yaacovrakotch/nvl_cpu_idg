#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Check module - TP checker routines
"""
from gadget.strmore import to_str
from gadget.disk import Allfiles
from gadget.gizmo import Elapsed
from collections import defaultdict
import re
from gadget.dictmore import xmlfunc
from gadget.pylog import log
import json
import tarfile


class SpecialCharCheck:
    """Class that checks testprogram files for special chars"""

    def __init__(self, startdir=None):
        self.startdir = startdir
        self.result = defaultdict(list)    # {fullpath_to_file: list_of_lines_with_special_char}
        self.robj = re.compile(r'[^\x20-\x7F\s\b\r]')
        self._read = []     # list of files processed by this class

    def main(self):
        """
        Main Entry point. Iterate to all files of self.startdir

        :param startdir: testprogram/TPL
        :return: {ff: [<invalidlines>]},    # empty if no errors
        """
        sw = Elapsed()
        log.info(f'-i- Starting SpecialCharCheck. Reading all .xmls. Pls be patient')

        for ff in Allfiles(self.startdir):
            # check if file is readable first
            self.is_readable(ff)

            # special handling files
            if ff.lower().endswith('.xml'):
                self.check_xml(ff)
                continue

            # ignore these files
            if ff.endswith(('.dll', '.pdb', '.zip', '.pinObj', '.gz', '.cat', '.xlsx', '.xlsm', '.docx')):   # These are binary
                continue

            # check every line of target file
            self.non_ascii_line(ff)

        log.info(f'-i- Finished SpecialCharCheck in {sw}')
        return self

    def is_readable(self, ff):
        """Checks if file is readable or not"""
        try:
            with open(ff, mode='rb') as fh:
                for _ in fh:
                    return     # success upon read of first line
        except Exception as e:
            self.result[ff].append(f"Cannot open/read: {e}")

    def check_xml(self, ff):
        """Special handling for xml"""
        self._read.append(ff)
        try:
            xmldict = xmlfunc.xml2dict(ff)
        except Exception as e:
            self.result[ff].append(f"Cannot read xml file: {e}")
            return

        # logic: convert to json, then read the json text. Unicode are converted to \u
        jsontext = json.dumps(xmldict, indent=3)
        for n, line in enumerate(jsontext.split('\n'), start=1):
            if r'\u' in line:
                self.result[ff].append("XML Line with special char: %s" % line.strip())

    def non_ascii_line(self, ff):
        """
        Returns first non-ascii line - Does not use compressed files!

        :return: (lno, non-ascii-line) or None
        """
        self._read.append(ff)
        with open(ff, mode='rb') as fh:
            for n, line in enumerate(fh, start=1):
                line = to_str(line)
                if line.strip().startswith('#'):     # ignore comment lines
                    continue
                if self.robj.search(line):
                    self.result[ff].append('line#%s: %r' % (n, line))

        return None


# import tarfile
# tar = tarfile.open("sample.tar.gz", "w:gz")
# tar.add("mtt_tp")
# tar.close()

# tar = tarfile.open("sample.tar.gz", "r:gz")
# tar.extractall()
# tar.close()
#
# exit(0)

# class CopyTPTar:          # This is unused for now, originally meant for TPIE copy
#     """
#     #a. full tp: do only if release candidate (we can tell this). No need to put username because module owners don't run anyway.
#     Keep only latest 5 TPs.
#     #b. mv tp: we can also tell this. We need a "limited-approved-list" of folks so the routine will not execute for all module owner runs.
#     Keep only latest 5 TPs.
#     #c. The mechanism is via tar so it's fast.
#     """
#
#     def main(self):
#         """
#         Main routine to copy testprogram
#         """
#         valid, tptype = self.is_copy()
#         if not valid:
#             return
#
#         # copy tp
#         fdir = ''
#         n = self.get_number(fdir)
#         tar = tarfile.open(f'{fdir}/{n}.{tptype}.tar.gz', 'w:gz')
#         tar.add('.')
#         tar.close()
#
#         # Is this tp full or mv
#         # if full, is user part of valid list
#         # tar, then copy to specific area
