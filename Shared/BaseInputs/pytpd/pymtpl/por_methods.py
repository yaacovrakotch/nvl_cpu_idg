"""
python module importer for por_methods.py

Look into Shared/BaseInputs/Scripts/por_methods.py (cwd is relative to tp root)
Then ../../Shared/BaseInputs/Scripts/por_methods.py (cwd is relative to module)
"""
import glob
import os
from importlib.machinery import SourceFileLoader

POR_METHOD_SEARCH_PATHS = (
    'Shared/BaseInputs/Scripts/por_methods.py',             # tp root first
    '../../Shared/BaseInputs/Scripts/por_methods.py',       # module folder next
    '../../../Shared/BaseInputs/Scripts/por_methods.py',    # module folder 2nd level
    '../../../../Shared/BaseInputs/Scripts/por_methods.py',    # module folder 3rd level
    '../../../../../Shared/BaseInputs/Scripts/por_methods.py',    # module folder 4th level
    '../../../../../../Shared/BaseInputs/Scripts/por_methods.py',    # module folder 5th level
    'UserCode/[Pp]ymtpl/por_methods.py',                       # tp root first
    '../../UserCode/[Pp]ymtpl/por_methods.py',                 # module folder next
    '../../../UserCode/[Pp]ymtpl/por_methods.py',                 # module level 2nd next
    '../../../../UserCode/[Pp]ymtpl/por_methods.py',                 # module level 3rd level
    '../../../../../UserCode/[Pp]ymtpl/por_methods.py',                # module level 4th level
    '../../../../../../UserCode/[Pp]ymtpl/por_methods.py',
    'Shared/BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',             # with pymtpl parent so that it can be loaded as a python module
    '../../Shared/BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',       # module folder next
    '../../../Shared/BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',    # module folder 2nd level
    '../../../../Shared/BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',    # module folder 3rd level
    '../../../../../Shared/BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',    # module folder 4th level
    '../../../../../../Shared/BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',    # module folder 5th level
    'BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',             # tp root first in common repo
    '../../BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',       # module folder next in common repo
    '../../../BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',    # module folder 2nd level in common repo
    '../../../../BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',    # module folder 3rd level in common repo
    '../../../../../BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',    # module folder 4th level in common repo
    '../../../../../../BaseInputs/Scripts/[Pp]ymtpl/por_methods.py',    # module folder 5th level in common repo
    'Scripts/[Pp]ymtpl/[Pp]ymtpl/por_methods.py',                       # for DMR-HD support
    '../../Scripts/[Pp]ymtpl/[Pp]ymtpl/por_methods.py',                 # module folder
    '../../../Scripts/[Pp]ymtpl/[Pp]ymtpl/por_methods.py',              # module folder 2
    '../../../../Scripts/[Pp]ymtpl/[Pp]ymtpl/por_methods.py',           # module folder 3
    '../../../../../Scripts/[Pp]ymtpl/[Pp]ymtpl/por_methods.py',        # module folder 4
)


def imp(fname):
    """
    Will do the equivalent of: "from {fname} import *"

    :param fname: fullpath to python file
    :return: None
    """
    print(f'-i- por_methods: {fname}')
    module_name = os.path.splitext(os.path.basename(fname))[0]

    # Import it
    module = SourceFileLoader(module_name, fname).load_module()  # TODO: load_module is deprecated, need to use exec_module

    # Get all attributes from the module and add them to the global namespace
    globals().update({name: getattr(module, name) for name in dir(module) if not name.startswith('_')})


# Do the import
for wild in POR_METHOD_SEARCH_PATHS:
    files = sorted(glob.glob(wild))
    if files:
        imp(files[0])
        break
else:
    # import por_methods_default if TP repo por_methods.py does not exist
    print('-i- Warning: using default por_methods')
    from pymtpl.por_methods_default import *
