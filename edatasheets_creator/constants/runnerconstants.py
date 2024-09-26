"""
Contains the runner constants.
"""
# For console parameter help
JOB_HELP_ARGUMENT = 'Selects the jobs to execute'

# Console parameter
JOB_ARGUMENT = '--p'

# Execution constants for jobs
INITIAL_JOB_ID = 1
NO_NEXT_JOB_ID = None

# Execution constants for tasks
INITIAL_TASK_ID = 1
NO_NEXT_TASK_ID = None

# Execution constants for plugin
PLUGINGUIDTAG = "pluginGUID"
PLUGINNAME = "pluginName"
PLUGIN_ARGUMENTS = "case"
PLUGIN_DESCRIPTION = "description"
PLUGIN_INPUT_FORMATS = "inputFormats"
PLUGIN_OUTPUT_FORMAT = "outputFormat"
PLUGIN_VALIDATE_INPUTS = "validateInputs"
PLUGIN_CASE_FORMATS = "validateInputs"

# Paths
PLUGIN_CFG_PATH = "settings/plugin_cfg.json"
PIPELINE_SCHEMA = "schemas/pipeline_schema.json"

# Object types
JOB_OBJECT = 1
TASK_OBJECT = 2
PLUGIN_OBJECT = 3

# Vocabulary and map sufixxes
MAP_SUFFIX = "_map.json"
VOCABULARY_SUFFIX = "_vocabulary.json"

# Case Formats
CASE_FORMAT_DEFAULT = 'default'
