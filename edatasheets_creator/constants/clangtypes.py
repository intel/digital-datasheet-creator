# ********************** COPYRIGHT INTEL CORPORATION ***********************
#
# THE SOFTWARE CONTAINED IN THIS FILE IS CONFIDENTIAL AND PROPRIETARY
# TO INTEL CORPORATION. THIS PRINTOUT MAY NOT BE PHOTOCOPIED,
# REPRODUCED, OR USED IN ANY MANNER WITHOUT THE EXPRESSED WRITTEN
# CONSENT OF INTEL CORPORATION. ALL LOCAL, STATE, AND FEDERAL
# LAWS RELATING TO COPYRIGHTED MATERIAL APPLY.
#
# Copyright (c), Intel Corporation
#
# ********************** COPYRIGHT INTEL CORPORATION ***********************

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
