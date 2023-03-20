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
Contains the JSON keys for the jobs and task parsing process.
"""
# Validation constants
MAP_SCHEMA_PATH = "schemas/map-schema.json"

# Pipeline constants
PIPELINE_DESCRIPTION = 'pipelineDescription'
PIPELINE_JOBS = 'pipelineJobs'


# Job constants
JOB_DESCRIPTION = 'description'
JOB_ID = 'jobID'
NEXT_JOB = 'nextJob'
JOB_TASKS = 'jobTasks'

# Task constants
TASK_ID = 'taskID'
TASK_DESCRIPTION = 'description'
TASK_GUID = 'taskGUID'
TASK_MAP = 'map'
TASK_VOCABULARY = 'vocabulary'
TASK_ARGUMENT_1 = 'arg1'
TASK_ARGUMENT_2 = 'arg2'
TASK_CODE_GENERATION_TARGET = 'codeGenerationTarget'
TASK_OUTPUT = 'output'
NEXT_TASK = 'nextTask'
