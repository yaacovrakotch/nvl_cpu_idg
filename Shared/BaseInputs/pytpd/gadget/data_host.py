#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston
"""
CGI Data Host module

Startegy:
python3.6 to 3.9:     Use CgiConnect()  and pytpdhost.cgi on webserver
python3.10 and above: Use CgiConnect2() and pytpdhost2.cgi on webserver
Unfortuantely, cannot mix and match the two "protocols" together since they are implemented differently.
"""
from .strmore import sha1, to_bytes, zlib_compress, zlib_uncompress
from os.path import dirname, join, exists, basename, isdir    # used by datahost.cgi
from contextlib import contextmanager
import pickle
import sys
import os
import hashlib
# NOTE: Do not add any more imports above!


is_py_10new = bool(sys.version_info >= (3, 10))


if is_py_10new:      # pragma: no cover  (tested via systemcall)
    # Python 3.10 and above
    import http.client
    import uuid
    from urllib.parse import urlparse
else:
    # Hack so that local http (which is modified) will work. This works up to 3.9.6.
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'httplocal'))


from http.client import HTTPSConnection


# ====== start_copy_block =======
class CgiConnect:
    """
    For python 3.9 and lower
    CGI Client/Server Class to send/receive data to and from server

    Client Usage:
       conn = CgiConnect('http://someurl/tvpv.cgi')
       result = conn.send(mydata)

    Server Usage:
       # set the correct sys.paths
       conn = CgiConnect(None)
       data = conn.receive()
       # do something, there should be no print in here
       conn.reply(data)
    """

    def __init__(self, url):
        """Set the url"""
        self.url = url

    def send(self, data):
        """Client: Send data, and get back result"""
        import urllib.request
        from gadget.files import TempName
        from io import FileIO

        with TempName(name=True) as tn:
            data = zlib_compress(pickle.dumps(data, protocol=4))
            with open(tn, 'wb') as fho:
                fho.write(to_bytes(self._header(data)))
                fho.write(data)

            with FileIO(tn, 'rb') as theFile:
                theHeaders = {'Content-Type': 'application/octet-stream'}
                theRequest = urllib.request.Request(self.url, theFile, theHeaders)
                response = urllib.request.urlopen(theRequest)

            rawdata = response.read()
            data = pickle.loads(zlib_uncompress(rawdata), encoding='latin1')   # trusted
            return data

    def _header(self, data):
        """Return the secure header"""
        return f"beef{hashlib.sha1(to_bytes(data)).hexdigest()}feed"

    def receive(self):         # pragma: no cover  (tested in test_basic)
        """Server: receive data"""
        import cgitb
        import cgi
        cgitb.enable()
        form = cgi.FieldStorage()
        message = form.value
        if len(message) < 48:
            exit(0)        # Invalid data

        head = message[:48]
        data = message[48:]
        if head != to_bytes(self._header(data)):
            exit(0)        # Invalid data

        return pickle.loads(zlib_uncompress(data))   # trusted data

    def reply(self, data):     # pragma: no cover  (tested in test_basic)
        """Server: send data (reply)"""
        print("Content-Type: application/octet-stream")
        print("Content-Disposition: attachment; filename=pytpd.data")
        print()

        prdata = zlib_compress(pickle.dumps(data, protocol=4))

        # Sys.stdout cannot be written with bytes directly in Python 3, need to open a new handle.
        try:
            sys.stdout.buffer.write(prdata)
        # This happens when adding -b to the unit test ... Python is hijacking STDOUT by mocking it with
        # a io.StringIO object that does not have a 'buffer' attribute and will not only accept unicode strings
        # not bytes() data.
        except AttributeError:
            pass
        exit(0)


