import defusedxml.ElementTree as ET
from xml.etree.ElementTree import Element  # nosec
""" Bandit ignore warning reason
Element is only used to create objects defined in the application code,
not from the input files. The parse functionality is also secured by
the implementation of defusedxml.Element tree.
"""
import xmltodict
import json
from defusedxml import ElementTree
from edatasheets_creator.utility.collateral_utilities import CollateralUtilities
from edatasheets_creator.utility.datasheet_utilities import DataSheetUtilities
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.utility.format import Format
from edatasheets_creator.utility.xml_utilities import XMLUtilities
from edatasheets_creator.utility.xml_validator import XMLValidator
import edatasheets_creator.constants.dita_constants as dita_c


class DataTablePDGDCAI:
    def __init__(self, file_name, output_file_name):
        """
        Initialize parameters for class
        """
        self.file_name: str = file_name
        self.output_file_name: str = output_file_name
        self.column_header_keys: dict[str, dict] = {}
        self.xml_utilities = XMLUtilities()
        self.xml_validator = XMLValidator()
        self.datasheet_utilities = DataSheetUtilities(file_name, output_file_name)
        self.collateral_utilities = CollateralUtilities()
        self.format = Format()

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
        output_element = self.process_xml(file_name)
        self.write_to_xml(output_element)
        self.datasheet_utilities.write_to_json(output_element)

    def process_xml(self, file_name):
        tree = ET.parse(file_name)
        root = tree.getroot()
        source_element = Element(dita_c.DATASHEET_TAG)
        source_element = self.datasheet_utilities.generate_meta_data(source_element, root)
        check_body = list(root.iter('body'))
        check_conbody = list(root.iter('conbody'))
        check_glossdef = list(root.iter('glossdef'))
        if len(check_body) > 0:
            all_sections = list(root.iter('section'))
            if len(all_sections) != 0:
                for section in all_sections:
                    title = list(section.iterfind('title'))
                    if len(title) > 0:
                        title_text = title[0].text.replace(" ", "_")
                        title_text = title_text.replace("[", "_")
                        title_text = title_text.replace(":", "_")
                        section_element = Element(title[0].text.replace(" ", "_"))
                    else:
                        section_element = Element('section')
                    section_element = self.process_section(section, section_element)
                    source_element.append(section_element)
        elif len(check_conbody) > 0:
            all_sections = list(root.iter('section'))
            if len(all_sections) > 0:
                for section in all_sections:
                    title = list(section.iterfind('title'))
                    if len(title) > 0:
                        section_element = Element(title[0].text.replace(" ", "_"))
                    else:
                        section_element = Element('section')
                    section_element = self.process_section(section, section_element)
                    source_element.append(section_element)
            else:
                section_element = Element('section')
                processed_section_element = self.process_conbody(check_conbody, section_element)
                source_element.append(processed_section_element)
        elif len(check_glossdef) > 0:
            all_sections = list(root.iter('section'))
            if len(all_sections) > 0:
                for section in all_sections:
                    title = list(section.iterfind('title'))
                    if len(title) > 0:
                        section_element = Element(title[0].text.replace(" ", "_"))
                    else:
                        section_element = Element('section')
                    section_element = self.process_section(section, section_element)
                    source_element.append(section_element)
            else:
                section_element = Element('section')
                processed_section_element = self.process_glossdef(check_glossdef, section_element)
                all_glossBody = list(root.iterfind('glossBody'))
                if len(all_glossBody) > 0:
                    section_element = self.datasheet_utilities.process_gloss_body(all_glossBody, processed_section_element)
                source_element.append(processed_section_element)
        return source_element

    def process_glossdef(self, check_glossdef, section_element):
        all_ph = list(check_glossdef[0].iterfind('ph'))
        section_element = self.datasheet_utilities.process_ph(all_ph, section_element)
        return section_element

    def process_conbody(self, check_conbody, section_element):
        all_p = list(check_conbody[0].iterfind('p'))
        if len(all_p) > 0:
            section_element = self.datasheet_utilities.process_p(all_p, section_element)
        all_ul = list(check_conbody[0].iterfind('ul'))
        if len(all_ul) > 0:
            section_element = self.datasheet_utilities.process_ul(all_ul, section_element)
        all_fig = list(check_conbody[0].iterfind('fig'))
        if len(all_fig) > 0:
            fig_element = self.datasheet_utilities.process_fig(all_fig)
            section_element.append(fig_element)
        all_tables = list(check_conbody[0].iterfind('table'))
        all_notes = list(check_conbody[0].iterfind('note'))
        section_element = self.datasheet_utilities.build_table_with_notes(all_tables, all_notes, section_element)

        return section_element

    def process_section(self, current_section_element, new_section_element):
        all_p = list(current_section_element.iterfind('p'))
        if len(all_p) > 0:
            new_section_element = self.datasheet_utilities.process_p(all_p, new_section_element)
        all_ul = list(current_section_element.iterfind('ul'))
        if len(all_ul) > 0:
            new_section_element = self.datasheet_utilities.process_ul(all_ul, new_section_element)
        all_fig = list(current_section_element.iterfind('fig'))
        if len(all_fig) > 0:
            fig_element = self.datasheet_utilities.process_fig(all_fig)
            new_section_element.append(fig_element)
        all_tables = list(current_section_element.iterfind('table'))
        all_notes = list(current_section_element.iterfind('note'))
        new_section_element = self.datasheet_utilities.build_table_with_notes(all_tables, all_notes, new_section_element)
        return new_section_element

    def write_to_xml(self, source_element):
        b_xml = ET.tostring(source_element)
        with open("GFG_2.xml", "wb") as f:
            f.write(b_xml)

    def write_to_json(self, source_element):
        xmlstr = ElementTree.tostring(source_element).decode("utf-8")
        data_dict = xmltodict.parse(xmlstr)
        with open('test_2.json', "w", encoding="utf8") as output_json:
            json.dump(data_dict, output_json, indent=2, ensure_ascii=False)
