from edatasheets_creator.drivers.field_replacement import FieldReplacement
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.functions import t
from edatasheets_creator.utility.dictionary_utilities import DictionaryUtilities
from edatasheets_creator.utility.path_utilities import validateRealPath


class Plugin:
    def process(self, input_file_name, output_file_name, fixup_file=""):
        """
        Compares the structure of a datasheet with a json file containing field names and values to replace.
        Validates if it exists in the input file, and replaces its values, if it doesn't exist, the plugin adds the fields
        and values in the input file.

        Args:
            input_file_name (PosixPath): Input path to datasheet.
            output_file_name (PosixPath): Output path to store the generated datasheet.
        """
        try:
            # Validate if the input files exists on the system as they are required

            if (not validateRealPath(input_file_name)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("Input file does not exists"))

            else:
                dictionary_utilities = DictionaryUtilities()
                fixup_file = dictionary_utilities.json_to_dictionary(fixup_file)
                if self.is_fixup_file(fixup_file):
                    msg = "Fixup plugin is loaded...\n"
                    ExceptionLogger.logInformation(__name__, msg)
                    field_replacement = FieldReplacement()
                    field_replacement.read_process(input_file_name, fixup_file, output_file_name)
                else:
                    msg = "Arg2 must be a fixup file"
                    ExceptionLogger.logError(__name__, msg)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def is_fixup_file(self, fixup_file: dict):
        filetype = fixup_file.get("filetype", None)
        if isinstance(fixup_file, dict) and filetype and filetype == "fixup-file":
            return True
        else:
            return False
