import glob
import json
import os

from defusedxml import ElementTree
from marshmallow import Schema, fields, validate

from edatasheets_creator.base.plugin_base import PluginBase
from edatasheets_creator.constants.pluginconstants import DITA_SUFFIX
from edatasheets_creator.document.jsondatasheetschema import \
    JsonDataSheetSchema
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.utility.path_utilities import validateRealPath
from edatasheets_creator.utility.xml_utilities import XMLUtilities


class DirectoryListingSchema(Schema):
    """Input Schema definition
    """
    dir1 = fields.Str(required=True, validate=validate.Length(min=1, error="directoryInput can't be empty"))
    output = fields.Str(required=True, validate=validate.Length(min=1, error="output can't be empty"))


class Plugin(PluginBase):
    """Directory Listing Plugin to read dita files in a directory,
    using base plugin to validate input schema.
    """
    INPUT_SCHEMA = DirectoryListingSchema

    def __init__(self) -> None:
        super().__init__()
        self.xml_utilities = XMLUtilities()

    def process(self, **kwargs):
        ExceptionLogger.logInformation(__name__, "Initializing Directory Listing Plugin...", "\n")
        directory_input = kwargs.get("dir1", "")
        output_file = kwargs.get("output", "")
        tables_listing = {}

        directory_path = f"{directory_input}/**/*{DITA_SUFFIX}"

        directories_list = glob.iglob(directory_path, recursive=True)
        for file_name in directories_list:
            if validateRealPath(file_name):
                try:
                    source_element = ElementTree.parse(file_name).getroot()
                    suffix_file_name = os.path.basename(file_name)
                    if not (self.xml_utilities.get_tables(source_element) == []):
                        metadata = self.xml_utilities.get_attributes_from_dita(source_element, suffix_file_name)
                        tables_listing.update(metadata)
                except Exception as e:
                    ExceptionLogger.logError(__name__, "", e)

        msg = f"Writing the output json file: {output_file}...\n"
        ExceptionLogger.logInformation(__name__, msg)
        with open(output_file, "w+") as output_json:
            output_dictionary = {"tableListing": tables_listing}
            json.dump(output_dictionary, output_json, indent=2)

        json_schema = JsonDataSheetSchema(output_file)
        json_schema.write()

        msg = "Finished Directory Listing Plugin execution\n"
        ExceptionLogger.logInformation(__name__, msg)
        return
