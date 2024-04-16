"""
Translation constants for translator plugin.
"""

_NUL = object()  # unique value guaranteed to never be in JSON data

PLUGIN = 'translator'
PLUGIN_DESC = "Specification Translator"

PLUGIN_TYPE_OUTPUT_DESIGNATOR = "-translated"

PLUGINARGUMENT = "--vocabulary"

VOCABULARY_HELP_ARGUMENT = 'Target vocabulary for translation'

pluginExtensions = {
    'jsonExtension': '.json'
}

IEC_61360_SPECIFICATION_NAME = "IEC 61360-4"

'''
Field Name Constants
'''
GUID_FIELD_NAME = "guid"
SPECIFICATION_FIELD_NAME = "specification"
DESCRIPTION_FIELD_NAME = "description"
URI_FIELD_NAME = "uri"
AUTOMATION_URI_FIELD_NAME = "automationUri"
VOCABULARY_FIELD_NAME = "vocabulary"
