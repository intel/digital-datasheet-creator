from pathlib import Path
from typing import List
from edatasheets_creator.utility.collateral_utilities import CollateralUtilities
from edatasheets_creator.utility.xml_utilities import XMLUtilities
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from xml.etree.ElementTree import Element  # nosec
from edatasheets_creator.utility.time_utilities import get_current_utc_datetime
import edatasheets_creator.constants.header_constants as header_constants
import edatasheets_creator.constants.ditamap_constants as ditamap_c
import edatasheets_creator.constants.transformer_constants as transformer_constants


class DitamapDriver:
    LIST_STRUCTURE_ENABLED = False

    def __init__(self) -> None:
        self.xml_utilities = XMLUtilities()
        self.collateral_utilities = CollateralUtilities()

    def get_hierarchy_file(self, root_element: Element, inputFileName: str) -> dict:
        """Method to return the hierarchy dictionary, that includes all the elements inside the ditamap.

        Args:
            root_element (Element): root element of the ditamap.
            inputFileName (str): input file name, to get some information from this.

        Returns:
            dict: hierarchy document from the ditamap.
        """
        try:
            target_namespace = self.xml_utilities.get_target_namespace()
            title = self.xml_utilities.get_title(root_element)
            generated_on = get_current_utc_datetime()

            datasheet_map = {
                self.xml_utilities.NAMESPACE_FIELD_NAME: target_namespace,
                header_constants.GENERATED_ON: generated_on,
                header_constants.TITLE: title.strip(),
                header_constants.INPUT_FILE: Path(inputFileName).name,
                header_constants.GENERATED_BY: transformer_constants.GENERATED_BY,
                header_constants.DOCUMENT_TYPE: ditamap_c.DOCUMENT_TYPE
            }

            root_id = root_element.attrib.get(ditamap_c.ID_ATTRIBUTE)
            hierarchy_list = []
            guid = self.collateral_utilities.get_first_guid_from_string(root_id)
            for child in root_element:
                if child.tag == ditamap_c.TOPIC_REF_TAG:
                    references = self.get_ref_from_element(child, guid, [])
                    hierarchy_list.append(references)

            parent_object = {
                ditamap_c.REFERENCE_KEY: root_id + ditamap_c.DITAMAP_EXT,
                ditamap_c.GUID_KEY: guid,
                ditamap_c.TITLE_KEY: title.strip(),
                ditamap_c.CHILDREN_KEY: hierarchy_list
            }

            datasheet_map[ditamap_c.TREE_KEY] = parent_object

            return datasheet_map
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def get_ref_from_element(self, topic_element: Element, parent: str, predecessors: List[str]) -> dict:
        """Method to get any nested topicref tag inside one, and return the last obj with all the references.

        Args:
            topic_ref (Element): Topic Ref Element, that contains the reference of the dita file.
            parent (str): Parent Element Id.
            predecessors (List[str]): List of predecessors for the current element.

        Returns:
            dict: object with references.
        """
        try:
            child_references = []
            root_reference: dict = self.get_reference(topic_element, parent, predecessors)
            root_ref = topic_element.attrib.get(ditamap_c.HREF_ATTRIBUTE)
            root_guid = self.collateral_utilities.get_first_guid_from_string(root_ref)
            if root_reference:
                for child in topic_element:
                    if child.tag == ditamap_c.TOPIC_REF_TAG:
                        nested_reference = self.get_ref_from_element(child, root_guid, [parent] + predecessors)
                        if nested_reference:
                            child_references.append(nested_reference)
            if child_references:
                root_reference[ditamap_c.CHILDREN_KEY] = child_references
            return root_reference
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def get_reference(self, topic_ref: Element, parent: str, predecessors: List[str]) -> dict:
        """Returns the reference with the format to be exported.

        Args:
            topic_ref (Element): Topic Ref Element, that contains the reference of the dita file.
            parent (str): Parent element of the reference.
            predecessors (List[str]): List of elements that is before the parent (in order).

        Returns:
            dict: reference object.
        """
        try:
            reference = {}
            format_attrib = topic_ref.attrib.get(ditamap_c.FORMAT_ATTRIBUTE)
            type_attrib = topic_ref.attrib.get(ditamap_c.TYPE_ATTRIBUTE)
            if type_attrib == ditamap_c.TOPIC_TYPE and format_attrib == ditamap_c.DITA_FORMAT:
                nav_title = self.xml_utilities.get_navtitle(topic_ref)
                ref = topic_ref.attrib.get(ditamap_c.HREF_ATTRIBUTE)
                guid = self.collateral_utilities.get_first_guid_from_string(ref)
                reference.update({
                    ditamap_c.REFERENCE_KEY: ref,
                    ditamap_c.GUID_KEY: guid,
                    ditamap_c.TITLE_KEY: nav_title
                })
                if self.LIST_STRUCTURE_ENABLED:
                    reference.update({
                        ditamap_c.PARENT_KEY: parent,
                        ditamap_c.PREDECESSORS_KEY: predecessors
                    })
            return reference
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)
