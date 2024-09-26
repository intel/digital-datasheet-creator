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
