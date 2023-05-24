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
Plug-in constants for spreadsheet parser.
"""

PLUGIN = 'spreadsheet'

spreadsheetExtensions = {
    'xlsExtension': '.xls',
    'xlsxExtension': '.xlsx',
    'sheetsExtension': '.gsheet'
}

# Spreadsheet map field name constants
SPREADSHEET_MAP_COL_FIELD = 'col'
SPREADSHEET_MAP_COLUMNS_FIELD = 'columns'
SPREADSHEET_MAP_DATA_START_COL_FIELD = 'dataStartCol'
SPREADSHEET_MAP_DATA_START_ROW_FIELD = 'dataStartRow'
SPREADSHEET_MAP_DATA_VALUE_COL_FIELD = 'dataValueCol'
SPREADSHEET_MAP_DATASHEET_DESC_LOCATION_FIELD = 'datasheetDescLocation'
SPREADSHEET_MAP_DESCRIPTION_FIELD = 'description'
SPREADSHEET_MAP_FIELDHEADERS_FIELD = 'fieldHeaders'
SPREADSHEET_MAP_FIELDLABEL_FIELD = 'fieldLabel'
SPREADSHEET_MAP_FIELDVALUE_FIELD = 'fieldValue'
SPREADSHEET_MAP_GUID_FIELD = 'guid'
SPREADSHEET_MAP_GROUPS_FIELD = 'groupBy'
SPREADSHEET_MAP_HEADER_FIELD = 'header'
SPREADSHEET_MAP_INCLUDE_IN_DATASHEET_FIELD = 'includeInDatasheet'
SPREADSHEET_MAP_INCLUDE_TAGS_FIELD = 'includeTags'
SPREADSHEET_MAP_INDEX_ON_FIELD = 'indexOn'
SPREADSHEET_MAP_IGNORE_BLANKS_FIELD = 'ignoreBlanks'
SPREADSHEET_MAP_IGNORE_COLS_FIELD = 'ignoreCols'
SPREADSHEET_MAP_IGNORE_ROWS_FIELD = 'ignoreRows'
SPREADSHEET_MAP_MAPTYPE_FIELD = 'mapType'
SPREADSHEET_MAP_MAX_ROWS_FIELD = 'maxRows'
SPREADSHEET_MAP_NAME_FIELD = 'name'
SPREADSHEET_MAP_ORIENTATION_FIELD = 'orientation'
SPREADSHEET_MAP_ORIENTATION_TYPE_COL = 'col'
SPREADSHEET_MAP_ORIENTATION_TYPE_ROW = 'row'
SPREADSHEET_MAP_ROW_FIELD = 'row'
SPREADSHEET_MAP_SECTIONS_FIELD = 'sections'
SPREADSHEET_MAP_SHEETS_FIELD = 'sheets'
SPREADSHEET_MAP_SPANS_FIELD = 'spans'
SPREADSHEET_MAP_SHEETNAME_FIELD = 'sheetName'
SPREADSHEET_MAP_TYPE_FIELD = PLUGIN
SPREADSHEET_MAP_VALUE_COLUMN_FIELD = 'valueCol'
SPREADSHEET_MAP_EMPTY_VAL = "value not specified, none"

SPREADSHEET_TABLES = "tables"
SPREADSHEET_DATASHEET = "datasheet"
