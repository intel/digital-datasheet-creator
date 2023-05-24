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

from json import load, dump
from typing import Any
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.constants.pluginconstants import JSON_SUFIX, PREFIX_NAME, BLACKLIST_SCHEMA_PATH, VOCABULARY_HEADER, VOCABULARY_TAG
from edatasheets_creator.functions import t
from pathlib import Path
from edatasheets_creator.utility.filevalidation import validateJson
from edatasheets_creator.utility.path_utilities import get_relative_path, validateRealPath


class Plugin:

    def process(self, inputFilePath: str, outputFilePath: str = "", blackListPath: str = "") -> None:
        """This function takes any json file and creates a vocabulary file

        Args:
            inputFileName (str): Input file path in json format
            outputFileName (str, optional): Output file path in json format. Defaults to "".
            blackListPath (str, optional): Input list of words to skip when creating a vocabulary file. Defaults to "".
        """
        try:

            msg = t("Vocabulary template file creator Plugin is loaded...\n")
            ExceptionLogger.logInformation(__name__, msg)

            # Validate if the input file exists on the system as it is required
            if (not validateRealPath(inputFilePath)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("Input file does not exists"))
                print()
                return

            # Verify inputFileName
            if (self.__verifyFormat(inputFilePath, JSON_SUFIX)):
                self._inputFilePath = inputFilePath
            else:
                raise TypeError(f"Unexpected format.... Expected format: {JSON_SUFIX}")

            # Verifying the output filename
            self._outputFileName = self.__verifyOutputName(inputFilePath, outputFilePath)

            # Verifying blacklist
            blacklist = self.__verifyBlackList(blackListPath)

            # Getting input json file as dict
            jsonFileDict = self.__parseJsonToDict(self._inputFilePath)

            # Creating vocabulary file
            vocabularyDict = self.__createVocabularyFile(jsonFileDict, blacklist)

            # Storing the dictionary
            with open(outputFilePath, "w") as file:
                dump(vocabularyDict, file, indent=4)

            return

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def __verifyBlackList(self, blackListPath: str = "") -> list:
        blacklist = list()

        if (blackListPath != ""):
            if (not validateRealPath(blackListPath)):
                # Word black list file does not exist
                raise TypeError("Provided path for the blacklist file does not exist or is invalid...")

            else:
                if (self.__verifyFormat(blackListPath, JSON_SUFIX)):

                    if (not validateJson(get_relative_path(BLACKLIST_SCHEMA_PATH), blackListPath)):
                        raise TypeError("Schema of the input blacklist file is invalid...")
                    else:
                        blacklist = self.__parseJsonToDict(blackListPath)

                else:
                    raise TypeError(f"Unexpected format of the blacklist.... Expected format: {JSON_SUFIX}")

        return blacklist

    def __parseJsonToDict(self, inputFilePath: str) -> dict:
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

    def __verifyOutputName(self, inputFileName: str, outputFileName: str, format: str = JSON_SUFIX) -> str:
        """
        Function that verify if the output name is correct or assign a correct one if it is not defined

        Args:
            inputFileName (string): Name of the input file used in case the output name is not defined.
            outputFileName (string): Name of the output file is it is defined.

        Returns:
            string: Output file name verified or created.
        """
        if (outputFileName == ""):
            inputFileNamePath = Path(inputFileName)
            newOutName = PREFIX_NAME + inputFileNamePath.stem + + format
            return newOutName

        else:

            if (self.__verifyFormat(outputFileName, format)):
                return outputFileName

            else:
                raise TypeError(f"Unexpected format.... Expected format: {format}")

    def __verifyFormat(self, fileName: str, format: str) -> bool:
        """
        This function provides the functionality to verify the format of a file, based on its sufix

        Args:
            fileName (string): Complete file name including its sufix.
            format (string): Expected format that the file has to be.

        Returns:
            bool: True if the format is correct or False if it is not.
        """
        fileNamePath = Path(fileName)
        fileNameSufix = fileNamePath.suffix.lower()

        if (fileNameSufix == format):
            return True

        else:
            return False

    def __getListDependOnDataType(self, value: Any, outputList: list, blackList: list) -> list:
        """Function that allows to process data depending if it is a dictionary of a list

        Args:
            value (Any): Could be a dictionary or a list
            outputList (list): list to append data
            blackList (list): list with the words to be ommited

        Returns:
            list: output list
        """

        if (isinstance(value, dict)):

            # Get the keys of the nested dictionary
            subOuputList = self.__parseDictionary(value, blackList)
            # List comprehension to delete duplicated items
            outputList = outputList + [value for value in subOuputList if value not in outputList]
            return outputList

        elif (isinstance(value, list)):
            # Get the keys of the nested dictionary
            subOuputList = self.__parseList(value, blackList)
            # List comprehension to delete duplicated items
            outputList = outputList + [value for value in subOuputList if value not in outputList]
            return outputList

        else:
            return outputList

    def __parseDictionary(self, inputJsonDict: dict, blackList: list) -> list:
        """Function in charge to parse the input dictionary

        Args:
            inputJsonDict (dict): Input dictionary
            blackList (list): Words to skip

        Returns:
            list: Output list of words
        """
        outputList = []

        for key, value in inputJsonDict.items():

            # If the value is in the blacklist or were already added
            if (key not in blackList and key not in outputList):
                outputList.append(key)

            outputList = self.__getListDependOnDataType(value, outputList, blackList)

        return outputList

    def __parseList(self, inputList: list, blackList: list) -> list:

        outputList = []

        for value in inputList:

            outputList = self.__getListDependOnDataType(value, outputList, blackList)

        return outputList

    def __createVocabularyFile(self, inputJsonDict: dict, blackList: list) -> dict:
        """Function that creates a list of words from the dictionary keys

        Args:
            inputJsonDict (dict): Dictionary representation of the input json file
            blackList (list): Word list to be skipped

        Returns:
            dict: Dictionary representation of the output vocabulary file.
        """
        # Adding the header of the vocabulary file
        vocabularyDict = VOCABULARY_HEADER

        # Getting all the fielNames in the json file
        fieldNameList = self.__parseDictionary(inputJsonDict, blackList)

        # Creating list of dict objects
        vocabularyList = list()

        for fieldName in fieldNameList:
            # Adding fieldNames with empty lists
            tempDict = {fieldName: list()}
            vocabularyList.append(tempDict)

        vocabularyDict[VOCABULARY_TAG] = vocabularyList

        return vocabularyDict
