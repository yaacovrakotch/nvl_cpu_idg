import evg
import sys
import re

VERBOSE = "DISABLED"

ENABLED_LOCATIONS = ['6248', '6274']
ENABLED_PROCESS_STEP = ['CLASSHOT', 'CLASSCOLD']
ENABLED_GT_SKU = ['1x6x16VD0VD2']
ENABLED_SLICESTATUS = ['00001111']

ENABLED_DOWNBIN_LOCATIONS = ['6248']
ENABLED_DOWNBIN_PROCESS_STEP = ['CLASSHOT']

PRE_EXECUTE_ENABLE_PORT = 2

PROCESS_STEP = ''
LOCATION = ''

RE_TAG = re.compile("(?<=_)P\d+T\d+$")
RE_ARGS = re.compile("\s*(\w+)\s*=\s*([^\s]+)\s*")


def print_dbg(*args):
    """
    A print function which respects debug_mode parameter setting
    """
    if VERBOSE != "DISABLED":
        for a in args:
            evg.PrintToConsole("-%s- %s" % ('ccr.py', a))


def respect_verbosity(func):
    """
    Check debug_mode paramter at function call time and update internal tracking
    """
    def _respect_verbosity(*args, **kwargs):
        global VERBOSE
        try:
            VERBOSE = evg.GetTestParam(evg.GetInstanceName(), "debug_mode")
        except:
            VERBOSE = "UNKNOWN"
        print_dbg("%s start" % func.__name__)
        r = func(*args, **kwargs)
        print_dbg("%s end" % func.__name__)
        return r
    return _respect_verbosity


def get_args(func):
    """
    Convert calling functions passed parameters into a standard args dictionary
    """
    def _get_args_wrapper():
        arg_string = evg.GetUFArgument()
        test_name = evg.GetInstanceName()
        split_name = test_name.split('::')
        if len(split_name) == 3:
            intra_domain = split_name[0]
            module_name = split_name[1]
        else:
            intra_domain = ""
            module_name = split_name[0]
        kwargs = dict(RE_ARGS.findall(arg_string))
        kwargs['test_name'] = test_name
        kwargs['module_name'] = module_name
        kwargs['intra_domain'] = intra_domain
        return(func(**kwargs))
    return _get_args_wrapper


def get_gsds_str(gsds_var):
    """
    Helper function to get gsds string values safely
    """
    value = ''
    try:
        value = evg.GetGSDSData(gsds_var, 'string', 'UNT', -99, 0)
        print_dbg('GetGSDSData::%s = %s\n' % (gsds_var, value))
    except:
        e = sys.exc_info()[0]
        print_dbg("ERROR(GetGSDSData)::%s\n" % e)
    return value


def set_bypass_var(var, value):
    """
    Helper function to set bypass variables safely
    """
    print_dbg("setting %s = %s" % (var, value))
    try:
        evg.SetTpGlobalIntValue(var, value)
    except:
        e = sys.exc_info()[0]
        print_dbg("ERROR(SetTpGlobalIntValue %s %s)::%s\n" % (var, value, e))


def downbin_is_allowed():
    """
    Determine if location is valid for CCR based on PROCESS_STEP and LOCATION
    Varaibles are not refreshed on call, only during init()
    """
    print_dbg("read LOCATION as %s" % LOCATION)
    print_dbg("read PROCESS_STEP as %s" % PROCESS_STEP)
    if LOCATION in ENABLED_DOWNBIN_LOCATIONS:
        if PROCESS_STEP in ENABLED_DOWNBIN_PROCESS_STEP:
            return True
    return False


def location_is_enabled():
    """
    Determine if location is valid for CCR based on PROCESS_STEP and LOCATION
    Varaibles are not refreshed on call, only during init()
    """
    print_dbg("read LOCATION as %s" % LOCATION)
    print_dbg("read PROCESS_STEP as %s" % PROCESS_STEP)
    if LOCATION in ENABLED_LOCATIONS:
        if PROCESS_STEP in ENABLED_PROCESS_STEP:
            return True
    return False


