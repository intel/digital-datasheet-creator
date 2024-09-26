import os
import sys

from cx_Freeze import Executable, setup
from setuptools import find_packages

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

packages = [
    'bs4', 'conf_diff', 'genson', 'jsonpath_rw_ext',
    'openpyxl', 'pandas', 'xlsxwriter', 'xmltodict', 'defusedxml'
]

main_packages = ['edatasheets_creator', 'edatasheets_creator.*']

packages += find_packages(include=main_packages)

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": packages,  # required packages
    "excludes": ["lief", "tkinter", "sqlite3", "Pillow"],  # not required package
    "build_exe": "build/tox/exe-win-output",
}

# A CMD application
base = None

# Main target file
target_main = "./edatasheets_creator/main.py"

setup(name="TestApp",
      version="0.1",
      description="Tool description",
      author="Author",
      options={"build_exe": build_exe_options},
      executables=[Executable(target_main, base=base)]
      )
