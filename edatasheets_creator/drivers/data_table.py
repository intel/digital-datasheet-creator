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


import json
from pathlib import Path
import re
from xml.etree.ElementTree import Element  # nosec
""" Bandit ignore warning reason
Element is only used to create objects defined in the application code,
not from the input files. The parse functionality is also secured by
the implementation of defusedxml.Element tree.
"""
from defusedxml import ElementTree
import edatasheets_creator.constants.header_constants as header_constants
import edatasheets_creator.constants.transformer_constants as transformer_constants
import edatasheets_creator.constants.dita_constants as dita_c
from edatasheets_creator.document.jsondatasheetschema import JsonDataSheetSchema
from edatasheets_creator.utility.table_attributes_utilities import TableAttributesUtilities
from edatasheets_creator.utility.format import Format
from edatasheets_creator.utility.collateral_utilities import CollateralUtilities
from typing import List
from edatasheets_creator.utility.time_utilities import get_current_utc_datetime
from edatasheets_creator.utility.xml_utilities import XMLUtilities
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class DataTable:
    def __init__(self, file_name, output_file_name):
        self.file_name: str = file_name
        self.output_file_name: str = output_file_name
        self.xml_utilities = XMLUtilities()
        self.collateral_utilities = CollateralUtilities()
        self.table_attributes_utilities = TableAttributesUtilities()
        self.format = Format()
        self.column_header_keys: dict[str, dict] = {}

    def transform(self):
        """Call the main process to tranform the input file name, using the global path.
        """
        try:
            self.transform_file(self.file_name)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def transform_file(self, file_name: str):
        """Execute the file processing using the given file_name.

        Args:
            file_name (str): pathname of the input file.
        """
        try:
            self.process_file(file_name)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def process_file(self, file_name: str):
        """Open the input file name and check if is a normal dita file or is an EDS Register file.

        Args:
            file_name (str): pathname of the input dita file.
        """
        try:
            root = ElementTree.parse(file_name).getroot()

            if (self.xml_utilities.is_eds_register_file(root)):
                self.translate_xml_to_json(root)
            else:
                self.build_output_xml_document(root)

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def translate_xml_to_json(self, source: Element):
        """If the input dita file, is an EDS Register file, we just convert it to a json file.

        Args:
            source (Element): Dita Element.
        """
        try:
            target_namespace = self.xml_utilities.get_target_namespace()
            root_element = Element(header_constants.DATASHEET)

            namespace_element = Element(self.xml_utilities.NAMESPACE_FIELD_NAME)
            namespace_element.text = target_namespace

            root_element.append(namespace_element)

            # Build Output File Name
            path = Path(self.file_name)

            if self.output_file_name:
                output_file_name = self.output_file_name
            else:
                output_file_name = str(path.parent) + "\\" + path.stem + ".json"

            root_element.append(source)

            if len(list(root_element.iter())) > 2:
                try:
                    msg = f"Writing the output json file: {output_file_name}...\n"
                    ExceptionLogger.logInformation(__name__, msg)

                    dictionary = self.xml_utilities.xml_to_dictionary(root_element)
                    with open(output_file_name, "w") as output_json:
                        json.dump(dictionary, output_json, indent=2)

                    json_schema = JsonDataSheetSchema(output_file_name)
                    json_schema.write()

                except FileNotFoundError as fnf:
                    ExceptionLogger.logError(__name__, "", fnf)

            else:
                msg = f"{path.name} was not converted."
                ExceptionLogger.logError(__name__, msg)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def build_output_xml_document(self, input: Element):
        """Converts the readed xml (dita) document to an edatasheet format.

        Args:
            input (Element): Dita Element.
        """
        try:
            target_namespace = self.xml_utilities.get_target_namespace()
            source_root = input
            title = self.xml_utilities.get_title(source_root)

            root_element = Element(header_constants.DATASHEET)
            namespace_element = Element(self.xml_utilities.NAMESPACE_FIELD_NAME)
            namespace_element.text = target_namespace

            generated_on = get_current_utc_datetime()
            generated_on_element = Element(header_constants.GENERATED_ON)
            generated_on_element.text = generated_on

            title_element = Element(header_constants.TITLE)
            title_element.text = title.strip()

            input_file_element = Element(header_constants.INPUT_FILE)
            input_file_element.text = Path(self.file_name).name

            generated_by_element = Element(header_constants.GENERATED_BY)
            generated_by_element.text = transformer_constants.GENERATED_BY

            platform_abbreviation = self.xml_utilities.get_first_platform_name(source_root)

            platform_abbreviation_element = Element(header_constants.PLATFORM_ABBREVIATION)
            platform_abbreviation_element.text = platform_abbreviation

            segment_element = Element(header_constants.SKU)

            segment_element.text = transformer_constants.UNKNOWN

            root_element.append(namespace_element)
            root_element.append(generated_on_element)
            root_element.append(generated_by_element)
            root_element.append(input_file_element)
            root_element.append(platform_abbreviation_element)
            root_element.append(segment_element)
            root_element.append(title_element)

            # Get the GUID from the file name
            guid = self.collateral_utilities.get_first_guid_from_string(self.file_name)

            if guid:
                source_guid_element = Element(header_constants.GUID)
                source_guid_element.text = guid
                root_element.append(source_guid_element)

            # Build Output File Name
            path = Path(self.file_name)

            if self.output_file_name:
                output_file_name = self.output_file_name
            else:
                output_file_name = str(path.parent) + "\\" + path.stem + ".json"

            # Some DITA files do not have sections so we will have to have an alternate path for to handle that case
            tables_element = self.build_tables(root_element, title, self.xml_utilities.get_tables(source_root))

            tables_element = self.xml_utilities.build_attachments(root_element, source_root)

            if len(list(root_element.iter())) > 2:
                try:
                    msg = f"Writing the output json file: {output_file_name}...\n"
                    ExceptionLogger.logInformation(__name__, msg)

                    dictionary = self.xml_utilities.xml_to_dictionary(tables_element, (transformer_constants.TABLE_ENTRIES))
                    with open(output_file_name, "w", encoding="utf8") as output_json:
                        json.dump(dictionary, output_json, indent=2, ensure_ascii=False)

                    json_schema = JsonDataSheetSchema(output_file_name)
                    json_schema.write()

                except FileNotFoundError as fnf:
                    ExceptionLogger.logError(__name__, "", fnf)

            else:
                msg = f"{path.name} was not converted."
                ExceptionLogger.logError(__name__, msg)

        except Exception as e:
            msg = f"File={self.file_name}, Message={e}"
            ExceptionLogger.logError(__name__, msg)

    def build_tables(self, root_element: Element, document_title: str, table_list: List[Element]) -> Element:
        """Convert all the tables in the root element or main document, to the required format, in this case
        is the table title, table entries and table attributes.

        Args:
            root_element (Element): main document with the tables to convert.
            document_title (str): main title for the document.
            table_list (List[Element]): list of table Elements inside the document.

        Returns:
            Element: main document with the converted tables.
            (this means with the table title, table entries and table attributes).
        """
        try:
            document_title = transformer_constants.TABLES_CONTAINER
            for table in table_list:
                description = self.xml_utilities.get_desc(table)
                # Exists a particular case when table title has attributes, for that we need to handle and include it to the table
                table_attributes = self.table_attributes_utilities.get_table_attributes(description)
                children = list(table)
                if children:
                    try:
                        is_vertical = self.xml_utilities.is_orientation_vertical(table)
                        builded_table = None
                        if is_vertical:
                            builded_table = self.build_table_on_left(document_title, table, table_attributes)
                        else:
                            builded_table = self.build_table_on_top(document_title, table, table_attributes)
                        if builded_table:
                            root_element.append(builded_table)
                        else:
                            ExceptionLogger.logError(__name__, f"Unexpected null encountered in building table entry in {self.file_name}")
                    except Exception as e:
                        msg = f"File={self.file_name}, Message={e}"
                        ExceptionLogger.logError(__name__, msg)
            return root_element

        except Exception as e:
            msg = f"File={self.file_name}, Message={e}"
            ExceptionLogger.logError(__name__, msg)

    def build_table_on_left(self, document_title: str, source: Element, table_attributes: Element) -> Element:
        """Get an Element with the entries for all the table, this applies for the vertical tables.

        Args:
            document_title (str): main title for the document.
            source (Element): table Element with the entries to convert.
            table_attributes (Element): table attributes Element included in the description tag of the table.

        Returns:
            Element: table entries Element to include it in the main document.
        """
        try:
            output_element: Element = None
            table_container: Element = None
            title = self.xml_utilities.get_title(source)
            if self.xml_utilities.has_elements(table_attributes):
                splitted_elements = title.split(transformer_constants.TITLE_SEPARATOR)
                title = splitted_elements[-1].strip()
            table_title = self.format.format_name(title)
            table_rows = self.xml_utilities.get_row_body_elements(source)

            if (not self.initialize_fields(source)):
                msg = f"No table header detected in '{document_title}'. Table '{title}' will be skipped. "
                ExceptionLogger.logError(__name__, msg)
                return output_element
            self.column_header_keys = dict(sorted(self.column_header_keys.items()))

            table_rows = self.xml_utilities.get_row_body_elements(source)

            if table_rows:
                output_element = Element(document_title)
                table_container = Element(table_title)
                for row_num, row in enumerate(table_rows):
                    try:
                        row_elements = self.build_row_on_left(row)
                        table_entries = Element(transformer_constants.TABLE_ENTRIES)

                        for row in row_elements:
                            table_entries.append(row)

                        table_container.append(table_entries)
                    except Exception as e:
                        msg = f"Error encountered in extracting required values for row number {row_num} in {self.file_name}, Message={e}"
                        ExceptionLogger.logError(__name__, msg)
                if self.xml_utilities.has_elements(table_attributes):
                    table_container.append(table_attributes)
                output_element.append(table_container)

            return output_element

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def build_table_on_top(self, document_title: str, source: Element, table_attributes: Element) -> Element:
        """Get an Element with the entries for all the table, this applies for the horizontal tables.

        Args:
            document_title (str): main title for the document.
            source (Element): table Element with the entries to convert.
            table_attributes (Element): table attributes Element included in the description tag of the table.

        Returns:
            Element: table entries Element to include it in the main document.
        """
        try:
            output_element: Element = None
            table_container: Element = None
            title = self.xml_utilities.get_title(source)
            if self.xml_utilities.has_elements(table_attributes):
                splitted_elements = title.split(transformer_constants.TITLE_SEPARATOR)
                title = splitted_elements[-1].strip()
            table_title = self.format.format_name(title)

            if (not self.initialize_fields(source)):
                msg = f"No table header detected in '{document_title}'. Table '{title}' will be skipped. "
                ExceptionLogger.logError(__name__, msg)
                return output_element
            self.column_header_keys = dict(sorted(self.column_header_keys.items()))

            table_rows = self.xml_utilities.get_row_body_elements(source)

            if table_rows:
                output_element = Element(document_title)
                table_container = Element(table_title)
                col_element: dict[str, Element] = {}
                for key in self.column_header_keys:
                    col_element[key] = None
                for row in table_rows:
                    try:
                        row_elements = self.build_row_on_top(row, col_element)
                        table_entries = Element(transformer_constants.TABLE_ENTRIES)
                        for entry in row_elements:
                            table_entries.append(entry)
                        table_container.append(table_entries)
                    except Exception as e:
                        ExceptionLogger.logError(__name__, "", e)
                if self.xml_utilities.has_elements(table_attributes):
                    table_container.append(table_attributes)
                output_element.append(table_container)
            return output_element

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def build_row_on_left(self, source: Element) -> Element:
        """Gets the entries for vertically oriented tables with his respective header
        in a XML structure to include it in the general table Element.

        Args:
            source (Element): Table row with the entries to convert as a key: value structure but in a XML Element.
            col_element (dict[str, Element]): Dictionary with the colnames to set the respective columns.

        Returns:
            Element: XML Element with the entry info formatted to include it in the general table Element.
        """
        try:
            s_col_name = None
            s_col_unit = None
            item_list: List[Element] = []
            entries = self.xml_utilities.get_entries(source)
            if len(entries) == 1:
                note_element = Element(transformer_constants.NOTE)
                note_element.text = self.format.format_value(self.xml_utilities.get_text(entries[0]).strip())
            else:
                try:
                    for entry in entries:
                        s_col_name, s_col_unit = self.xml_utilities.get_column_name_from_dictionary(entry, self.column_header_keys)
                        if not s_col_name:
                            # TODO: Check if is necessary to apply col_units here
                            s_col_name = self.xml_utilities.get_column_name_string_from_dictionary_range(entry, self.column_header_keys)
                        s_value = self.format.format_value(self.xml_utilities.get_text(entry).strip())
                        if (s_value) and (len(s_value) > 0) and (s_value.lower() != transformer_constants.NOT_FOUND.lower()):
                            s_element = Element(s_col_name)
                            if s_col_unit:
                                value_element = Element(dita_c.VALUE_HEADER)
                                value_element.text = s_value
                                s_element.append(value_element)
                                unit_element = Element(dita_c.UNIT_HEADER)
                                unit_element.text = s_col_unit
                                s_element.append(unit_element)
                            else:
                                s_element.text = s_value
                            item_list.append(s_element)
                        else:
                            s_element = Element(s_col_name)
                            s_element.text = transformer_constants.NOT_FOUND
                            item_list.append(s_element)
                except Exception as e:
                    ExceptionLogger.logError(__name__, '', e)
                return item_list
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def build_row_on_top(self, source: Element, col_element: dict[str, Element]) -> Element:
        """Gets the entries for non vertically oriented tables with his respective header
        in a XML structure to include it in the general table Element.

        Args:
            source (Element): Table row with the entries to convert as a key: value structure but in a XML Element.
            col_element (dict[str, Element]): Dictionary with the colnames to set the respective columns.

        Returns:
            Element: XML Element with the entry info formatted to include it in the general table Element.
        """
        try:
            entries = self.xml_utilities.get_entries(source)
            element_temp = source
            item_list: List[Element] = []
            column_number = 0
            for entry in entries:
                column_index: List[str] = self.xml_utilities.get_column_index(entry)

                if column_index:
                    for item in column_index:
                        col_element[item] = entry
                else:
                    item = self.xml_utilities.get_column_header_key_from_ordinal_pos(self.column_header_keys, column_number)
                    if item:
                        col_element[item] = entry
                    else:
                        ExceptionLogger.logError(__name__, f"Could not find any value for this entry {self.xml_utilities.element_to_string(entry)}")

                element_temp = entry
                column_number += 1

            is_note = True
            for _, value in col_element.items():
                if value != element_temp:
                    is_note = False
                    break

            if is_note:
                note = self.xml_utilities.get_text(entries[0]) if entries else ""
                note_element = Element(transformer_constants.NOTES)
                note_element.text = note
                item_list.append(note_element)

            else:
                for key, value in col_element.items():
                    try:
                        col_name, col_unit = self.xml_utilities.get_column_name_from_dictionary_by_key(key, self.column_header_keys)
                        if value is not None:
                            element_value = self.xml_utilities.get_text(value)
                            p_list = self.xml_utilities.get_p_list(value)
                            if p_list:
                                p_string = ""
                                for p in p_list:
                                    if len(p_string) > 0:
                                        p_string += ","
                                    p_value = self.format.format_value(self.xml_utilities.get_text(p))
                                    p_string += p_value
                                element_value = p_string

                            if element_value and len(element_value) > 0:
                                column_name_element = Element(col_name)
                                if col_unit:
                                    value_element = Element(dita_c.VALUE_HEADER)
                                    value_element.text = self.format.format_special_fields(col_name, element_value)
                                    column_name_element.append(value_element)
                                    unit_element = Element(dita_c.UNIT_HEADER)
                                    unit_element.text = col_unit
                                    column_name_element.append(unit_element)
                                else:
                                    column_name_element.text = self.format.format_special_fields(col_name, element_value)
                                item_list.append(column_name_element)

                    except Exception as e:
                        ExceptionLogger.logError(__name__, "", e)
            return item_list

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def initialize_fields(self, source: Element) -> bool:
        """Initialize table headers and store it on the global column_header_keys dictionary, to
        to use it to build the stucture of the final table.

        Args:
            source (Element): XML Element with the entire fields on the document.

        Returns:
            bool: Returns a boolean value if the initialization of the headers is successful, returns False if
            the document doesn't have table headers (using the path tgroup/thead/row).
        """
        try:
            row_index = -1
            col_index = 0
            self.column_header_keys.clear()
            header_rows = self.xml_utilities.get_table_headers(source)

            if not header_rows:
                return False

            for row in header_rows:
                row_index += 1
                entries = self.xml_utilities.get_entries(row)

                for entry in entries:

                    entry_value = self.xml_utilities.get_text(entry)
                    col_name = entry.attrib.get(dita_c.COLNAME, None)
                    col_num = entry.attrib.get(dita_c.COLNUM, None)
                    name_start = entry.attrib.get(dita_c.NAMEST, None)
                    name_end = entry.attrib.get(dita_c.NAMEEND, None)
                    more_rows = entry.attrib.get(dita_c.MOREROWS, None)

                    column_headers = {}
                    key = []

                    if not col_num:
                        column_headers[dita_c.COL_NUM] = str(col_index)

                    if (not col_name and not name_start):
                        key.append(entry_value)
                        column_headers[dita_c.NAME] = entry_value

                    if col_name:
                        key.append(col_name.strip())
                        column_headers[dita_c.NAME] = col_name.strip()

                    start = 0
                    end = 0

                    if name_start:
                        column_headers[dita_c.NAME_START] = name_start.strip()
                        if (len(name_start) < 4):
                            msg = f"The namest is incorrect: {name_start}"
                            raise ExceptionLogger.logError(__name__, msg)
                        start = int(name_start[3:])

                    if name_end:
                        column_headers[dita_c.NAME_END] = name_end.strip()
                        if (len(name_end) < 4):
                            msg = f"The namest is incorrect: {name_end}"
                            raise ExceptionLogger.logError(__name__, msg)
                        end = int(name_end[3:])

                    if more_rows:
                        column_headers[dita_c.MORE_ROWS] = more_rows.strip()
                        column_headers[dita_c.ROW_END] = int(more_rows) + row_index

                    column_headers[dita_c.ROW_START] = row_index
                    if (start - end != 0):
                        for i in range(start, end + 1):
                            key.append("col" + str(i))
                    if len(entry_value) >= 1:
                        # column_units = re.findall(r"\(([^)]+)\)", entry_value)
                        column_units = re.findall(r"\[([^)]+)\]", entry_value)
                        if column_units:
                            unit = column_units[-1]
                            column_headers[dita_c.UNIT_HEADER] = unit
                            # entry_value = entry_value.replace(f"({unit})", "").strip()
                            entry_value = entry_value.replace(f"[{unit}]", "").strip()
                        column_headers[dita_c.LABEL_HEADER] = self.format.format_name(entry_value)
                    else:
                        column_headers[dita_c.LABEL_HEADER] = transformer_constants.EMPTY

                    for item in key:
                        if item in self.column_header_keys:
                            header = self.column_header_keys[item]
                            column_headers[dita_c.LABEL_HEADER] = header[dita_c.LABEL_HEADER] + "-" + column_headers[dita_c.LABEL_HEADER]
                        self.column_header_keys[item] = column_headers
                    col_index += 1
            return True

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