def sku_is_enabled():
    """
    sku_is_enabled() will return True if current device meets all sku requirements for CCR
    Otherwise it will return False
    Valid sku options are defined by ENABLED_SLICESTATUS and ENABLED_GT_SKU
    """
    slice_status = ""
    gt_sku = ""

    try:
        assert evg.ExecuteFunction("DIE_RECOVERY!ExecSequence", "MirrorTracking")
        slice_status = get_gsds_str("SLICESTATUS")
    except AssertionError:
        e = sys.exc_info()[0]
        print_dbg("ERROR(ExecuteFunction.DIE_RECOVERY!ExecSequence MirrorTracking)\n%s" % e)
        print_dbg("SLICESTATUS could not be retrieved.  Concurrency will be disabled!")

    gt_sku = get_gsds_str("GT_SKU")

    print_dbg("read SLICESTATUS as %s" % slice_status)
    print_dbg("read GT_SKU as %s" % gt_sku)

    if slice_status in ENABLED_SLICESTATUS and gt_sku in ENABLED_GT_SKU:
        return True

    return False


def enable(setting=True, intra='', module='', tag=''):
    """
    User is to define the CCR enable state in CCR_BYPASS_VARS
    disable state is assumed to be the opposite of user defined state
    """
    if module == '':
        raise TypeError("argument module can not be null")

    if type(tag) is not str or tag == '':
        raise TypeError("passed parameter 'tag' must be of type str")

    if tag != "":
        print_dbg("setting CCR enable = %s for tag:%s" % (setting, tag))
    else:
        raise TypeError("argument tag can not be null")

    if intra:
        collection_name = "%s::%s::%s" % (intra, module, module)
    else:
        collection_name = "%s::%s" % (module, module)

    if setting:
        set_bypass_var("%s.CCR_%s" % (collection_name, tag), -1)
        set_bypass_var("%s.SERIAL_%s" % (collection_name, tag), 1)
    else:
        set_bypass_var("%s.CCR_%s" % (collection_name, tag), 1)
        set_bypass_var("%s.SERIAL_%s" % (collection_name, tag), -1)


@respect_verbosity
def init():
    """
    init() is intended to run once per test step (ie in test program init)
    function simply stores current process step and location for future reference
    """

    global PROCESS_STEP
    global LOCATION
    PROCESS_STEP = evg.GetTpGlobalValue("SCVars.SC_CURRENT_PROCESS_STEP", "string")
    LOCATION = evg.GetTpGlobalValue("SCVars.SC_LOCN", "string")

    print_dbg("init is setting LOCATION:%s PROCESS_STEP:%s" % (LOCATION, PROCESS_STEP))


@get_args
@respect_verbosity
def pre_execute(**kwargs):
    """
    pre_execute is to run once per pairing, before any CCR tests have executed
    Checks sku, slice status, location and process step to determine if CCR should be attempted
    CCR will be either disable or enabled for all tests in a pair based on this check
    User must supply current pair as a UF argument of the form pair=#
    """
    result = True
    pair = '\d+'
    tag = ''

    test_name = kwargs["test_name"]
    module_name = kwargs["module_name"]
    intra_domain = kwargs["intra_domain"]

    if 'tag' in kwargs:  # passed tag parameter has overriding priority
        print_dbg("processing argument tag=%s" % (kwargs['tag']))
        tag = kwargs['tag']
    else:
        try:
            tag = RE_TAG.findall(test_name)[-1]
        except IndexError:
            raise RuntimeError("tag of the form _P#I# expected but not found in test name %s further ccr.py processing will be skipped" % (test_name))
            return

    if sku_is_enabled() and location_is_enabled():
        result = enable(True, intra=intra_domain, module=module_name, tag=tag)
        evg.SetSitePort(0, PRE_EXECUTE_ENABLE_PORT)
    else:
        result = enable(False, intra=intra_domain, module=module_name, tag=tag)


