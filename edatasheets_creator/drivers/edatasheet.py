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

from uuid import uuid4
from edatasheets_creator.drivers.field_replacement import FieldReplacement
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
import edatasheets_creator.constants.header_constants as header_constants
import edatasheets_creator.constants.transformer_constants as transformer_constants
from edatasheets_creator.schemas.edatasheet import EDatasheetEntity
from edatasheets_creator.utility.collateral_utilities import CollateralUtilities
from edatasheets_creator.utility.time_utilities import get_current_utc_datetime


class EDatasheet:
    TARGET_NAMESPACE = "https://www.intel.com/design"
    DATASHEET_SCHEMA = EDatasheetEntity

    def __init__(self, title: str, file_name: str):
        self.collateral_utilities = CollateralUtilities()
        self.field_replacement = FieldReplacement()
        self.edatasheet: dict = {}
        self.namespace = self.TARGET_NAMESPACE
        self.title = title
        self.file_name = file_name

    def __generate_headers(self) -> dict:
        """Returns the headers for the current edatasheet

        Returns:
            dict: Headers content
        """
        try:
            generated_on = get_current_utc_datetime()
            guid = self.collateral_utilities.get_first_guid_from_string(self.file_name)

            headers = {
                header_constants.NAMESPACE: self.namespace,
                header_constants.TITLE: self.title.strip(),
                header_constants.INPUT_FILE: self.file_name,
                header_constants.GENERATED_ON: generated_on,
                header_constants.GENERATED_BY: transformer_constants.GENERATED_BY,
                header_constants.PLATFORM_ABBREVIATION: transformer_constants.UNKNOWN,
                header_constants.SKU: transformer_constants.UNKNOWN,
                header_constants.COLLATERAL: transformer_constants.UNKNOWN,
                header_constants.REVISION: transformer_constants.UNKNOWN
            }
            if guid:
                headers[header_constants.GUID] = guid
            else:
                headers[header_constants.GUID] = str(uuid4())

            return headers

        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def get_edatasheet(self, additional_content: dict) -> dict:
        """Generates an edatasheet using the given content and getting the headers for this.

        Args:
            additional_content (dict): Any other content to include inside the output.

        Returns:
            dict: Edatasheet
        """
        try:
            headers = self.__generate_headers()
            self.edatasheet.update(headers)
            content_edatasheet = additional_content.get(header_constants.DATASHEET)

            if content_edatasheet:
                self.edatasheet.update(content_edatasheet)
            else:
                self.edatasheet.update(additional_content)

            return {header_constants.DATASHEET: self.edatasheet}

        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def get_edatasheet_with_mapper(self, additional_content: dict, mapper: dict) -> dict:
        """Generates an edatasheet using the given content and getting the headers for this.

        Args:
            additional_content (dict): Any other content to include inside the output.
            fixup_mapper (dict): Fixup mapper to replace content in the edatasheet.

        Returns:
            dict: EDatasheet
        """
        try:
            edatasheet = self.get_edatasheet(additional_content)
            self.field_replacement.replace_fields_and_values(edatasheet, mapper)
            return edatasheet
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)
