import re
from typing import List
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class CollateralUtilities:
    def get_guids_from_string(self, text: str) -> List[str]:
        """Returns the list of matches to get the GUID of the given string.

        Args:
            text (str): text to search for if it has a GUID.

        Returns:
            List[str]: matches of the regex pattern.
        """
        try:
            pattern = r"([a-z0-9]{8}[-][a-z0-9]{4}[-][a-z0-9]{4}[-][a-z0-9]{4}[-][a-z0-9]{12})"
            return re.findall(pattern, text.lower())

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def get_first_guid_from_string(self, text: str) -> str:
        """Gets the first GUID match of the given string.

        Args:
            text (str):  text to search for if it has a UUID.

        Returns:
            str: GUID found.
        """
        try:
            guid = None
            matches = self.get_guids_from_string(text)
            if matches:
                guid = matches[0]
            return guid

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