class CgiConnect2:     # pragma: no cover  (tested via systemcall, -s)
    """
    Newer python (3.10 and above) version for CgiConnect()
    This class is only on client side.
    See pytpdhost2.cgi for Server side.
    See CgiConnect() for usage
    """

    def __init__(self, url):
        """Set the url"""
        self.url = url

    def _header(self, data):
        """Return the secure header"""
        return f"beef{hashlib.sha1(to_bytes(data)).hexdigest()}feed"

    def send(self, data):
        """Client: Send data, and get back result"""
        # Parse the URL
        parsed = urlparse(self.url)
        host = parsed.netloc
        path = parsed.path

        # Prepare the boundary
        boundary = uuid.uuid4().hex

        # Guess the mime-type of the file
        mime_type = 'application/octet-stream'

        # Create the body
        data = zlib_compress(pickle.dumps(data, protocol=4))
        data = to_bytes(self._header(data)) + data

        # send it
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file";filename="data.bin"\r\n'
            f'Content-Type: {mime_type}\r\n\r\n'
        ).encode('utf-8') + data + f'\r\n--{boundary}--\r\n'.encode('utf-8')

        # Perform the request
        conn = http.client.HTTPSConnection(host)
        conn.request("POST", path, body=body, headers={
            "Content-Type": f'multipart/form-data; boundary={boundary}'
        })
        response = conn.getresponse()
        response_data = response.read()
        conn.close()

        data = pickle.loads(zlib_uncompress(response_data))
        return data


class HTTPSConnection_TLS(HTTPSConnection):
    """
    HTTPSConnection override to use a specific ssl_version
    PG and IDC machine need this
    by gbalmas
    """

    def connect(self):
        """Connect to a host on a given (SSL) port."""
        import socket
        import ssl
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout, self.source_address)
        if self._tunnel_host:      # pragma: no cover  (not tested, copied from python library)
            self.sock = sock
            self._tunnel()

        # This is the only line we modified from the httplib.py file
        # we added the ssl_version variable
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                    ssl_version=ssl.PROTOCOL_TLSv1)


class Chunk:
    """
    Chunk class.

    Chunking Usage / protocol:
    a) Sender of large data [ie, DataHost do_<methods>()]:

        return Chunk.process(large_object)

        # 1. If size is less than threshold, then return object as-is
        # 2. create tmpdir
        # 3. split the pickled file into pieces
        # 4. return an instantiated Chunk() to receiver

    b) Receiver:

        if type(obj) is Chunk:
            for piece_n in xrange(obj.length):
                 # call the transport routine via obj,get_piece(piece_n)
                 # store into tempdir
            obj.assemble(tempdir, obj.sha)

    Performance: 179 MB is success - @759 sec (JF->PG)

    """
    CHUNK_LIMIT = 25000000      # limit of tbe pickled object, in bytes (see chunk_it() for compressed or compressed)
    # 10MB compressed is ~40-50 sec JF->PG
    # 25MB compressed is ~96-122 sec JF->PG
    TMPDIR = '/tmp/datahost_chunks'
    I_AM_CHUNK_DATAHOST = True

    def __init__(self, tdir):
        """Instantiated object attributes"""
        self.length = len(os.listdir(tdir))
        self.sha = basename(tdir)

    def assemble(self, tdir):
        """Return the unpickled object given the (client) tdir"""
        from gadget.files import SplitFile, TempName
        with TempName(name=True) as tn:
            SplitFile(tdir, tn)   # assemble
            with open(tn, 'rb') as fh:
                shafile = sha1(fh.read())
            if self.sha != shafile:
                raise Exception("Chunk(): data image was not transferred correctly: %s vs %s"
                                "" % (self.sha, shafile))
            with open(tn, 'rb') as fh:
                return pickle.load(fh)

    @classmethod
    def get_piece(cls, sha, n):
        """Return the contents of this particular piece"""
        fname = join(cls.TMPDIR, sha, 'file.%d' % n)
        length = len(os.listdir(dirname(fname)))
        if exists(fname):
            with open(fname, 'rb') as fh:
                data = fh.read()
            if n + 1 == length:
                import shutil
                shutil.rmtree(dirname(fname))
            return data
        else:
            raise Exception("[%s] does not exist on server" % fname)

    @classmethod
    def process(cls, obj, compress=False):
        """
        Return the obj as-is if the pickled size of object is < chunk limit
        If >, then return a Chunk() object
        Set compress=True to use the compressed size for chunk limit determination
        However, the chunking is done on the uncompressed pickle file
        """
        from gadget.disk import mkdirs
        from gadget.files import SplitFile, TempName

        pkl = pickle.dumps(obj)
        size = len(pkl)
        if compress:
            size = len(zlib_compress(pkl))

        if size < cls.CHUNK_LIMIT:
            return obj    # nothing to do

        # at this point, do the chunking process (uncompressed pickle data)
        sha = sha1(pkl)
        tdir = join(cls.TMPDIR, sha)
        mkdirs(tdir, mode='02777')
        # TODO: need code to delete stale sha directories

        with TempName(name=True) as tn:
            with open(tn, 'wb') as fh:
                fh.write(pkl)                    # write the pickle file
            SplitFile(tn, tdir, size=cls.CHUNK_LIMIT)    # split it up

        return cls(tdir)    # instantiated object of Chunk()


