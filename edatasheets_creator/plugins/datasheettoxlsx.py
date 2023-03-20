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


# DataSheet to xlsx plugin class

from pathlib import Path
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.functions import t
from json import load
from openpyxl import Workbook
from edatasheets_creator.constants.datasheettoxlsxconstants import INITIAL_SHEET, HEADER_DATASHEET_LIST
from edatasheets_creator.constants.pluginconstants import XLSX_SUFIX, JSON_SUFIX
from edatasheets_creator.utility.path_utilities import validateRealPath


class Plugin:

    # define static method, so no self parameter
    def process(self, inputFileName, outputFileName="", mapFileName=""):
        """

        Plugin that converts json file to xlsx.

        Args:
            inputFileName (PosixPath): Input file name
            outputFileName (PosixPath): Output file name
            mapFileName (PosixPath): Map file to guide parser (unused in this plugin)
        """
        try:
            msg = t("Datasheettoxlsx Plugin is loaded...\n")
            ExceptionLogger.logInformation(__name__, msg)

            # Validate if the input file exists on the system as it is required
            if (not validateRealPath(inputFileName)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("Input file does not exists"))
                print()
                return

            # Verify inputFileName
            if (self.__verifyFormat(inputFileName, JSON_SUFIX)):
                self._inputFileName = inputFileName
            else:
                raise TypeError(f"Unexpected format.... Expected format: {JSON_SUFIX}")

            # Verifying the output filename
            self._outputFileName = self.__verifyOutputName(inputFileName, outputFileName)

            # Loading the dictionary representation of the Json eDataSheet
            eDatasheetDict = self.__parseJsonToDict(self._inputFileName)

            # Creating the xl file
            workBook = self.__createXlFile(eDatasheetDict)

            # Saving the workbook file into a xlsx file
            workBook.save(filename=self._outputFileName)

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

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

    def __verifyOutputName(self, inputFileName: str, outputFileName: str) -> str:
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
            newOutName = inputFileNamePath.stem + XLSX_SUFIX
            return newOutName

        else:

            if (self.__verifyFormat(outputFileName, XLSX_SUFIX)):
                return outputFileName

            else:
                raise TypeError(f"Unexpected format.... Expected format: {XLSX_SUFIX}")

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

    def __createXlFile(self, eDataSheet: dict) -> Workbook:
        """
        This function provides the functionality to create the workbook using the dictionary eDatasheet representation.

        Args:
            eDataSheet (dict): Dictionary with the information of the eDatasheet to convert into a xlsx file.

        Returns:
            Workbook: Workbook with the eDataSheet information.
        """
        workbook = Workbook()

        sheet = workbook.active
        sheet.title = INITIAL_SHEET

        keysToDelete = []

        # Defining DataSheet file headers
        for eDataSheetKey, value in eDataSheet.items():

            if (eDataSheetKey in HEADER_DATASHEET_LIST):
                sheet.append([value])
                keysToDelete.append(eDataSheetKey)

            else:
                continue

        # Deleting non needed keys
        for key in keysToDelete:
            eDataSheet.pop(key)

        # Creating and populating sheets
        for sheetName, rowList in eDataSheet.items():

            sheet = workbook.create_sheet(sheetName)

            # Get header names
            headerList = list(rowList[0].keys())

            # Adding the headers to the sheet
            sheet.append(headerList)

            # Adding the content of the rows to the sheet
            for rowObject in rowList:
                rowContent = list(rowObject.values())
                sheet.append(rowContent)

        return workbook
