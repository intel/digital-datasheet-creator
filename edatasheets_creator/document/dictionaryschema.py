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

from genson import SchemaBuilder
from pathlib import Path
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.constants import serializationconstants
from edatasheets_creator.functions import t


class DictionarySchema:
    def get_schema(self, dictionary: dict) -> dict:
        """Returns the schema of the dictionary

        Args:
            dictionary (dict): Content to get the schema

        Returns:
            dict: Schema
        """
        try:
            builder = SchemaBuilder()
            builder.add_object(dictionary)

            builder.to_schema()

            schema = builder.to_json(indent=serializationconstants.JSON_SCHEMA_INDENT_DEFAULT)
            return schema

        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def write_schema(self, dictionary: dict, inputFile: str):
        """Write the schema of the dictionary in memory

        Args:
            dictionary (dict): Content to get the schema
            inputFile (str): Path to store the schema
        """
        try:
            outputPath = Path(inputFile)
            outputSchemaFileName = str(outputPath.parent) + "\\" + outputPath.stem + "-" + serializationconstants.JSON_SCHEMA_NAME + '.' + serializationconstants.JSON_FILE_EXTENSION

            schema = self.get_schema(dictionary)

            ExceptionLogger.logInformation(__name__, t("Writing") + " " + t("schema") + ":  " + outputSchemaFileName + "...\n")
            with open(outputSchemaFileName, "w") as outfile:
                outfile.write(schema)
                outfile.close()
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)
