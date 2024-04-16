import os
import uuid


from datetime import date
from edatasheets_creator.constants import datasheetconstants
from edatasheets_creator.constants import fieldnameconstants
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class JsonDataSheet:
    """
    JsonDataSheet class.
    """

    def __init__(self, fileName):
        """
        Class initializer.

        Args:
            fileName (PosixPath): path to output file.
        """

        try:
            self._fileName = fileName
            self._datasheet = dict()

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def getDatasheet(self):
        """
        Returns the datasheet ouptut.

        Returns:
            dict: a JSON datasheet.
        """
        try:
            return self._datasheet
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    @staticmethod
    def generateGUID():
        """
        Generates a unique GUID.  This is used in the datasheet metadata generation.

        Returns:
            string: a guid.
        """
        return uuid.uuid4()

    @staticmethod
    def getCurrentDate():
        """
        Returns a string containing the current date. Thi sis used in the datasheet metadata generation.

        Returns:
            string: current date.
        """
        today = date.today()

        d = today.strftime("%m/%d/%Y")
        return d

    @staticmethod
    def setMetadata(title, description, inputFile):
        """
        Sets the datasheet metadatata.

        Args:
            title (string): datasheet title.
            description (string): datasheet description.
            inputFile (PosixPath): path to input file.

        Returns:
            dict: datasheet header.
        """

        datasheetHeader = dict()

        try:

            if (len(title) > 0):
                datasheetHeader[datasheetconstants.DATASHEET_TITLE_FIELD] = title
            else:
                datasheetHeader[datasheetconstants.DATASHEET_TITLE_FIELD] = datasheetconstants.DATASHEET_DEFAULT_TITLE

            if description is not None and (len(description) > 0):
                datasheetHeader[datasheetconstants.DATASHEET_DESCRIPTION_FIELD] = description
            else:
                datasheetHeader[datasheetconstants.DATASHEET_DESCRIPTION_FIELD] = datasheetconstants.DATASHEET_DEFAULT_DESCRIPTION

            if (len(str(inputFile)) > 0):
                datasheetHeader[datasheetconstants.DATASHEET_INPUT_FILE_FIELD] = os.path.basename(inputFile).strip()
            else:
                datasheetHeader[datasheetconstants.DATASHEET_INPUT_FILE_FIELD] = datasheetconstants.DATASHEET_DEFAULT_INPUT_FILE_FIELD

            datasheetHeader[datasheetconstants.DATASHEET_GUID_FIELD] = str(JsonDataSheet.generateGUID())

            datasheetHeader[datasheetconstants.DATASHEET_CREATION_DATE_FIELD] = JsonDataSheet.getCurrentDate()

            datasheetHeader[datasheetconstants.DATASHEET_NAMESPACE_FIELD] = datasheetconstants.DATASHEET_NAMESPACE
            datasheetHeader[datasheetconstants.DATASHEET_CREATION_BY_FIELD] = datasheetconstants.DATASHEET_CREATOR

            datasheetHeader[datasheetconstants.DATASHEET_PLATFORM_ABBREVIATION_FIELD] = datasheetconstants.DATASHEET_DEFAULT_INPUT_FILE_FIELD
            datasheetHeader[datasheetconstants.DATASHEET_SKU_FIELD] = datasheetconstants.DATASHEET_DEFAULT_INPUT_FILE_FIELD
            datasheetHeader[datasheetconstants.DATASHEET_REVISION_FIELD] = datasheetconstants.DATASHEET_DEFAULT_INPUT_FILE_FIELD

            return datasheetHeader

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    @staticmethod
    def generateValidJsonFieldName(fieldName):
        """
        Generates a valid JSON field name based on the argument passed.

        Args:
            fieldName (string): field name used in JSON fieldName generation.

        Returns:
            string: a valid JSON fieldName.
        """
        try:

            validFieldName = ""

            if fieldName is not None:

                if isinstance(fieldName, int):
                    fieldName = str(fieldName)

                validFieldName = fieldName.strip()
                encodedString = validFieldName.encode("ascii", "ignore")
                validFieldName = encodedString.decode()

                # remove items between parentheses
                # validFieldName = re.sub(r"\([^()]*\)", "", validFieldName)

                validFieldName = validFieldName.title()  # capitalize first letter of every word

                # character substitutions
                validFieldName = validFieldName.replace('\n', '')
                validFieldName = validFieldName.replace('.', '')
                validFieldName = validFieldName.replace('#', fieldnameconstants.FIELD_NAME_NUMBER)
                validFieldName = validFieldName.replace('_', '')
                validFieldName = validFieldName.replace('*', '')
                validFieldName = validFieldName.replace(':', '')
                validFieldName = validFieldName.replace('?', '')
                validFieldName = validFieldName.replace('/', '')
                validFieldName = validFieldName.replace('(', '')
                validFieldName = validFieldName.replace(')', '')

                if validFieldName[0] == '-':
                    validFieldName = validFieldName[1:]

                validFieldName = validFieldName.replace(' ', '')  # remove spaces
                validFieldName = validFieldName[0].lower() + validFieldName[1:]  # make first character lowercase

                validFieldName = validFieldName[0].lower() + validFieldName[1:]  # make first character lowercase

            return validFieldName

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
