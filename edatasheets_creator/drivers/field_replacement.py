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

from pathlib import Path
from typing import List
from edatasheets_creator.document.jsondatasheetschema import JsonDataSheetSchema
from edatasheets_creator.utility.dictionary_utilities import DictionaryUtilities
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class FieldReplacement:
    def __init__(self, ) -> None:
        self.dictionary_utilities = DictionaryUtilities()

    def read_process(self, input_file_name: str, input_fix_mapper: dict, output_file_name: str = ""):
        """Reads the input files, and then sent to replace the fields and values based on the input_fix_mapper file.

        Args:
            input_file_name (str): path of the datasheet file to replace.
            input_fix_mapper (dict): mapper file path with the fields and values to include or replace.
        """

        try:
            input_dictionary = self.dictionary_utilities.json_to_dictionary(input_file_name)
            mapper = input_fix_mapper

            mapper_fields = mapper.get("fields", None)

            if mapper_fields:
                self.replace_fields_and_values(input_dictionary, mapper_fields)
            else:
                msg = "Mapper file is not correct, check README to see an example"
                ExceptionLogger.logError(__name__, msg)

            # Build Output File Name
            path = Path(input_file_name)

            if not output_file_name:
                output_file_name = str(path.parent) + "\\" + path.stem + ".json"

            self.dictionary_utilities.stores_dictionary_to_json_file(output_file_name, input_dictionary)

            # Stores the new json schema
            json_schema = JsonDataSheetSchema(output_file_name)
            json_schema.write()

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def is_filter(self, source: dict) -> bool:
        """Determines if the source is a filter dictionary, this is inferred if the source
        dictionary has a '_keys' key.

        Args:
            source (dict): Dictionary to check.

        Returns:
            bool
        """
        try:
            if isinstance(source, dict):
                return "_keys" in source
            else:
                return False
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def update_values(self, source: List[dict], values_to_change: dict):
        """Updates each element by reference in the source list, with the provided dictionary (values_to_change)

        Args:
            source (List[dict])
            values_to_change (dict)
        """
        try:
            if isinstance(source, dict):
                source.update(values_to_change)
            else:
                source = [item.update(values_to_change) for item in source]
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def replace_fields_and_values(self, source: dict, mapper_fields: dict) -> dict:
        """Checks using recursion each nested dictionary or list with the mapper object.

        Args:
            source (dict): dictionary to replace.
            mapper_fields (dict): dictionary with the values or field to replace.

        Returns:
            dict: modified dictionary.
        """
        try:
            # Validate if the current mapper field, is a filter
            if self.is_filter(mapper_fields):
                if isinstance(source, list):
                    for item in source:
                        self.replace_fields_and_values(item, mapper_fields)
                elif isinstance(source, dict):
                    mapper_keys = mapper_fields.get("_keys", [])
                    mapper_fields = mapper_fields.get("_fields", {})
                    for key, value in source.items():
                        if key in mapper_keys or not mapper_keys:
                            self.update_values(value, mapper_fields)
            else:
                for mapper_key, mapper_value in mapper_fields.items():
                    if mapper_key in source:
                        source_value = source.get(mapper_key, None)
                        if isinstance(mapper_value, dict):
                            if isinstance(source_value, list) and not self.is_filter(mapper_value):
                                source[mapper_key] = mapper_value
                            else:
                                self.replace_fields_and_values(source_value, mapper_value)
                        else:
                            source[mapper_key] = mapper_value
                    else:
                        source[mapper_key] = mapper_value

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
