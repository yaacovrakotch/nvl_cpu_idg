#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
This script will is run in tp folder
"""
import setenv      # must be first in the imports
import glob
from gadget.pylog import log
from gadget.files import File
import re
from os.path import basename


class DffProc:

    def cl2rc(self):
        """
        Read MTL_ALL_*_CLASS.xml, rename by removing spaces in the name, replace file data (from OLBCC2 to OLBCC), save
        Creates MTL_ALL_*_RAWCLASS.xml files inside TPI_DFF_XXX/InputFiles based from MTL_ALL_*_CLASS.xml
        :return: None
        """
        # remove spaces from the filename
        c2rcfiles = (glob.glob('Modules/TPI_DFF_*/InputFiles/*_CLASS.xml') +
                     glob.glob('Modules/*/TPI_DFF_*/InputFiles/*_CLASS.xml') +
                     glob.glob('Shared/Modules/*/TPI_DFF_*/InputFiles/*_CLASS.xml'))
        for f in c2rcfiles:
            fnn = basename(f).replace(' ', '_')  # rename fn, remove spaces, replace with underscore
            File(f).rename(fnn)  # nested move+rename

        # replace OLBCC2 with OLBCC
        c2rcfiles = (glob.glob('Modules/TPI_DFF_*/InputFiles/*_CLASS.xml') +
                     glob.glob('Modules/*/TPI_DFF_*/InputFiles/*_CLASS.xml'))
        cc2 = '<name>OLBCC2</name>'
        cc = '<name>OLBCC</name>'
        for f in c2rcfiles:
            with open(f, 'r') as file:
                log.info(f'-i- Reading inputFile {f}...')
                xmldata = file.read()
            xmldata = xmldata.replace(cc2, cc)
            File(f).rewrite(xmldata, 'OLBCC2 replace')

        # replace OLBPC2 to OLBPC
        # From Malou, 7/24/24: update the DFF script to include OLBPC2 for PHMROOM to OLBPC.
        # Dhanya created a new token to support combined CVV/EQA.
        # DoXiGen does not allow to submit duplicate token even for different process_step, this token will be for PHMROOM and PHMCOLD.
        cc2 = '<name>OLBPC2</name>'
        cc = '<name>OLBPC</name>'
        for f in c2rcfiles:
            with open(f, 'r') as file:
                log.info(f'-i- Reading inputFile {f}...')
                xmldata = file.read()
            xmldata = xmldata.replace(cc2, cc)
            File(f).rewrite(xmldata, 'OLBPC2 replace')

        # create the _RAWCLASS.xml files
        c2rcfiles = (glob.glob('Modules/TPI_DFF_*/InputFiles/*_CLASS.xml') +
                     glob.glob('Modules/*/TPI_DFF_*/InputFiles/*_CLASS.xml') +
                     glob.glob('Shared/Modules/*/TPI_DFF_*/InputFiles/*_CLASS.xml'))
        cl = '<first_socket_upload>PBIC_DAB'
        rc = '<first_socket_upload>RC_S1'
        for f in c2rcfiles:
            ff = f[:-9] + 'RAWCLASS.xml'
            with open(f, 'r') as file:
                log.info(f'-i- Reading inputFile {f}...')
                xmldata = file.read()
            xmldata = xmldata.replace(cl, rc)
            File(ff).rewrite(xmldata, f'{ff} created')

        return


if __name__ == '__main__':  # pragma: no cover
    obj = DffProc()
    obj.cl2rc()
