"""
Plug-in location information.
"""

PLUGIN_DIRECTORY = 'edatasheets_creator.plugins.'

DEFAULT_PLUGIN_TYPE = 'spreadsheet'
DIFF_PLUGIN_TYPE = 'diff'

# Plugins indexes
CLANG_HEADER_INDEX = "dbbb4b96-3142-4a1f-9002-2ab857ed0f0d"
DEFAULT_INDEX = "28d1491d-b368-49a0-a9ac-9ed2d917171d"
DIFF_INDEX = "6efd8af2-ea34-49f4-826c-a2ad45595c5f"
SPREADSHEET_INDEX = "a8a799ed-969a-4c77-b21b-bf9b77461037"
TRANSLATOR_INDEX = "3034c0e7-782a-4c39-8b4b-fb400a4c2063"
XLSM_TO_XLSX_INDEX = "69909873-c30a-4961-bd2a-b057054e3b62"
XLS_TO_XLSX_INDEX = "31880d5a-641f-4a56-a2d6-8ff852698e7a"
CLANG_FILE_INDEX = "3060d9b5-a170-4469-b43b-56746036a7e8"
DATASHEET_TO_XLSX = "39794f7f-43c8-4156-a920-f718ed9b18df"
DITA_TO_JSON = "7696d6b4-fb25-4917-8fd9-2958f0f1a47a"
DITA_TO_JSON_CCG = "fb54fa35-e3c0-4c70-ac41-c7cde733429f"
DITA_TO_JSON_DCAI = "925a4651-d713-421c-bf75-c1c09b641826"
POWER_SEQUENCING = "eef1881c-7712-4dae-a5bd-ffdb58042eb6"
FIXUP_INDEX = "9289a2cf-7e17-4d36-8f18-186ecadbbe07"
VOCABULARY_FILE_CREATOR = "8eca4fce-77dd-44b6-a7c7-9b3764507aec"
DIRECTORY_LISTING = "3bf4ede9-9ede-4883-aca6-6cc7876e3ded"
PPTX_TO_JSON = "c378e34a-9f26-463a-ad78-65ddeb7952f2"

"""
Constants for the Datasheets
"""
XLSX_SUFIX = ".xlsx"
JSON_SUFIX = ".json"
DITA_SUFFIX = ".xml"
"""
Constants for the vocabulary file creator plugin
"""
PREFIX_NAME = "IEC-61360-4-"
BLACKLIST_SCHEMA_PATH = "schemas/blacklist-schema.json"
VOCABULARY_HEADER = {"guid": "1994225a-c7f8-4b1a-983d-2fff1dcdab62",
                     "specification": "IEC 61360-4",
                     "description": "IEC 61360 Part 4 Vocabulary File",
                     "uri": "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/TreeFrameset?OpenFrameSet",
                     "automationUri": "https://cdd.iec.ch/cdd/iec61360/iec61360.nsf/TU0/"}
VOCABULARY_TAG = "vocabulary"

HTML_TO_JSON = "012aa326-49a1-4bdd-8bfc-b860021fd91d"
