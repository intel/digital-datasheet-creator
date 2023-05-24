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
from edatasheets_creator.constants import serializationconstants
from edatasheets_creator.functions import t
from bs4 import BeautifulSoup as bs
import uuid
from edatasheets_creator.utility.format import Format
from edatasheets_creator.utility.time_utilities import get_current_utc_datetime
from edatasheets_creator.utility.path_utilities import validateRealPath

from edatasheets_creator.constants import htmlconstants


from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class Plugin:
    def __init__(self):
        return

    def __del__(self):
        return

    def process(self, html_file, output_filename, mapFile=""):
        """
        Plugin that converst an HTML file to JSON

        Args:
            html_file (PosixPath): Input file name
            output_filename (PosixPath): Output file name
            mapFile (str, optional): _description_. Defaults to "".
        """

        try:
            msg = "HTML Plugin is loaded...\n"
            ExceptionLogger.logInformation(__name__, msg)
            self._html_file = html_file
            self._output_path = output_filename
            self.formatter = Format()

            # All the devs that hold the tables
            wrapper_pages = []

            # Validate if the input files exists on the system as they are required
            if (not validateRealPath(self._html_file)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\n Input file does not exists"))
                print()
                return

            # Read the HTML input file
            with open(self._html_file) as fp:
                # Soup will be the html object to operate
                soup = bs(fp, 'html.parser')

                # Lets look for table wrappers in the HTML
                wrapper_pages = soup.find_all(class_=htmlconstants.HTML_TABLE_WRAPPER)

                fp.close()

            html_document_path = Path(html_file)
            html_file_name = html_document_path.stem
            complete_html_name = html_document_path.name

            # Parse the HTML objects retrieved
            parsed_JSON = self.__create_JSON(wrapper_pages, html_file_name, complete_html_name)

            # Write the json file parsed
            with open(self._output_path, "w", encoding='utf-8') as out:
                json.dump(parsed_JSON, out, ensure_ascii=False, indent=serializationconstants.JSON_INDENT_DEFAULT)
                out.close()

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def __create_JSON(self, wrappers_table: list[bs], file_name: str, complete_name: str) -> object:
        """
            Creates JSON dictionary form the html

        Args:
            wrappers_table (list[bs]): HTML wrapper objects extracted from the input
            file_name (str): file name with no extension
            complete_name (str): file name with no extension

        Returns:
            object: _description_
        """
        dictionary_to_fill = []
        file_descritpion = ""
        html_parsed_to_json = {}
        introduction_read = False
        try:
            # Check each wrapper as will be a new JSON object
            for wrapper in wrappers_table:
                # Check that the wrapper contains a table
                table = wrapper.find_all(htmlconstants.HTML_TABLE_TAG)
                table_content_len = len(table)

                # Process only wrappers that contain tables
                if (table_content_len > 0):
                    # validate type of table
                    type_of_table = self.__get_type_of_table(wrapper)

                    # get the header of the table
                    json_element_header = self.__get_table_header(wrapper, type_of_table)
                    table_name = json_element_header[0]

                    # get the columns of the table
                    table_column_headers = self.__get_columns_headers(wrapper)

                    # create list of objects with the headers retrieved
                    json_data = self.__get_table_data(table_column_headers, wrapper)

                    # create table entry
                    table_entry = ["", []]
                    table_entry[0] = self.formatter.format_html_name(table_name)
                    table_entry[1] = json_data
                    # '-Ia32_Monitor_Filter_Size-ÂOffset6'

                    # include into the list of objects
                    dictionary_to_fill.append(table_entry)

                elif (not introduction_read):
                    # This will handle the description of the file
                    paragraphs_in_introduction = wrapper.find_all(htmlconstants.HTML_PARAGRAPH_TAG)
                    # Read teh introduction paragraph
                    value_read = ""
                    for paragraph in paragraphs_in_introduction:
                        temp_value_read = self.__read_paragraph_types(paragraph, value_read)
                        value_read = temp_value_read + "   "

                    file_descritpion = value_read
                    introduction_read = True

            # create the dictionary to be dumped
            html_parsed_to_json = self.__build_json_output(file_name, complete_name, file_descritpion, dictionary_to_fill)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return html_parsed_to_json

    def __get_type_of_table(self, wrapper: bs) -> int:
        """
            Returns the type of table an HTML can have

        Args:
            wrapper (beautifulsoup): Beautiful soup wrappers containing a table

        Returns:
            int: Type of the identified table
        """
        type_of_table = htmlconstants.NO_VALID_TABLE_TYPE
        try:
            # Lets get the type of table to parse
            table_h1_tag = wrapper.find_all(htmlconstants.HTML_H1_TAG)
            table_h2_tag = wrapper.find_all(htmlconstants.HTML_H2_TAG)

            if (table_h1_tag != []):
                # H1 was found
                type_of_table = htmlconstants.SUMMARY_TABLE_TYPE
            elif (table_h2_tag != []):
                # H2 was found
                type_of_table = htmlconstants.DATA_TABLE_TYPE

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return type_of_table

    def __get_table_header(self, wrapper: bs, type_of_table: int) -> list:
        """
            Returns the table name and the table description from the HTML

        Args:
            wrapper (beautifulsoup): html wrapper element to retrieve data
            type_of_table (list): table identifier

        Returns:
            list: string list contatining the table name and description
        """
        header_data = ["", ""]
        try:
            # Validate the tiptle depending on the type of table
            if (type_of_table == htmlconstants.SUMMARY_TABLE_TYPE):
                header_data[0] = wrapper.h1.text
                header_data[1] = wrapper.span.text

            elif (type_of_table == htmlconstants.DATA_TABLE_TYPE):
                header_data[0] = wrapper.h2.text
                header_data[1] = wrapper.p.text

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return header_data

    def __get_columns_headers(self, wrapper: bs) -> list:
        """
            Get the headers of the table being parsed

        Args:
            wrapper (beautifulsoup): wrapper that contains the table to be parsed

        Returns:
            list: names of the headers of the table
        """
        columns_names = []
        try:
            # Get the header element of the table
            table_header_to_parse = wrapper.thead
            header_elements = table_header_to_parse.find_all(htmlconstants.HTML_TABLE_HEADER_TAG)

            # populate the columns name with the header strings
            for element in header_elements:
                header_name = element.p.text
                # Add the element
                columns_names.append(header_name)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return columns_names

    def __get_table_data(self, headers: list[str], wrapper: bs) -> list:
        """
            Creates the JSON objects with the data
        Args:
            headers (list[str]): retrieved headers from the table
            wrapper (bs): wrapper that contains the table

        Returns:
            list: parsed json object list
        """
        table_data = []

        try:
            # Only check the data for the amount f headers on the table
            amount_of_headers = len(headers)
            table_body = wrapper.tbody
            table_rows = table_body.find_all(htmlconstants.HTML_TABLE_ROW_TAG)

            # iterate over the row data
            for row in table_rows:
                row_data = row.find_all(htmlconstants.HTML_TABLE_ROW_DATA_TAG)
                json_row = {}

                # Check for the paragraphs in the row
                # for data in row_data:
                for index in range(0, amount_of_headers):
                    paragraphs_in_row = row_data[index].find_all(htmlconstants.HTML_PARAGRAPH_TAG)
                    amount_of_paragraphs = len(paragraphs_in_row)
                    value_read = ""

                    # Validate if it is needed to concatenate strings
                    if (amount_of_paragraphs > 1):
                        # Concatenate strings
                        for paragraph in paragraphs_in_row:
                            temp_value_read = self.__read_paragraph_types(paragraph, value_read)
                            value_read = temp_value_read + "   "
                    else:
                        # Get the string values and add it to the row
                        value_read = self.__read_paragraph_types(paragraphs_in_row[0], value_read)

                    # Create the key and value on the json object
                    formated_key = self.formatter.format_html_name(headers[index].strip())
                    json_row[formated_key] = value_read.strip()

                # append the object to the table data list
                table_data.append(json_row)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return table_data

    def __read_paragraph_types(self, paragraph: bs, existing_value: str) -> str:
        """_summary_

        Args:
            paragraph (beautifulsoup): html paragraph element
            existing_value (str): string that will be added to the result of reading the paragraph

        Returns:
            str: concatenated string of existing_value and new paragraph value
        """
        paragraph_value = ""
        try:
            read_value = paragraph.text

            # check if it is a reference link or a strong type
            if (read_value is None):
                link = paragraph.a
                strong = paragraph.strong
                if (link is not None):
                    read_value = paragraph.a.text
                elif (strong is not None):
                    read_value = paragraph.strong.text
                else:
                    read_value = ""
                    msg = "Invalid type of html element being read\n"
                    ExceptionLogger.logInformation(__name__, msg)

            paragraph_value = existing_value + read_value

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return paragraph_value

    def __build_json_output(self, title: str, input_file: str, description: str, data: list) -> object:
        """
            Builds the JSON datasheet output

        Args:
            title (str): name of the html document
            input_file (str): path name of the html document
            description (str): introduction from the html document
            data (list): tables parsed from the html document

        Returns:
            object: json datasheet
        """
        json_created = {}
        try:
            # Start with the data filling
            json_created[htmlconstants.HTML_TITLE] = title
            json_created[htmlconstants.HTML_DESCRIPTION] = description
            json_created[htmlconstants.HTML_INPUT_FILE] = input_file
            json_created[htmlconstants.HTML_GUID] = str(uuid.uuid4())
            json_created[htmlconstants.HTML_CREATED_ON] = get_current_utc_datetime("%m/%d/%Y")

            # add new table keys and objects
            for key in data:
                # Add table key and data
                table_name = key[0]
                table_data = key[1]
                json_created[table_name] = table_data

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return json_created