class DataHost:
    NOTFOUND = {}            # empty object, unique identifier of NOTFOUND

    # --- commands ---
    def do_sendmail(self, data):
        """
        Send email (unix)
        :param data: (address, title, message) or dict
        :return:
        """
        from gadget.gizmo import send_mail

        if isinstance(data, dict):
            args = data
        else:
            address, subject, message = data
            args = {'to_list': address,
                    'subject': subject,
                    'message': message}

        if 'fromemail' not in args:
            args['fromemail'] = 'frombot'

        send_mail(**args)

    def do_move_job(self, data):
        """
        Given the job from pool, move it remotely

        :param data: (pkg, job, tester)
        :return: True for success, False for not
        """
        from main.manager_botos import BotOS
        from gadget.files import File
        from gadget.disk import mkdirs

        pkg, job, tester = data

        stagingfolder = f'{BotOS.root}/staging/{pkg}'
        destination = f'{BotOS.root}/testers/{tester}'

        mkdirs(destination, mode='02775')
        if not os.path.exists(f'{stagingfolder}/{job}'):
            return False

        File(f'{stagingfolder}/{job}').rename(f'{job}.wip.gz')         # rename to wip first
        File(f'{stagingfolder}/{job}.wip.gz').move(destination)        # Do the move
        File(f'{destination}/{job}.wip.gz').rename(job)                # remove the wip
        return True

    def do_get_files(self, data):
        """
        Get files and their age in a remote_site

        :param data: is_staging: True|False
        :return: {tester: {fname: age}}
        """
        from main.manager_botos import BotOS
        import time
        return BotOS.get_files_local(time.time(), is_staging=data)

    def do_write_json(self, data):
        """
        Write json file in given folder

        :param data: (data, nrfname, folder)
        :return: success string
        """
        import json
        (data2write, nrfname, folder) = data

        if not exists(f'{folder}/{nrfname}'):
            with open(f'{folder}/{nrfname}', 'w') as fp:
                json.dump(data2write, fp, indent=3)

        return f'Written: {folder}/{nrfname}'

    def do_write_file(self, data):
        """
        Write json file in given folder

        :param data: (fname, text, is_mkdir)
        :return: success string
        """
        (fname, text, is_mkdir) = data
        from gadget.files import File
        File(fname).touch(text, mkdir=is_mkdir, newfile=True)

        return f'Written: {fname}'

    def do_read_completed(self, data):
        """
        Read all json in completed folder
        :param data: unused
        :return: {'filename.json': <data>}
        """
        from main.manager_botos import BotOS
        root = f'{BotOS.root}/completed'
        result = {}
        for fname in os.listdir(root):
            if fname.endswith('.json'):
                result[fname] = BotOS.json.load(f'{root}/{fname}', 'datahost:read_completed()')
        return result

    def do_read_json(self, data):
        """
        Read json file given the file

        :param data: fname
        :return: data
        """
        import json
        with open(data) as fp:
            return json.load(fp)

    def do_cleanup_dir(self, data):
        """
        Delete oldest file of these folders
        :param data: {dir: max_count}
        :return:
        """
        from gadget.disk import delete_oldest

        result = []
        for folder in data:
            result.extend(delete_oldest(folder, keep=data[folder], message=None))
        return result

    def do_delete_files(self, data):
        """
        Delete the files in data

        :param data: list of files (fullpath)
        :return:
        """
        result = []
        for fname in data:
            if exists(fname):
                result.append(f'Deleted: {fname}')
                os.unlink(fname)
            else:
                result.append(f'For delete but not found: {fname}')

        return '\n'.join(result)

    def do_get_meta_content(self, data):
        """
        Read the meta_content json of staging
        :param data: None
        :return: {package: {fname: value}}
        """
        from main.manager_botos import BotOS
        return BotOS.get_meta_content()

    def do_gitpull(self, data, _cmd={'gitpull': 'git pull',
                                     'gitlog': 'git log -n 1'}):
        """
        Do a git pull and git log
        :param data: cwd_path (string)
        :return: {'out_pull': stdout_git_pull,
                  'err_pull': stderr_git_pull,
                  'out_log': stdout_git_log,
                  'err_log': stderr_git_log)
        """
        from gadget.disk import Chdir
        from gadget.shell import SystemCall, HOSTNAME

        # set required env so git pull is successful
        os.environ["https_proxy"] = 'http://proxy-dmz.intel.com:912'
        os.environ['USER'] = 'p6vector'
        os.environ['LOGNAME'] = 'p6vector'
        os.environ['HOME'] = '/nfs/site/home/p6vector'

        with Chdir(data):
            _, out_pull, err_pull = SystemCall(_cmd['gitpull']).run_sout_serr()
            _, out_log, err_log = SystemCall(_cmd['gitlog']).run_sout_serr()
            cwd = os.getcwd()

        return {'out_pull': out_pull,
                'err_pull': err_pull,
                'out_log': out_log,
                'err_log': err_log,
                'machine': HOSTNAME,
                'cwd': cwd}

    def do_test1(self, data):
        """unittest only"""
        print("some-stdout")
        sys.stderr.write("Some-stderr ")
        return data + 200

    def do_test2(self, data):
        """unittest only - exception occurred"""
        data[45] = None
        return data

    def do_test3(self, data):
        """unittest only - small chunks"""
        from gadget.gizmo import MockVar
        with MockVar(Chunk, "CHUNK_LIMIT", 100000):
            return Chunk.process(data)

    def do_get_chunk(self, data):
        """Return the file contents of this n"""
        sha, n = data
        return Chunk.get_piece(sha, n)

    def do_ulat_copy(self, data, _root='/intel/engineering/dev/sctp/tptorrent/ulat/fsm/hdmx'):
        """
        Copy ulat folder to a specific site
        root folder: I:/engineering/dev/sctp/tptorrent/ulat/fsm/hdmx   (JF,PG,FM,IDC,BA standard)
        data is ('nvl/CLASS_S58C/05D00/FullSkipModelInput.csv', <content_of_csv>)
        """
        # process args
        fname, contents = data
        product = dirname(dirname(dirname(fname)))
        self._ulat_copy(product, _root, fname, contents)

    def _ulat_copy(self, product, _root, fname, contents):
        """Do the actual copy"""
        # do imports
        import gadget.files
        from gadget.tvpv import TvpvEnv
        from gadget.disk import mkdirs
        from gadget.files import File

        assert os.path.isdir(f'{_root}/{product}'), f'{_root}/{product} does not exist in {TvpvEnv.get_site()}'

        # make the directory
        mkdirs(f'{_root}/{dirname(fname)}', mode="02775")    # $root/nvl/CLASS_S58C/05D00

        # write the file
        File(f'{_root}/{fname}').touch(contents, newfile=True)

    def do_ulatmv_copy(self, data, _root='/intel/engineering/dev/sctp/tptorrent/hdmxprogs'):
        """
        Copy ulat mv folder to local site
        root folder: I:/engineering/dev/sctp/tptorrent/hdmxprogs   (JF,PG,FM,IDC,BA standard)
        data is ('nvl/ulat_mv/fsm/{timesec}/FullSkipModelInput.csv', <content_of_csv>)
        """
        # process args
        fname, contents = data
        product = dirname(dirname(dirname(dirname(fname))))
        self._ulat_copy(product, _root, fname, contents)

    def do_getinfo(self, data):
        """
        Return the info of server
        Usage:
        python -c 'from sockets.data_host import DataHost;print DataHost().product('getinfo', 1)'

        for vmsize >2GB check:
        python -c 'from sockets.data_host import DataHost;print DataHost().product('getinfo', 70000000)'
        """
        from gadget.shell import vmsize, HOSTNAME, USERNAME
        from gadget.strmore import curtime

        var = [x for x in range(data)]
        return (HOSTNAME,
                vmsize(),
                os.path.realpath(sys.executable),
                curtime(),
                USERNAME,
                data + 1000)

    def do_check_destdir(self, data):
        """
        Check destination dir if it is writeable. Make sure to turn on check=True on call.
        :param data: unix path destination directory
        """
        from gadget.errors import check
        check.is_dir_empty_writeable(data)
        return f"Success check: {data}"

    def do_path_exists(self, data):
        """
        Return if list of paths exists
        :param data: list of paths (either windows or unix paths)
        :return: dict {path: bool if path exist}
        """
        from tp.testprogram import Env
        return {p: exists(Env.xpath(p)) for p in data}

    def do_untar(self, data):
        """
        Untar the tar file. Untar into the <path>. Delete the tar after
        :param data: <path>/tar
        """
        import tarfile
        from gadget.disk import Chdir, Allfiles
        from gadget.files import File
        from gadget.shell import SystemCall

        dirpath = dirname(data)
        list(Allfiles(dirname(dirpath)))     # This is needed to refresh the filer, or else the file is not found.
        tar = tarfile.open(data, "r:gz")
        with Chdir(dirpath):
            tar.extractall()
        tar.close()
        File(data).unlink()
        SystemCall(f'chmod -R g+w {dirpath}').run_outtxt()
        SystemCall(f'chgrp -R gdlusers {dirpath}').run_outtxt()
        return "OK"

    def do_invokellm(self, data):
        """
        Invoke LLM model with given prompt

        :param data: (model_name, prompt)
        :return: response content
        """
        sys.path.insert(0, '/intel/tpvalidation/engtools/tptools/mtl/tools/py3genai')
        from langchain_openai import ChatOpenAI
        import truststore
        truststore.inject_into_ssl()
        # Get prompt and api_key
        prompt = data.get("prompt", "No input prompt provided.")
        api_key = data.get("api_key", None)
        if api_key is None:
            try:
                with open('/nfs/pdx/disks/tvpvweb/cgi-bin/important/SYS_TPROBOT_EXPERTGPT_API.txt') as fh:
                    text = fh.read()
                    api_key = bytes.fromhex(text.strip()).decode()
            except Exception as e:
                message = f"Failed to get API key: {e}"
                return message

        llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://expertgpt.intel.com/v1",
            model="gpt-5-mini",
            temperature=0
        )
        try:
            response = llm.invoke(prompt)
            return response.content
        except Exception as e:
            message = f"Error invoking LLM model: {e}"
            return message

    def _receive_chunk(self, root, prod, data, conn):
        """Return the obj as-is if it is not a Chunk object, else get all the pieces"""
        if not hasattr(data, 'I_AM_CHUNK_DATAHOST'):
            return data
        from gadget.files import TempDir
        command = 'get_chunk'
        with TempDir(name=True) as tdir:
            for piece_n in range(data.length):
                print("Getting chunk %s of %s" % (piece_n + 1, data.length))
                res = conn.send((command, root, prod, (data.sha, piece_n)))
                if res[0] == 'Ok':
                    with open(join(tdir, 'file.%d' % piece_n), 'wb') as fh:
                        fh.write(res[1])
                else:
                    raise Exception("DataHost [%s]: %s" % (command, res))

            return data.assemble(tdir)

    SITEMAP = {'PG': 'https://tvpv.png.intel.com/cgi-bin/pytpdhost.cgi',
               'FM': 'https://tvpv.fm.intel.com/cgi-bin/pytpdhost.cgi',
               'JF': 'https://tvpv.pdx.intel.com/cgi-bin/pytpdhost.cgi',
               'IDC': 'https://tvpv.iil.intel.com/cgi/pytpdhost.cgi',
               'BA': 'https://tvpv1.iind.intel.com/cgi-bin/pytpdhost.cgi'}

    @classmethod
    def _process_urp(cls, urp, site):
        """
        Return the conn, root, prod to use

        :param urp: (url, root, prod) tuple
        :param site: site string (must be one of SITEMAP)
        :return: (conn, root, prod)
        """
        from settings.default_product import DEFAULT_PRODUCT

        # check first
        msg = '[%s] is not a valid site. Valid: %s' % (site, ','.join(cls.SITEMAP))
        assert site in cls.SITEMAP, msg

        if urp:
            # If urp is specified, use as-is
            url, root, prod = urp
        else:
            url = cls.SITEMAP[site]
            root = '/intel/tpvalidation/engtools/tptools/mtl/beta/gen1'
            # root = '/intel/tpvalidation/jqdelosr/pytpd'

            prod = DEFAULT_PRODUCT    # unused

        # update correct url based on python version
        if is_py_10new:
            url = url.replace('pytpdhost.cgi', 'pytpdhost2.cgi')

        # Need this setting for older python
        if not is_py_10new:
            import http.client
            http.client.HTTPSConnection = HTTPSConnection_TLS       # so that IDC connection will work

        if 'pytpdhost2.cgi' in url:
            conn = CgiConnect2(url)
        else:
            conn = CgiConnect(url)

        return conn, root, prod

    def central(self, command, data, check=False, urp=None, site='JF'):
        """
        Execute command in central server

        :param command: string. This must match do_<command> routine.
        :param data: Any python object or data-structure
        :param check: Set to True to check results and just return the data
        :param urp: (url, root, prod) tuple, for development use
        :param site: Which site to talk to. Default is JF
        :return:
        """
        conn, root, prod = self._process_urp(urp, site)

        res = conn.send((command, root, prod, data))

        if check:
            if res[0] != 'Ok':
                raise Exception("DataHost [%s]: %s" % (command, res[1]))
            return self._receive_chunk(root, prod, res[1], conn)

        return res


