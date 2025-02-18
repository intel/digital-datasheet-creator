import copy
import json
import re
import defusedxml.ElementTree as ET
from pathlib import Path
from defusedxml import ElementTree
from xml.etree.ElementTree import Element  # nosec
""" Bandit ignore warning reason
Element is only used to create objects defined in the application code,
not from the input files. The parse functionality is also secured by
the implementation of defusedxml.Element tree.
"""
import edatasheets_creator.constants.dita_constants as dita_c
import edatasheets_creator.constants.header_constants as header_constants
import edatasheets_creator.constants.transformer_constants as transformer_constants
import edatasheets_creator.constants.datasheetconstants as datasheet_c
import xmltodict
from edatasheets_creator.document.jsondatasheetschema import JsonDataSheetSchema
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.utility.collateral_utilities import CollateralUtilities
from edatasheets_creator.utility.format import Format
from edatasheets_creator.utility.time_utilities import get_current_utc_datetime
from edatasheets_creator.utility.xml_utilities import XMLUtilities
from edatasheets_creator.utility.xml_validator import XMLValidator


class DataTablePDGCCG:
    def __init__(self, file_name, output_file_name):
        """
        Initialize parameters for class
        """
        self.file_name: str = file_name
        self.output_file_name: str = output_file_name
        self.column_header_keys: dict[str, dict] = {}
        self.xml_utilities = XMLUtilities()
        self.xml_validator = XMLValidator()
        self.collateral_utilities = CollateralUtilities()
        self.format = Format()
        self.header_keys()

    def transform(self):
        """
        Transform method for file processing
        """
        try:
            self.transform_file(self.file_name)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def transform_file(self, file_name: str):
        """
        Transform particular file

        Args:
        file_name (string) : file to be converted
        """
        try:
            self.process_file(file_name)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def process_file(self, file_name):
        """
        Process particular file

        Args:
        file_name (string) : file to be converted
        """
        # output_element = self.process_xml(file_name)
        output_element = self.process_xml_flat(file_name)
        self.write_to_json(output_element)

    def header_keys(self):
        """
        Returns list of header keys expected in the PDG file
        """
        self.header_keys = datasheet_c.DATASHEET_HEADER_KEYS

    def get_headers(self, element):
        """
        Get headers in any particular table

        Args:
        element (Element) : Element from which headers are to be gotten from

        Returns:
        dictionary : Dictionary containing all headers in a table
        """
        rows_headers = list(element.findall("tgroup/thead/row"))
        try:
            entries = list(rows_headers[0].iter(dita_c.ENTRY_TAG))
        except Exception:
            entries = []
        headers = {}
        for i in range(len(entries)):
            concatenated_string = ""
            concatenated_string = ElementTree.tostring(entries[i], 'unicode', 'text').strip().replace(" ", "").replace("/", "").lower()
            concatenated_string = re.split("\[|\(|,|/", concatenated_string)
            headers[i] = concatenated_string
        return headers

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
                if concatenated_string == "":
                    concatenated_string = " "
                content.append(concatenated_string)
            all_rows[row_num] = content
            row_num = row_num + 1

        return all_rows

    def get_text(self, entry):
        """
        Get text from an entry

        Args:
        entry (Element) : Element from which text is to gotten from

        Returns:
        string : entry value in string
        """
        concatenated_string = ""
        concatenated_string = ElementTree.tostring(entry, 'unicode', 'text').strip()
        return concatenated_string

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
        # elif len(row_header[string_key][dita_c.LABEL_HEADER]) == 3:
        #     new_element = Element(row_header[string_key][dita_c.LABEL_HEADER])
        #     sub_element_1 = Element('type')
        #     sub_element_1.text = row_header[j][1].replace(")", "").replace("]", "")
        #     new_element.append(sub_element_1)
        #     sub_element_2 = Element(dita_c.UNIT_IDENTIFIER)
        #     sub_element_2.text = row_header[j][2].replace(")", "").replace("]", "")
        #     new_element.append(sub_element_2)
        #     sub_element_3 = Element(dita_c.VALUE_CREATOR)
        #     sub_element_3.text = row_content[i + 1][j]
        #     new_element.append(sub_element_3)
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

    def map_row_to_element_with_desc(self, element, row_header, row_content):
        """
        Maps rows to elements with description tags

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
                            column_headers['unit'] = mid_value[1][:-1]
                        elif len_of_delimiter == 2:
                            mid_value = entry_value.rsplit('(', 1)
                            entry_value = mid_value[0]
                            column_headers['unit'] = mid_value[1][:-1]

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

    def decouple_property(self, element_name, source_element, new_name=None):
        """
        Break json component into multiple components based on specific attribute

        Args:
        element_name (String) : name of component to be decoupled
        source_element (Element) : Original element to attach decoupled element
        new_name (String) : new name of component to be transformed to

        Returns:
        datasheet_element (Element) : New element containing all decoupled components
        """
        datasheet_element = Element(dita_c.DATASHEET_TAG)
        datasheet_element = self.generate_meta_data(datasheet_element, source_element)
        all_pdgs = list(source_element.iter(dita_c.PDG_TAG))
        for pdg in all_pdgs:
            check_for_element_presence = list(pdg.iter(element_name.lower()))
            text_information = check_for_element_presence[0].text.split(",")
            if len(text_information) > 1:
                all_pdg_elements = list(pdg.iter())
                for value in text_information:
                    new_pdg_element = Element(dita_c.PDG_TAG)
                    for i in range(1, len(all_pdg_elements)):
                        if all_pdg_elements[i].tag.lower() == element_name.lower():
                            if new_name is not None:
                                pdg_temp_element = Element(new_name)
                            else:
                                pdg_temp_element = Element(all_pdg_elements[i].tag)
                            pdg_temp_element.text = value
                            new_pdg_element.append(pdg_temp_element)
                        else:
                            pdg_temp_element = Element(all_pdg_elements[i].tag)
                            pdg_temp_element.text = all_pdg_elements[i].text
                            new_pdg_element.append(pdg_temp_element)
                    datasheet_element.append(new_pdg_element)
            else:
                datasheet_element.append(new_pdg_element)
        return datasheet_element

    def process_xml(self, file_name, decouple_element=None, new_name=None):
        """
        Main method to process XML/DITA files

        Args:
        file_name (String) : name of file to be transformed
        decouple_element (String) : name of component to decouple
        new_name (String) : new name of component to be transformed to

        Returns:
        source_element (Element) : New transformed element for writing to JSON
        """
        tree = ET.parse(file_name)
        root = tree.getroot()
        check_xml = self.xml_validator.check_for_valid_xml(root)
        if check_xml is True:
            all_tables = list(root.iter(dita_c.TABLE_TAG))
            source_element = Element(dita_c.DATASHEET_TAG)
            source_element = self.generate_meta_data(source_element, root)
            for i in range(len(all_tables)):
                all_description_tags = list(all_tables[i].iter(dita_c.DESC_TAG))
                root_element = Element(dita_c.PDG_TAG)
                if len(all_description_tags) > 0:
                    root_element = self.update_root_element(root_element, all_description_tags)
                    headers = self.get_headers_2(all_tables[i])
                    row_content = self.get_entries(all_tables[i])
                    processed_element = self.map_row_to_element_with_desc(root_element, headers, row_content)
                else:
                    headers = self.get_headers_2(all_tables[i])
                    row_content = self.get_entries(all_tables[i])
                    processed_element = self.map_row_to_element(root_element, headers, row_content)

                for element in processed_element:
                    source_element.append(element)
            if decouple_element is not None:
                source_element = self.decouple_property(decouple_element, source_element, new_name)
            return source_element
        else:
            msg = "Invalid XML tag found or some XML tags cannot be processed by E-datasheet "
            raise ExceptionLogger.logError(__name__, msg)

    def process_xml_flat(self, file_name):
        tree = ET.parse(file_name)
        root = tree.getroot()
        check_xml = self.xml_validator.check_for_valid_xml(root)
        listing = []
        if check_xml is True:
            all_tables = list(root.iter(dita_c.TABLE_TAG))
            source_element = Element(dita_c.DATASHEET_TAG)
            source_element = self.generate_meta_data(source_element, root)
            for i in range(len(all_tables)):
                all_description_tags = list(all_tables[i].iter(dita_c.DESC_TAG))
                if len(all_description_tags) > 0:
                    desc_base = self.get_description_tag_content(all_description_tags)
                    headers = self.get_headers_2(all_tables[i])
                    row_content = self.get_entries(all_tables[i])
                    flattened_dictionary = self.get_flattened_base(desc_base, headers, row_content)
                    for data in flattened_dictionary:
                        listing.extend(self.parse_pdg_entry(data))
            all_pdgs = []
            for entry in listing:
                pdg_element = Element(dita_c.PDG_TAG)
                for key in entry:
                    new_element = Element(key)
                    new_element.text = entry[key]
                    pdg_element.append(new_element)
                all_pdgs.append(pdg_element)
            for element in all_pdgs:
                source_element.append(element)
            return source_element

    def parse_pdg_entry(self, entry):
        baserow = {}
        splits = []
        rule = []
        for k, v in entry.items():
            if k in datasheet_c.DATASHEET_KNOWN_RULES:
                rule.append((k, v))
            elif isinstance(v, list):
                splits.append((k, v))
            else:
                baserow[k] = v
        rows = []
        for rule_name, rule_value in rule:
            baserow["ruleName"] = rule_name
            if isinstance(rule_value, dict):
                baserow[datasheet_c.DATASHEET_RULE_VALUE] = rule_value[dita_c.VALUE_CREATOR]
                baserow[datasheet_c.DATASHEET_RULE_UNIT] = rule_value[dita_c.UNIT_IDENTIFIER]
            else:
                baserow[datasheet_c.DATASHEET_RULE_VALUE] = rule_value
        self.update_rows(baserow, splits, rows)
        return rows

    def update_rows(self, baserow: dict, splits: list, rows: list):
        row = baserow.copy()
        while (len(splits)) != 0:
            key_name, values = splits[0]
            for val in values:
                row[key_name] = val
                self.update_rows(row, splits[1:], rows)
            return
        rows.append(row)

    def get_new_base(self, desc_base, headers, row_content):
        new_base = desc_base.copy()
        key_check = [x.replace(" ", "").lower() for x in datasheet_c.DATASHEET_SIGNALS]
        for j in range(len(headers)):
            string_key = 'col' + str(j + 1)
            if headers[string_key][dita_c.LABEL_HEADER] not in datasheet_c.DATASHEET_RULES_LIST and headers[string_key][dita_c.LABEL_HEADER].lower() not in key_check:
                if (",") in row_content[j]:
                    new_base[headers[string_key][dita_c.LABEL_HEADER]] = row_content[j].split(',')
                elif ("/") in row_content[j]:
                    new_base[headers[string_key][dita_c.LABEL_HEADER]] = row_content[j].split('/')
                else:
                    new_base[headers[string_key][dita_c.LABEL_HEADER]] = row_content[j]
        new_base = {datasheet_c.DATASHEET_SIGNAL_TYPE if k == datasheet_c.DATASHEET_SIGNAL_NAME else k: v for k, v in new_base.items()}

        return new_base

    def get_flattened_base(self, desc_base, headers, row_contents):
        all_entries = []
        key_check = [x.replace(" ", "").lower() for x in datasheet_c.DATASHEET_SIGNALS]
        for i in range(len(row_contents)):
            new_base = self.get_new_base(desc_base, headers, row_contents[i + 1])
            for j in range(len(headers)):
                string_key = 'col' + str(j + 1)
                if headers[string_key][dita_c.LABEL_HEADER] in datasheet_c.DATASHEET_RULES_LIST:
                    replica_base = new_base.copy()
                    if (headers[string_key][dita_c.LABEL_HEADER] == datasheet_c.DATASHEET_A_SE or headers[string_key][dita_c.LABEL_HEADER] == datasheet_c.DATASHEET_A_DIFF) and not row_contents[i + 1][j].isspace():
                        replica_base[datasheet_c.DATASHEET_RULE_NAME] = datasheet_c.DATASHEET_RULES_LIST_MAPPING[headers[string_key][dita_c.LABEL_HEADER]]
                        replica_base[datasheet_c.DATASHEET_RULE_VALUE] = row_contents[i + 1][j]
                        if dita_c.UNIT_IDENTIFIER in headers[string_key]:
                            replica_base[datasheet_c.DATASHEET_RULE_UNIT] = headers[string_key][dita_c.UNIT_IDENTIFIER]
                        replica_base[datasheet_c.DATASHEET_INTERFACE_TYPE] = datasheet_c.DATASHEET_MEMORY
                        all_entries.append(replica_base)
                    elif (headers[string_key][dita_c.LABEL_HEADER] == datasheet_c.DATASHEET_A_SE or headers[string_key][dita_c.LABEL_HEADER] == datasheet_c.DATASHEET_A_DIFF) and row_contents[i + 1][j].isspace():
                        pass
                    elif (headers[string_key][dita_c.LABEL_HEADER] == datasheet_c.DATASHEET_Z_DIFF_DEFAULT or headers[string_key][dita_c.LABEL_HEADER] == datasheet_c.DATASHEET_Z_SE_DEFAULT) and not row_contents[i + 1][j].isspace():
                        replica_base[datasheet_c.DATASHEET_RULE_NAME] = datasheet_c.DATASHEET_RULES_LIST_MAPPING[headers[string_key][dita_c.LABEL_HEADER]]
                        replica_base[datasheet_c.DATASHEET_RULE_VALUE] = row_contents[i + 1][j]
                        if dita_c.UNIT_IDENTIFIER in headers[string_key]:
                            replica_base[datasheet_c.DATASHEET_RULE_UNIT] = headers[string_key][dita_c.UNIT_IDENTIFIER]
                        replica_base[datasheet_c.DATASHEET_INTERFACE_TYPE] = datasheet_c.DATASHEET_MEMORY
                        all_entries.append(replica_base)
                    elif (headers[string_key][dita_c.LABEL_HEADER] == datasheet_c.DATASHEET_Z_DIFF_DEFAULT or headers[string_key][dita_c.LABEL_HEADER] == datasheet_c.DATASHEET_Z_SE_DEFAULT) and row_contents[i + 1][j].isspace():
                        pass
                    elif (headers[string_key][dita_c.LABEL_HEADER] == datasheet_c.DATASHEET_INTRA_PAIR) and row_contents[i + 1][j].isspace():
                        pass
                    else:
                        replica_base[datasheet_c.DATASHEET_RULE_NAME] = datasheet_c.DATASHEET_RULES_LIST_MAPPING[headers[string_key][dita_c.LABEL_HEADER]]
                        replica_base[datasheet_c.DATASHEET_RULE_VALUE] = row_contents[i + 1][j]
                        if dita_c.UNIT_IDENTIFIER in headers[string_key]:
                            replica_base[datasheet_c.DATASHEET_RULE_UNIT] = headers[string_key][dita_c.UNIT_IDENTIFIER]
                        replica_base[datasheet_c.DATASHEET_INTERFACE_TYPE] = datasheet_c.DATASHEET_MEMORY
                        all_entries.append(replica_base)
                elif headers[string_key][dita_c.LABEL_HEADER].lower() in key_check:
                    replica_base = new_base.copy()
                    if datasheet_c.DATASHEET_SIGNAL_NAME in replica_base:
                        del replica_base[datasheet_c.DATASHEET_SIGNAL_NAME]
                    if headers[string_key][dita_c.LABEL_HEADER][0].lower() != datasheet_c.DATASHEET_K_VALUE_NAME:
                        parts = headers[string_key][dita_c.LABEL_HEADER].split('To')
                        parts.sort()
                        signal2signal = f"{parts[0].upper()}-{parts[1].upper()}"
                        replica_base[datasheet_c.DATASHEET_SIGNALS_NAME] = signal2signal
                        replica_base[datasheet_c.DATASHEET_RULE_NAME] = datasheet_c.DATASHEET_TRACE_SPACING_NAME
                        replica_base[datasheet_c.DATASHEET_RULE_VALUE] = row_contents[i + 1][j]
                        if dita_c.UNIT_IDENTIFIER in headers[string_key]:
                            replica_base[datasheet_c.DATASHEET_RULE_UNIT] = headers[string_key][dita_c.UNIT_IDENTIFIER]
                    elif headers[string_key][dita_c.LABEL_HEADER][0].lower() == datasheet_c.DATASHEET_K_VALUE_NAME:
                        parts = headers[string_key][dita_c.LABEL_HEADER][1:].split('To')
                        parts.sort()
                        signal2signal = f"{parts[0].upper()}-{parts[1].upper()}"
                        replica_base[datasheet_c.DATASHEET_SIGNALS_NAME] = signal2signal
                        replica_base[datasheet_c.DATASHEET_RULE_NAME] = datasheet_c.DATASHEET_K_VALUE_NAME
                        replica_base[datasheet_c.DATASHEET_RULE_VALUE] = row_contents[i + 1][j]
                        if dita_c.UNIT_IDENTIFIER in headers[string_key]:
                            replica_base[datasheet_c.DATASHEET_RULE_UNIT] = headers[string_key][dita_c.UNIT_IDENTIFIER]
                    replica_base[datasheet_c.DATASHEET_INTERFACE_TYPE] = datasheet_c.DATASHEET_MEMORY
                    all_entries.append(replica_base)
        return all_entries

    def get_description_tag_content(self, description_tags):
        all_desc_text = description_tags[0].text
        desc_dictionary = {}
        for item in all_desc_text.split(","):
            attributes = item.split(":")
            if len(attributes) > 1:
                name_item = attributes[0].strip()
                name_item = self.format.convert_to_camel_case(name_item)
                if name_item == datasheet_c.DATASHEET_CHANNELS_NAME:
                    channel_value = attributes[1].split('/')
                    desc_dictionary[name_item] = channel_value
                elif name_item.lower() == datasheet_c.DATASHEET_VARIANT:
                    desc_dictionary[name_item] = attributes[1]
                elif name_item.lower() == datasheet_c.DATASHEET_PCB_LAYER_COUNT:
                    desc_dictionary[name_item] = attributes[1].replace(" ", "")[0]
                elif name_item.lower() == datasheet_c.DATASHEET_TOPOLOGY and attributes[1].replace(" ", "").startswith('LPD'):
                    desc_dictionary[name_item] = attributes[1][9:]
                    desc_dictionary[datasheet_c.DATASHEET_INTERFACE] = attributes[1][0:9].replace(" ", "")
                else:
                    desc_dictionary[name_item] = attributes[1].replace(" ", "")
        return desc_dictionary

    def write_to_xml(self, source_element):
        """
        Write element to XML file

        Args:
        source_element (Element) : Element to write to XML

        """
        b_xml = ET.tostring(source_element)
        with open("output.xml", "wb") as f:
            f.write(b_xml)

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
            output_file_name = str(path.parent) + "/" + path.stem + ".json"
        xmlstr = ElementTree.tostring(source_element).decode("utf-8")
        data_dict = xmltodict.parse(xmlstr)
        with open(output_file_name, "w", encoding="utf8") as output_json:
            json.dump(data_dict, output_json, indent=2, ensure_ascii=False)
        self.generate_json_schema(output_file_name)

    def generate_json_schema(self, file_name):
        """
        Generate JSON schema

        Args:
        file_name (String) : File name for JSON schema
        """
        json_schema = JsonDataSheetSchema(file_name)
        json_schema.write()

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

    def update_root_element(self, root_element, all_description_tags):
        """
        Updates root element with information from description tags

        Args:
        root_element (Element) : Root element to add description tags to
        all_description_tags (Element) : Elements with description tags

        Returns:
        root_element (Element) : Root element with description information updated
        """
        all_desc_text = all_description_tags[0].text
        for item in all_desc_text.split(","):
            attributes = item.split(":")
            name_item = attributes[0].strip().replace(" ", "").lower()
            if name_item in self.header_keys:
                if name_item == datasheet_c.DATASHEET_CHANNELS_NAME:
                    channel_value = attributes[1].split('/')
                    if type(channel_value) is list:
                        for item in channel_value:
                            new_element = Element(name_item)
                            new_element.text = item
                            root_element.append(new_element)
                else:
                    new_element = Element(name_item)
                    new_element.text = attributes[1]
                    root_element.append(new_element)

        return root_element
