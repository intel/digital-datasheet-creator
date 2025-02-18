#  ********************** COPYRIGHT INTEL CORPORATION ***********************,

#  THE SOFTWARE CONTAINED IN THIS FILE IS CONFIDENTIAL AND PROPRIETARY,
#  TO INTEL CORPORATION. THIS PRINTOUT MAY NOT BE PHOTOCOPIED,,
#  REPRODUCED, OR USED IN ANY MANNER WITHOUT THE EXPRESSED WRITTEN,
#  CONSENT OF INTEL CORPORATION. ALL LOCAL, STATE, AND FEDERAL,
#  LAWS RELATING TO COPYRIGHTED MATERIAL APPLY.,

#  Copyright (c), Intel Corporation,

#  ********************** COPYRIGHT INTEL CORPORATION ***********************


from typing import Optional
from edatasheets_creator.constants.datasheetconstants import DATASHEET_COMPONENT_COMMON_MAPPING, DATASHEET_MACRO_MAPPING

class ExcelUtilities:
    
    _instance = None
    sheetName = ''
    allowedSpecialCharacters = ['+']

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ExcelUtilities, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def updateSheetName(self, newSheetName: str) -> None:
        """
        Update current sheet name that it is processing
        
        :params newSheetName:
        
        :returns: 
        
        """
        self.sheetName = newSheetName
        
    def getPropertyValueFromDatasheetComponentCommonMapping(self, dictKey: str) -> Optional[str]:
        """
        Get property value from DATASHEET_COMPONENT_COMMON_MAPPING using sheet name as a first level and then
        the dictKey param as a second level to get the correct value
        The value expected is the name of the json schema where this property was defined
        In case the property is not found, check if it is a macro
        
        :params dictKey:
        
        :returns:
        
        """
        
        return DATASHEET_COMPONENT_COMMON_MAPPING.get(self.sheetName, {}).get(dictKey) or DATASHEET_MACRO_MAPPING.get(dictKey)