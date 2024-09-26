import json
from pathlib import Path

from edatasheets_creator.constants.file_extensions import JSON_EXTENSION_NAME
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class DictionaryUtilities:
    def json_to_dictionary(self, file_name) -> dict:
        """Validates if the file name is a json and then open it an returns readed data.

        Args:
            file_name (_type_)

        Returns:
            dict: readed data from json
        """
        try:
            file_path = Path(file_name)
            data = {}
            if file_path.suffix == JSON_EXTENSION_NAME:
                with open(file_name, encoding='utf8') as json_file:
                    data = json.load(json_file)
            else:
                msg = f"The file '{file_name}' is not a json file"
                ExceptionLogger.logError(__name__, msg)
            return data

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def stores_dictionary_to_json_file(self, output_file_name: str, dictionary: dict):
        """Takes a dictionary and store it in a json file (using the output file name provided).

        Args:
            output_file_name (str): Path to the output json file.
            dictionary (dict): dictionary to store.
        """
        try:
            with open(output_file_name, "w+", encoding='utf8') as output_json:
                json.dump(dictionary, output_json, indent=2, ensure_ascii=False)

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
