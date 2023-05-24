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


# Header plugin class

import re
import os
import inspect
import json
import jsonpath_rw_ext as jp
from edatasheets_creator.constants import clangtypes
from edatasheets_creator.document.jsondatasheet import JsonDataSheet
from edatasheets_creator.functions import t
from edatasheets_creator.constants import serializationconstants
from edatasheets_creator.constants import spreadsheettypes
from edatasheets_creator.plugins.spreadsheetmap import SpreadsheetMap
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.utility.path_utilities import validateRealPath


class Plugin:
    """
    Spreadsheet plugin class that implements datasheet generation from an XLSX
    """

    def __init__(self):
        """
        Class initialization
        """

        self._worksheetSectionIndexWritten = False  # used in multisection worksheets to indicate that index values are already written
        self._indexOnRow = -1
        self._indexOnCol = -1

    def __repr__(self):
        """
            Returns a name for the class

        Returns:
            string : class name
        """
        return __name__ + '.' + inspect.currentframe().f_code.co_name

    def process(self, inputFileName, outputFileName, mapFileName=""):
        """

       Main logic method for creating the header

       Args:
           inputFileName (PosixPath): Input .json file
           outputFileName (PosixPath): Output file name
           mapFileName (PosixPath): Map file to guide parser if applicable
       """

        try:
            msg = t("Header Plugin is loaded")
            ExceptionLogger.logInformation(__name__, msg)

            # Validate if the input files exists on the system as they are required
            if (not validateRealPath(inputFileName)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\n Input file does not exists"))
                print()
                return

            if (not validateRealPath(mapFileName)):
                # Map file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\nMap file does not exists"))
                print()
                return

            fileDetails = os.path.splitext(inputFileName)
            self._fileName = fileDetails[0] + "." + serializationconstants.JSON_FILE_EXTENSION

            self._outputFileName = fileDetails[0] + "." + serializationconstants.C_HEADER_NAME

            self._mapFileName = mapFileName

            # Load map file
            map = SpreadsheetMap(self._mapFileName)

            # wb = load_workbook(filename=inputFileName, data_only=True)
            self.createHeaderFile(self._fileName, self._outputFileName, map)

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def createHeaderFile(self, inputFileName, outputFileName, map):
        """

         Main method for generating and writing to a header file

         Args:
            inputFileName (PosixPath): Input .json file
            outputFileName (PosixPath): Output header file
            mapFileName (PosixPath): Map file to guide parser if applicable
        """

        try:
            # defining all the needed variables
            self._inputFileName = inputFileName
            self._outputFileName = outputFileName

            # open the passed in file and load it as an object
            with open(self._inputFileName) as inputFile:
                inputContents = json.load(inputFile)

            # open the output file so that we can write to it
            with open(self._outputFileName, "w") as outfile:
                outfile.write("/* AUTO-GENERATED by clangfile.py, do not edit! */\n")

                # define lists for the pin name and the place it maps to
                names = []
                mapsTo = []
                muxConfig = []

                # get the sheet names
                sheetName = map.getSheetNames()

                # getting the worksheet name from the map
                worksheetName = str(JsonDataSheet.generateValidJsonFieldName(sheetName[0]))
                finalName = self.getTitle(worksheetName)

                outfile.write(clangtypes.HEADER_IFNDEF_FIELD + " " + finalName.upper() + "\n")
                outfile.write(clangtypes.HEADER_DEFINE_FIELD + " " + finalName.upper() + "\n\n")

                # getting the necessary column names
                keysList = []
                for fields in jp.match("$." + worksheetName + "[*]", inputContents):
                    keysList.append(list(fields.keys()))

                # splitting up the keys so that we are able to use them
                splitUpKeys = str(keysList[0]).split("'")

                regexPattern = '/|&| |\(|#|-'  # noqa
                # using jsonpath, append the names of the pins
                for name in jp.match("$." + worksheetName + "[*]." + splitUpKeys[1], inputContents):
                    firstPin = re.split(regexPattern, name)
                    # firstPin = name.split("/")
                    names.append(firstPin[0])
                for mapName in jp.match("$." + worksheetName + "[*]." + splitUpKeys[3], inputContents):
                    mapsTo.append(mapName)
                for mux in jp.match("$." + worksheetName + "[*]." + splitUpKeys[5], inputContents):
                    muxConfig.append(mux)

                for i in range(len(names)):
                    if ("GPIO" in names[i]):
                        names[i] = names[i][:4] + "_" + names[i][4:]
                    else:
                        names[i] = spreadsheettypes.SPREADSHEET_MAP_EMPTY_VAL
                # combine the pins and the location of the pins
                combinedNames = zip(names, mapsTo, muxConfig)

                # write to the header file
                for element1, element2, element3 in combinedNames:
                    if (element3 != "GPIO" or element1 == spreadsheettypes.SPREADSHEET_MAP_EMPTY_VAL):
                        pass
                    else:
                        outfile.write(clangtypes.HEADER_DEFINE_FIELD + " " + element2 + "  " + clangtypes.HEADER_EC_FIELD + "_" + element1 + "\n")

                self.getIOExpanders(sheetName, inputContents, outfile, 1)
                self.getIOExpanders(sheetName, inputContents, outfile, 2)

                outfile.write("\n" + clangtypes.HEADER_ENDIF_FIELD + " /*" + finalName.upper() + " */")

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getTitle(self, worksheetName):
        self.worksheetName = worksheetName

        formattedName = worksheetName.replace('-', '_')
        formattedName.upper()
        return formattedName

    def getIOExpanders(self, sheetName, inputContents, outfile, sheetIndex):
        self._sheetName = sheetName
        self._inputContents = inputContents
        self._outfile = outfile
        self._sheetIndex = sheetIndex
        # getting the worksheet name from the map
        worksheetName = str(JsonDataSheet.generateValidJsonFieldName(self._sheetName[self._sheetIndex]))
        # getting the necessary column names
        keysList = []
        for fields in jp.match("$." + worksheetName + "[*]", self._inputContents):
            keysList.append(list(fields.keys()))

        # splitting up the keys so that we are able to use them
        splitUpKeys = str(keysList[0]).split("'")
        ports = []
        names = []
        for port in jp.match("$." + worksheetName + "[*]." + splitUpKeys[1], inputContents):
            # firstPin = port.split("_")
            # firstPin = name.split("/")
            ports.append(port)
        for name in jp.match("$." + worksheetName + "[*]." + splitUpKeys[3], inputContents):
            names.append(name)

        finalPorts = self.convertToHex(ports)
        # print(finalPorts)
        combinedNames = zip(names, finalPorts)
        # write to the header file
        self._outfile.write("\n/*Writing IO Expander " + str(sheetIndex) + "*/\n")
        for element1, element2 in combinedNames:
            self._outfile.write(clangtypes.HEADER_DEFINE_FIELD + " " + element1 + "\t" + clangtypes.HEADER_EC_FIELD + "_" +
                                clangtypes.HEADER_GPIO_FIELD + "_" + clangtypes.HEADER_PORT_FIELD + "_" +
                                clangtypes.HEADER_PIN_FIELD + "(" + clangtypes.HEADER_EC_FIELD + "_" +
                                clangtypes.HEADER_EXP_FIELD + "_" + clangtypes.HEADER_PORT_FIELD + "_" +
                                str(self._sheetIndex) + ", " + element2 + ")\n")

    def convertToHex(self, ports):
        self._ports = ports
        for i in range(len(ports)):
            ports[i] = ports[i][2:3] + ports[i][4:]

            ports[i] = int(ports[i])
            if (ports[i] > 9):
                ports[i] = ports[i] - 2

            ports[i] = hex(ports[i])

            ports[i] = str(ports[i])
            ports[i] = ports[i][:2] + "0" + ports[i][2:]
        return ports
        # print(ports)
