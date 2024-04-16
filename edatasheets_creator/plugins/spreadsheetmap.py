# Spreadsheet map file class

import json
import re
import xlsxwriter
from edatasheets_creator.constants import spreadsheettypes
from xlsxwriter.utility import xl_cell_to_rowcol
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class SpreadsheetMap:
    """
    SpreadsheetMap class provides parser rule functionality used in creating datasheets from XLSX input files.
    """

    def __init__(self, mapFileName):
        """Class initialization.

        Args:
            mapFileName (PosixPath): a filesystem path to a map file containing parser rules.
        """

        try:

            self._mapFileName = mapFileName
            self.loadMap()
        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def loadMap(self):
        """Loads the parser rule map file using the mapFileName instance variable that is set in the class initializer.
        """

        try:

            with open(self._mapFileName, 'r') as f:
                mapFile = json.load(f)  # Load the file into a python object
                self._mapFile = mapFile

                # Get Sheet Map File Metadata - The map file indicates where data exists and how to organize
                self._description = mapFile[spreadsheettypes.SPREADSHEET_MAP_DESCRIPTION_FIELD]
                self._guid = mapFile[spreadsheettypes.SPREADSHEET_MAP_GUID_FIELD]
                self._mapType = mapFile[spreadsheettypes.SPREADSHEET_MAP_MAPTYPE_FIELD]

                # Get Sheets - this is the list of sheets that will be added to the datasheet
                self._sheets = mapFile[spreadsheettypes.SPREADSHEET_MAP_SHEETS_FIELD]

                # idx = self.getColumnIndex('AX')  # gets the column index for a column label

                f.close()

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except AttributeError as ae:
            ExceptionLogger.logError(__name__, "", ae)

        except NameError as ne:
            ExceptionLogger.logError(__name__, "", ne)

        except TypeError as te:
            ExceptionLogger.logError(__name__, "", te)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getDescription(self):
        """Returns the description of the input file using location information housed in the input map file.

        Returns:
            string: indicating the input file description.
        """
        return self._description

    def getGUID(self):
        """
        Returns a guid that is created during class initialization.

        Returns:
            string: a guid.
        """
        return self._guid

    def getFieldHeaders(self, jsonDict):
        """
        Returns field headers for columns.  These field headers are used to generate datasheet field names.

        Args:
            jsonDict (dict): dictionary containing references to field headers.

        Returns:
            _type_: _description_
        """

        try:
            return jsonDict.get(spreadsheettypes.SPREADSHEET_MAP_FIELDHEADERS_FIELD)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getRow(self, jsonDict):
        """Returns the row value for a dictionary input item.

        Args:
            jsonDict (dict): the input dictionary

        Returns:
            number: a row number.
        """

        try:
            return jsonDict.get(spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getIndexOn(self, jsonDict):
        """
        Returns the indexOn dictionary item for the dictionary passed as an argument.

        Args:
            jsonDict (dict): source dictionary containing an indexOn entry.

        Returns:
            dict: a dictionary containing the indexOn entry.
        """

        try:
            return jsonDict.get(spreadsheettypes.SPREADSHEET_MAP_INDEX_ON_FIELD)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getIncludeTagsDictionaryList(self, jsonDict):
        """
        Returns a list of dictionary items containing static fields for inclusion in the datasheet.

        Args:
            jsonDict (dict): a dictionary containing includeTags.

        Returns:
            list: contains an array of dictionary items pointing to fields to include.
        """

        outputList = None

        try:
            outputList = jsonDict.get(spreadsheettypes.SPREADSHEET_MAP_INCLUDE_TAGS_FIELD)
            return outputList
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getSpansColumns(self, jsonDict):
        """
        Returns an array of column spans indicating which columns to include within a grouping.

        Args:
            jsonDict (dict): a dictionary containing the spans information.

        Returns:
            list: containing columns to include within a group.
        """

        outputList = None

        try:
            colSpansDict = jsonDict.get(spreadsheettypes.SPREADSHEET_MAP_SPANS_FIELD)

            if colSpansDict is not None:
                outputList = colSpansDict.get(spreadsheettypes.SPREADSHEET_MAP_COLUMNS_FIELD)
            return outputList
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getSpans(self, jsonDict):
        try:
            return jsonDict.get(spreadsheettypes.SPREADSHEET_MAP_SPANS_FIELD)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getValue(self, key, obj):
        """
        Returns the value for a key/value pair.

        Args:
            key (string): a key for a key/value pair
            obj (object): the value for the key object.
        Returns:
            object: The object could be a list, a string, a number or a dictionary so it is suggested to check the type of the returned object.

        """
        try:

            if isinstance(obj, dict):
                return obj.get(key.strip())

            # if type(obj) is list:
            if isinstance(obj, list):
                return obj[int(key)]

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getSheetNames(self):
        """
        Returns a list containing the sheetnames to be processed in the map file.

        Returns:
            list: contains the worksheet names to be processed.
        """

        outputList = []

        try:

            for s in self._sheets:
                outputList.append(s[spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD])

            return outputList
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getSheetMap(self, sheetName):
        """
        Returns a dictionary section for the specified sheet.

        Args:
            sheetName (string): the worksheet name to query.

        Returns:
            dict: the parser rules for the specified worksheet.
        """

        try:
            for s in self._sheets:

                # find the specified sheet
                if spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD in s:
                    name = s[spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD]

                    if name == sheetName:

                        # verify that there is a key for sheet inclusion into datasheet
                        if spreadsheettypes.SPREADSHEET_MAP_INCLUDE_IN_DATASHEET_FIELD in s:
                            return s

                        break

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getDatasheetDescriptionLocation(self):
        """
        Returns the datasheet description location information.

        Returns:
            dict: the location of the datasheet description information.
        """

        descriptionLocation = ""

        try:
            if spreadsheettypes.SPREADSHEET_MAP_DATASHEET_DESC_LOCATION_FIELD in self._mapFile:
                descriptionLocation = self._mapFile[spreadsheettypes.SPREADSHEET_MAP_DATASHEET_DESC_LOCATION_FIELD]

            return descriptionLocation

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getRowsToIgnore(self, sheetName):
        """
        Returns a list of the rows to ignore in the spreadsheet.  Note:  currently this is not utilized within the processing.

        Args:
            sheetName (string): the name of the worksheet information to query.

        Returns:
            list: contains the list of rows to ignore.
        """

        outputList = []

        try:
            for s in self._sheets:

                # find the specified sheet
                if spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD in s:
                    name = s[spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD]

                if name == sheetName:

                    # verify that there is a key for sheet inclusion into datasheet
                    if spreadsheettypes.SPREADSHEET_MAP_IGNORE_ROWS_FIELD in s:

                        # get the value and convert it to boolean
                        outputList = s[spreadsheettypes.SPREADSHEET_MAP_IGNORE_ROWS_FIELD]
                    break

            return outputList
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getSections(self, sheetName):
        """
        Returns a list of the sections for a worksheet.

        Args:
            sheetName (string): name of the worksheet to query.

        Returns:
            list: contains dictionary entries for the section rules for the specified worksheet.
        """
        outputList = []

        try:
            for s in self._sheets:

                # find the specified sheet
                if spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD in s:
                    name = s[spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD]

                    if name == sheetName:

                        # verify that there is a key for sheet inclusion into datasheet
                        if spreadsheettypes.SPREADSHEET_MAP_IGNORE_COLS_FIELD in s:

                            # get the value and convert it to boolean
                            outputList = s[spreadsheettypes.SPREADSHEET_MAP_SECTIONS_FIELD]
                        break

            return outputList

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    @staticmethod
    def getGroupBySpansList(jsonItem):
        """
        Returns a list of the columns included within a groupBy definition.

        Args:
            jsonItem (dict): a dictionary containing the groupBy information.

        Returns:
            list: contains columns to include within a groupBy definition.
        """

        outputList = []
        try:

            jsonType = type(jsonItem)

            if jsonItem is not None and jsonType == list:

                if len(jsonItem) > 0 and spreadsheettypes.SPREADSHEET_MAP_SPANS_FIELD in jsonItem[0]:
                    # ExceptionLogger.logDebug(__name__,(spreadsheettypes.SPREADSHEET_MAP_SPANS_FIELD + ' was found in jsonItem='),jsonItem)
                    spans = jsonItem[0][spreadsheettypes.SPREADSHEET_MAP_SPANS_FIELD][spreadsheettypes.SPREADSHEET_MAP_COLUMNS_FIELD]

                    # ExceptionLogger.logDebug(__name__,'spans =',spans)
                    if spans is not None:

                        if (type(spans) is list):

                            outputList = spans
                            # ExceptionLogger.logDebug(__name__,'first group by list =',l)
            else:
                # a dictionary was pass
                spans = jsonItem[spreadsheettypes.SPREADSHEET_MAP_SPANS_FIELD][spreadsheettypes.SPREADSHEET_MAP_COLUMNS_FIELD]
                outputList = spans
                # ExceptionLogger.logInformation(__name__,spreadsheettypes.SPREADSHEET_MAP_GROUPS_FIELD + 'Spans passed is not a list.  Spans=',spans)

            return outputList

        except Exception as e:
            ExceptionLogger.logError(__name__, str(e), e)

    @staticmethod
    def getListSpanInGroupBy(jsonItem):
        """
        Returns a list of the columns included within a groupBy definition.

        Args:
            jsonItem (dict): a dictionary containing the groupBy information.

        Returns:
            list: contains columns to include within a groupBy definition.
        """

        outputList = []
        try:

            jsonType = type(jsonItem)

            if jsonItem is not None and jsonType == dict:

                for listItem in jsonItem[spreadsheettypes.SPREADSHEET_MAP_GROUPS_FIELD]:
                    rowSpans = listItem[spreadsheettypes.SPREADSHEET_MAP_SPANS_FIELD][spreadsheettypes.SPREADSHEET_MAP_COLUMNS_FIELD]
                    outputList.extend(rowSpans)

            return outputList

        except Exception as e:
            ExceptionLogger.logError(__name__, str(e), e)

    @staticmethod
    def getSubObjectFlag(groupByItem, column_letter):
        """
        Returns a boolean stating if the subobject flag is activated for a group by array item.

        Args:
            groupByItem (dict): a dictionary containing the groupBy information.
            column_letter (str): a string of the column letter.

        Returns:
            boolean: if group by should be a subobject or not.
        """
        result = False
        try:

            jsonType = type(groupByItem)

            if groupByItem is not None and jsonType == list:

                for listItem in groupByItem:
                    if column_letter in listItem[spreadsheettypes.SPREADSHEET_MAP_SPANS_FIELD][spreadsheettypes.SPREADSHEET_MAP_COLUMNS_FIELD]:
                        if spreadsheettypes.SPREADSHEET_MAP_INCLUDE_AS_SUBOBJECT in listItem:
                            result = listItem[spreadsheettypes.SPREADSHEET_MAP_INCLUDE_AS_SUBOBJECT]

            return result

        except Exception as e:
            ExceptionLogger.logError(__name__, str(e), e)

    def getGroups(self, jsonItem):
        """
        Returns groupBy information for a specified section.

        Args:
            jsonItem (dict): a section within a worksheet.

        Returns:
            dict: contains the groupBy entries for the specified section.
        """

        try:

            if spreadsheettypes.SPREADSHEET_MAP_GROUPS_FIELD in jsonItem:
                return jsonItem[spreadsheettypes.SPREADSHEET_MAP_GROUPS_FIELD]

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getColsToIgnore(self, sheetName):
        """
        Returns a list of columns to ignore.

        Args:
            sheetName (string): name of the worksheet to query.

        Returns:
            list: containing a list of columns to ignore.
        """

        outputList = []

        try:
            for s in self._sheets:

                # find the specified sheet
                if spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD in s:
                    name = s[spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD]

                if name == sheetName:

                    # verify that there is a key for sheet inclusion into datasheet
                    if spreadsheettypes.SPREADSHEET_MAP_IGNORE_COLS_FIELD in s:

                        # get the value and convert it to boolean
                        outputList = s[spreadsheettypes.SPREADSHEET_MAP_IGNORE_COLS_FIELD]
                    break

            return outputList

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def ignoreBlanks(self, sheetName):
        """
        Returns a boolean value indicating whether to include blank columns.
        Note: This is currently not used by the processor and blank entries will be ignored and excluded from the datasheet.

        Args:
            sheetName (string): the worksheet to query within the parser rule (map) file.
        Returns:
            bool: indicated whether to include blank entries in the datasheet.
        """
        bln = True

        try:
            for s in self._sheets:

                # find the specified sheet
                if spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD in s:
                    name = s[spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD]

                if name == sheetName:

                    # verify that there is a key for sheet inclusion into datasheet
                    if spreadsheettypes.SPREADSHEET_MAP_IGNORE_BLANKS_FIELD in s:

                        # get the value and convert it to boolean
                        bln = bool(s[spreadsheettypes.SPREADSHEET_MAP_IGNORE_BLANKS_FIELD])
                    break

            return bln

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getDataStartRow(self, group):
        """
        Returns the row number indicating the start of data.

        Args:
            group (dict): the section dictionary within a worksheet entry in the parser rule (map file).

        Returns:
            number: row number.
        """

        index = -1

        try:

            # verify that there is a key for sheet inclusion into datasheet
            if spreadsheettypes.SPREADSHEET_MAP_DATA_START_ROW_FIELD in group:

                # get the value and convert it to boolean
                index = group[spreadsheettypes.SPREADSHEET_MAP_DATA_START_ROW_FIELD]

            return index

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getDataStartCol(self, group):
        """
        Returns the column indicating the start of data.

        Args:
            group (dict): the section dictionary within a worksheet entry in the parser rule (map file).  Note that this is currently not used by the parser.

        Returns:
            string: column indicator.  This is an alpha character that maps to the worksheet column.
        """

        i = -1

        try:

            # verify that there is a key for sheet inclusion into datasheet
            if spreadsheettypes.SPREADSHEET_MAP_DATA_START_COL_FIELD in group:

                # get the value and convert it to boolean
                i = group[spreadsheettypes.SPREADSHEET_MAP_DATA_START_COL_FIELD]

            return i
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def includeInDatasheet(self, sheetName):
        """
        Returns a boolean indicating whether to include the worksheet in the datasheet output.

        Args:
            sheetName (string): worksheet name.

        Returns:
            bool: indicates whether to include the data in the datasheet output.
        """
        bln = True

        try:
            for s in self._sheets:

                # find the specified sheet
                if spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD in s:
                    name = s[spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD]

                    if name == sheetName:

                        # verify that there is a key for sheet inclusion into datasheet
                        if spreadsheettypes.SPREADSHEET_MAP_INCLUDE_IN_DATASHEET_FIELD in s:

                            # get the value and convert it to boolean
                            bln = bool(s[spreadsheettypes.SPREADSHEET_MAP_INCLUDE_IN_DATASHEET_FIELD])
                        break

            return bln

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def onlyTableName(self, sheetName):
        """
        Returns a boolean indicating if tables should be compounded with tab name or not.

        Args:
            sheetName (string): worksheet name.

        Returns:
            bool: indicates whether tables should be compounded with tab name or not.
        """
        bln = False

        try:
            for s in self._sheets:

                # find the specified sheet
                if spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD in s:
                    name = s[spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD]

                    if name == sheetName:

                        # verify that there is a key for sheet inclusion into datasheet
                        if spreadsheettypes.SPREADSHEET_MAP_ONLY_TABLE_NAME in s:

                            # get the value and convert it to boolean
                            bln = bool(s[spreadsheettypes.SPREADSHEET_MAP_ONLY_TABLE_NAME])
                        break

            return bln

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def includeMetadata(self):
        """
        Returns a boolean indicating if metadata should be included in datasheet or not.

        Args:


        Returns:
            bool: indicates whether metadata should be included in datasheet or not.
        """
        bln = True

        try:
            # get value from map file
            if spreadsheettypes.SPREADSHEET_MAP_INCLUDE_METADATA in self._mapFile:
                bln = self._mapFile[spreadsheettypes.SPREADSHEET_MAP_INCLUDE_METADATA]

            return bln

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def checkIndustryFormat(self):
        """
        Returns a boolean indicating if the datasheet is to conform with industry workgroup specifications.

        Args:


        Returns:
            bool: indicates if the datasheet is to conform with industry workgroup specifications.
        """
        bln = False

        try:
            # get value from map file
            if spreadsheettypes.SPREADSHEET_MAP_INDUSTRY_FORMAT in self._mapFile:
                bln = self._mapFile[spreadsheettypes.SPREADSHEET_MAP_INDUSTRY_FORMAT]

            return bln

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def macroEnabled(self):
        """
        Returns a boolean indicating if the sheet is macro enabled.

        Args:


        Returns:
            bool: indicates whether the sheet is macro enabled or not.
        """
        bln = False

        try:
            # get value from map file
            if spreadsheettypes.SPREADSHEET_MAP_MACRO_ENABLED in self._mapFile:
                bln = self._mapFile[spreadsheettypes.SPREADSHEET_MAP_MACRO_ENABLED]

            return bln

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getComponentType(self):
        """
        Returns a boolean indicating if tables should be compounded with tab name or not.

        Args:
            sheetName (string): worksheet name.

        Returns:
            bool: indicates whether tables should be compounded with tab name or not.
        """
        bln = 'default'

        try:

            # get value from map file
            if spreadsheettypes.SPREADSHEET_MAP_COMPONENT_TYPE in self._mapFile:
                bln = self._mapFile[spreadsheettypes.SPREADSHEET_MAP_COMPONENT_TYPE]

            return bln

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getSheets(self):
        """
        Returns a list containing the worksheets in the map file.

        Returns:
            list: _contains the list of worksheets described by the map file.
        """
        return self._sheets

    def getMapFile(self):
        """
        Returns the PosixPath for the parser rule (map) file.

        Returns:
            PosixPath: path to map file.
        """
        return self._mapFile

    def getMapType(self):
        """
        Returns the map type of the map file (e.g. spreadsheet).

        Returns:
            string: describes the map file type.
        """
        return self._mapType

    @staticmethod
    def getGroupByDictionary(groupByField):
        """
        Not implemented.

        Args:
            groupByField (string): field name.
        """

        try:
            pass
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    @staticmethod
    def getGroupByItemHeaderDictList(groupBy):
        """
        Returns a list of the headers for groupBy items.  This is used to generate field names in the datasheet.

        Args:
            groupBy (dict): dictionary containing the groupBy information.

        Returns:
            list: contains groupBy entries.
        """
        try:
            outputList = []

            # make sure a groupBy was passed
            if groupBy is not None and len(groupBy) > 0:
                # ExceptionLogger.logDebug(__name__,"groupBy=",groupBy)

                # itemType = type(groupBy)
                # ExceptionLogger.logDebug(__name__,"itemType =",itemType)

                for g in groupBy:
                    # row = g[spreadsheettypes.SPREADSHEET_MAP_NAME_FIELD][spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD]
                    # col = g[spreadsheettypes.SPREADSHEET_MAP_NAME_FIELD][spreadsheettypes.SPREADSHEET_MAP_COL_FIELD]
                    header = dict(g[spreadsheettypes.SPREADSHEET_MAP_NAME_FIELD])
                    outputList.append(header)
            return outputList
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    @staticmethod
    def columnInGroupByList(colIdx, groupBy):
        """
        Returns a boolean value indicating whether a column is in the groupBy list within a section.

        Args:
            colIdx (number): a column number
            groupBy (dict): the groupBy dictionary.

        Returns:
            bool: indicating whether the column is in the specified groupBy dictionary.
        """

        # idx = -1
        isInList = False

        try:
            for currentSpan in groupBy:
                # ExceptionLogger.logDebug(__name__,"groupBy=",groupBy)
                spansList = SpreadsheetMap.getGroupBySpansList(currentSpan)

                # ExceptionLogger.logDebug(__name__,"spansList=",spansList)
                colIdxType = type(colIdx)

                if colIdxType == str and len(colIdx) > 0:

                    # a letter was passed so set up for check
                    colLetter = colIdx
                else:

                    # a number was passed so get the column letter
                    colLetter = SpreadsheetMap.getColumnLetter(colIdx)

                if colLetter is not None and len(colLetter) > 0:
                    if colLetter in spansList:
                        # idx = spansList.index(colLetter)
                        isInList = True
                        break

                # ExceptionLogger.logDebug(__name__,"idx=",idx)

            return isInList
        except ValueError as ve:
            ExceptionLogger.logError(__name__, "", ve)
            return False

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    @staticmethod
    def getColumnLetter(colNumber):
        """
        Returns the column letter for a given column index.  Example:  1 returns "A".

        Args:
            colNumber (number): column number.

        Returns:
            string: column letter.
        """

        letter = ""

        try:

            if colNumber >= 0:
                letter = xlsxwriter.utility.xl_col_to_name(colNumber)

            return letter
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    @staticmethod
    def getColumnIndex(columnString):
        """
        Returns the column index for a given column letter.

        Args:
            columnString (string): column letter(s).

        Returns:
            number: column index.
        """

        row = -1
        col = -1

        try:
            reMatch = re.search(r'\d+$', columnString)

            if reMatch is None:
                columnString = columnString + (str(1))  # just add a 1, the row will be thrown away

            (row, col) = xl_cell_to_rowcol(columnString)

            return col
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
