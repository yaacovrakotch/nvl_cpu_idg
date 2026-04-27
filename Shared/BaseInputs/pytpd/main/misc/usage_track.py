"""
This library will track the usage per script per user
It tracks the number of times the script was started and how many times it successfully finished
The idea is to generate stats for prioritizing development on the scripts that are used the most
"""
import os, sys, re, getpass, datetime
import pandas as pd
from gadget.helperclass import IS_UT


from pathlib import PurePath
sys.path.append ( os.fspath ( PurePath ( os.path.realpath(__file__) ).parents [ 1 ] ) + "/Lib" )

#Logger
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()] )
logger = logging.getLogger(__name__)



def add_start_hit ( script_name ):
    """
    Tracks the number of times the scripts are called by each user
    """
    if IS_UT:
        return 1 # Do not log unittests
    user_id = getpass.getuser()
    try:
        add_hit ( script_name, user_id, "start" )
    except Exception as e:
        logger.error( f"Likely unable to add start hit to '{script_name}' userid '{user_id}' due to '{e}'")
        pass


def add_finish_hit ( script_name ):
    """
    Tracks the number of times per user that a script successfully finished its execution
    """
    if IS_UT:
        return 1 # Do not log unittests
    user_id = getpass.getuser()
    try:
        add_hit ( script_name, user_id, "finish" )
    except Exception as e:
        logger.error( f"Likely unable to add finish hit to '{script_name}' userid '{user_id}' due to '{e}'")
        pass


def add_hit ( script_name, user_id, mode ):
    hit_file_path = get_hit_file_path()

    if not os.path.exists ( hit_file_path ):        #Tracking file not created yet
        create_file ( hit_file_path, ["#tp_diff usage tracking file"] )

    #Parse existing hits
    hit_contents = parse_hit_file_contents ( hit_file_path )    #Dict DF: ["Script_name", "User_id", "Start_hits", "Finish_hits"]

    hits = hit_contents[ ( hit_contents["User_id"] == user_id ) & ( hit_contents["Script_name"] == script_name )]

    start_hits = 0
    finish_hits = 0
    if hits.shape[0] > 0:
        start_hits = hits["Start_hits"].tolist()[0]
        finish_hits = hits["Finish_hits"].tolist()[0]

        if mode == "start":
           logger.info(f"You've executed this script '{start_hits}' times out of which '{finish_hits}' times finished w/o errors. ")
    else:
        if mode == "start":
            logger.info("This is the 1st time you execute this script this month!")
            hit_contents = hit_contents.append ( {'Script_name': script_name, "User_id": user_id, "Start_hits": 0, "Finish_hits": 0 }, ignore_index=True )

    if mode == "start":
        start_hits += 1
    elif mode == "finish":
        finish_hits += 1

    #Update DF
    hit_contents.loc [ ( hit_contents["User_id"] == user_id ) & ( hit_contents["Script_name"] == script_name ), [ "Start_hits"] ] = start_hits
    hit_contents.loc [ ( hit_contents["User_id"] == user_id ) & ( hit_contents["Script_name"] == script_name ), [ "Finish_hits"] ] = finish_hits

    update_hit_file ( hit_file_path, hit_contents )


def update_hit_file ( hit_file_path, hit_contents ):        #Takes csv
    csv_file_contents = hit_contents.to_csv ( header=False, index=False ).splitlines()
    create_file ( hit_file_path, csv_file_contents )


def parse_hit_file_contents ( hit_file_path ):      #Dict DF: ["Script_name", "User_id", "Start_hits", "Finish_hits"]
    try:
        file_contents = read_file ( hit_file_path )
    except Exception as e:
        raise Exception (f"Error reading hit file '{hit_file_path}' due to '{e}'")


    rcontents = []
    for x in file_contents:
        match = re.search ( r"^(\w+?),(\w+?),(\d+?),(\d+)$", x )
        if match:
            script_name = match.group ( 1 )
            user_id = match.group ( 2 )
            start_hits = int ( match.group ( 3 ) )
            finish_hits = int ( match.group ( 4 ) )
            rcontents.append ( [ script_name, user_id, start_hits, finish_hits ] )
        else:
            logger.warning ( f"Line '{x}' in the hit file not meeting the expected syntax" )

    hit_contents = pd.DataFrame( rcontents, columns = ["Script_name", "User_id", "Start_hits", "Finish_hits"] )

    return hit_contents


def get_hit_file_path ():
    """ The filename is one per month. YYYY_Month.hit
        Syntax like "SCRIPT,user,start_hits,finish_hits"
    """
    year = datetime.date.today().strftime("%Y")
    mon = datetime.date.today().strftime("%B")
    filename = year + '_' + mon + ".hits"

    uglobals = "/intel/engtools/tptools/mtl/logs/tp_diff/Hits"
    if not os.path.exists(uglobals):
        raise Exception (f"User globals file {uglobals} doesnt exist")

    hit_folder = uglobals

    hit_file_path = hit_folder + "/" + filename

    hit_file_path = re.sub(r"//+","/", hit_file_path)

    return hit_file_path

def create_file(filepath, contents):
    try: 
        with open(filepath, 'w') as f:
            for x in contents:
                f.write( x )
                f.write( "\n" )
    except Exception as err:
        raise Exception(f'Unable to write the file {filepath} due to {err}')

    try: 
        os.chmod(filepath, 0o770)
    except Exception as err:
        logger.error(f'Unable to change permission of file {filepath} during its creation due to {err}')


def read_file(filepath):
    """
    :param filepath: simple path to the file to read
    :return: contents: arr of lines
    """
    rcontents = read_file_raw(filepath)
    ccontents = raw_to_no_commented_lines(rcontents)

    return ccontents

def read_file_raw(filepath):
    """
    :param filepath: simple path to the file to read
    :return: contents: (array)
    """
    if not os.path.exists(filepath):
        raise Exception(f'Unable to read file {filepath} due to the file does not exists.')

    rcontents = []
    try:
        with open(filepath, "r") as fh:
            rcontents = fh.read().splitlines()
    except Exception as err:
        raise Exception(f'Unable to read file {filepath} due to {err}')

    return rcontents

def raw_to_no_commented_lines(rcontents):
    ccontents = []
    empty_line_re = re.compile(r"^\s*(#.*)?$") # removes parse_hit_file_contents
    for x in rcontents:
        if x == '':
            continue

        if empty_line_re.search(x): #ignore empty lines
            continue

        #removes comments if any
        line = x.split('#')
        stripped_string = line[0].rstrip()
        ccontents.append(stripped_string)

    return ccontents

def get_script_name ( fullfilepath ):
    osr = SRegex()
    if osr.search (r"/(\w+?)\.py", fullfilepath, re.IGNORECASE):
        return osr.get_match(0)
    elif osr.search (r"(\w+)\.py", fullfilepath, re.IGNORECASE):
        return osr.get_match(0)
    else:
        raise Exception ( f"Unknown script name out of filepath '{fullfilepath}'" )


class SRegex(object):
    def __init__(self):
      self.n_matches = 0
      self.regex_hits_matches = []

    def search ( self, pattern, text, flags ):
        regexo = ''
        if flags == '':
            regexo = re.compile ( pattern )
        else:
            regexo = re.compile(pattern, flags)

        regex_res = regexo.search ( text )

        if regex_res:
            matches = regex_res.groups()
            self.regex_hits_matches = matches
            return 1

        return 0

    def get_matches ( self ):
        return self.regex_hits_matches


    def get_match ( self, idx ):
        return self.regex_hits_matches[idx]