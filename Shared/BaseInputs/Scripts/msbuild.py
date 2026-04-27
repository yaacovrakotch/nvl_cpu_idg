#!/intel/tpvalidation/engtools/tptools/mtl/pyston/pyston2.3.4/bin/pyston -u
"""
Run msbuild

Usage:
msbuild.py ArrowLake_H68.sln
"""
import sys
try:
    import setenv      # must be first in imports
except ImportError:    # pragma: no cover    - Used when local qgate .py is in tp area
    sys.path.append('Shared/BaseInputs/pytpd')     # This works, as long as script is called from TP root area
    sys.path.append('I:/tpvalidation/engtools/tptools/mtl/beta/latest')

from gadget.gizmo import Elapsed
from gadget.shell import SystemCall
from gadget.errors import exit1
from os.path import exists, dirname
import shutil


# Below is a simple way to inform user if they are using old python version
f'If you see SyntaxError, this means your python version is old. Pls upgrade to python3.8 minimum: https://wiki.ith.intel.com/display/ITSpdxtp/python+download'

choices = (r'C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\amd64\MSBuild.exe',
           r'C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\amd64\MSBuild.exe')

def copy_dll_file():
    """
    This is a bandage temporarily while we root cause the issue with ValueTuple.dll because it's leaky on the source version that dll was built cause intermitten issue on INIT.
    """
    source_file = './UserCode/ValueTuple/System.ValueTuple.dll'
    dest_file = './UserCode/lib/Release/System.ValueTuple.dll'
    shutil.copyfile(source_file, dest_file)

def main():

    arg1 = sys.argv[1]
    sw = Elapsed()

    for msbuild_exe in choices:
        if exists(msbuild_exe):
            break
    else:
        exit1(f'[{choices[0]}] does not exist', 'Where is MSBuild.exe?')

    # run it
    slnfile = arg1
    cmd = ([msbuild_exe, slnfile] +
           "-m -verbosity:normal -nologo -restore -p:Configuration=Release".split() +
           ["-p:Platform=Any CPU"])
    code, sout, serr = SystemCall(cmd, disp=True).run_sout_serr()

    # expect "1 Error(s)" in sout
    success = ' 1 Error(s)'
    for line in sout.split('\n'):
        line = line.strip()
        if line == success:
            break
    else:
        exit1(f"Build Errors found. Expecting '{success}' in the build.",
              "Refer to log messages above. Pls fix build errors first.")

    print(f"MSBUILD is DONE in {sw}.")
    # print("Start correcting the ValueTuple dll file...")
    # copy_dll_file()
    


if __name__ == '__main__':  # pragma: no cover
    main()
