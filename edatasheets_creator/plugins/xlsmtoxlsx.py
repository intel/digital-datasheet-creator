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

from edatasheets_creator.functions import t
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
import pandas as pd, gc as gc
from edatasheets_creator.utility.path_utilities import validateRealPath


class Plugin:

    def process(self, inputFileName, outputFileName, mapFileName=""):
        """

        Plugin that converts xlsm file to xlsx.

        Args:
            inputFileName (PosixPath): Input file name
            outputFileName (PosixPath): Output file name
            mapFileName (PosixPath): Map file to guide parser
        """

        try:
            msg = t("Xlsm Plugin is loaded...\n")
            ExceptionLogger.logInformation(__name__, msg)

            self._inputFileName = inputFileName
            self._outputFileName = outputFileName
            self._mapFileName = mapFileName

            # Validate if the input file exists on the system as it is required
            if (not validateRealPath(inputFileName)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\n Input file does not exists"))
                print()
                return

            gc.enable()

            fileName = self._inputFileName
            xlsxFileName = self._outputFileName

            # Create ExcelFile object and retrieve sheet names
            xlsmFile = pd.ExcelFile(self._inputFileName)
            sheetNames = xlsmFile.sheet_names

            # Build dict of sheetname: dataframe for each sheet
            dict = {}
            for sheet in sheetNames:
                dict[sheet] = pd.read_excel(fileName, sheet_name=sheet, header=None)

            # Loop through dict, and have the writer write them to a single file
            writer = pd.ExcelWriter(xlsxFileName, engine='xlsxwriter')
            for sheet, frame in dict.items():
                frame.to_excel(writer, sheet_name=sheet, header=None, index=None)

            writer.close()

            # Delete objects and free memory
            del xlsmFile, sheetNames, dict, writer
            gc.collect()

            print("Finished converting xlsm to xlsx")

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
