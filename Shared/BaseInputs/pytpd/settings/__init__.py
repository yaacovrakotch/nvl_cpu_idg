"""
Package init file. To identify the directory is a python package
"""

# these two lines will allow python to continue searching to the rest of
# the PYTHONPATH dirs even if the module is not found in the first one.

import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)
