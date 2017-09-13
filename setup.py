from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')
sys.argv.append('-q')

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = "0.2.1"
        self.company_name = "SK Holdings"
        self.copyright = "copyleft"
        self.name = "vdiff2"

target = Target(
    description = "Advanced vdiff2 Program",
    script = "vdiff2.py",
    dest_base = "vdiff2")
        
setup(
    options = {'py2exe': {'bundle_files': 1,
                          'compressed'  : True,
                          'excludes':['_ssl',  # Exclude _ssl
                                    'pyreadline', 'difflib', 'doctest', 
                                    'optparse', 'pickle', 'calendar'],  # Exclude standard library
                          'dll_excludes':['msvcr71.dll']
                          }},
    windows = [target],
    zipfile = None
)