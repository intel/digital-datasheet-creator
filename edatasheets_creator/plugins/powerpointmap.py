import json
from edatasheets_creator.constants import powerpointtypes
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class PowerPointMap:
    """
    PowerPoint Map class provides parser rule functionality used in creating datasheets from XLSX input files.
    """
    def __init__(self, mapFileName):
        self._mapFileName = mapFileName
        self.loadMap()

    def loadMap(self):
        """Loads the parser rule map file using the mapFileName instance variable that is set in the class initializer.
        """

        try:

            with open(self._mapFileName, 'r') as f:
                mapFile = json.load(f)  # Load the file into a python object
                self._mapFile = mapFile

                # Get Sheet Map File Metadata - The map file indicates where data exists and how to organize
                self._description = mapFile[powerpointtypes.POWERPOINT_MAP_DESCRIPTION_FIELD]
                self._guid = mapFile[powerpointtypes.POWERPOINT_MAP_GUID_FIELD]
                self._mapType = mapFile[powerpointtypes.POWERPOINT_MAP_MAPTYPE_FIELD]

                # Get Slide Details - this is the list of sheets that will be added to the datasheet
                self._slideDetails = mapFile[powerpointtypes.POWERPOINT_MAP_SLIDEDETAILS_FIELD]

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

    def getSlideDetails(self):
        return self._slideDetails

    def getPowerPointDescription(self):
        return self._description