@get_args
@respect_verbosity
def post_execute(**kwargs):
    """
    post_execute should be called as a post_instance UF on each relevant CCR test
    If the CCR test passes it will reapply CCR ENABLED bypass variables to tests of the same "tag"
    If the CCR test fails and current test operation allows downbinning, it will set CCR DISABLED
     bypass variables and exit port 1
    If the CCR test fails and current test operation does not allow downbinning, it will set CCR
     DISABLED bypass variables and exit port 0
    The "tag" is inferred from the name of the instance running.
    """
    exit_port = evg.GetSitePort(0)

    test_name = kwargs["test_name"]
    module_name = kwargs["module_name"]

    if "test_name_override" in kwargs:
        test_name = kwargs["test_name_override"]

    if "exit_port_override" in kwargs:
        exit_port = int(kwargs["exit_port_override"])
        evg.SetSitePort(0, exit_port)

    # Determine tag from currently executing test instance name
    try:
        tag = RE_TAG.findall(test_name)[-1]
    except IndexError:
        raise RuntimeError("tag of the form _P#I# expected but not found in test name %s further ccr.py processing will be skipped" % (test_name))

    if exit_port == 0 and downbin_is_allowed():  # CCR failed and downbin is allowed
        print_dbg("CCR %s failed, enabling serial downbin retest for %s instances" % (tag, tag))
        # set all bypass variables corresponding to current tag to CCR DISABLE state
        enable(setting=False, module=module_name, tag=tag)

        # force exit port 1 to allow for serial tests in main flow to rebin
        print_dbg("forcing exit port 1")
        evg.SetSitePort(0, 1)

    elif exit_port == 0 and not downbin_is_allowed():  # CCR failed and downbin is not allowed
        print_dbg("CCR %s failed, downbin not allowed for LOCATION:%s and PROCESS_STEP:%s" % (tag, LOCATION, PROCESS_STEP))
        # set all bypass variables corresponding to current tag to CCR ENABLE state
        enable(setting=True, module=module_name, tag=tag)

    else:  # CCR passed
        print_dbg("CCR %s passed" % (tag))  # Could skip for exec time improvement
        enable(setting=True, module=module_name, tag=tag)


@respect_verbosity
def do_nothing():
    pass


"""

Init subflow function
if location = 6248 and 6274
# set CCR_ON
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_P1I1 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_P1I2 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_P1I3 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_P1I4 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_SCN_GT_INSTANCE_P1I1 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_SCN_GT_INSTANCE_P1I2 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_SCN_GT_INSTANCE_P1I3 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_SCN_GT_INSTANCE_P1I4 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_P1I1 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_P1I2 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_P1I3 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_P1I4 = 1;

else
# set CCR_OFF
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_P1I1 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_P1I2 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_P1I3 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_P1I4 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_SCN_GT_INSTANCE_P1I1 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_SCN_GT_INSTANCE_P1I2 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_SCN_GT_INSTANCE_P1I3 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_SCN_GT_INSTANCE_P1I4 = 1;
set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_P1I1 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_P1I2 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_P1I3 = -1;
set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_P1I4 = -1;

CHK subflows fuction preintance
EXECUSERFUNC DIE_RECOVERY!ExecSequence,MirrorTracking
if not G.U.S.SLICESTATUS = 00001111
set CCR_OFF
if not G.U.S.GT_SKU = full sku
set CCR_OFF

CHK subflows fuction postinstance
CHK intance1

get flagtype (CCRP1I1) from intance name


if exit port 0 and (location = 6248 and SCVars.SC_CURRENT_PROCESS_STEP = "CLASSHOT");
    set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_+flagtype = -1;
    set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_+$flagtype = -1;
    Set port 1

else if exit port 0 and location != 6248 and SCVars.SC_CURRENT_PROCESS_STEP != "CLASSHOT";
    Set port 0
    set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_flagtype = 1;
    set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_flagtype = 1;

else
    set CCR_ARR_CORE_SCN_GT.CCR_ARR_CORE_INSTANCE_flagtype = 1;
    set CCR_ARR_CORE_SCN_GT.CCR_SCN_GT_INSTANCE_flagtype = 1;

"""
