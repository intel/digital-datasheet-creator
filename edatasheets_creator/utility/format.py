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


from typing import Tuple
import re

from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class Format:
    FORMATTERS_NAME_MAP = {
        "format_1": {
            "characters": [0xAE, 0xB2, 0xB9, 0x09, 0x0D, 0x0A, 0x21, 0x2A, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26,
                           0x27, 0x2B, 0x2C, 0x2E, 0x2F, 0x3B, 0x3C, 0x3D, 0x3E, 0x2F, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F,
                           0x40, 0x5B, 0x5C, 0x5D, 0x5E, 0x7B, 0x7C, 0x7D, 0xA0, 0xB1, 0x2122, 0x2019, 0x201C, 0x201D],
            "replace_to": ' '
        },
        "format_2": {
            "characters": [0x28, 0x29, 0x3A, 0x2013],
            "replace_to": '-'
        },
        "format_3": {
            "characters": [0x20],
            "replace_to": '*'
        },
        "format_4": {
            "characters": [0xB3],
            "replace_to": '3'
        },
        "format_5": {
            "characters": [0x221A],
            "replace_to": 'c'
        }
    }

    FORMATTERS_HTML_MAP = {
        "format_1": {
            "characters": [194, ord("€"), ord("“")],
            "replace_to": ''
        },
        "format_2": {
            "characters": [0x28, 0x29, 0x3A, 0x2013],
            "replace_to": ''
        }

    }

    FORMATTERS_VALUE_MAP = {
        "format_1": {
            "characters": [0xA0, 0xAE, 0xB2, 0x2122],
            "replace_to": ' '
        }
    }

    def int_try_parse(self, value) -> Tuple[int, bool]:
        """Validates if can parse the provided value

        Args:
            value (any)

        Returns:
            Tuple[int, bool]: Parsed value and boolean value if the operation was successful
        """
        try:
            return int(value), True
        except ValueError:
            return value, False

    def convert_to_camel_case(self, string: str) -> str:
        """Takes the given string an convert it to a camel case format.

        Args:
            string (str): string to convert.

        Returns:
            str: converted string.
        """
        if string:
            words = string.lower().split(" ")
            return words[0] + ''.join(word.title() for word in words[1:])
        return string

    def format_by_mapper(self, string: str, mapper: dict) -> str:
        """Replace values from a string using a mapper dictionary, check the examples on the top of this class

        Args:
            string (str): string to format
            mapper (dict): dictionary mapper

        Returns:
            str: formatted string.
        """
        try:
            for _, value in mapper.items():
                replace_to = value.get("replace_to", "")
                for character in value.get("characters", []):
                    string = string.replace(chr(character), replace_to)

            return string

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def format_value(self, string: str) -> str:
        """Replace values from a string using the global FORMATTERS_VALUE_MAP.

        Args:
            string (str): string to format.

        Returns:
            str: formatted string.
        """
        try:
            string = self.format_by_mapper(string, self.FORMATTERS_VALUE_MAP)
            string = string.strip()
            string = re.sub("([ ]{2,})", ' ', string)

            return string

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def format_special_fields(self, field_name: str, value: str) -> str:
        """There are a few special fields that have to be formatted correctly.
           There is currently a bug in techpubs documentation.  When techpubs uses a PI, it looks correct in the final generated PDF.
           But in the parsed data there is a space.   So we need to do some manual fixups temporarily until we can resolve this.

        Args:
            field_name (str): special field to convert his value.
            value (str):; value of the field name

        Returns:
            str: formatted value.
        """
        if field_name.lower() == "pinname":
            value = value.replace(' ', '')
        return value
    
    def format_name_spreadsheet(self, string: str) -> str:
        """Replaces the supplied characters in FORMATTERS_NAME_MAP and converts the string to camel case for spreadsheet files.

        Args:
            string (str): string to format.

        Returns:
            str: formatted string.
        """
        try:
            string = self.convert_to_camel_case(string)

            string = self.format_by_mapper(string, self.FORMATTERS_NAME_MAP)

            string = string.replace(' ', "")
            string = string.replace('*', "")

            if (string.endswith("-")):
                string = string[:-1]

            return string

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def format_name(self, string: str) -> str:
        """Replaces the supplied characters in FORMATTERS_NAME_MAP and converts the string to camel case.

        Args:
            string (str): string to format.

        Returns:
            str: formatted string.
        """
        try:
            string = self.convert_to_camel_case(string)

            string = self.format_by_mapper(string, self.FORMATTERS_NAME_MAP)
            _, is_numeric = self.int_try_parse(string)
            if is_numeric:
                string = "n" + string
            else:
                digit = string[0]
                if (digit >= '0' and digit <= '9'):
                    string = "n" + string

            string = string.replace(' ', "")
            string = string.replace('*', "")

            if (string.endswith("-")):
                string = string[:-1]

            return string

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def format_html_name(self, string: str) -> str:
        """Replaces html characters to create keys

        Args:
            string (str): HTML read string

        Returns:
            str: converted string
        """
        try:
            string = self.convert_to_camel_case(string)

            string = self.format_by_mapper(string, self.FORMATTERS_HTML_MAP)

            return string

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
