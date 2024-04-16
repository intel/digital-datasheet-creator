import json
from defusedxml import ElementTree  # nosec
from pathlib import Path
from edatasheets_creator.document.dictionaryschema import DictionarySchema
from edatasheets_creator.drivers.data_table import DataTable
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.functions import t
from edatasheets_creator.utility.path_utilities import validateRealPath


class Plugin:
    def __init__(self, store_data_in_memory=True):
        """ Initializer Method

        Args:
            store_data_in_memory (bool, optional): If you only want the data set this to false. Defaults to True.
        """
        self.store_data_in_memory = store_data_in_memory

    def process(self, inputFileName, outputFileName, mapFileName=""):
        """
        Plugin that converts DITA file to JSON.

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

            msg = "DITA Plugin is loaded...\n"
            ExceptionLogger.logInformation(__name__, msg)

            # Build Output File Name
            path = Path(inputFileName)
            msg = f"Processing file: {path.name}\n"
            ExceptionLogger.logInformation(__name__, msg)

            source = ElementTree.parse(inputFileName).getroot()

            data_table = DataTable(inputFileName, source)
            edatasheet = data_table.transform()

            # Stop execution if the edatasheet is empty
            if (edatasheet == {}):
                return
            # Build Outputs
            schema_builder = DictionarySchema()
            if (self.store_data_in_memory):
                if outputFileName:
                    output_file_name = outputFileName
                else:
                    output_file_name = str(path.parent) + "\\" + path.stem + ".json"

                msg = f"Writing the output json file: {output_file_name}...\n"
                ExceptionLogger.logInformation(__name__, msg)
                with open(output_file_name, "w", encoding="utf8") as output_json:
                    json.dump(edatasheet, output_json, indent=2, ensure_ascii=False)

                schema_builder.write_schema(edatasheet, output_file_name)

            else:
                schema = schema_builder.get_schema(edatasheet)
                return edatasheet, schema

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
