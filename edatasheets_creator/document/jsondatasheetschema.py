import json
import os

from edatasheets_creator.functions import t
from genson import SchemaBuilder
from edatasheets_creator.constants import serializationconstants
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class JsonDataSheetSchema:
    """
    JsonDataSheetSchema class.
    """

    def __init__(self, fileName):
        """
        Class initializer.

        Args:
            fileName (PosixPath): path to JSON input file.  This class will automatically deserialize
            the input file and generate a schema for the input file.

        """
        try:
            self._fileName = fileName
            fileDetails = os.path.splitext(self._fileName)
            self._outputFileName = fileDetails[0] + "-" + serializationconstants.JSON_SCHEMA_NAME + '.' + serializationconstants.JSON_FILE_EXTENSION

            builder = SchemaBuilder()
            with open(self._fileName, 'r', encoding='utf-8') as f:
                datastore = json.load(f)
                builder.add_object(datastore)

            builder.to_schema()

            self._schema = builder.to_json(indent=serializationconstants.JSON_SCHEMA_INDENT_DEFAULT)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def write(self):
        """Writes the schema to disk
        """
        try:
            ExceptionLogger.logInformation(__name__, t("Writing") + " " + t("schema") + ":  " + self._outputFileName + "...\n")
            with open(self._outputFileName, "w") as outfile:
                outfile.write(self._schema)
                outfile.close()

        except Exception as e:
            ExceptionLogger.logError(__name__, e)
