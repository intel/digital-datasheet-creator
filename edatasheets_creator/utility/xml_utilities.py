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
import os
from typing import List, Tuple
from xml.etree.ElementTree import Element  # nosec
import mimetypes

from defusedxml import ElementTree

""" Bandit ignore warning reason
Element is only used to create objects defined in the application code,
not from the input files. The parse functionality is also secured by
the implementation of defusedxml.Element tree.
"""
import xmltodict

import edatasheets_creator.constants.dita_constants as dita_c
import edatasheets_creator.constants.ditamap_constants as ditamap_c
import edatasheets_creator.constants.transformer_constants as transformer_constants
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.utility.format import Format


class XMLUtilities:
    """Contains Row Operation Utility Functions
    """
    NAMESPACE_FIELD_NAME = "namespace"
    TARGET_NAMESPACE = "https://www.intel.com/design"

    def __init__(self) -> None:
        self.format = Format()

    def is_eds_register_file(self, source: Element) -> bool:
        """Determines if the source Element is a EDS Register file.

        Args:
            source (Element): Element to Determine.

        Returns:
            bool
        """
        is_eds = False
        registerFileElements = list(source.iter(dita_c.REGISTERFILE_TAG))
        is_eds = len(registerFileElements) != 0
        return is_eds

    def build_attachments(self, root_element: Element, source: Element) -> Element:
        """Get the list of images from the source, in a XML Element to include it in the
        general table Element.

        Args:
            root_element (Element): main document with the tables to convert.
            source (Element): Element with image tags.

        Returns:
            Element: Output Element with the list of images in the source, if doesn't have
            image tags returns an empty Element.
        """
        try:
            figures = self.get_figures(source)

            for figure in figures:
                figure_title = self.get_title(figure)
                if figure_title == transformer_constants.UNKNOWN:
                    figure_title = figure.attrib.get(transformer_constants.ID_ATTRIBUTE, transformer_constants.UNKNOWN)
                figure_image = self.get_image(figure)
                if figure_image is not None:
                    image_href = self.get_image_href(figure_image)
                    file_name, extension = os.path.splitext(image_href)
                    # Parent
                    attachment_element = Element(transformer_constants.ATTACHMENTS)
                    # Attributes of Attachment
                    reference_element = Element(transformer_constants.ATTACHMENT_REFERENCE)
                    reference_element.text = file_name
                    attachment_element.append(reference_element)
                    mimetype_element = Element(transformer_constants.ATTACHMENT_TYPE)
                    mimetype = mimetypes.guess_type(image_href)[0]
                    mimetype_element.text = mimetype
                    attachment_element.append(mimetype_element)
                    name_element = Element(transformer_constants.ATTACHMENT_NAME)
                    name_element.text = f'{figure_title}{extension}'
                    attachment_element.append(name_element)
                    root_element.append(attachment_element)
            return root_element

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def has_elements(self, source: Element) -> bool:
        """Determines if the source Element has children.

        Args:
            source (Element): Element to determine.

        Returns:
            bool
        """
        elements = list(source.iter())
        return len(elements) > 1

    def has_table_element(self, source: Element) -> bool:
        """Determines if the source Element has table elements inside.

        Args:
            source (Element): Element to determine.

        Returns:
            bool
        """
        elements = list(source.iter(transformer_constants.TABLES_CONTAINER))
        return len(elements) > 1

    def get_images(self, source: Element) -> List[Element]:
        """Get the list of images (image tag) in a source.

        Args:
            source (Element): Element to get the images.

        Returns:
            List[Element]: List of image Elements from the source.
        """
        return list(source.iter(dita_c.IMAGE_TAG))

    def get_image(self, source: Element) -> Element:
        """Get the first image inside of figure or Element (image tag) in a source.

        Args:
            source (Element): Element to get the image.

        Returns:
            Element: Image element from the source.
        """
        images = list(source.iter(dita_c.IMAGE_TAG))
        return images[0] if images else None

    def get_figures(self, source: Element) -> List[Element]:
        """Get the list of figures (fig tag) in a source.

        Args:
            source (Element): Element to get the figures.

        Returns:
            List[Element]: List of figures Elements from the source.
        """
        return list(source.iter(dita_c.FIG_TAG))

    def get_image_href(self, source: Element) -> str:
        """Returns the href attribute from the source Element.

        Args:
            source (Element): Element to get the attribute.

        Returns:
            str: Href attribute value
        """
        return source.attrib.get(dita_c.HREF_ATTRIBUTE, None)

    def get_attributes_from_dita(self, source: Element, file_name: str) -> dict:
        """Gets the title, id and file name from the provided input file.

        Args:
            source (Element): Element to get the attributes.
            file_name (str): File name of the provided source.

        Returns:
            dict: output metadata.
        """
        try:
            main_id = source.attrib.get("id", "")
            tables_metadata = []
            tables = self.get_tables(source)
            for table in tables:
                table_metadata = {
                    "fileName": file_name,
                    "id": table.attrib.get("id", ""),
                    "title": self.get_title(table)
                }
                tables_metadata.append(table_metadata)
            return {main_id: tables_metadata}

        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def get_namespace(self, file_name: str) -> str:
        """Returns the namespace for a document

        Args:
            file_name (str): Input file name

        Returns:
            str: namespace string
        """
        try:
            namespace: str = ""

            namespaces = {node[0]: node[1] for _, node in ElementTree.iterparse(file_name, events=['start-ns'])}

            if namespaces:
                namespace = list(namespaces.values())[0]
                if namespace is None:
                    namespace = self.TARGET_NAMESPACE
            else:
                namespace = self.TARGET_NAMESPACE

            return namespace

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
            
    def get_text_from_tag(self, source: Element, tag: str) -> str:
        """Get title text from Element using a tag.

        Args:
            source (Element): Element that contains text.
            tag (str): Tag name of the element to search.

        Returns:
            str: Content of text in the tag.
        """
        text = None
        if source:
            matched_tags = list(source.iter(tag))
            text = self.get_text(matched_tags[0]) if matched_tags else text
        return text

    def get_title(self, source: Element) -> str:
        """Get title text from Element

        Args:
            source (Element): Element tag that needs to has a title tag to be returned.

        Returns:
            str: Content of the title tag
        """
        title = "Unknown"
        if source:
            matched_tags = list(source.iter(dita_c.TITLE_TAG))
            title = self.get_text(matched_tags[0]) if matched_tags else title

        return title

    def get_desc(self, source: Element) -> str:
        """Get desc text from Element

        Args:
            source (Element): Element tag that needs to has a desc tag to be returned.
        Returns:
            str: Content of the desc tag
        """
        desc = "Unknown"
        if source:
            matched_tags = list(source.iter(dita_c.DESC_TAG))
            desc = self.get_text(matched_tags[0]) if matched_tags else desc

        return desc

    def get_element_by_tag(self, source: Element, tag: str) -> Element:
        """Returns the first Element using the given tag name.

        Args:
            source (Element): Element to get the tag.
            tag (str): tag name.

        Returns:
            Element: Filtered Element, if not exists returns None.
        """
        try:
            if source:
                matched_tags = list(source.iter(tag))
                match = matched_tags[0] if matched_tags else None
                return match
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def get_first_platform_name(self, source: Element) -> str:
        """Looks through all elements and gets a list of elements that have an attribute matching "platform".
           This method assumes that docs will not mix multiple platforms.
           Returns the first platform name

        Args:
            source (Element): Document Element

        Returns:
            str: platform name
        """
        platform = "Unknown"
        if source:
            matched_tags = list(source.iter(dita_c.PLATFORM_TAG))
            platform = self.get_text(matched_tags[0]) if matched_tags else platform

        return platform

    def get_tables(self, source: Element) -> List[Element]:
        """Returns a list of table elements

        Args:
            source (Element)

        Returns:
            List[Element]: Table elements list
        """
        return list(source.iter(dita_c.TABLE_TAG))

    def get_topicref(self, source: Element) -> List[Element]:
        """Returns a list of topicref elements

        Args:
            source (Element)

        Returns:
            List[Element]: Topicref elements list
        """
        return list(source.find(ditamap_c.TOPIC_REF_TAG))

    def get_navtitle_from_meta(self, source: Element) -> str:
        """Returns the navtitle from a topicmeta.

        Args:
            source (Element): topicref with a topic meta inside.

        Returns:
            str: navtitle.
        """
        try:
            nav_title = None
            topic_meta = self.get_element_by_tag(source, ditamap_c.TOPIC_META_TAG)
            if topic_meta:
                nav_title = self.get_text_from_tag(topic_meta, ditamap_c.NAV_TITLE_TAG)
            return nav_title
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def get_navtitle(self, source: Element) -> str:
        """Returns the navtitle from a topicref, first check if is part of the attributes,
        if not exists, check the topicmeta for the navtitle.

        Args:
            source (Element): topicref Element.

        Returns:
            str: navtitle of the topicref.
        """
        try:
            if source.tag == ditamap_c.TOPIC_REF_TAG:
                nav_title = source.attrib.get(ditamap_c.NAV_TITLE_ATTRIBUTE)
                if not nav_title:
                    nav_title = self.get_navtitle_from_meta(source)
                return nav_title
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def get_sections(self, source: Element) -> List[Element]:
        """Returns a list of section elements

        Args:
            source (Element)

        Returns:
            List[Element]: Section elements list
        """
        return list(source.iter(dita_c.SECTION_TAG))

    def get_entries(self, source: Element) -> List[Element]:
        """Get the entry list from the source.

        Args:
            source (Element): Element with entry tags.

        Returns:
            List[Element]: List of Element entries.
        """
        return list(source.iter(dita_c.ENTRY_TAG))

    def get_target_namespace(self) -> str:
        """Returns the target namespace defined in the constant

        Returns:
            str: target namespace constant
        """
        return self.TARGET_NAMESPACE

    def is_orientation_vertical(self, source: Element) -> bool:
        """Pass a THEAD and if the headings have attributes that include "outputclass=rotate90"
        then this is a vertically oriented table.

        Args:
            source (Element)

        Returns:
            bool
        """
        entries = list(source.iter(dita_c.ENTRY_TAG))
        for entry in entries:
            attributes = entry.attrib
            if attributes.get(dita_c.OUTPUTCLASS_ATTRIBUTE, None):
                return True
        return False

    def get_row_body_elements(self, source: Element) -> List[Element]:
        """Returns row elements from a table element

        Args:
            source (Element)

        Returns:
            List[Element]: Row body elements list
        """
        rows = list(source.findall("tgroup/tbody/row"))
        return rows

    def get_table_headers(self, source: Element):
        """Get the rows list from the source using the path 'tgroup/thead/row' to find them.

        Args:
            source (Element): Element with row tags.

        Returns:
            List[Element]: List of Element rows.
        """
        rows = list(source.findall("tgroup/thead/row"))
        return rows

    def get_rows(self, source: Element) -> List[Element]:
        """Returns list of rows for a table

        Args:
            source (Element)

        Returns:
            List[Element]: List of rows
        """
        return list(source.iter(dita_c.ROW_TAG))

    def get_p_list(self, source: Element):
        """Get the p list from the source.

        Args:
            source (Element): Element with p tags.

        Returns:
            List[Element]: List of Element p.
        """
        return list(source.iter(dita_c.P_TAG))

    def get_p_text(self, source: Element) -> str:
        """Get the text inside an entry.

        Args:
            source (Element): Element with p tags, to get the text inside it.

        Returns:
            str: Text inside the Element.
        """
        return source.findtext(dita_c.P_TAG)

    def get_column_name_string_from_dictionary_range(self, source: Element, dictionary: dict):
        """Get the colname from the range in the attribute list, this applies for the namest and namend.

        Args:
            source (Element): Entry element to get the colname attribute (namest and nameend).
            dictionary (dict): column_header_keys with the headers name of the table.

        Returns:
            _type_: column name in the range
        """
        col_name = ""
        col_range: List[int] = []
        col_names_list: List[tuple] = self.get_column_name_attribute_list(source)
        for _, value in col_names_list:
            data = re.match(r"\d+", value)
            col_num = int(data)
            col_range.append(col_num)
        col_range.sort()
        if len(col_range) > 1:
            for i in range(col_range[0], col_range[1] + 1):
                col = "col" + str(i)
                col_name += dictionary[col].get(dita_c.LABEL_HEADER, "") + " "
        col_name = col_name.strip()
        col_name = col_name.replace(" ", "-")
        return col_name

    def get_column_name_from_dictionary_by_key(self, key: str, dictionary: dict) -> str:
        """Returns the column header name using the provided key, and the global dictionary.

        Args:
            key (str): key of the column.
            dictionary (dict): column_header_keys with the headers name of the table.

        Returns:
            str: column name
        """
        try:
            column_name = None
            column_unit = None

            if key in dictionary:
                column_name = dictionary[key].get(dita_c.LABEL_HEADER)
                column_unit = dictionary[key].get(dita_c.UNIT_HEADER)
            else:
                match = re.findall("(\d)+", key)
                if match:
                    pos = int(match[0]) - 1
                    item = self.get_column_header_key_from_ordinal_pos(dictionary, pos)
                    column_name = dictionary[item].get(dita_c.LABEL_HEADER, None)
                    column_unit = dictionary[item].get(dita_c.UNIT_HEADER, None)
                    if column_name and len(column_name) < 1:
                        msg = f"get_column_name_from_dictionary_by_key:  Could not find value for key {key}"
                        ExceptionLogger.logError(__name__, msg)
                else:
                    msg = f"get_column_name_from_dictionary_by_key:  Could not find value for key {key}"
                    ExceptionLogger.logError(__name__, msg)
                    raise Exception(msg)
            return column_name, column_unit

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
            raise e

    def get_column_header_key_from_ordinal_pos(self, dictionary: dict, position: int) -> str:
        """Returns the column header key from the dictionary, using the index value.

        Args:
            dictionary (dict): column_header_keys with the headers name of the table.
            position (int): index of the column

        Returns:
            str: column name
        """
        found_key = None
        try:
            for key, value in dictionary.items():
                if value[dita_c.COL_NUM] == str(position):
                    found_key = key
                    break

            return found_key

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def get_column_index(self, source: Element) -> List[str]:
        """Get the list of column index from an entry Element, if the entry has no the colname attribute,
        check for the namest and namest attributes and include all the colnames based on these range.

        Args:
            source (Element): Element with an entry tag.

        Returns:
            List[str]: list of column index values.
        """
        try:
            element_key: List[str] = []
            if source.tag == dita_c.ROW_TAG:
                source = source.find(dita_c.ENTRY_TAG)

            source_attributes = source.attrib

            colname_attribute = source_attributes.get(dita_c.COLNAME, None)

            if not colname_attribute:
                column_start_key = source_attributes.get(dita_c.NAMEST, None)
                if column_start_key:
                    column_end_key = source_attributes.get(dita_c.NAMEEND, None)
                    if column_end_key and (len(column_start_key) < 4 or len(column_end_key) < 4):
                        msg = f"Unexpected String {ElementTree.tostring(source, encoding='unicode')}"
                        ExceptionLogger.logError(__name__, msg)
                        element_key.append(transformer_constants.FAILED)
                        return element_key

                    start_index = int(column_start_key[3:])
                    end_index = int(column_end_key[3:])

                    for i in range(start_index, end_index + 1):
                        element_key.append("col" + str(i))
            else:
                element_key.append(colname_attribute)

            return element_key

        except Exception as e:
            raise ExceptionLogger.logError(__name__, "", e)

    def get_text(self, source: Element) -> str:
        """Gets the concatenated text contents of this element.

        Args:
            source (Element): Element with the text.

        Returns:
            str: A string that contains all of the text content of this element. If there are multiple text nodes,
            they will be concatenated.
        """
        try:
            concatenated_string = ""
            concatenated_string = ElementTree.tostring(source, 'unicode', 'text').strip()

            return concatenated_string

        except Exception as e:
            raise ExceptionLogger.logError(__name__, "", e)

    def element_to_string(self, source: Element) -> str:
        """Convert an element to a string.

        Args:
            source (Element): Element to be converted.

        Returns:
            str: Converted element.
        """
        xmlstr = ElementTree.tostring(source, encoding='utf8', method='xml')
        return xmlstr

    def get_column_name_from_dictionary(self, source: Element, dictionary: dict) -> Tuple[str, str]:
        """Get the header name and if applies the unit for the value.

        Args:
            source (Element): entry Element to find his column header name.
            dictionary (dict): column_header_keys with the headers name of the table.

        Returns:
            Tuple[str, str]: column name and column unit
        """
        column_name = None
        column_unit = None
        if source.tag == dita_c.ROW_TAG:
            entries = self.get_entries(source)
            if entries:
                source = entries[0]
        if (not source.attrib.get(dita_c.COLNAME, None)):
            if source.attrib.get(dita_c.NAMEST):
                start_key = source.attrib.get(dita_c.NAMEST, "").strip()
                end_key = source.attrib.get(dita_c.NAMEEND, "").strip()
                start_value = dictionary[start_key].get(dita_c.LABEL_HEADER, "")
                end_value = dictionary[end_key].get(dita_c.LABEL_HEADER, "")
                column_name = str(start_value) + "-" + str(end_value)
            else:
                msg = f"Could not find column key for element {self.element_to_string(source)}"
                ExceptionLogger.logError(__name__, msg)
        else:
            element_key = source.attrib.get(dita_c.COLNAME, "").strip()
            column_name = dictionary[element_key].get(dita_c.LABEL_HEADER, None)
            column_unit = dictionary[element_key].get(dita_c.UNIT_HEADER, None)
        return column_name, column_unit

    def get_column_name_attribute_list(self, source: Element) -> List[Tuple[str, str]]:
        """Get the colname attribute key and value from the source, if it doesn't have
        colname, check for the namest and nameend and include the key and value for these attributes.

        Args:
            source (Element): Entry element to get the attributes.

        Returns:
            List[Tuple[str, str]]: List with the attributes from the entry source.
        """
        attribute_list: List[tuple] = []
        attributes = source.attrib
        if not attributes.get(dita_c.COLNAME, None):
            namest_value = attributes.get(dita_c.NAMEST, None)
            nameend_value = attributes.get(dita_c.NAMEEND, None)
            if namest_value:
                attribute_list.append((dita_c.NAMEST, namest_value))
                if nameend_value:
                    attribute_list.append((dita_c.NAMEEND, nameend_value))
            else:
                msg = "Could not found column key"
                ExceptionLogger.logError(__name__, msg)
        else:
            attribute_list.append((dita_c.COLNAME, attributes.get(dita_c.COLNAME, "").strip()))
        return attribute_list

    def xml_to_dictionary(self, source: Element, individual_tables_name: tuple = ()) -> dict:
        """Transform XML Element to dictionary using xmltodict library

        Args:
            source (Element): Root element

        Returns:
            dict: Converted XML
        """
        try:
            xmlstr = ElementTree.tostring(source, method='xml', short_empty_elements=False)
            data_dict = xmltodict.parse(xmlstr, force_list=individual_tables_name)
            return data_dict
        except Exception as e:
            raise ExceptionLogger.logError(__name__, "", e)
