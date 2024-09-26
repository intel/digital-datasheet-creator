from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.drivers.data_table_dcai import DataTablePDGDCAI
from edatasheets_creator.functions import t
from edatasheets_creator.utility.path_utilities import validateRealPath


class Plugin:
    def process(self, inputFileName, outputFileName, mapFileName=""):
        """
        Plugin that converts DITA file to JSON for PDG checker.

        Args:
            inputFileName (PosixPath): Input file name
            outputFileName (PosixPath): Output file name
        """

        try:
            # Validate if the input file exists on the system as it is required
            if (not validateRealPath(inputFileName)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\n Input file does not exists"))
                print()
                return

            msg = "DITA to JSON for DCAI PDG Checker Plugin is loaded...\n"
            ExceptionLogger.logInformation(__name__, msg)
            data_table = DataTablePDGDCAI(inputFileName, outputFileName)
            data_table.transform()

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
