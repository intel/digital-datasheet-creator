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

from xml.etree.ElementTree import Element  # nosec
""" Bandit ignore warning reason
Element is only used to create objects defined in the application code,
not from the input files. The parse functionality is also secured by
the implementation of defusedxml.Element tree.
"""
import edatasheets_creator.constants.header_constants as header_constants
from edatasheets_creator.utility.time_utilities import get_current_utc_datetime
import edatasheets_creator.constants.transformer_constants as transformer_constants
import edatasheets_creator.constants.dita_constants as dita_c
import edatasheets_creator.constants.datasheetconstants as datasheet_c
import edatasheets_creator.constants.header_constants as header_c
import edatasheets_creator.constants.xmltagconstants as xml_tag_c
from pathlib import Path
import xmltodict
import json
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from defusedxml import ElementTree
from edatasheets_creator.utility.xml_utilities import XMLUtilities
from edatasheets_creator.utility.xml_validator import XMLValidator
from edatasheets_creator.utility.collateral_utilities import CollateralUtilities
from edatasheets_creator.document.jsondatasheetschema import JsonDataSheetSchema
from edatasheets_creator.utility.format import Format
import copy


class DataSheetUtilities:
    def __init__(self, file_name, output_file_name):
        self.xml_utilities = XMLUtilities()
        self.xml_validator = XMLValidator()
        self.collateral_utilities = CollateralUtilities()
        self.format = Format()
        self.column_header_keys: dict[str, dict] = {}
        self.file_name = file_name
        self.output_file_name: str = output_file_name

    def generate_meta_data(self, source_element, root):
        """
        Generates meta data for source element

        Args:
        source_element (Element) : Source element to add meta data to from root
        root (Element) : Root element to add meta data to

        Returns:
        source_element (Element) : New transformed element with meta data attached
        """
        target_namespace = self.xml_utilities.get_target_namespace()
        namespace_element = Element(self.xml_utilities.NAMESPACE_FIELD_NAME)
        namespace_element.text = target_namespace
        generated_on = get_current_utc_datetime()
        generated_on_element = Element(header_constants.GENERATED_ON)
        generated_on_element.text = generated_on
        title = self.xml_utilities.get_title(root)
        title_element = Element(header_constants.TITLE)
        title_element.text = title.strip()

        input_file_element = Element(header_constants.INPUT_FILE)
        input_file_element.text = Path(self.file_name).name

        generated_by_element = Element(header_constants.GENERATED_BY)
        generated_by_element.text = transformer_constants.GENERATED_BY

        platform_abbreviation = self.xml_utilities.get_first_platform_name(root)

        platform_abbreviation_element = Element(header_constants.PLATFORM_ABBREVIATION)
        platform_abbreviation_element.text = platform_abbreviation

        segment_element = Element(header_constants.SKU)

        segment_element.text = transformer_constants.UNKNOWN

        source_element.append(namespace_element)
        source_element.append(generated_on_element)
        source_element.append(generated_by_element)
        source_element.append(input_file_element)
        source_element.append(platform_abbreviation_element)
        source_element.append(segment_element)
        source_element.append(title_element)

        # Get the GUID from the file name
        guid = self.collateral_utilities.get_first_guid_from_string(self.file_name)

        if guid:
            source_guid_element = Element(header_constants.GUID)
            source_guid_element.text = guid
            source_element.append(source_guid_element)

        return source_element

    def build_table_with_notes(self, table_list, note_list, section_element):
        for i in range(len(table_list)):
            root = Element(datasheet_c.DATASHEET_TABLES)
            headers = self.get_headers_2(table_list[i])
            row_content = self.get_entries(table_list[i])
            title = list(table_list[i].iterfind(header_c.TITLE))
            if len(title) == 0:
                title_text = datasheet_c.DATASHEET_TABLE
            else:
                title_text = title[0].text.replace(" ", "_")
                title_text = title_text.replace("[", "_")
                title_text = title_text.replace("]", "_")
                title_text = title_text.replace(":", "_")
                title_text = title_text.replace("(", "_")
                title_text = title_text.replace(")", "_")
                title_text = title_text.replace(",", "_")
            root_element = Element(title_text)
            root_element = Element(title_text)
            processed_element = self.map_row_to_element(root_element, headers, row_content)
            notes_element = Element(title_text + '_' + datasheet_c.DATASHEET_NOTES)
            try:
                ordered_list = list(note_list[i].iter(xml_tag_c.XML_TAG_ORDERED_LIST))
                response = self.process_ol(ordered_list)
                notes_element.append(response)
                processed_element.append(notes_element)
            except Exception:
                ExceptionLogger.logInformation(__name__, "", "Error when building table with notes")
            for unit_element in processed_element:
                root.append(unit_element)
            section_element.append(root)

        return section_element

    def process_ol(self, all_ol):
        listing = list(all_ol[0].iter(xml_tag_c.XML_TAG_LIST))
        list_values = Element(datasheet_c.DATASHEET_LIST)
        for i in range(len(listing)):
            sub_element_1 = Element(datasheet_c.DATASHEET_SERIAL_NUMBER)
            p_element = list(listing[i].iterfind(xml_tag_c.XML_TAG_PARAGRAPH))
            sub_element_1.text = p_element[0].text
            list_values.append(sub_element_1)
        return list_values

    def process_fig(self, all_fig):
        root_element = Element(datasheet_c.DATSHEET_FIGURE)
        for i in range(len(all_fig)):
            sub_element_1 = Element(header_c.TITLE)
            title = list(all_fig[i].iterfind(header_c.TITLE))
            if len(title) > 0:
                sub_element_1.text = title[0].text
                root_element.append(sub_element_1)
            sub_element_2 = Element(transformer_constants.ATTACHMENTS)
            image = list(all_fig[i].iterfind(dita_c.IMAGE_TAG))
            if len(image) > 0:
                sub_element_2.text = image[0].attrib.get(dita_c.HREF_ATTRIBUTE, None)
                root_element.append(sub_element_2)
        return root_element

    def process_ph(self, all_ph, section_element):
        for element in all_ph:
            sub_element = Element(datasheet_c.DATASHEET_HEADING)
            sub_element.text = ElementTree.tostring(element, 'unicode', 'text').strip().replace('\n', " ")
            section_element.append(sub_element)
        return section_element

    def process_p(self, all_p, section_element):
        for element in all_p:
            decorators = list(element.iter())
            if len(decorators) == 1:
                sub_element = Element(datasheet_c.DATASHEET_HEADING)
                sub_element.text = ElementTree.tostring(decorators[0], 'unicode', 'text').strip().replace('\n', " ")
                section_element.append(sub_element)
            else:
                sub_element = Element(datasheet_c.DATASHEET_HEADING)
                # sub_element.text = decorators[-1].text
                sub_element.text = ElementTree.tostring(decorators[0], 'unicode', 'text').strip().replace('\n', " ")
                section_element.append(sub_element)
        return section_element

    def process_gloss_body(self, all_glossBody, section_element):
        all_glossSurface = list(all_glossBody[0].iterfind(xml_tag_c.XML_TAG_GLOSS_SURFACE_FORM))
        for element in all_glossSurface:
            surface_element = Element(datasheet_c.DATASHEET_SURFACE_FORM)
            surface_element.text = ElementTree.tostring(element, 'unicode', 'text').strip().replace('\n', " ")
            section_element.append(surface_element)
        return section_element

    def process_ul(self, all_ul, section_element):
        for ul in all_ul:
            for li in ul.findall(xml_tag_c.XML_TAG_LIST):
                sub_element = Element(datasheet_c.DATASHEET_LISTING)
                sub_element.text = ElementTree.tostring(li, 'unicode', 'text').strip().replace('\n', " ")
                section_element.append(sub_element)
        return section_element

    def map_row_to_element(self, element, row_header, row_content):
        """
        Maps rows to elements with no description tags

        Args:
        element (Element) : Element
        row_header (Dictionary) : dictionary containing row headers
        row_content (Dictionary) : dictionary containing all contents of the rows

        Returns:
        Element : element containing processed information
        """

        all_elements = []
        element_to_use = copy.deepcopy(element)
        for i in range(len(row_content)):
            for j in range(len(row_header)):
                element_to_use = self.check_for_special_rules(i, j, row_header, row_content, element_to_use)
            all_elements.append(element_to_use)
            element_to_use = copy.deepcopy(element)
        return all_elements

    def check_for_special_rules(self, i, j, row_header, row_content, element_to_use):
        """
        Check and implement special rules in an element
        Args:
        i (Integer): index for accessing row value
        j (Integer) : index for accessing row values
        row_header (Dictionary) : dictionary containing row headers
        row_content (Dictionary) : dictionary containing all contents of the rows
        element_to_use (Element) : element to check for special rules


        Returns:
        element_to_use (Element) : Element with special rules implemented
        """
        string_key = 'col' + str(j + 1)
        if dita_c.UNIT_IDENTIFIER in row_header[string_key]:
            new_element = Element(row_header[string_key][dita_c.LABEL_HEADER])
            sub_element_1 = Element(dita_c.UNIT_IDENTIFIER)
            sub_element_1.text = row_header[string_key][dita_c.UNIT_IDENTIFIER]
            new_element.append(sub_element_1)
            sub_element_2 = Element(dita_c.VALUE_CREATOR)
            sub_element_2.text = row_content[i + 1][j]
            new_element.append(sub_element_2)
            element_to_use.append(new_element)
        elif len(row_header[string_key][dita_c.LABEL_HEADER]) == 3:
            new_element = Element(row_header[string_key][dita_c.LABEL_HEADER])
            sub_element_1 = Element('type')
            sub_element_1.text = row_header[j][1].replace(")", "").replace("]", "")
            new_element.append(sub_element_1)
            sub_element_2 = Element(dita_c.UNIT_IDENTIFIER)
            sub_element_2.text = row_header[j][2].replace(")", "").replace("]", "")
            new_element.append(sub_element_2)
            sub_element_3 = Element(dita_c.VALUE_CREATOR)
            sub_element_3.text = row_content[i + 1][j]
            new_element.append(sub_element_3)
        elif row_header[string_key][dita_c.LABEL_HEADER].lower() == datasheet_c.DATASHEET_ROUTING_LAYER:
            routingLayerValue = row_content[i + 1][j].split(',')
            if len(routingLayerValue) > 1:
                for i in range(len(routingLayerValue)):
                    new_element = Element(row_header[string_key][dita_c.LABEL_HEADER])
                    new_element.text = routingLayerValue[i]
                    element_to_use.append(new_element)
            else:
                try:
                    new_element = Element(row_header[string_key][dita_c.LABEL_HEADER])
                    new_element.text = row_content[i + 1][j]
                except Exception:
                    new_element.text = datasheet_c.DATASHEET_NOT_AVAILABLE
                element_to_use.append(new_element)
        else:
            new_element = Element(row_header[string_key][dita_c.LABEL_HEADER])
            try:
                new_element.text = row_content[i + 1][j]
            except Exception:
                new_element.text = datasheet_c.DATASHEET_NOT_AVAILABLE
            element_to_use.append(new_element)
        return element_to_use

    def get_headers(self, source: Element):
        """
        Get headers in any particular table

        Args:
        element (Element) : Element from which headers are to be gotten from

        Returns:
        dictionary : Dictionary containing all headers in a table with information about columns, more_rows etc attributes
        """
        column_header_keys = {}
        try:
            row_index = -1
            col_index = 0
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
                    if '(' in entry_value:
                        mid_value = entry_value.split('(')
                        entry_value = mid_value[0]
                        column_headers[dita_c.UNIT_HEADER] = mid_value[1][:-1]

                    if len(entry_value) >= 1:
                        column_headers[dita_c.LABEL_HEADER] = self.format.format_name(entry_value)
                    else:
                        column_headers[dita_c.LABEL_HEADER] = transformer_constants.EMPTY

                    for item in key:
                        if item in self.column_header_keys:
                            header = self.column_header_keys[item]
                            column_headers[dita_c.LABEL_HEADER] = header[dita_c.LABEL_HEADER] + "-" + column_headers[dita_c.LABEL_HEADER]

                        column_header_keys[item] = column_headers
                    col_index += 1
        except Exception:
            print(Exception)

        column_header_keys = dict(sorted(column_header_keys.items()))
        return column_header_keys

    def get_entries(self, element):
        """
        Get entries in any particular row of a table

        Args:
        element (Element) : Element from which entries are to be gotten from

        Returns:
        dictionary : Dictionary containing all rows in an element
        """
        rows_content = list(element.findall("tgroup/tbody/row"))
        row_num = 1
        all_rows = {}
        for row in rows_content:
            entries = list(row.iter(dita_c.ENTRY_TAG))
            content = []
            for entry in entries:
                concatenated_string = datasheet_c.DATASHEET_NOT_AVAILABLE
                concatenated_string = ElementTree.tostring(entry, 'unicode', 'text').strip().replace('\n', "")
                concatenated_string = " ".join(concatenated_string.split())
                p_tags = list(entry.iterfind(xml_tag_c.XML_TAG_PARAGRAPH))
                for p_tag in p_tags:
                    xref_tag = list(p_tag.iterfind(xml_tag_c.XML_TAG_XREF))
                    if len(xref_tag) > 0:
                        concatenated_string = concatenated_string + xref_tag[0].attrib[dita_c.HREF_ATTRIBUTE]
                if concatenated_string == "":
                    concatenated_string = " "
                content.append(concatenated_string)
            all_rows[row_num] = content
            row_num = row_num + 1

        return all_rows

    def generate_json_schema(self, file_name):
        """
        Generate JSON schema

        Args:
        file_name (String) : File name for JSON schema
        """
        json_schema = JsonDataSheetSchema(file_name)
        json_schema.write()

    def write_to_json(self, source_element):
        """
        Write element to JSON file

        Args:
        source_element (Element) : Element to write to JSON
        """
        path = Path(self.file_name)
        if self.output_file_name:
            output_file_name = self.output_file_name
        else:
            output_file_name = str(path.parent) + "\\" + path.stem + ".json"
        xmlstr = ElementTree.tostring(source_element).decode("utf-8")
        data_dict = xmltodict.parse(xmlstr)
        with open(output_file_name, "w", encoding="utf8") as output_json:
            json.dump(data_dict, output_json, indent=2, ensure_ascii=False)
        self.generate_json_schema(output_file_name)

    def get_headers_2(self, source: Element):
        """
        Get headers in any particular table

        Args:
        element (Element) : Element from which headers are to be gotten from

        Returns:
        dictionary : Dictionary containing all headers in a table with information about columns, more_rows etc attributes
        """
        column_header_keys = {}
        try:
            row_index = -1
            col_index = 0
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
                    if '(' in entry_value:
                        len_of_delimiter = entry_value.count('(')
                        # for char in entry_value:
                        #     if char == "(":
                        #         len_of_delimiter = len_of_delimiter + 1
                        if len_of_delimiter == 1:
                            mid_value = entry_value.split('(')
                            entry_value = mid_value[0]
                            column_headers[dita_c.UNIT_IDENTIFIER] = mid_value[1][:-1]
                        elif len_of_delimiter == 2:
                            mid_value = entry_value.rsplit('(', 1)
                            entry_value = mid_value[0]
                            column_headers[dita_c.UNIT_IDENTIFIER] = mid_value[1][:-1]

                    if len(entry_value) >= 1:
                        column_headers[dita_c.LABEL_HEADER] = self.format.format_name(entry_value)
                    else:
                        column_headers[dita_c.LABEL_HEADER] = transformer_constants.EMPTY

                    for item in key:
                        if item in self.column_header_keys:
                            header = self.column_header_keys[item]
                            column_headers[dita_c.LABEL_HEADER] = header[dita_c.LABEL_HEADER] + "-" + column_headers[dita_c.LABEL_HEADER]

                        column_header_keys[item] = column_headers
                    col_index += 1
        except Exception:
            print(Exception)

        column_header_keys = dict(sorted(column_header_keys.items()))
        return column_header_keys
