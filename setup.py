from distutils.core import setup
import py2exe

py2exe_options = dict(
                      ascii=True,  # Exclude encodings
                      excludes=['_ssl',  # Exclude _ssl
                                'pyreadline', 'difflib', 'doctest',  
                                'optparse', 'pickle', 'calendar'],  # Exclude standard library
                      dll_excludes=["MSVCP90.dll", 'w9xpopen.exe'],  # Exclude msvcp
                      compressed=True,  # Compress library.zip
                      )

setup(
    name='Lava lamp',
    version='1.0',
    description='Lava lamp - client',
    author='Marek Krempa',
    options = {"py2exe": py2exe_options},
    windows = [{'script': 'lava.py'}]
)
