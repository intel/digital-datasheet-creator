import pathlib
import json
import re

from edatasheets_creator.utility.path_utilities import validateRealPath
from edatasheets_creator.constants import fieldnameconstants
from edatasheets_creator.constants import serializationconstants
from edatasheets_creator.functions import t

from edatasheets_creator.document.jsondatasheetschema import JsonDataSheetSchema

from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.constants import translatorconstants as c


class Plugin:

    """
    Translator class plugin class that implements datasheet generation from an XLSX
    """

    def __init__(self):
        """
        Class initialization
        """
        self._fileName = ""
        self._outputFileName = ""
        self._targetVocabulary = ""
        self._targetVocabularyFileObject = ""

        # sys.stdout = open('debug.txt', 'w')

    def __del__(self):

        if self._targetVocabularyFileObject:
            self._targetVocabularyFileObject.close()
        # sys.stdout.close()

    def process(self, inputFileName, outputFileName, targetVocabulary=""):
        """
        Plugin process method that is called generically

         Args:
            inputFileName (Posix Path): Posix Path for input file
            outputFileName (Posix Path): Posix Path for output file.
            targetVocabulary string: A translation target specified in translatorconstants.py
        Returns:
            object: The object could be a list, a string, a number or a dictionary so it is suggested to check the type of the returned object.

        """

        datasheet = {}

        try:
            self._fileName = inputFileName
            self._outputFileName = outputFileName
            self._targetVocabulary = targetVocabulary

            msg = t("Plugin is loaded") + ":  " + t(c.PLUGIN_DESC) + "..."
            ExceptionLogger.logInformation(__name__, msg)

            # Validate if the input files exists on the system as they are required
            if (not validateRealPath(inputFileName)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\nInput file does not exists"))
                print()
                return

            # Check the file type (must be JSON)
            fileExtension = pathlib.Path(inputFileName).suffix.lower()
            if not self._isJsonFileType(fileExtension):
                msg = t("Input file must be a JSON file") + ":  " + inputFileName
                ExceptionLogger.logError(__name__, msg)
                return

            if self._targetVocabulary == "":
                msg = t("\nNo translation target specified")
                ExceptionLogger.logInformation(__name__, msg)
                return
            else:
                ExceptionLogger.logInformation(__name__, t("\n\nProcessing") + ":  " + str(inputFileName) + "...\n")
                # fileDetails = os.path.splitext(outputFileName)
                self.loadVocabulary()  # Load the vocabulary file
                self.performPluginAction(datasheet)  # Perform plugin-specific processing

                strMsg = "\n\n" + t("Writing") + " " + str((self._outputFileName)) + "...\n"
                ExceptionLogger.logInformation(__name__, strMsg)

                # self._outputFileName = fileDetails[0] + '-' + self._translatedFileNameSubstring + '.' + serializationconstants.JSON_FILE_EXTENSION
                # pretty print JSON, preserving unicode characters
                with open(self._outputFileName, "w", encoding='utf-8') as outfile:
                    json.dump(datasheet, outfile, ensure_ascii=False, indent=serializationconstants.JSON_INDENT_DEFAULT)
                    outfile.close()

                # write the schema
                schema = JsonDataSheetSchema(self._outputFileName)
                schema.write()

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def performPluginAction(self, datasheet):
        """
        Performs the plugin-specific processing
        """

        try:
            with open(self._fileName, 'r', encoding='utf-8') as f:
                fileToTranslate = json.load(f)  # Load the file into an object

                self._fileToTranslate = fileToTranslate

                self.translate(datasheet, fileToTranslate)

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

    def translate(self, datasheet, jsonStr):

        if isinstance(jsonStr, dict):

            for k, v in jsonStr.items():
                vKey = self.findVocabularyKey(k)
                if vKey is not None:
                    k = vKey

                if isinstance(v, list):

                    fieldList = []
                    for i in v:
                        if (isinstance(i, str)):
                            fieldList.append(i)
                        else:
                            datasheetSubDict = {}
                            subDatasheet = self.translate(datasheetSubDict, i)
                            fieldList.append(subDatasheet)

                    datasheet[k] = fieldList

                elif isinstance(v, dict):
                    datasheet[k] = {}
                    self.translate(datasheet[k], v)
                else:
                    datasheet[k] = v
        elif isinstance(jsonStr, list):
            print("The json str is a list so we have to turn the list into a dict first.  Implementation not completed yet.")

        return datasheet

    def findVocabularyKey(self, val):

        retVal = None

        try:
            for vocabEntry in self._vocabularyList:
                vE = dict(vocabEntry)
                firstKey = list(vE.keys())[0]

                if val in vE:
                    retVal = firstKey
                    return retVal
                else:
                    vL = vE.get(firstKey)
                    for i in range(len(vL)):
                        vL[i] = vL[i].lower()

                    if val.lower() in vL:
                        retVal = firstKey
                        return retVal

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return retVal

    def iterateNestedDict(self, data_dict):

        for key, value in data_dict.items():

            if isinstance(value, dict):
                for key_value in self.iterateNestedDict(value):
                    yield (key, *key_value)
            else:
                yield (key, value)

    def loadVocabulary(self):
        """Loads the translation vocabulary file.
        """

        try:

            with open(self._targetVocabulary, 'r') as self._targetVocabularyFileObject:
                vocabularyFile = json.load(self._targetVocabularyFileObject)  # Load the file into a python object
                self._vocabularyFile = vocabularyFile

                # Get Sheet Map File Metadata - The map file indicates where data exists and how to organize
                self._description = vocabularyFile[c.DESCRIPTION_FIELD_NAME]
                self._guid = vocabularyFile[c.GUID_FIELD_NAME]
                self._specificationName = vocabularyFile[c.SPECIFICATION_FIELD_NAME]
                self._translatedFileNameSubstring = self.generateSpecificationName(self._specificationName)
                self._uri = vocabularyFile[c.URI_FIELD_NAME]
                self._automationUri = vocabularyFile[c.AUTOMATION_URI_FIELD_NAME]
                self._vocabularyList = vocabularyFile[c.VOCABULARY_FIELD_NAME]

            return
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

    # Check spreadsheet type
    def _isJsonFileType(self, ext):

        bln = False

        try:
            bln = ext in c.pluginExtensions.values()

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return bln

    def generateSpecificationName(self, specString):
        """
        Generates a string based on the specification name for use in file naming,
        Args:
            fieldName (string): field name used in JSON fieldName generation.

        Returns:
            string: a valid file name substring component.
        """
        try:

            validFieldName = specString.strip()
            encodedString = validFieldName.encode("ascii", "ignore")
            validFieldName = encodedString.decode()

            # remove items between parentheses
            validFieldName = re.sub(r"\([^()]*\)", "", validFieldName)

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
            validFieldName = validFieldName.lower()

            return validFieldName

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