# Execute to test:
# gadget/test/test_data_host.py -v BaseNumber_Analysis.tgl

class ProxyManager:
    """Utility class for managing Intel proxy settings"""

    @staticmethod
    @contextmanager
    def intel_proxy():
        """
        Context manager to set Intel proxy environment variables.
        Sets http_proxy and https_proxy to Intel DMZ proxy servers.
        Restores original values on exit.
        """
        # Store original values
        original_http = os.environ.get('http_proxy')
        original_https = os.environ.get('https_proxy')

        try:
            # Set Intel proxy values
            os.environ['http_proxy'] = 'http://proxy-dmz.intel.com:911'
            os.environ['https_proxy'] = 'http://proxy-dmz.intel.com:912'
            yield
        finally:
            # Restore original values
            if original_http is None:
                os.environ.pop('http_proxy', None)
            else:
                os.environ['http_proxy'] = original_http

            if original_https is None:
                os.environ.pop('https_proxy', None)
            else:
                os.environ['https_proxy'] = original_https

    @staticmethod
    @contextmanager
    def no_proxy():
        """
        Context manager to temporarily remove proxy environment variables.
        Removes http_proxy and https_proxy if they exist.
        Restores original values on exit.
        """
        # Store original values
        original_http = os.environ.get('http_proxy')
        original_https = os.environ.get('https_proxy')

        try:
            # Remove proxy settings if they exist
            os.environ.pop('http_proxy', None)
            os.environ.pop('https_proxy', None)
            yield
        finally:
            # Restore original values if they existed
            if original_http is not None:
                os.environ['http_proxy'] = original_http
            if original_https is not None:
                os.environ['https_proxy'] = original_https
