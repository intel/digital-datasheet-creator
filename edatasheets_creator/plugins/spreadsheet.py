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


# Spreadsheet plugin class
import re
import os
from openpyxl import load_workbook
import inspect
import json

from edatasheets_creator.document.jsondatasheet import JsonDataSheet
from edatasheets_creator.document.jsondatasheetschema import JsonDataSheetSchema
from edatasheets_creator.utility.path_utilities import validateRealPath
from edatasheets_creator.utility.format import Format


from edatasheets_creator.functions import t
from collections import deque
from edatasheets_creator.constants import datasheetconstants
from edatasheets_creator.constants import serializationconstants
from edatasheets_creator.constants import spreadsheettypes
from edatasheets_creator.exceptions.configurationerror import ConfigurationError
from edatasheets_creator.plugins.spreadsheetmap import SpreadsheetMap
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class Plugin:
    """
    Spreadsheet plugin class that implements datasheet generation from an XLSX
    """

    def __init__(self):
        """
        Class initialization
        """

        self._worksheetSectionIndexWritten = False  # used in multisection worksheets to indicate that index values are already written
        self._indexOnRow = -1
        self._indexOnCol = -1
        self.format = Format()

    def __repr__(self):
        """
            Returns a name for the class

        Returns:
            string : class name
        """
        return __name__ + '.' + inspect.currentframe().f_code.co_name

    def process(self, inputFileName, outputFileName, mapFileName=""):
        """

        Main logic method for spreadsheet processing

        Args:
            inputFileName (PosixPath): Input file name
            outputFileName (PosixPath): Output file name
            mapFileName (PosixPath): Map file to guide parser
        """

        datasheet = {}

        try:
            msg = t("Spreadsheet Plugin is loaded")
            ExceptionLogger.logInformation(__name__, msg)

            # Validate if the input files exists on the system as they are required
            if (not validateRealPath(inputFileName)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\n Input file does not exists"))
                print()
                return

            if ((not validateRealPath(mapFileName)) and mapFileName != ""):
                # Map file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\n Map file does not exists"))
                print()
                return

            self._fileName = inputFileName
            self._outputFileName = outputFileName
            self._mapFileName = mapFileName

            wb = load_workbook(filename=inputFileName, data_only=True)
            ExceptionLogger.logInformation(__name__, t("\n\nProcessing") + " " + t("workbook") + ":  " + str(inputFileName) + "...\n")

            outputSuffix = os.path.splitext(self._outputFileName)
            if outputSuffix[1] == ("." + serializationconstants.C_HEADER_NAME):
                msg1 = t("\nCreating Header File\n")
                ExceptionLogger.logInformation(__name__, msg1)
                # Header.createHeaderFile(wb,self._fileName,self._outputFileName)
                self.createHeaderFile(wb, inputFileName, outputFileName)

            if self._mapFileName == "":
                msg1 = t("\nNo map file so will use defualt processing\n")
                ExceptionLogger.logInformation(__name__, msg1)
                self.processWithoutMap(wb, inputFileName, outputFileName, datasheet)
            if self._mapFileName != "":

                # Load map file
                map = SpreadsheetMap(self._mapFileName)

                # get the sheet names
                sheetNames = map.getSheetNames()

                # get the title
                baseName = os.path.basename(inputFileName).split('.')[0]
                datasheetTitle = datasheetconstants.DATASHEET_DEFAULT_TITLE + ' - ' + baseName

                # get the datasheet description
                datasheetDescription = self.getDatasheetDescription(wb, map.getDatasheetDescriptionLocation())

                if datasheetDescription is not None:
                    datasheetDescription = datasheetDescription.replace('\n', ' ')

                jds = JsonDataSheet(self._outputFileName)  # outputfile

                # generate the datasheet header
                datasheetHeader = jds.setMetadata(datasheetTitle, datasheetDescription, self._fileName)

                # add header information to the datasheet
                datasheet = datasheetHeader

                # ExceptionLogger.logDebug(__name__,"datasheet:",datasheet)

                # iterate through the sheets described in the map file, ignore other worksheets
                for i in sheetNames:

                    ExceptionLogger.logInformation(__name__, t("\nProcessing") + " " + t("spreadsheet") + ":  " + i + "...")
                    self._worksheetSectionIndexWritten = False  # controls writing the IndexOn item
                    ws = wb[i]

                    for i, s in enumerate(wb.sheetnames):
                        if s == ws.title:
                            break

                    wb.active = i
                    sheet = wb.active

                    # if the worksheet should be included in the datasheet, process it
                    if map.includeInDatasheet(sheet.title):

                        self._indexOnCol = -1
                        self._indexOnRow = -1
                        self.parseWorksheet(datasheet, wb, sheet.title, map)

                        # ExceptionLogger.logDebug(__name__,"datasheet:",v)

                strMsg = "\n\n" + t("Writing") + " " + str((self._outputFileName)) + "...\n"
                ExceptionLogger.logInformation(__name__, strMsg)

                # pretty print JSON, preserving unicode characters
                with open(self._outputFileName, "w", encoding='utf-8') as outfile:
                    json.dump(datasheet, outfile, ensure_ascii=False, indent=serializationconstants.JSON_INDENT_DEFAULT)
                    outfile.close()

                # write the schema
                schema = JsonDataSheetSchema(self._outputFileName)
                schema.write()

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def processWithoutMap(self, wb, inputFileName, outputFileName, datasheet):
        """

       Main logic method for spreadsheet processing without a map file needed

       Args:
           wb : Workbook of the given file name
           inputFileName (PosixPath): Input file name
           outputFileName (PosixPath): Output file name
           datasheet : The outputted data
       """
        try:
            # defining all the needed variables
            self._wb = wb
            self._inputFileName = inputFileName
            self._outputFileName = outputFileName
            self._datasheet = datasheet

            indexOnDict = dict()

            # get the title
            baseName = os.path.basename(inputFileName).split('.')[0]
            datasheetTitle = datasheetconstants.DATASHEET_DEFAULT_TITLE + ' - ' + baseName
            dataSheetDescription = " "
            jds = JsonDataSheet(self._outputFileName)  # outputfile
            datasheetHeader = jds.setMetadata(datasheetTitle, dataSheetDescription, self._inputFileName)

            # put the datasheet header on the datasheet
            self._datasheet = datasheetHeader

            # iterate through the sheets of the excel file
            for i in wb.sheetnames:

                worksheetName = JsonDataSheet.generateValidJsonFieldName(str(i))
                self._datasheet[worksheetName] = []

                ExceptionLogger.logInformation(__name__, t("\nProcessing") + " " + t("spreadsheet") + ":  " + i + "...")

                self._worksheetSectionIndexWritten = False  # controls writing the IndexOn item
                self._indexOnCol = 0
                self._indexOnRow = 1
                self._colLetter = SpreadsheetMap.getColumnLetter(self._indexOnCol)

                cellContents = self.getCellValue(wb, i, self._indexOnRow, self._colLetter)
                indexFieldName = cellContents
                values = []

                # while we are not at the end of the excel spreadsheet, keep iterating through it
                while self._indexOnRow != (wb[i].max_row) and self._indexOnCol != (wb[i].max_column):
                    self._indexOnRow += 1

                    if self._indexOnRow == 1:
                        cellContents = self.getCellValue(wb, i, self._indexOnRow, self._colLetter)
                        indexFieldName = cellContents
                    else:
                        cellContents = self.getCellValue(wb, i, self._indexOnRow, self._colLetter)
                        values.append(cellContents)

                    if self._indexOnRow == wb[i].max_row and self._indexOnCol != wb[i].max_column:
                        indexOnDict[indexFieldName] = values
                        values = []
                        self._indexOnRow = 0
                        self._indexOnCol += 1
                    self._colLetter = SpreadsheetMap.getColumnLetter(self._indexOnCol)

                # adding the values of the dictionary to the output file
                strMsg = "\n\n" + t("Writing") + " " + str((self._outputFileName)) + "...\n"
                ExceptionLogger.logInformation(__name__, strMsg)
                self._datasheet[worksheetName].append(indexOnDict)
                indexOnDict = dict()

                # pretty print JSON, preserving unicode characters
                with open(self._outputFileName, "w", encoding='utf-8') as outfile:
                    json.dump(self._datasheet, outfile, ensure_ascii=False, indent=serializationconstants.JSON_INDENT_DEFAULT)
                    outfile.close()

            # writing the schema
                schema = JsonDataSheetSchema(self._outputFileName)
                schema.write()

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def createHeaderFile(self, wb, inputFileName, outputFileName):
        """

       Main logic method for creating a header file given user inputted a .h file

       Args:
           wb : Workbook of the given file name
           inputFileName (PosixPath): Input file name
           outputFileName (PosixPath): Output file name
       """
        try:

            self._inputFileName = inputFileName
            self._wb = wb
            self._outputFileName = outputFileName
            with open(outputFileName, "a") as outputFile:

                for i in wb.sheetnames:
                    self._indexOnCol = 0
                    self._indexOnRow = 2
                    self._colLetter = SpreadsheetMap.getColumnLetter(self._indexOnCol)

                    cellContents = self.getCellValue(wb, i, self._indexOnRow, self._colLetter)

                    while self._indexOnRow != (wb[i].max_row) and self._indexOnCol != (wb[i].max_column):
                        self._indexOnCol += 1

                        if self._indexOnCol == (wb[i].max_column):
                            cellContents = self.getCellValue(wb, i, self._indexOnRow, self._colLetter)
                            outputFile.write(cellContents + "\n")
                        else:
                            cellContents = self.getCellValue(wb, i, self._indexOnRow, self._colLetter)
                            outputFile.write("#define ")
                            outputFile.write(cellContents + "   ")

                        if self._indexOnRow != wb[i].max_row and self._indexOnCol == wb[i].max_column:
                            self._indexOnCol = 0
                            self._indexOnRow += 1
                        self._colLetter = SpreadsheetMap.getColumnLetter(self._indexOnCol)

        except FileNotFoundError as fnf:
            ExceptionLogger.logError(__name__, "", fnf)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getDatasheetDescription(self, wb, descriptionLocation):
        """
        Returns a datasheet description based referenced from the specified location in the workbook.  This can be in any worksheet.

        Args:
            wb (workbook): Spreadsheet workbook object
            descriptionLocation (dict): Contains the worksheetname, row and column containing the description

        Returns:
            string: description
        """

        s = datasheetconstants.DATASHEET_DEFAULT_DESCRIPTION  # initialize to default

        try:
            if (len(descriptionLocation) > 0):

                # get the location information for the datasheet description
                sheetName = descriptionLocation[spreadsheettypes.SPREADSHEET_MAP_SHEETNAME_FIELD]
                rowNum = descriptionLocation[spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD]
                colLetter = descriptionLocation[spreadsheettypes.SPREADSHEET_MAP_COL_FIELD]

                # set the active worksheet to the sheet containing the datasheet description
                # ws = wb[sheetName]
                wb.active = wb.worksheets.index(wb[sheetName])
                sheet = wb.active

                # build the cell name
                cell = colLetter + str(rowNum)

                # get the value from the cell
                s = sheet[cell].value

                return s

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getCellValue(self, wb, sheetName, row, col):
        """

        Returns the value contained in a cell within a workbook and worksheet.

        Args:
            wb (openpyxl workbook): The workbook to reference
            sheetName (string): The worksheet within the workbook to reference
            row (number): The row to reference
            col (number): The cell to reference

        Returns:
            Any : The value contained within the cell.
        """
        try:
            # set the active worksheet to the sheet containing the datasheet description
            # ws = wb[sheetName]
            wb.active = wb.worksheets.index(wb[sheetName])
            sheet = wb.active

            # build the cell name
            cell = col + str(row)

            # get the value from the cell
            if (self.isMerged(wb, row, col)):
                # Row num plus one to make it match with the excel numeration
                rng = [s for s in sheet.merged_cells.ranges if sheet[cell].coordinate in s]
                return sheet.cell(rng[0].min_row, rng[0].min_col).value if len(rng) != 0 else cell.value
            elif sheet[cell].value is None:
                # cellValue = "defaultValue"
                return "empty"
            return sheet[cell].value
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getColValueFromRow(self, rowObj, col, wb=None, rowNum=None):
        """
        Returns the value contained within the specified column from a row object.  This method should be used when an entire row of data is read
        from the workbook.

        Returns:
            Any: The value contained within the cell.
        """
        try:

            if rowObj is not None and col is not None:
                colIdx = SpreadsheetMap.getColumnIndex(col)
                cell = rowObj[colIdx]
                cellValue = cell.value
                if (cellValue is None):
                    if (wb is None or rowNum is None):
                        msg = "There was a problem retrieving the column value, the value is null."
                        ExceptionLogger.logError(__name__, msg)
                        defaultValue = "defaultValue"
                        return defaultValue
                    else:
                        if (self.isMerged(wb, rowNum + 1, col)):
                            # Row num plus one to make it match with the excel numeration
                            cellValue = self.getCellValueIfMerged(wb, rowNum + 1, col)
                            return cellValue
                        else:
                            # cellValue = "defaultValue"
                            cellValue = " "

                return cellValue

            else:
                msg = "There was a problem retrieving the column value from the row object"
                ExceptionLogger.logError(__name__, msg)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getCellValueIfMerged(self, wb, row, col):
        try:
            returnValue = None
            currentCell = str(col) + str(row)
            # Col plus 1 because the bounds in the merged ranges start in 1
            colIndex = SpreadsheetMap.getColumnIndex(currentCell) + 1
            sheet = wb.active

            for range_ in sheet.merged_cells.ranges:
                min_row = range_.min_row
                min_col = range_.min_col
                max_row = range_.max_row
                max_col = range_.max_col
                if (min_row <= row and min_col <= colIndex and row <= max_row and colIndex <= max_col):
                    cells = str(range_).split(':')[0]
                    # ExceptionLogger.logDebug(__name__, "cells=", cells)
                    mergedRowNum = int(re.search("\d+", str(cells))[0])  # noqa
                    # ExceptionLogger.logDebug(__name__, "mergedRowNum=", mergedRowNum)
                    cIdx = SpreadsheetMap.getColumnIndex(cells)
                    colLetter = SpreadsheetMap.getColumnLetter(cIdx)
                    # ExceptionLogger.logDebug(__name__, "cells.value=", self.getCellValue(wb, sheet.title, mergedRowNum, colLetter))
                    returnValue = self.getCellValue(wb, sheet.title, mergedRowNum, colLetter)
                    if returnValue is None:
                        returnValue = ' '
                    break
            return returnValue
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def isMerged(self, wb, row, col):
        try:
            sheet = wb.active
            cell = sheet.cell(row, SpreadsheetMap.getColumnIndex(col) + 1)
            # strMsg = "row=" + str(row) + ", col=" + str(col)
            # ExceptionLogger.logDebug(__name__, strMsg)

            # ExceptionLogger.logDebug(__name__, "merged_cells.ranges=", sheet.merged_cells.ranges)
            for m in sheet.merged_cells.ranges:

                # ExceptionLogger.logDebug(__name__, "m=", m)
                # ExceptionLogger.logDebug(__name__, "cell.coordinate=", cell.coordinate)
                if (cell.coordinate in m):
                    # ExceptionLogger.logDebug(__name__, "Yes, it's merged!", m)
                    return True
            return False

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getRow(self, wb, sheetName, row):
        """
        Reads and returns the specified row from a worksheet within a workbook

        Args:
            wb (workbook): The workbook to reference
            sheetName (string): The worksheet to reference
            row (number): The row to read and return

        Returns:
            Row Object: A row object containing the cells and values from the worksheet.
        """
        try:
            # set the active worksheet to the sheet containing the datasheet description
            # ws = wb[sheetName]
            wb.active = wb.worksheets.index(wb[sheetName])
            sheet = wb.active

            # ExceptionLogger.logDebug(__name__,"Merged cells=",sheet.merged_cells)
            # ExceptionLogger.logDebug(__name__,"Merged cellRanges=",sheet.merged_cell_ranges)
            return sheet[row + 1]

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def parseWorksheet(self, datasheet, wb, sheetName, map):
        """
        Main worksheet parser entry method.

        Args:
            datasheet (dict): A dictionary referencing the output datasheet
            wb (workbook): The workbook object containing the worksheet.
            sheetName (string): The worksheet name contained in the workbook to parse.
            map (dict): A map containing the parser rules for the worksheet
        """

        try:

            # ExceptionLogger.logDebug(__name__,"datasheet inside this func",datasheet)

            # activate the worksheep
            # ws = wb[sheetName]
            wb.active = wb.worksheets.index(wb[sheetName])
            # sheet = wb.active
            sheetKey = JsonDataSheet.generateValidJsonFieldName(sheetName)

            datasheet[sheetKey] = []

            # at this point the active sheet should be set to the worksheet named in the sheetName argument

            sections = map.getSections(sheetName)
            self.parseSections(datasheet, sheetKey, wb, sheetName, sections, map)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def parseSections(self, datasheet, sheetKey, wb, sheetName, sections, map):
        """

        This main processing loop for sections within a worksheet.

        Args:
            datasheet (dict): A dictionary referencing the output datasheet
            sheetKey (string):  The dictionary key referencing the output item in the datasheet (output) document
            wb (workbook): The workbook object containing the worksheet.
            sheetName (string): The worksheet name contained in the workbook to parse.
            sections (dict): A dictionary containing the parsing rules for one or more sections within the worksheet.
            map (dict): A map containing the parser rules for the worksheet

        Raises:
            ConfigurationError: An error indicating that the parser rules for the worksheet could not be found.
        """
        try:

            sectionIdx = -1

            # ExceptionLogger.logDebug(__name__,"Beginning to parse sections.  Sections=",sections)

            if len(sections) > 0:
                self._worksheetSectionIndexWritten = False
                for i in sections:
                    sectionIdx += 1

                    self.parseSection(datasheet, sheetKey, wb, sheetName, i, map)

                    # ExceptionLogger.logDebug(__name__,"datasheet after processing section:", datasheet)

            else:
                s = t('No sections found in map file.  A map file must have at least 1 section')
                d = str(map._mapFileName)
                raise ConfigurationError(s, d)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getDatasheetRowIndex(self, datasheet, rowObj, section, map):
        """
        Returns the index value from a row object containing values read from the worksheet.

        Args:
            datasheet (dict): A dictionary referencing the output datasheet.
            rowObj (object): Contains a row of cells/values read from the spreadsheet.
            section(dict): A dictionary containing the parser rules for the current section.
            map (dict): A map containing the parser rules for the worksheet
        """

        try:
            indexOn = map.getIndexOn(section)

            if indexOn is not None:
                # indexOnRow = indexOn[spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD][spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD]
                indexOnCol = indexOn[spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD][spreadsheettypes.SPREADSHEET_MAP_COL_FIELD]

                # get the column value
                val = self.getColValueFromRow(rowObj, indexOnCol)
                # ExceptionLogger.logDebug(__name__,"Index On Value:  ", val)
                return val

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def _rowHasData(self, rowValues, indexColLetter):
        """
        Returns a boolean indicating whether  the row has any data in it beyond what might be a section header

        Args:
            rowValues:  An array containing row values
            indexColLetter:  The letter of an the indexed column

        """

        hasData = False
        valueCount = 0

        try:

            if rowValues is not None:
                # itemCount = len(rowValues)

                # First see if there is a value in the indexed field.  If not, then the entire row should be skipped
                colIdx = SpreadsheetMap.getColumnIndex(indexColLetter)
                indexColVal = rowValues[colIdx]

                if indexColVal is not None:
                    for i in rowValues:
                        if hasattr(i, "column_letter"):
                            if i.column_letter == indexColLetter:
                                continue
                            else:
                                if i.value is not None:
                                    valueCount += 1

                if valueCount > 0:
                    hasData = True

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return hasData

    def serializeIndex(self, datasheet, sheetKey, wb, sheetName, section, map):
        """
        Writes the index values to the datasheet output file (in-memory).

        Args:
            datasheet (dict): Dictionary object containing the output datasheet.
            sheetKey (string): A string containing the dictionary key to use for writing index.
            wb (object): Workbook object.
            sheetName (string): Contains the current worksheet name.
            section (dict): Contains the parser rules for the current section for the specified worksheet.
            map (dict): Processing rules for the workbook.
        """

        try:

            # ExceptionLogger.logDebug(__name__,"!=!=!=SerializeIndex Called, datasheet=",datasheet)

            # get the indexOn field that specifies the data orientation
            indexOn = map.getIndexOn(section)
            indexOnRow = indexOn[spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD][spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD]
            indexOnCol = indexOn[spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD][spreadsheettypes.SPREADSHEET_MAP_COL_FIELD]

            if indexOn is not None:
                # orientation = map.getValue(spreadsheettypes.SPREADSHEET_MAP_ORIENTATION_FIELD, indexOn)
                header = map.getValue(spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD, indexOn)
                headerRow = map.getValue(spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD, header)
                headerCol = map.getValue(spreadsheettypes.SPREADSHEET_MAP_COL_FIELD, header)
                dataStartRow = map.getValue(spreadsheettypes.SPREADSHEET_MAP_DATA_START_ROW_FIELD, indexOn)
                maxRows = map.getValue(spreadsheettypes.SPREADSHEET_MAP_MAX_ROWS_FIELD, indexOn)
                headerFieldName = self.getCellValue(wb, sheetName, headerRow, headerCol)
                headerFieldName = JsonDataSheet.generateValidJsonFieldName(headerFieldName)
                indexFieldName = JsonDataSheet.generateValidJsonFieldName(self.getCellValue(wb, sheetName, indexOnRow, indexOnCol))

                tagList = map.getIncludeTagsDictionaryList(section)

                rowNum = dataStartRow - 1

                indexOnDict = dict()
                # dsRowIdx = -1

                for _ in range(rowNum, (rowNum + maxRows) + 1):

                    rowValues = self.getRow(wb, sheetName, rowNum)
                    val = self.getColValueFromRow(rowValues, headerCol, wb, rowNum)

                    rowHasData = self._rowHasData(rowValues, headerCol)

                    # See if this might be a section header in the spreadsheet
                    if (rowHasData) and (val is None):
                        # This is a section header in the spreadsheet
                        rowNum += 1
                        continue
                    elif ((not rowHasData) and ((val is None) or (val == 'defaultValue'))):
                        # End of spreadsheet
                        break
                    else:
                        # Normal row
                        indexOnDict = dict()
                        indexOnDict[indexFieldName] = val

                        if tagList is not None and len(tagList) > 0:
                            # ExceptionLogger.logDebug(__name__,"tagList=",tagList)

                            for tag in tagList:

                                fieldLabel = self.getCellValue(wb, sheetName,
                                                               tag[spreadsheettypes.SPREADSHEET_MAP_FIELDLABEL_FIELD][spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD],
                                                               tag[spreadsheettypes.SPREADSHEET_MAP_FIELDLABEL_FIELD][spreadsheettypes.SPREADSHEET_MAP_COL_FIELD])
                                fieldValue = self.getCellValue(wb, sheetName,
                                                               tag[spreadsheettypes.SPREADSHEET_MAP_FIELDVALUE_FIELD][spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD],
                                                               tag[spreadsheettypes.SPREADSHEET_MAP_FIELDVALUE_FIELD][spreadsheettypes.SPREADSHEET_MAP_COL_FIELD])
                                fieldLabel = JsonDataSheet.generateValidJsonFieldName(fieldLabel)

                                if fieldLabel is None:
                                    fieldLabel = "Value not Specified, None"
                                if fieldValue is None:
                                    fieldValue = "Value not Specified, None"
                                if fieldLabel is not None and fieldValue is not None:
                                    indexOnDict[fieldLabel] = fieldValue

                            # fieldLabelCheck1 = fieldLabel in indexOnDict
                            # try:
                            #     fieldLabelCheck2 = fieldLabel in datasheet[sheetKey][rowNum - dataStartRow -1]
                            # except:
                            #     pass

                            datasheet[sheetKey].append(indexOnDict)
                            rowNum += 1

                        else:
                            datasheet[sheetKey].append(indexOnDict)
                            rowNum += 1

                self._worksheetSectionIndexWritten = True

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getDatasheetDict(self, datasheet, sheetKey, key, value):
        """
        Returns an object (dictionary or list) that contains the nodes for the datasheet subdocument referenced in the key/value parameters.  This is used
        to look up existing indices.

        Args:
            datasheet (dict): The output datasheet.
            sheetKey (string): Key name for the worksheet subtree to retrieve.
            key (string): Key name for the sub-item to return from the worksheet subtree.
            value (object): The value object for lookup.

        Returns:
            _type_: _description_
        """
        try:

            sheet = datasheet[sheetKey]

            if isinstance(sheet, list):
                for i in sheet:
                    v = i[key]
                    if v == value:
                        return i

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getDatasheetDictGroupBy(self, datasheet, sheetKey, key, value, subHeader):
        try:

            sheet = datasheet[sheetKey]

            if isinstance(sheet, list):
                for i in sheet:
                    v = i[key]
                    if v == value and subHeader not in i:
                        return i

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def updateDatasheetDict(self, datasheet, sheetKey, key, value, updatedDict, rowNum, dataStartOffset):
        """
        Updates the datasheet output subdocument with new/updated values.

        Args:
            datasheet (dict): the output datasheet.
            sheetKey (string): Key name for the worksheet subtree to update.
            key (string): Key name for the sub-item to return from the worksheet subtree.
            value (object): The value object for lookup.
            updatedDict (dict): The dictionary item to replace/update in the datasheet.
        """
        try:
            # idx = -1
            # foundIdx = -1

            # print(type(datasheet))

            # sheet = datasheet[sheetKey]

            # if isinstance(sheet, list):
            #     for i in sheet:
            #         idx += 1
            #         v = i[key]
            #         if v == value:
            #             foundIdx = idx
            #             break

            # if foundIdx >= 0:
            #     dictKeys = list(updatedDict)
            #     key = dictKeys[0]
            #     datasheetDict = datasheet[sheetKey][foundIdx]
            #     if(key in datasheet[sheetKey][foundIdx]):
            #         if(datasheetDict[key] != updatedDict[key]):
            #             dataArray = []
            #             dataArray.append(datasheetDict[key])
            #             dataArray.append(updatedDict[key])
            #             datasheet[sheetKey][foundIdx].update({key: dataArray})
            #     else:
            #         datasheet[sheetKey][foundIdx].update(updatedDict)
            dictKeys = list(updatedDict)
            key = dictKeys[0]
            rowNumindex = rowNum - dataStartOffset
            datasheetDict = datasheet[sheetKey][rowNumindex]
            if (key in datasheet[sheetKey][rowNumindex]):
                if (datasheetDict[key] != updatedDict[key]):
                    # dataArray = []
                    # dataArray.append(datasheetDict[key])
                    # dataArray.append(updatedDict[key])
                    # datasheet[sheetKey][rowNumindex].update({key: dataArray})
                    pass
            else:
                datasheet[sheetKey][rowNumindex].update(updatedDict)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    # returns a list containing  the field headers for a section and returns a list

    def getFieldHeadersForSection(self, wb, sheetName, section, map):
        """Returns a list containing the field headers for a section.

        Args:
            wb (object): The workbook object.
            sheetName (string): Worksheet name.
            section (dict): The parser rules for the current section.
            map (object): The parser rules for the worksheet.

        Raises:
            ConfigurationError: Error if parser rules are not found.

        Returns:
            list: List containing the field headers for a section.
        """
        try:
            # ExceptionLogger.logDebug(__name__,"section:",section)

            spans = map.getSpansColumns(section)

            # ExceptionLogger.logDebug(__name__,"spans:",spans)
            # ExceptionLogger.logDebug(__name__,"section:",section)

            if spans is not None:

                spanHeader = []
                fieldHeaderObj = map.getFieldHeaders(section)
                fieldHeaderRow = map.getRow(fieldHeaderObj)

                for i in range(len(spans)):
                    col = spans[i]
                    isMerge = self.isMerged(wb, fieldHeaderRow, col)
                    if (isMerge):
                        data = self.getCellValueIfMerged(wb, fieldHeaderRow, col)
                    else:
                        data = self.getCellValue(wb, sheetName, fieldHeaderRow, col)
                    # if(headerProperties["merged"]):
                    #     spanHeader.append(spanHeader[-1])
                    fieldHeader = self.format.format_name_spreadsheet(data)
                    # fieldHeader = JsonDataSheet.generateValidJsonFieldName(data)
                    if fieldHeader not in spanHeader:
                        spanHeader.append(fieldHeader)
                    else:
                        spanHeader.append(fieldHeader + '_repeated_' + col + '_' + str(i))

                return spanHeader
            else:
                # expecting at east one span
                s = t('No spans found in map file.  Map file and a section must have at least 1 span')
                d = map._mapFileName
                raise ConfigurationError(s, d)

            # ExceptionLogger.logDebug(__name__,"spanHeader:",spanHeader)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getFieldHeaderList(self, wb, sheetName, itemHeaderDictList):  # itemHeaderDictList is list of {row:n,col:a} items
        """Returns a list containing field headers for a worksheet.  These headers are used to generate the field names in the resulting datasheet.

        Args:
            wb (object): Workbook object.
            sheetName (string): Current worksheet name.
            itemHeaderDictList (dict): The dictionary containing the field headers.

        Returns:
            list: Contains the field headers.
        """

        json_field_names = []
        try:

            # ExceptionLogger.logDebug(__name__,"itemHeaderDictList=",itemHeaderDictList)
            for i in itemHeaderDictList:
                # fieldName = JsonDataSheet.generateValidJsonFieldName(self.getCellValue(wb,sheetName,
                #                                                                        i[spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD],
                #                                                                        i[spreadsheettypes.SPREADSHEET_MAP_COL_FIELD]))

                fieldName = self.getCellValue(wb, sheetName, i[spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD],
                                              i[spreadsheettypes.SPREADSHEET_MAP_COL_FIELD])

                if spreadsheettypes.SPREADSHEET_MAP_VALUE_COLUMN_FIELD in i:
                    if len(i[spreadsheettypes.SPREADSHEET_MAP_VALUE_COLUMN_FIELD]):
                        fieldValue = self.getCellValue(wb, sheetName, i[spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD],
                                                       i[spreadsheettypes.SPREADSHEET_MAP_VALUE_COLUMN_FIELD]).strip()
                        # if there is a field value, append
                        if len(fieldValue) > 0:
                            fieldName += fieldValue

                # ExceptionLogger.logDebug(__name__,"fieldName=",fieldName)
                jsonFieldName = JsonDataSheet.generateValidJsonFieldName(fieldName)
                json_field_names.append(jsonFieldName)

            return json_field_names

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def processSpanValuesForIndexedSection(self, datasheet, sheetKey, wb, sheetName, section, spans, fieldHeaders, indexOn, rowNumber, rowValues, map, dataStartOffset, rowNumTracker):
        """
        Processing loop for the spans within an indexed section.

        Args:
            datasheet (dict): datasheet output document.
            sheetKey (string): worksheet key.
            wb (object): workbook object_
            sheetName (string): name of current worksheet
            section (dict): describes processing rules within the map file for a section.
            spans (list): list of columns to process in the curent section
            fieldHeaders (list): field headers to use in writing datasheet
            indexFieldName (string): field name of the index.
            rowValues (object): a row of values from the worksheet
            map (dict): parser rules for the worksheet
        """
        try:
            if indexOn is not None:
                columnIndex = -1

                colsToIgnore = map.getColsToIgnore(sheetName)
                ignoreBlanksFlag = map.ignoreBlanks(sheetName)
                header = map.getValue(spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD, indexOn)
                indexOnRow = indexOn[spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD][spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD]
                indexOnCol = indexOn[spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD][spreadsheettypes.SPREADSHEET_MAP_COL_FIELD]
                headerCol = map.getValue(spreadsheettypes.SPREADSHEET_MAP_COL_FIELD, header)

                # dataStartRow = map.getValue(spreadsheettypes.SPREADSHEET_MAP_DATA_START_ROW_FIELD, indexOn)
                indexFieldName = JsonDataSheet.generateValidJsonFieldName(self.getCellValue(wb, sheetName, indexOnRow, indexOnCol))

                if spans is not None and len(spans) > 0:
                    for s in spans:
                        if s in colsToIgnore:
                            columnIndex += 1
                            pass
                        else:
                            val = None
                            itemDict = None
                            groupBy = None
                            groupByItemHeaderDictList = None
                            groupByItemHeaders = None
                            itemSubDict = None
                            deepKey = None
                            newDict = None
                            itemKeyName = None
                            columnIndex += 1

                            val = self.getColValueFromRow(rowValues, s, wb, rowNumber)

                            # if val is None:
                            #     val = spreadsheettypes.SPREADSHEET_MAP_EMPTY_VAL
                            if ignoreBlanksFlag is True and len(str(val).strip()) == 0:
                                pass
                            elif ((val is not None) and (len(str(val)) > 0)):
                                # this is the value from the key value pair to look up in the generated datasheet

                                # if isinstance(val, str):
                                #     val = val.strip()

                                #     val = val.replace('\n', '')

                                indexValue = self.getColValueFromRow(rowValues, headerCol, wb, rowNumber)

                                # itemDict is the subdocument containing the key.

                                # check whether this is item is in a GroupBy.  If it is, get the subdocument and insert new value
                                groupBy = map.getGroups(section)
                                # groupByList = SpreadsheetMap.getGroupBySpansList(section)

                                if groupBy is None:
                                    itemDict = self.getDatasheetDict(datasheet, sheetKey, indexFieldName, indexValue)

                                if groupBy is not None:

                                    if SpreadsheetMap.columnInGroupByList(s, groupBy):

                                        # Build the header list for the subdocument field names to be added
                                        groupByItemHeaderDictList = SpreadsheetMap.getGroupByItemHeaderDictList(groupBy)
                                        groupByItemHeaders = self.getFieldHeaderList(
                                            wb, sheetName, groupByItemHeaderDictList)  # get a list of the item headers

                                        # itemDict = self.getDatasheetDictGroupBy(datasheet, sheetKey, indexFieldName, indexValue, groupByItemHeaders[0])
                                        itemDict = datasheet[sheetKey][rowNumTracker]

                                        itemSubDict = itemDict.get(groupByItemHeaders[0])  # get from a dictionary

                                        # see if there is a subgroup in the itemDict
                                        if itemSubDict is not None:

                                            # itemSubDict already exists so append the current key/value pair to the subdocument
                                            # the document already exists, but when we pull this back, it is missing the top level padParameters key add it back in
                                            itemSubDict = dict({groupByItemHeaders[0]: itemSubDict})

                                            deepKey = ""
                                            for g in groupByItemHeaders:
                                                deepKey = deepKey + g + '.'
                                            deepKey = deepKey + fieldHeaders[columnIndex]

                                        else:

                                            # No subdictionary found
                                            # Create an empty dictionary with the top level groupby header
                                            itemSubDict = dict({})

                                            deepKey = ""
                                            for g in groupByItemHeaders:
                                                deepKey = deepKey + g + '.'
                                            deepKey = deepKey + fieldHeaders[columnIndex]

                                            if len(groupByItemHeaders) > 0:
                                                for ih in groupByItemHeaders[1::]:

                                                    newDict = dict({ih: {}})
                                                    self.insertNestedDictionary(itemSubDict, newDict, groupByItemHeaders, groupByItemHeaders[0])

                                        self.set(itemSubDict, deepKey, val)

                                        # save the subdocument back to the index
                                        itemKeyName = groupByItemHeaders[0]
                                        itemDict[itemKeyName] = itemSubDict[itemKeyName]

                                    else:

                                        # Not a groupBy Element
                                        itemDict[fieldHeaders[columnIndex]] = val

                                else:
                                    # this is not a groupBy element so just add it
                                    # New value will be inserted into the subdocument and the datasheet updated

                                    if val is not None and len(str(val)) > 0:

                                        # ExceptionLogger.logDebug(__name__,"fieldHeaders=",fieldHeaders)
                                        # ExceptionLogger.logDebug(__name__,"columnIndex=",columnIndex)
                                        # ExceptionLogger.logDebug(__name__,"itemDict=",itemDict)
                                        itemDict = dict({fieldHeaders[columnIndex]: val})

                                if itemDict is not None:

                                    self.updateDatasheetDict(datasheet, sheetKey, indexFieldName, indexValue, itemDict, rowNumber, dataStartOffset)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def processSpanValuesForNonIndexedSection(self, datasheet, sheetKey, wb, sheetName, section, spans, fieldHeaders, rowNumber, rowValues, map):
        """
        Processing loop for the spans within a non-indexed section (no key row).

        Args:
            datasheet (dict): datasheet output document.
            sheetKey (string): worksheet key.
            wb (object): workbook object_
            sheetName (string): name of current worksheet
            section (dict): describes processing rules within the map file for a section.
            spans (list): list of columns to process in the curent section
            fieldHeaders (list): field headers to use in writing datasheet
            indexFieldName (string): field name of the index.
            rowValues (object): a row of values from the worksheet
            map (dict): parser rules for the worksheet
        """
        try:

            columnIndex = -1

            # dataStartRow = map.getValue(spreadsheettypes.SPREADSHEET_MAP_DATA_START_ROW_FIELD, section)
            # maxRows = map.getValue(spreadsheettypes.SPREADSHEET_MAP_MAX_ROWS_FIELD, section)
            itemSubDict = dict({})

            # ExceptionLogger.logDebug(__name__,"fieldHeaders=",fieldHeaders)

            if spans is not None and len(spans) > 0:
                for i in range(len(spans)):
                    s = spans[i]
                    val = None
                    groupBy = None
                    groupByItemHeaderDictList = None
                    groupByItemHeaders = None
                    deepKey = None
                    newDict = None
                    # itemKeyName = None
                    columnIndex += 1

                    val = self.getColValueFromRow(rowValues, s)

                    st = "Cell " + str(s) + str(rowNumber + 1) + ' value='
                    ExceptionLogger.logDebug(__name__, st, val)

                    if val is not None or len(str(val)) < 1:
                        ExceptionLogger.logDebug(__name__, "No value retrieved so will check and see if this is a merged cell..")
                        # No value retrieved so check if this is a merged cell.
                        if self.isMerged(wb, rowNumber + 1, s):
                            ExceptionLogger.logDebug(__name__, "This is a MERGED Cell, so we will attempt to get the value from the merged cell.")
                            val = self.getCellValueIfMerged(wb, rowNumber + 1, s)
                            ExceptionLogger.logDebug(__name__, "MERGED CELL,val=", val)

                    if ((val is not None) and (len(str(val)) > 0)):

                        if isinstance(val, str):
                            val = val.strip()

                            val = val.replace('\n', '')

                        # check whether this is item is in a GroupBy.  If it is, get the subdocument and insert new value
                        groupBy = map.getGroups(section)
                        # groupByList = SpreadsheetMap.getGroupBySpansList(section)

                        if groupBy is not None:
                            if SpreadsheetMap.columnInGroupByList(s, groupBy):

                                # Build the header list for the subdocument field names to be added
                                groupByItemHeaderDictList = SpreadsheetMap.getGroupByItemHeaderDictList(groupBy)
                                groupByItemHeaders = self.getFieldHeaderList(
                                    wb, sheetName, groupByItemHeaderDictList)  # get a list of the item headers

                                deepKey = ""
                                for g in groupByItemHeaders:
                                    deepKey = deepKey + g + '.'
                                deepKey = deepKey + fieldHeaders[columnIndex]

                                if len(groupByItemHeaders) > 0:
                                    for ih in groupByItemHeaders[1::]:

                                        newDict = dict({ih: {}})
                                        self.insertNestedDictionary(itemSubDict, newDict, groupByItemHeaders, groupByItemHeaders[0])

                                self.set(itemSubDict, deepKey, val)

                                # save the subdocument back to the index
                                # itemKeyName = groupByItemHeaders[0]
                                # ExceptionLogger.logDebug(__name__,"Adding itemSubDict[filedHeaders[columnIndex]]=",itemSubDict)
                                # itemSubDict[fieldHeaders[columnIndex]] = val
                            else:
                                # Not a groupBy Element
                                dbgStr = "not a GroupByElement:  fieldHeaders[columnIndex]=" + fieldHeaders[columnIndex] + ", val="
                                ExceptionLogger.logDebug(__name__, dbgStr, val)
                                itemSubDict[fieldHeaders[columnIndex]] = val
                        else:
                            # This is not a groupByElement
                            dbgStr = "GroupBy is None:  fieldHeaders[columnIndex]=" + fieldHeaders[columnIndex] + ", val="
                            ExceptionLogger.logDebug(__name__, dbgStr, val)
                            itemSubDict[fieldHeaders[columnIndex]] = val
                            # #this is not a groupBy element so just add it
                            # #New value will be inserted into the subdocument and the datasheet updated
                            # ExceptionLogger.logDebug(__name__,"itemSubDict[filedHeaders[columnIndex]]=",itemSubDict)
                            # ExceptionLogger.logDebug(__name__,"itemSubDict=",itemSubDict)
                            # ExceptionLogger.logDebug(__name__,"datasheet[sheetkey]=",datasheet[sheetKey])
                            # ExceptionLogger.logDebug(__name__,"itemSubDict=",itemSubDict)

                            # ExceptionLogger.logDebug(__name__,"datasheet[sheetKey]=",datasheet[sheetKey])
                    else:
                        # value is none
                        dbgStr = "val is NOT None so will see if " + s + str(rowNumber) + ' is a merged cell.  Val='
                        ExceptionLogger.logDebug(__name__, dbgStr, val)
                        # see if this is a merged cell
                        if self.isMerged(wb, rowNumber, s):
                            ExceptionLogger.logDebug(__name__, "MERGED CELL")

                if itemSubDict is not None and len(itemSubDict) > 0:
                    datasheet[sheetKey].append(itemSubDict)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def addSectionColumnsToDatasheet(self, datasheet, sheetKey, wb, sheetName, section, fieldHeaders, rowNum, rowValues, map, dataStartOffset, rowNumTracker):
        """The main method that adds columns in a section to a datasheet.   This is one of the key functions in datasheet production from spreadsheets.

        Args:
            datasheet (dict): the output datasheet.
            sheetKey (string): the key name for the worksheet output in the datasheet.
            wb (object): workbook object.
            sheetName (string): worksheet name.
            section (dict): parsing rules for the current section
            fieldHeaders (list): contains the field headers (field names) for the column data.
            rowValues (object): a row object containing data to be written to the datasheet.
            map (dict): parsing rules for the workbook.
        """
        try:

            # columnIndex = -1
            # colLetter = ""
            indexOn = map.getIndexOn(section)
            spans = map.getSpansColumns(section)

            if indexOn is not None:

                # Write the row values for a section that is indexed
                self.processSpanValuesForIndexedSection(datasheet, sheetKey, wb, sheetName, section,
                                                        spans, fieldHeaders, indexOn, rowNum, rowValues, map, dataStartOffset, rowNumTracker)
            else:
                # Section is not indexed so process each row
                self.processSpanValuesForNonIndexedSection(datasheet, sheetKey, wb, sheetName, section,
                                                           spans, fieldHeaders, rowNum, rowValues, map)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def insertNestedDictionary(self, currentDict, newDict, keyList, name):
        """A recursive function that inserts a dictionary object at the lowest level within the referenced dictionary object.

        Args:
            currentDict (dict): current document.
            newDict (dict): dictionary item to insert at lowest/deepest level.
            keyList (list): a list of keys in the current dictionary.
            name (string): used by recursive function to traverse  dictionary.
        """
        try:
            key_in_dict = None
            for key in keyList:
                if key in currentDict:
                    key_in_dict = key
                break
            if key_in_dict is not None:
                self.insertNestedDictionary(currentDict[key_in_dict], newDict, keyList, name)
            else:
                currentDict[name] = newDict
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def depth(self, d):
        """Returns the depth of the referenced dictionary.

        Args:
            d (dict): dictionary to traverse.

        Returns:
            number: integer value indicating depth.
        """

        try:
            queue = deque([(id(d), d, 1)])
            memo = set()
            while queue:
                id_, o, level = queue.popleft()
                if id_ in memo:
                    continue
                memo.add(id_)
                if isinstance(o, dict):
                    queue += ((id(v), v, level + 1) for v in o.values())

            return level
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def set(self, d, key, value):
        """Sets a key/value in a dictionary

        Args:
            d (dict): a dictionary.
            key (string): specifies value of a key/value pair to set.
            value (object): the value to set.
        """

        # ExceptionLogger.logDebug(__name__,"Inside set",value)

        dd = d
        keys = key.split('.')
        latest = keys.pop()
        for k in keys:
            dd = dd.setdefault(k, {})
        dd.setdefault(latest, value)
        # ExceptionLogger.logDebug(__name__,"",value)

    def findDeepestKey(self, data):
        """Returns the key of the deepest subdictionary

        Args:
            data (dict): a dictionary to traverse.

        Returns:
            string: the key of the deepest dictionary item.
        """
        try:
            if not any([isinstance(data.get(k), dict) for k in data]):
                return data
            else:
                for dkey in data:
                    if isinstance(data.get(dkey), dict):
                        return self.findDeepestKey(data.get(dkey))
                    else:
                        continue
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def parseSection(self, datasheet, sheetKey, wb, sheetName, section, map):
        """Main processing for an individual section.

        Args:
            datasheet (dict): the output datasheet.
            sheetKey (string): the key for the section in the datasheet.
            wb (object): a workbook object.
            sheetName (string): the name of the current worksheet.
            section (dict): parser rules for the current section.
            map (dict): parser rules for the workbook.

        Raises:
            ConfigurationError: returned if at least one section is not found.
        """
        try:
            # orientation = spreadsheettypes.SPREADSHEET_MAP_ORIENTATION_FIELD
            # header = None
            # headerRow = None
            # headerCol = None
            dataStartRow = None
            # groupList = []
            maxRows = datasheetconstants.DATASHEET_DEFAULT_MAX_ROWS
            # headerFieldName = None

            if section is not None:

                fieldHeaders = self.getFieldHeadersForSection(wb, sheetName, section, map)
                # ExceptionLogger.logDebug(__name__,"fieldHeaders:",fieldHeaders)

                # returns a list of the groupBy entries for the current section
                # groupList = self.parseGroups(section, map)  # get the groups in a section

                indexOn = map.getIndexOn(section)
                # ExceptionLogger.logDebug(__name__,"indexOn:",indexOn)

                # Check whether an indexOn was specified
                if indexOn is not None:
                    # header = map.getValue(spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD, indexOn)
                    indexOnRow = indexOn[spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD][spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD]
                    indexOnCol = indexOn[spreadsheettypes.SPREADSHEET_MAP_HEADER_FIELD][spreadsheettypes.SPREADSHEET_MAP_COL_FIELD]
                    # headerCol = map.getValue(spreadsheettypes.SPREADSHEET_MAP_COL_FIELD, header)
                    # indexFieldName = JsonDataSheet.generateValidJsonFieldName(self.getCellValue(wb, sheetName, indexOnRow, indexOnCol))
                    maxRows = map.getValue(spreadsheettypes.SPREADSHEET_MAP_MAX_ROWS_FIELD, indexOn)
                    # ExceptionLogger.logDebug(__name__,"indexFieldName=",indexFieldName)
                    dataStartRow = map.getValue(spreadsheettypes.SPREADSHEET_MAP_DATA_START_ROW_FIELD, indexOn)

                    # ExceptionLogger.logDebug(__name__, "Checking to see if we need to write the index")
                    # if len(datasheet[sheetKey])<1:
                    if self._indexOnRow != indexOnRow or self._indexOnCol != indexOnCol:

                        self._indexOnRow = indexOnRow
                        self._indexOnCol = indexOnCol

                        # ExceptionLogger.logDebug(__name__,"++++++WRITING the Index For This Sheet",datasheet)

                        # add the indexOn dictionary to the datasheet
                        self.serializeIndex(datasheet, sheetKey, wb, sheetName, section, map)

                        # ExceptionLogger.logDebug(__name__,"++++++AFTER WRITING the Index For This Sheet",datasheet)

                    rowNumTracker = self.getRowNumberTracker(wb, map, section, datasheet, sheetKey, sheetName)
                    dataStartOffset = dataStartRow - 1
                    rowNum = dataStartOffset
                    rowsToIgnore = map.getRowsToIgnore(sheetName)
                    # dsRowIdx = -1

                else:
                    # IndexOn was not found so just process each row/column
                    dataStartRow = map.getValue(spreadsheettypes.SPREADSHEET_MAP_DATA_START_ROW_FIELD, section)
                    if dataStartRow is None:
                        dataStartRow = datasheetconstants.DATASHEET_DEFAULT_DATASTART
                    maxRows = map.getValue(spreadsheettypes.SPREADSHEET_MAP_MAX_ROWS_FIELD, section)
                    if maxRows is None:
                        maxRows = datasheetconstants.DATASHEET_DEFAULT_MAX_ROWS
                    dataStartOffset = dataStartRow - 1
                    rowNum = dataStartOffset
                    # ExceptionLogger.logDebug(__name__,"IndexOn not found so processing rows")
                while rowNum < (maxRows + dataStartRow):

                    # ExceptionLogger.logDebug(__name__,"++++++++++++++++++++++++++New Row.   Row Number=",rowNum)
                    if indexOn is not None:
                        if rowNum + 1 in rowsToIgnore:
                            rowNum += 1
                            continue

                    rowValues = self.getRow(wb, sheetName, rowNum)

                    if rowValues is not None:

                        # add the columns identified in the section configuration
                        if indexOn is not None:
                            self.addSectionColumnsToDatasheet(datasheet, sheetKey, wb, sheetName, section, fieldHeaders, rowNum, rowValues, map, dataStartOffset, rowNumTracker)
                            rowNumTracker += 1
                        else:
                            self.addSectionColumnsToDatasheet(datasheet, sheetKey, wb, sheetName, section, fieldHeaders, rowNum, rowValues, map, dataStartOffset, rowNumTracker=None)
                    else:
                        break

                    rowNum += 1

                    # ExceptionLogger.logDebug(__name__,"---------------------End of Row Number=",rowNum-1)

            else:
                # did not find a section, raise an error
                s = t('Expected item not found')
                d = str(spreadsheettypes.SPREADSHEET_MAP_INDEX_ON_FIELD)
                raise ConfigurationError(s, d)

                # groups = map.getGroups(section)  # get the groups in a section

            # ExceptionLogger.logDebug(__name__,"datasheet=",datasheet)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getRowNumberTracker(self, wb, map, section, datasheet, sheetKey, sheetName):
        try:
            tagList = map.getIncludeTagsDictionaryList(section)
            if tagList is None:
                return 0
            elif tagList is not None and len(tagList) > 0:
                for tag in tagList:
                    fieldLabel = self.getCellValue(wb, sheetName,
                                                   tag[spreadsheettypes.SPREADSHEET_MAP_FIELDLABEL_FIELD][spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD],
                                                   tag[spreadsheettypes.SPREADSHEET_MAP_FIELDLABEL_FIELD][spreadsheettypes.SPREADSHEET_MAP_COL_FIELD])
                    fieldValue = self.getCellValue(wb, sheetName,
                                                   tag[spreadsheettypes.SPREADSHEET_MAP_FIELDVALUE_FIELD][spreadsheettypes.SPREADSHEET_MAP_ROW_FIELD],
                                                   tag[spreadsheettypes.SPREADSHEET_MAP_FIELDVALUE_FIELD][spreadsheettypes.SPREADSHEET_MAP_COL_FIELD])
                    fieldLabel = JsonDataSheet.generateValidJsonFieldName(fieldLabel)
                    for i in range(len(datasheet[sheetKey])):
                        if fieldLabel in datasheet[sheetKey][i] and (datasheet[sheetKey][i][fieldLabel] == fieldValue):
                            rowNumTracker = i
                            return rowNumTracker
            return rowNumTracker
        except Exception:
            return 0

    def parseGroups(self, jsonObj, map):
        """Main processing method for a data grouping within a section.  This enables fields to be grouped under sub-documents.

        Args:
            jsonObj (dict): parser rules for the section.  These may contain optional groupBy elements.
            map (dict): parser rules for the worksheet.

        Returns:
            list: a list of groupBy elements.
        """
        parsed_groups = []
        try:
            groups = map.getGroups(jsonObj)

            if ((groups is not None) and (len(groups) > 0)):
                for group in groups:
                    parsed_groups.append(group)

            # debug message
            # ExceptionLogger.logDebug(__name__,"Groups:", groups)
            return parsed_groups

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def parseGroup(self, datasheet, wb, sheetName, group, map):
        """Main processing meethod for an individual grouping (groupBy).

        Args:
            datasheet (dict): the output datasheet.
            wb (object): the workbook.
            sheetName (string): the worksheet name.
            group (dict): a grouping rule.
            map (dict): the parser rules for the current workbook/worksheet.
        """
        try:
            pass
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
