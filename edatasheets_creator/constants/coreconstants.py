"""
Core Constants
"""

# Arguments help messages
INPUT_FILE_HELP_ARGUMENT = 'Input file name'
MAP_HELP_ARGUMET = 'Input map to guide parser (json file)'
OUTPUT_HELP_ARGUMENT = 'Output file name'
TARGET_HELP_ARGUMENT = 'Target specification of output'
FIXUP_HELP_ARGUMENT = 'Map file to replace or include fields in the input datasheet, please check the structure for this file provided in the README'
CCG_PDG_CHECKER_HELP_ARGUMENT = 'Specific for only CCG PDG checker'
DCAI_PDG_CHECKER_HELP_ARGUMENT = 'Specific for only DCAI PDG checker'
POWER_SEQUENCE_HELP_ARGUMENT = "Power Sequence File Conversion to WaveDrom"
DIRECTORY_LISTING_HELP_ARGUMENT = 'Input folder to list the DITA files (also includes the files inside folders that is part of the Input Folder)'

# Console parameter
INPUT_FILE_ARGUMENT = '--f'
MAP_ARGUMENT = '--m'
OUTPUT_ARGUMENT = '--o'
TARGET_ARGUMENT = "--t"
FIXUP_ARGUMENT = "--fixup"
CCG_PDG_CHECKER_ARGUMENT = "--fpdg"
DCAI_PDG_CHECKER_ARGUMENT = "--fdcai"
DIRECTORY_LISTING_ARGUMENT = "--d"
POWER_SEQUENCE_ARGUMENT = "--pow"

# TargetFile types
TARGET_FILE_C = 'c'
TARGET_FILE_HEADER = 'header'
