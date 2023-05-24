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
import edatasheets_creator.constants.xmltagconstants as tag_c


class XMLValidator:
    def __init__(self):
        pass

    def check_for_valid_xml(self, Element):
        all_xml_tags = self.get_all_tags(Element)
        result = all(elem in tag_c.TAG_LIST for elem in all_xml_tags)
        return result

    def get_all_tags(self, Element):
        elemList = []
        for elem in Element.iter():
            elemList.append(elem.tag)

        elemList = list(set(elemList))
        return elemList
