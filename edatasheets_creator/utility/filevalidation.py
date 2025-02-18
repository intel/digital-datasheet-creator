"""
    This file holds validation functions for file existence and format compliance.
"""

import platform
from os.path import isdir

import jsonschema

from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.constants import parserconstants as pc
from pathlib import Path
from typing import List
from jsonschema import validate, exceptions, ValidationError, Draft7Validator as Validator
from json import load, dump, dumps
from edatasheets_creator.utility.path_utilities import get_relative_path, validateRealPath
import os
import requests
from edatasheets_creator.constants import serializationconstants, datasheetconstants, schema_constants
from edatasheets_creator.utility.excel_utilities import ExcelUtilities

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


def validateJson(schemaPathXLSX: str, schemaPathPPTX: str, jsonDataPath: str, inputFormat: List[str]) -> bool:
    """
        Function to validate the schema of the input json.
        Args:
            schema_path: Path to read json schema file.
            json_data: Dictionary with the json data definition

        Return:
            Boolean: Status and message.
    """
    if inputFormat[0] == "xlsx":
        json_schema = parseJsonToDict(schemaPathXLSX)
    elif inputFormat[0] == "pptx":
        json_schema = parseJsonToDict(schemaPathPPTX)
    jsonData = parseJsonToDict(jsonDataPath)
    result = True
    errorMsg = None

    try:
        validate(instance=jsonData, schema=json_schema)

    except ValidationError as e:
        errorMsg = e.schema["error_msg"] if "error_msg" in e.schema else e.message
        result = False

    return result, errorMsg


def translate_error(error):
    if error.path:
        error_path = error.path[-1]
    else:
        error_path = "unknown"

    if error.validator == 'oneOf':
        schema_titles = [schema.get('title', 'unknown') for schema in error.schema['oneOf']]
        failing_value = error.instance.get('partType', 'unknown')
        return (
            f"Validation failed for '{error_path}':\n"
            f"The provided data does not match any of the allowed schemas.\n"
            f"Failing section/sheet name: {failing_value}\n"
            f"Data value: {dumps(error.instance, indent=4)}"

        )
    else:
        return (
            f"Validation failed for '{error_path}':\n"
            f"Validator: {error.validator}\n"
            f"Message: {error.message}\n"
            f"Instance path: {'/'.join(map(str, error.path))}\n"
            f"Invalid value: {error.instance}\n"
        )
    #return str(error)

def validateWithSchema(datasheet, componentType):
    """

    Main logic method for spreadsheet processing without a map file needed

    Args:
        componentType (PosixPath): Component to be validated
        datasheet : The outputted data
    """
    result = True
    errorMsg = None
    schema_load = readWorkgroupSchema(componentType, online=False, validation=True)

    schema_validator = Validator(schema_load)

    errors = schema_validator.iter_errors(datasheet)

    try:
        for index, error in enumerate(sorted(errors, key=exceptions.relevance)):
            translated_error = translate_error(error)
            ExceptionLogger.logError(__name__, '', f"{translated_error}")
            ExceptionLogger.logDebug(__name__, str(error))
            result = False
    except Exception as e:
        ExceptionLogger.logError(__name__, 'Validation error', e)
        raise e

    return result, errorMsg


def filesExistsOnPath(filePaths, argumentTypes, inputFormat, supportForEmpty):
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
                            response = validateJson(get_relative_path(pc.MAP_SCHEMA_PATH), get_relative_path(pc.PPTX_MAP_SCHEMA_PATH), paths[i], inputFormat)
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
                        "message": f'File specified in argument: {types[i]} with value: {paths[i]} has a schema error "{errorMsg}"',
                        "exception": "FileNotFound",
                    }
                else:
                    error_object = {
                        "message": f'File specified in argument: {types[i]} with value: {paths[i]} was not found or has a invalid format',
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


def readWorkgroupSchema(componentType, online=False, validation=False):
    """
        Reads the Industry Datasheet Workgroup schema

    Args:
        componentType (str): name of component
        online (boolean): if datasheet would be retrieved online or locally
        validation (boolean): if schema would be used for validation or not

    Returns:
        data (dict): dictionary of schema
    """
    try:
        excelUtilities = ExcelUtilities()
        componentTypeInSchemaComponentCommonMapping = excelUtilities.getPropertyValueFromDatasheetComponentCommonMapping(componentType)
        if componentTypeInSchemaComponentCommonMapping:
            componentType = componentTypeInSchemaComponentCommonMapping
        if validation is True:
            componentType = datasheetconstants.DATASHEET_ROOT_SCHEMA_NAME
        if componentType == datasheetconstants.DATASHEET_ROOT_SCHEMA_NAME:
            if online is False:
                path_list = [os.path.dirname(__file__), '..', 'schemas', 'edatasheet_schema', 'part-spec']
                base_path = os.path.abspath(os.path.join(*path_list))
                file_path = "{}/{}.json".format(base_path, componentType)
                with open(file_path) as f:
                    data = load(f)
            elif online is True:
                file_path = schema_constants.SCHEMA_URL + componentType + ".json"
                data = requests.get(file_path, timeout=25).json()
        else:
            component_folder = datasheetconstants.DATASHEET_GROUPING[componentType]
            if online is False:
                path_list = [os.path.dirname(__file__), '..', 'schemas', 'edatasheet_schema', 'part-spec', component_folder]
                base_path = os.path.abspath(os.path.join(*path_list))
                file_path = "{}/{}.json".format(base_path, componentType)
                with open(file_path) as f:
                    data = load(f)
            else:
                file_path = schema_constants.SCHEMA_URL + component_folder + "/" + componentType
                data = requests.get(file_path, timeout=25).json()
        return data

    except Exception as e:
        ExceptionLogger.logError(__name__, f"Error obtaining schema for component type {componentType}", e)
        raise e



def writeToJSON(edatasheet, outputFileName):
    with open(outputFileName, "w", encoding='utf-8') as outfile:
        dump(edatasheet, outfile, ensure_ascii=False, indent=serializationconstants.JSON_INDENT_DEFAULT)
        outfile.close()