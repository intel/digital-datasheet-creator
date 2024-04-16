from edatasheets_creator.drivers.ditamap_driver import DitamapDriver
from edatasheets_creator.utility.path_utilities import validateRealPath
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.functions import t
from edatasheets_creator.document.jsondatasheetschema import JsonDataSheetSchema
from xml.etree.ElementTree import Element  # nosec
""" Bandit ignore warning reason
Element is only used to create objects defined in the application code,
not from the input files. The parse functionality is also secured by
the implementation of defusedxml.Element tree.
"""
from defusedxml import ElementTree
import json
from pathlib import Path


class Plugin:
    def process(self, inputFileName, outputFileName, mapFileName=""):
        """
        Plugin that converts DITA file to JSON.

        Args:
            inputFileName (PosixPath): Input ditamap file name
            outputFileName (PosixPath): Output file name
        """

        try:
            # Validate if the input file exists on the system as it is required
            if (not validateRealPath(inputFileName)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\n Input file does not exists"))
                print()
                return

            msg = "Ditamap Plugin is loaded...\n"
            ExceptionLogger.logInformation(__name__, msg)

            root: Element = ElementTree.parse(inputFileName).getroot()
            driver = DitamapDriver()
            hierarchy_object = driver.get_hierarchy_file(root, inputFileName)

            # Build Output File Name
            path = Path(inputFileName)

            # Write output file here
            if not outputFileName:
                outputFileName = str(path.parent) + "\\" + path.stem + ".json"

            if hierarchy_object:
                try:
                    msg = f"Writing the output json file: {outputFileName}...\n"
                    ExceptionLogger.logInformation(__name__, msg)

                    with open(outputFileName, "w") as output_json:
                        json.dump(hierarchy_object, output_json, indent=2)

                    json_schema = JsonDataSheetSchema(outputFileName)
                    json_schema.write()

                except FileNotFoundError as fnf:
                    ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
