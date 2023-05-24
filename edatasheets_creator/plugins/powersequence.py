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

import inspect
import os
import shutil
import json
import ast
import re
from pathlib import Path


class Plugin:
    """
    Power Sequence plugin class that converts sequence files into one consumable by WaveDrom Timing Editor
    """

    def __init__(self):
        """
        Class initialization
        """

    def __repr__(self):
        """
            Returns a name for the class

        Returns:
            string : class name
        """
        return __name__ + '.' + inspect.currentframe().f_code.co_name

    def process(self, inputFileName, outputFileName="", mapFileName=""):
        self.file_name = inputFileName
        self.output_file_name = outputFileName
        cond1 = self.file_name.endswith('.txt')
        cond2 = self.file_name.endswith('.json')
        if cond1:
            with open(self.file_name, "r") as f:
                self.json_string = f.read()
            self.convertToDict(formatter='txt')
            if self.file_name == 'temp.txt':
                os.remove('temp.txt')
        elif cond2:
            # base = os.path.splitext(self.file_name)[0]
            # self.file_name = base +  '.txt'
            self.file_name = 'temp.txt'
            if os.path.exists(self.file_name):
                self.__init__(self.file_name)
            else:
                file_dir = os.path.dirname(os.path.abspath(__file__))
                s = os.path.join(file_dir, inputFileName)
                shutil.copy(s, os.path.join(file_dir, "temp.json"))
                base = os.path.splitext('temp.json')[0]
                self.file_name = base + '.txt'
                os.rename('temp.json', base + '.txt')
                self.__init__(self.file_name)
        elif cond1 is False and cond2 is False:
            print('Only txt and json files can be parsed')

    def convertToDict(self, formatter):
        """
        :param formatter: formmatter takes in the extension of the file to be converted
        :return: an updated class dictionary with correct json fromat
        """
        if formatter.lower() == 'txt':
            string_output = self.convertToJson()
            # __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            # completeName = os.path.join(__location__, "myfile.txt")
            # file1 = open(completeName, "w")
            # file1.write(string_output)
            # file1.close()
            test = ast.literal_eval(string_output)
            movie_list_str = test.__str__().replace("'", '"')
            json_object = json.loads(movie_list_str)
            path = Path(self.file_name)
            if not self.output_file_name:
                self.output_file_name = str(path.parent) + "\\" + path.stem + ".json"
            self.updated_dict = ast.literal_eval(string_output)
            with open(self.output_file_name, "w", encoding="utf8") as output_json:
                json.dump(json_object, output_json, indent=2, ensure_ascii=False)
            
        elif formatter.lower() == 'json':
            with open(self.file_name) as f:
                self.updated_dict = json.load(f)

    def convertToJson(self):
        """

        :return: an updated string in correct json format
        """
        parsed_string = self.json_string.rstrip()
        updated_string = re.sub("\['tspan', {fill:'blue'},", " ", parsed_string)
        updated_string = re.sub("\['tspan', {fill:'black'},", " ", updated_string)
        updated_string = re.sub("\['tspan', {fill:'red'},", " ", updated_string)
        updated_string = re.sub("\['tspan', {fill:'orange'},", " ", updated_string)
        updated_string = re.sub('"],', '",', updated_string)
        updated_string = re.sub(r"^'", '"', updated_string)
        updated_string = re.sub(r"'$", '"', updated_string)
        updated_string = re.sub("'tspan'", '"tspan"', updated_string)
        # updated_string = re.sub("'", '"', updated_string)
        updated_string = re.sub("{\shead", '{"head"', updated_string)
        updated_string = re.sub("{\stext", '{"text"', updated_string)
        updated_string = re.sub("{\ssignal", '{"signal"', updated_string)
        updated_string = re.sub("{\sname", '{"name"', updated_string)
        updated_string = re.sub("{\swave", '{"wave"', updated_string)
        updated_string = re.sub(",\snode", ',"node"', updated_string)
        # updated_string = re.sub('"\s},', '"}', updated_string)
        updated_string = re.sub("{text", '{"text"', updated_string)
        updated_string = re.sub("{class", '{"class"', updated_string)
        updated_string = re.sub("{head", '{"head"', updated_string)
        updated_string = re.sub("{signal", '{"signal"', updated_string)
        updated_string = re.sub("{name", '{"name"', updated_string)
        updated_string = re.sub(",wave", ',"wave"', updated_string)
        updated_string = re.sub(",node", ',"node"', updated_string)
        # updated_string  = re.sub('"},', '"}', updated_string )
        updated_string = re.sub("wave:", '"wave":', updated_string)
        updated_string = re.sub("node:", '"node":', updated_string)
        updated_string = re.sub("edge:", '"edge":', updated_string)
        updated_string = re.sub("data:", '"data":', updated_string)
        updated_string = re.sub("signal:", '"signal":', updated_string)
        updated_string = re.sub(r"\\", '-', updated_string)
        " ".join(updated_string.split())

        return updated_string
