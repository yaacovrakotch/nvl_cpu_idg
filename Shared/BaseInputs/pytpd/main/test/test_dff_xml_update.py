#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
Unit test for dff_xml_update.py
"""
from setenv_unittest import UT_DIR, ROOT_ENV     # must be first import for unittests
from main.dff_xml_update import *
from gadget.ut import TestCase, unittest, is_ut_option
from gadget.files import TempDir


class TestDffProc(TestCase):

    def test_cl2rc(self):
        with TempDir(name=True, chdir=True) as tdir:
            f1 = 'Modules/TPI_DFF_XXX/InputFiles/MTL_ALL CLASS_P68G2_CLASS.xml'  # with space in the name
            f1n = 'Modules/TPI_DFF_XXX/InputFiles/MTL_ALL_CLASS_P68G2_CLASS.xml'  # replaced space, for checking later
            f2 = 'Modules/TPI_DFF_XXX/InputFiles/MTL_ALL_CLASS_P28G2_CLASS.xml'  # no space in the name
            f3 = 'Modules/TPI_DFF_XXX/InputFiles/ARL_ALL_CLASS_P28G2_CLASS.xml'  # no space in the name
            f4 = 'Modules/TPI_DFF_XXX/InputFiles/somedummy.txt'
            nf1 = 'Modules/TPI_DFF_XXX/InputFiles/MTL_ALL_CLASS_P68G2_RAWCLASS.xml'
            nf2 = 'Modules/TPI_DFF_XXX/InputFiles/MTL_ALL_CLASS_P28G2_RAWCLASS.xml'
            nf3 = 'Modules/TPI_DFF_XXX/InputFiles/ARL_ALL_CLASS_P28G2_RAWCLASS.xml'

            dffdata = """            <Token>
                <dff_token_id>1</dff_token_id>
                <name>QDFS</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>2</dff_token_id>
                <name>OLBPC2</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>3</dff_token_id>
                <name>OLBCC2</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSCOLD</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>4</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CSM</upload_process_step>
            </Token>"""
            File(f1).touch(dffdata, mkdir=True, newfile=True)
            File(f2).touch(dffdata, mkdir=True, newfile=True)
            File(f3).touch(dffdata, mkdir=True, newfile=True)
            File(f4).touch(dffdata, mkdir=True, newfile=True)

            obj = DffProc()
            obj.cl2rc()

            # check for expected rawclass file data
            expect_rc = """            <Token>
                <dff_token_id>1</dff_token_id>
                <name>QDFS</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>2</dff_token_id>
                <name>OLBPC</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>3</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSCOLD</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>4</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CSM</upload_process_step>
            </Token>"""

            self.assertTextEqual(File(nf1).read(), expect_rc)
            self.assertTextEqual(File(nf2).read(), expect_rc)
            self.assertTextEqual(File(nf3).read(), expect_rc)

            # check for expected class file data
            expect_cl = """            <Token>
                <dff_token_id>1</dff_token_id>
                <name>QDFS</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>2</dff_token_id>
                <name>OLBPC</name>
                <first_socket_upload>RC_S1</first_socket_upload>
                <upload_process_step>CLASSHOT</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>3</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CLASSCOLD</upload_process_step>
            </Token>
            <Token>
                <dff_token_id>4</dff_token_id>
                <name>OLBCC</name>
                <first_socket_upload>PBIC_DAB</first_socket_upload>
                <upload_process_step>CSM</upload_process_step>
            </Token>"""

            self.assertTextEqual(File(f1n).read(), expect_cl)  # expected change is now in the renamed file f1n
            self.assertTextEqual(File(f2).read(), expect_cl)
            self.assertTextEqual(File(f3).read(), expect_cl)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
