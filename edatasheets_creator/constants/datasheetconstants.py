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
Key datasheet field name constants/defintions.
"""

DATASHEET_TITLE_FIELD = "title"
DATASHEET_DESCRIPTION_FIELD = "description"
DATASHEET_INPUT_FILE_FIELD = "inputFile"
DATASHEET_CREATION_DATE_FIELD = "createdOn"
DATASHEET_GUID_FIELD = "guid"
DATASHEET_HEADING = 'heading'
DATASHEET_LISTING = 'listing'
DATASHEET_TABLES = 'Tables'
DATASHEET_TABLE = 'table'
DATASHEET_NOTES = 'notes'
DATASHEET_LIST = 'list'
DATASHEET_SERIAL_NUMBER = 'SN'
DATSHEET_FIGURE = 'fig'
DATASHEET_SURFACE_FORM = 'surfaceForm'
DATASHEET_KNOWN_RULES = {"note", "traceWidth", "intra-pair", "zSe-Default", "zDiff-Default", "aSe", "aDiff", "traceSpacing", "k"}
DATASHEET_RULES_LIST = ["note", "traceWidth", "intra-pair", "zSe-Default", "zDiff-Default", "aSe", "aDiff", "traceSpacing", "k"]
DATASHEET_SIGNALS = ['catocs', 'cstoca', 'cstocs', 'catoca', 'dqtodq', 'dqtodqofsamebyte', 'byteTobyte', 'rdqspairtodqofsamebyte', 'dqtoca', 'DQ to CS',
                     'WCK to CA', 'WCK to CS ', 'WCK to CLK', 'K CA to CS', 'K CA to CS', 'clktoca', 'clktocs', 'K CA to CA',
                     'K CS to CS', 'K CS to CA', 'K CLK to CS', 'K CLK to CS', 'K DQ to DQ of same byte', 'K Byte to Byte', 'K RDQS pair to DQ of same byte',
                     'K WCK to CA', 'K WCK to CS', 'K WCK to CLK', 'dqsPairToDqOfSameByte', 'wckToDq', 'kDqsPairToDqOfSameByte', 'kClkToCa']
DATASHEET_RULES_LIST_MAPPING = {"traceWidth": "traceWidth", "intra-pair": "intraPair", "zDiff-Default": "impedance", "aSe": "losses", "note": "note",
                                "zSe-Default": "impedance", "aDiff": "losses", "traceSpacing": "traceSpacing", "k": "k"}
DATASHEET_SIGNAL_NAME = 'signal'
DATASHEET_SIGNALS_NAME = 'signals'
DATASHEET_CHANNELS_NAME = 'channels'
DATASHEET_PCB_LAYER_COUNT = 'pcblayercount'
DATASHEET_SIGNAL_TYPE = 'signalType'
DATASHEET_TRACE_SPACING_NAME = 'traceSpacing'
DATASHEET_K_VALUE_NAME = 'k'
DATASHEET_NOT_AVAILABLE = 'NA'
DATASHEET_ROUTING_LAYER = 'routinglayers'
DATASHEET_TOPOLOGY = 'topology'
DATASHEET_INTERFACE = 'interface'
DATASHEET_INTERFACE_TYPE = 'interfaceType'
DATASHEET_MEMORY = 'memory'
DATASHEET_A_SE = 'aSe'
DATASHEET_Z_SE_DEFAULT = 'zSe-Default'
DATASHEET_A_DIFF = 'aDiff'
DATASHEET_Z_DIFF_DEFAULT = 'zDiff-Default'
DATASHEET_INTRA_PAIR = 'intra-pair'
DATASHEET_VARIANT = 'variant'
DATASHEET_HEADER_KEYS = ['pcbtype', 'pcbthickness', 'pcblayercount', 'category', 'variant',
                         'interface', 'topology', 'channels', 'trace', 'tlinetype', 'routinglayers', 'signals',
                         'pingroup/location', 'tracewidth', 'intra-pair', 'zse',
                         'zdiff', 'ase', 'adiff']


DATASHEET_DEFAULT_TITLE = "Datasheet"
DATASHEET_DEFAULT_DESCRIPTION = "Describes a part"
DATASHEET_DEFAULT_INPUT_FILE_FIELD = "Unknown"
DATASHEET_RULE_VALUE = 'value'
DATASHEET_RULE_UNIT = 'unitOfMeasure'
DATASHEET_RULE_NAME = 'parameter'

DATASHEET_DEFAULT_MAX_ROWS = 23
DATASHEET_DEFAULT_DATASTART = 2
