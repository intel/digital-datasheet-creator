from pathlib import Path
import re
from xml.etree.ElementTree import Element  # nosec
""" Bandit ignore warning reason
Element is only used to create objects defined in the application code,
not from the input files. The parse functionality is also secured by
the implementation of defusedxml.Element tree.
"""
from edatasheets_creator.drivers.edatasheet import EDatasheet
import edatasheets_creator.constants.header_constants as header_constants
import edatasheets_creator.constants.transformer_constants as transformer_constants
import edatasheets_creator.constants.dita_constants as dita_c
from edatasheets_creator.utility.table_attributes_utilities import TableAttributesUtilities
from edatasheets_creator.utility.format import Format
from edatasheets_creator.utility.collateral_utilities import CollateralUtilities
from typing import List
from edatasheets_creator.utility.xml_utilities import XMLUtilities
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class DataTable:
    def __init__(self, file_name, source: Element):
        self.file_name_path: str = file_name
        self.source: Element = source
        self.xml_utilities = XMLUtilities()
        self.collateral_utilities = CollateralUtilities()
        self.table_attributes_utilities = TableAttributesUtilities()
        self.format = Format()
        self.column_header_keys: dict[str, dict] = {}
        self.col_name_exists: bool = False
        self.entry_to_repeat: list = []
        self.document_title = self.xml_utilities.get_title(self.source)
        self.file_name = Path(self.file_name_path).name
        self.edatasheet = EDatasheet(self.document_title, self.file_name)

    def transform(self) -> dict:
        """Open the input file name and check if is a normal dita file or is an EDS Register file.

        Args:
            file_name (str): pathname of the input dita file.

        Returns:
            dict: Generated E-Datasheet from the Input Dita File.
        """
        try:
            edatasheet = {}
            if (self.xml_utilities.is_eds_register_file(self.source)):
                edatasheet = self.translate_xml_to_json(self.source)
            else:
                edatasheet = self.build_output_xml_document(self.source)

            return edatasheet

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def translate_xml_to_json(self, source: Element) -> dict:
        """If the input dita file, is an EDS Register file, we just convert it to a json file.

        Args:
            source (Element): Dita Element.

        Returns:
            dict: Generated E-Datasheet from the Input Dita File.
        """
        try:
            root_element = Element(header_constants.DATASHEET)

            root_element.append(source)

            if len(list(root_element.iter())) > 2:
                try:
                    msg = "Generating the output dictionary...\n"
                    ExceptionLogger.logInformation(__name__, msg)

                    dictionary = self.xml_utilities.xml_to_dictionary(root_element)
                    edatasheet = self.edatasheet.get_edatasheet(dictionary)
                    return edatasheet

                except FileNotFoundError as fnf:
                    ExceptionLogger.logError(__name__, "", fnf)

            else:
                msg = f"{self.file_name_path} was not converted."
                ExceptionLogger.logError(__name__, msg)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def build_output_xml_document(self, input: Element) -> dict:
        """Converts the read xml (dita) document to an edatasheet format.

        Args:
            input (Element): Dita Element.

        Returns:
            dict: Generated E-Datasheet from the Input Dita File.
        """
        try:
            source_root = input
            title = self.xml_utilities.get_title(source_root)

            root_element = Element(header_constants.DATASHEET)

            # Get tables, if any, from the DITA file
            tables_on_file = self.xml_utilities.get_tables(source_root)

            # Validate if the DITA file needs to be processed by checking if it contains tables
            edatasheet = {}
            if tables_on_file:
                # Some DITA files do not have sections so we will have to have an alternate path for to handle that case
                tables_element = self.build_tables(root_element, title, tables_on_file)

                tables_element = self.xml_utilities.build_attachments(root_element, source_root)
                dictionary = {}
                if len(list(root_element.iter())) > 1:
                    dictionary = self.xml_utilities.xml_to_dictionary(tables_element, (transformer_constants.ATTACHMENTS, transformer_constants.TABLE_ENTRIES))

                msg = "Generating the output dictionary...\n"
                edatasheet = self.edatasheet.get_edatasheet(dictionary)
            else:
                msg = "DITA file does not contain tables, it will be skipped\n"
            ExceptionLogger.logInformation(__name__, msg)

            return edatasheet

        except Exception as e:
            msg = f"File={self.file_name_path}, Message={e}"
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
                            ExceptionLogger.logError(__name__, f"Unexpected null encountered in building table entry in {self.file_name_path}")
                    except Exception as e:
                        msg = f"File={self.file_name_path}, Message={e}"
                        ExceptionLogger.logError(__name__, msg)
            return root_element

        except Exception as e:
            msg = f"File={self.file_name_path}, Message={e}"
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
            if title and title != transformer_constants.UNKNOWN:
                if self.xml_utilities.has_elements(table_attributes):
                    splitted_elements = title.split(transformer_constants.TITLE_SEPARATOR)
                    title = splitted_elements[-1].strip()
                table_title = self.format.format_name(title)
            else:
                table_title = source.attrib.get(transformer_constants.ID_ATTRIBUTE, transformer_constants.UNKNOWN)
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
                        msg = f"Error encountered in extracting required values for row number {row_num} in {self.file_name_path}, Message={e}"
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
            if title and title != transformer_constants.UNKNOWN:
                if self.xml_utilities.has_elements(table_attributes):
                    splitted_elements = title.split(transformer_constants.TITLE_SEPARATOR)
                    title = splitted_elements[-1].strip()
                table_title = self.format.format_name(title)
            else:
                table_title = source.attrib.get(transformer_constants.ID_ATTRIBUTE, transformer_constants.UNKNOWN)

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
                        if row_elements:
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
                    counter = 0
                    for entry in entries:
                        s_col_name, s_col_unit = self.xml_utilities.get_column_name_from_dictionary(entry, self.column_header_keys, counter)
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
                        elif s_value == "":
                            # Do not add an entry as the value of the cell is empty
                            pass
                        else:
                            s_element = Element(s_col_name)
                            s_element.text = transformer_constants.NOT_FOUND
                            item_list.append(s_element)
                        counter += 1
                except Exception as e:
                    ExceptionLogger.logError(__name__, '', e)
                return item_list
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def build_row_on_top(self, source: Element, col_element: dict[str, Element]) -> List[Element]:
        """Gets the entries for non vertically oriented tables with his respective header
        in a XML structure to include it in the general table Element.

        Args:
            source (Element): Table row with the entries to convert as a key: value structure but in a XML Element.
            col_element (dict[str, Element]): Dictionary with the colnames to set the respective columns.

        Returns:
            List[Element]: List XML Elements with the entries info formatted to include it in the general table Element.
        """
        try:
            entries = self.xml_utilities.get_entries(source)
            element_temp = source
            item_list: List[Element] = []
            column_number = 0

            # Detect and add the entries that need to be repeated
            if len(self.entry_to_repeat) > 0:
                for entry_repeat in self.entry_to_repeat:
                    entries.insert(entry_repeat[dita_c.REPEAT_COLUMN], entry_repeat[dita_c.REPEAT_ELEMENT])
                    entry_repeat[dita_c.REPEAT_TIMES] = entry_repeat[dita_c.REPEAT_TIMES] - 1

            for entry in entries:
                merged_columns_count = 0
                column_index: List[str] = self.xml_utilities.get_column_index(entry)
                if column_index and self.col_name_exists:
                    for item in column_index:
                        # Make standard the col prefix
                        itemUsed = self.make_standard_col_name(item)
                        col_element[itemUsed] = entry
                        merged_columns_count += 1
                    merged_columns_count -= 1
                else:
                    item = self.xml_utilities.get_column_header_key_from_ordinal_pos(self.column_header_keys, column_number)
                    if item:
                        col_element[item] = entry
                    else:
                        ExceptionLogger.logInformation(__name__, f"Could not find any header for this entry {self.xml_utilities.element_to_string(entry)}")

                entry_attributes = entry.attrib
                # Validate vertically merged cells on table
                more_rows = entry_attributes.get(dita_c.MOREROWS, None)
                if more_rows and (entry not in self.entry_to_repeat):
                    already_present = False
                    # Validate if entry is already present
                    for element_entry in self.entry_to_repeat:
                        if element_entry[dita_c.REPEAT_ELEMENT] == entry:
                            already_present = True
                            if (element_entry.get(dita_c.REPEAT_TIMES, None) == 0):
                                # Delete the object that it is not repeated further
                                self.entry_to_repeat.remove(element_entry)
                            break
                    if not already_present:
                        # Add the new entries on the entries for the following rows
                        entry_to_add = dict()
                        entry_to_add[dita_c.REPEAT_TIMES] = int(more_rows)
                        entry_to_add[dita_c.REPEAT_ELEMENT] = entry
                        entry_to_add[dita_c.REPEAT_COLUMN] = column_number
                        self.entry_to_repeat.append(entry_to_add)

                element_temp = entry
                column_number += 1 + merged_columns_count

            is_note = True

            for _, value in col_element.items():
                if value != element_temp:
                    is_note = False
                    break

            amount_of_columns = len(col_element)
            if is_note and (amount_of_columns > 1):
                note = self.xml_utilities.get_text(entries[0]) if entries else ""
                note_element = self._handle_notes(entries[0], note)
                item_list.append(note_element)

            else:
                for key, value in col_element.items():
                    try:
                        col_name, col_unit = self.xml_utilities.get_column_name_from_dictionary_by_key(key, self.column_header_keys)
                        if value is not None:
                            element_value = self.xml_utilities.get_text(value)
                            element_value = self.format.format_value(element_value)
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

                                notes_in_entry = self.xml_utilities.get_note_list(value)
                                p_in_entry = self.xml_utilities.get_p_list(value)
                                namest = value.attrib.get(dita_c.NAMEST, None)
                                if notes_in_entry and not p_in_entry and namest:
                                    column_name_element = self._handle_notes(value, element_value)
                                    item_list = []
                                    item_list.append(column_name_element)
                                    break
                                elif len(entries) == 1 and namest:
                                    column_name_element = self._handle_notes(value, element_value)
                                    item_list = []
                                    item_list.append(column_name_element)
                                    break

                                # Do not add repeated entries
                                if len(item_list) > 0:
                                    add_entry = True
                                    for item_to_check in item_list:
                                        if item_to_check.text == column_name_element.text and item_to_check.tag == column_name_element.tag:
                                            # Do not add the repeated entry
                                            add_entry = False
                                            break
                                    if add_entry:
                                        item_list.append(column_name_element)
                                else:
                                    item_list.append(column_name_element)

                    except Exception as e:
                        ExceptionLogger.logError(__name__, "", e)
            return item_list

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def _handle_notes(self, value: Element, element_value: str) -> Element:
        """Creates a Note entry on the table
        Args:
            value (Element): Entry that will be formatted as Note
            element_value (Str): Value of the row being processed

        Returns:
            Element: Note element that was parsed
        """
        column_name_element = Element(transformer_constants.NOTES)
        bullets = self.xml_utilities.get_li_list(value)
        ordered = self.xml_utilities.get_ol_list(value)
        if bullets and ordered:
            bullets_text = ""
            counter = 1
            for bullet in bullets:
                bullets_text += f" {str(counter)}. {self.xml_utilities.get_text(bullet)}"
                counter += 1
            element_value = bullets_text
        else:
            element_value = f"1. {element_value}"
        column_name_element.text = self.format.format_value(element_value)

        return column_name_element

    def initialize_fields(self, source: Element) -> bool:
        """Initialize table headers and store it on the global column_header_keys dictionary, to
        to use it to build the structure of the final table.

        Args:
            source (Element): XML Element with the entire fields on the document.

        Returns:
            bool: Returns a boolean value if the initialization of the headers is successful, returns False if
            the document doesn't have table headers (using the path tgroup/thead/row).
        """
        try:
            row_index = -1
            self.column_header_keys.clear()
            header_rows = self.xml_utilities.get_table_headers(source)
            self.col_name_exists = False
            handle_multiple_rows = False

            if not header_rows:
                return False

            for row in header_rows:
                if not handle_multiple_rows:
                    col_index = 0
                    actual_col_index = 0
                row_index += 1
                entries = self.xml_utilities.get_entries(row)

                for entry in entries:

                    entry_value = self.xml_utilities.get_text(entry)
                    col_name = entry.attrib.get(dita_c.COLNAME, None)
                    col_num = entry.attrib.get(dita_c.COLNUM, None)
                    name_start = entry.attrib.get(dita_c.NAMEST, None)
                    name_end = entry.attrib.get(dita_c.NAMEEND, None)
                    more_rows = entry.attrib.get(dita_c.MOREROWS, None)

                    # Manage columns with empty headers
                    if (entry_value == "" or entry_value is None) and row_index == 0:
                        entry_value = f"{dita_c.EMPTY_HEADER}{col_index}"

                    # Manage tables with repeated header values, and that will be used as header keys
                    if (entry_value in self.column_header_keys):
                        entry_value = f"{entry_value}col{col_index}"

                    column_headers = {}
                    key = []

                    if not col_num:
                        column_headers[dita_c.COL_NUM] = str(col_index)

                    # This is being added as it is needed when data entries do not have colnum
                    if row_index > 0:
                        # As part of multiple header rows, it is needed to map them to an existing column
                        index_of_header = 0
                        for column_name, _ in self.column_header_keys.items():
                            if column_name == col_name:
                                column_headers[dita_c.COL_NUM_ENTRY] = str(index_of_header)
                                break
                            index_of_header += 1
                            column_headers[dita_c.COL_NUM_ENTRY] = str(actual_col_index)
                    else:
                        column_headers[dita_c.COL_NUM_ENTRY] = str(col_index)

                    if (not col_name and not name_start):
                        if row_index > 0:
                            # All child headers must have a parent header
                            if entry_value not in self.column_header_keys:
                                # Add the column name if there is a mismatch on the header key
                                key.append(f"col{actual_col_index + 1}")
                            else:
                                # The header exists, do nothing else
                                key.append(entry_value)
                        else:
                            key.append(entry_value)
                        column_headers[dita_c.NAME] = entry_value

                    if col_name:
                        self.col_name_exists = True
                        key.append(col_name.strip())
                        column_headers[dita_c.NAME] = col_name.strip()

                    start = 0
                    end = 0

                    if name_start:
                        self.col_name_exists = True
                        column_headers[dita_c.NAME_START] = name_start.strip()
                        name_start = re.sub('[^0-9,.]', '', name_start)
                        start = int(name_start)

                    if name_end:
                        column_headers[dita_c.NAME_END] = name_end.strip()
                        name_end = re.sub('[^0-9,.]', '', name_end)
                        end = int(name_end)

                    if more_rows:
                        column_headers[dita_c.MORE_ROWS] = more_rows.strip()
                        column_headers[dita_c.ROW_END] = int(more_rows) + row_index
                        handle_multiple_rows = True

                    column_headers[dita_c.ROW_START] = row_index
                    if (start - end != 0):
                        for i in range(start, end + 1):
                            key.append("col" + str(i))
                    if len(entry_value) >= 1:
                        # column_units = re.findall(r"\(([^)]+)\)", entry_value)
                        column_units = re.findall(r"\[([^)]+)\]", entry_value)
                        if column_units:
                            unit = column_units[-1]
                            if unit in dita_c.HEADER_UNITS:
                                # Just specify the unit of the column if it is part of the known parsed units
                                column_headers[dita_c.UNIT_HEADER] = unit
                                entry_value = entry_value.replace(f"[{unit}]", "").strip()
                        column_headers[dita_c.LABEL_HEADER] = self.format.format_name(entry_value)
                    else:
                        column_headers[dita_c.LABEL_HEADER] = self.format.format_name(f"{dita_c.EMPTY_HEADER}{col_index}")

                    for item in key:
                        temp_header = dict(column_headers)
                        # Make standard the col prefix
                        itemUsed = self.make_standard_col_name(item)
                        # Validate if the header is a child of another header
                        if itemUsed in self.column_header_keys:
                            temp_header = {}
                            header = self.column_header_keys[itemUsed]
                            header_name_start = header.get(dita_c.NAME_START, None)
                            header_name_end = header.get(dita_c.NAME_END, None)
                            column_name_start = column_headers.get(dita_c.NAME_START, None)
                            column_name_end = column_headers.get(dita_c.NAME_END, None)
                            # Dimension the column depending on the smallest element
                            if (header_name_start is None and header_name_end is None) and (column_name_start is not None and column_name_end is not None):
                                # First row is just a normal cell, take the properties from the smallest header
                                temp_header = header
                            else:
                                # Lower header is smaller, take these properties
                                temp_header = dict(column_headers)
                            temp_header[dita_c.LABEL_HEADER] = header[dita_c.LABEL_HEADER] + "-" + column_headers[dita_c.LABEL_HEADER]
                        self.column_header_keys[itemUsed] = temp_header
                        actual_col_index += 1
                    col_index += 1
            return True

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def make_standard_col_name(self, item: str) -> str:
        """If the column name is c, change it to col

        Args:
            item (str): name of the column

        Returns:
            str: name of the column making sure starts with col
        """
        itemChars = "".join(re.findall('[a-zA-Z]+', item))
        if itemChars == "c":
            # Need to format the entry
            itemNumbers = "".join(re.findall(r'\d+', item))
            itemUsed = f"col{itemNumbers}"
        else:
            itemUsed = item
        return itemUsed
