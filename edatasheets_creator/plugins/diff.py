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


import pathlib
import os
import conf_diff
from edatasheets_creator.functions import t
from bs4 import BeautifulSoup as bs
from edatasheets_creator.constants import diffconstants as d
from edatasheets_creator.constants.htmlconstants import HTML_H1_TAG, HTML_TITLE_TAG
from edatasheets_creator.utility.path_utilities import validateRealPath

from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class Plugin:
    def __init__(self):
        return

    def __del__(self):
        return

    def process(self, file1, file2, mapFile=""):

        try:
            msg = t("Diff Plugin is loaded")
            ExceptionLogger.logInformation(__name__, msg)

            self._file1 = file1
            self._file2 = file2

            # Validate if the input files exists on the system as they are required
            if (not validateRealPath(file1)):
                # Input file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\nInput file does not exist"))
                print()
                return

            if (not validateRealPath(file2)):
                # Map file does not exist
                ExceptionLogger.logInformation(__name__, "", t("\nMap file does not exist"))
                print()
                return

            pathComponent = str(pathlib.Path(self._file1).parent)  # Just the path
            file1Component = pathlib.Path(self._file1).name.strip()  # Just the file name
            f1Prefix = os.path.splitext(file1Component)
            # file1Details = os.path.splitext(self._file1)
            file2Component = pathlib.Path(self._file2).name.strip()  # Just the file name
            f2Prefix = os.path.splitext(file2Component)
            # file2Details = os.path.splitext(self._file2)

            outputHtml = pathComponent + "/" + f1Prefix[0] + "-" + f2Prefix[0] + '.html'
            fixedUpHtml = pathComponent + "/" + f1Prefix[0] + "-" + f2Prefix[0] + '-difference-report.html'

            diff = conf_diff.ConfDiff(self._file1, self._file2, outputHtml)
            diff.diff()
            self.fixUpHtml(outputHtml, fixedUpHtml)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def fixUpHtml(self, htmlFile, fixedUpHtml):
        try:

            # pathComponent = str(pathlib.Path(self._file1).parent)  # Just the path
            # file1Component = pathlib.Path(self._file1).name.strip()  # Just the file name
            # f1Prefix = os.path.splitext(file1Component)
            # file1Details = os.path.splitext(self._file1)
            # file2Component = pathlib.Path(self._file2).name.strip()  # Just the file name
            # f2Prefix = os.path.splitext(file2Component)
            # file2Details = os.path.splitext(self._file2)

            # reportHtml = pathComponent + "/" + f1Prefix[0] + "-" + f2Prefix[0] + '-difference-report.html'

            self._outputFileExtension = ""
            self._translationInputFileName = ""
            # inputFileExtension = pathlib.Path(args.f).suffix.lower()

            with open(htmlFile) as fp:
                soup = bs(fp, 'html.parser')
                # title = soup.title
                t = soup.find(HTML_TITLE_TAG)
                t.string = d.PLUGIN_REPORT_DESCRIPTION

                h = soup.find(HTML_H1_TAG)
                h.string = d.PLUGIN_REPORT_DESCRIPTION

                with open(fixedUpHtml, "wb") as fOut:
                    fOut.write(soup.prettify("utf-8"))

                fp.close()
                os.remove(htmlFile)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
