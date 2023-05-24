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
    This file holds validation functions for file existance and format compliance.
"""

import platform
from os.path import isdir
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.constants import parserconstants as pc
from pathlib import Path
from jsonschema import validate, ValidationError
from json import load
from edatasheets_creator.utility.path_utilities import get_relative_path, validateRealPath


def parseJsonToDict(inputFilePath: str) -> dict:
    """
    Returns a dictionary representation of the eDatasheet

    Args:
        inputFilePath (string): Path where the file is located

    Returns:
        dict: Dictionary representation of the input eDatasheet
    """
    try:
        with open(inputFilePath, 'r', encoding='utf-8') as f:
            # Open file and load it as JSON
            dictionary = load(f)
            return dictionary

    except Exception as e:
        ExceptionLogger.logError(__name__, e)


def validateJson(schemaPath: str, jsonDataPath: str) -> bool:
    """
        Function to validate the schema of the input json.
        Args:
            schema_path: Path to read json schema file.
            json_data: Dictionary with the json data definition

        Return:
            Boolean: Status and message.
    """

    json_schema = parseJsonToDict(schemaPath)
    jsonData = parseJsonToDict(jsonDataPath)
    result = True
    errorMsg = None

    try:
        validate(instance=jsonData, schema=json_schema)

    except ValidationError as e:
        errorMsg = e.schema["error_msg"] if "error_msg" in e.schema else e.message
        result = False

    return result, errorMsg


def filesExistsOnPath(filePaths, argumentTypes, supportForEmpty):
    """
        Checks if the array of paths received corresponds to existing files

    Args:
        filePaths: Array of strings containing the path of the files
        argumentTypes: Array of strings containing the argument types of the inputs
        supportForEmpty: Boolean flag that indicates if the plug-in supports a not specified
                         map/vocabulary input file

    Returns:
        Boolean: Flag indicating if the files were found or not
    """
    filesExists = False
    existFlags = [False, False, False]
    types = argumentTypes
    paths = filePaths

    # Setting the arguments that will and will not be validated
    argumentsToNotValidate = [pc.TASK_OUTPUT, ""]
    argumentsToValidate = [pc.TASK_MAP, pc.TASK_VOCABULARY, pc.TASK_ARGUMENT_1, pc.TASK_ARGUMENT_2]

    # This is are used by plug-ins that process their own maps or vocabularies when none are specified
    argumentSupportForEmpty = [pc.TASK_MAP]
    errorMsg = None
    try:
        # Check each input type depending on the argument type
        for i in range(0, 3):
            if (types[i] in argumentsToNotValidate):
                # The input corresponds to an output or argument that is not used
                # Set the output to True to not generate conflict on the validation
                existFlags[i] = True

            elif (types[i] in argumentsToValidate):
                # The input corresponds to a map, vocabulary or input file
                if ((types[i] in argumentSupportForEmpty) and supportForEmpty):
                    # The plug-in supports an empty value on the argument data
                    if (paths[i] == ""):
                        # Only when the input value is "" is set to true
                        existFlags[i] = True
                    else:
                        # Check if file exists
                        existFlags[i] = validateRealPath(paths[i])
                        if (existFlags[i]):
                            response = validateJson(get_relative_path(pc.MAP_SCHEMA_PATH), paths[i])
                            existFlags[i] = response[0]
                            errorMsg = response[1]

                else:
                    # Check if file exists
                    existFlags[i] = validateRealPath(paths[i])

        # Validate that all 3 parameters passed the validation correctly
        filesExists = existFlags[0] and existFlags[1] and existFlags[2]

        # Sets an error message for the invalid inputs
        for i in range(0, 3):
            if (not existFlags[i]):
                # File was not found, report it
                if errorMsg:
                    error_object = {
                        "message": f'File especified in argument: {types[i]} with value: {paths[i]} has a schema error "{errorMsg}"',
                        "exception": "FileNotFound",
                    }
                else:
                    error_object = {
                        "message": f'File especified in argument: {types[i]} with value: {paths[i]} was not found or has a invalid format',
                        "exception": "FileNotFound"
                    }
                ExceptionLogger.logError(__name__, "", error_object)

    except Exception as e:
        ExceptionLogger.logError(__name__, "", e)

    return filesExists


def outputPathExists(filePaths, argumentTypes):
    """
        Checks that the output path exists

    Args:
        filePaths: Array of strings containing the path of the files
        argumentTypes: Array of strings containing the argument types of the inputs

    Returns:
        Boolean: Flag indicating if the path exists or not
    """
    pathExists = False
    types = argumentTypes
    paths = filePaths

    try:
        if (pc.TASK_OUTPUT in types):
            # Check for the output, if it exists
            for i in range(0, 3):
                if (types[i] == pc.TASK_OUTPUT):
                    # Get the path of the file by deleting the name of the file
                    filePathToCheck = str(Path(paths[i]))
                    if platform.system().lower().startswith('win'):
                        pathDetails = filePathToCheck.split("\\")
                    else:
                        pathDetails = filePathToCheck.split("/")
                    fileNameIndex = len(pathDetails) - 1
                    fileName = pathDetails[fileNameIndex]
                    pathToCheck = filePathToCheck.replace(fileName, "")

                    # Validate if the directory exists
                    pathExists = isdir(pathToCheck)

                    if (not pathExists):
                        # Path was not found, report it
                        error_object = {
                            "message": f'Output path: {pathToCheck} was not found',
                            "exception": "FileNotFound"
                        }
                        ExceptionLogger.logError(__name__, "", error_object)

        else:
            # No need for validation on the output as it is not used
            pathExists = True

    except Exception as e:
        ExceptionLogger.logError(__name__, "", e)

    return pathExists

