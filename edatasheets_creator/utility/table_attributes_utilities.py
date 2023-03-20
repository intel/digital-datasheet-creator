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

import re
from xml.etree.ElementTree import Element  # nosec
""" Bandit ignore warning reason
Element is only used to create objects defined in the application code,
not from the input files. The parse functionality is also secured by
the implementation of defusedxml.Element tree.
"""
import edatasheets_creator.constants.transformer_constants as tc
import edatasheets_creator.constants.transformer_constants as transformer_constants
import edatasheets_creator.constants.common_constants as common_c
from edatasheets_creator.utility.format import Format


class TableAttributesUtilities:
    FORMATS = {
        "pcbLayerCount": {
            "type": "int"
        },
        "channels": {
            "type": "list",
            "separator": "/"
        }
    }

    def __init__(self) -> None:
        self.format = Format()

    def get_table_attributes(self, description: str) -> Element:
        """Returns the table attributes based on the desc tag of the table if applies

        Args:
            description (str): string with the structure of attributes (name: attribute, name2: attribute2)

        Returns:
            Element: Element with the parsed table attributes
        """
        table_attributes = Element(transformer_constants.TABLE_ATTRIBUTES)
        for item in description.split(transformer_constants.ATTRIBUTES_SEPARATOR):
            attributes = item.split(transformer_constants.ATTRIBUTES_KEY_VALUE_SEPARATOR)
            if len(attributes) == 2:
                key = self.format.format_name(attributes[0].strip())
                value = self.format.format_value(attributes[1].strip())
                key, value = self.format_attributes(key, value)
                if type(value) == list:
                    for item in value:
                        key_element = Element(key)
                        key_element.text = item
                        table_attributes.append(key_element)
                else:
                    key_element = Element(key)
                    key_element.text = value
                    table_attributes.append(key_element)
        return table_attributes

    def format_attributes(self, key, value) -> dict:
        """Format specific types of table attributes based on the FORMATS dictonary

        Args:
            table_attributes (dict): dictionary with the table_attributes

        Returns:
            dict: parsed table attributes with the format required
        """
        formatter = self.FORMATS.get(key, None)
        if formatter:
            _type = formatter.get(tc.TABLE_ATTRIBUTES_TYPE, common_c.STRING_TYPE)
            if _type == common_c.INT_TYPE:
                value = re.sub("[^0-9]", "", value)
            elif _type == common_c.LIST_TYPE:
                separator = formatter.get(tc.TABLE_ATTRIBUTES_SEPARATOR, "")
                value = self.split_value(value, separator)
        return key, value

    def split_value(self, value: str, separator: str) -> list:
        """Split values based on the given separator character and format with strip function
        each value.

        Args:
            value (str): value to split
            separator (str): character to use as separator

        Returns:
            list: list of the substrings in the string, using sep as the separator string.
        """
        values = value.split(separator)
        values = [value.strip() for value in values]
        return values
