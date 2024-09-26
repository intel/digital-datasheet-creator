"""
Plug-in constants for header generation.
"""

# from edatasheets_creator.constants.spreadsheettypes import PLUGIN


PLUGIN = 'clangheader'

clangheaderExtensions = {
    'hExtension': '.h'
}

# header constants
HEADER_DEFINE_FIELD = "#define"
HEADER_EC_FIELD = "EC"
HEADER_IFNDEF_FIELD = "#ifndef"
HEADER_GPIO_FIELD = "GPIO"
HEADER_PORT_FIELD = "PORT"
HEADER_PIN_FIELD = "PIN"
HEADER_EXP_FIELD = "EXP"
HEADER_ENDIF_FIELD = "#endif"
