"""
    Core application module that loads plugins and calls the process method on the plugins.
"""

# core.py

import pathlib
import argparse, sys, os
from edatasheets_creator.functions import t
from edatasheets_creator.constants import diffconstants as diff
from edatasheets_creator.constants import coreconstants
from edatasheets_creator.constants import jsontypes
from edatasheets_creator.constants import serializationconstants
from edatasheets_creator.constants import spreadsheettypes
from edatasheets_creator.constants import pluginconstants
from edatasheets_creator.constants import clangtypes
from edatasheets_creator.constants import runnerconstants
from edatasheets_creator.constants import translatorconstants as tc
from edatasheets_creator.constants import ctypes
from edatasheets_creator.constants import xlsxtypes
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from edatasheets_creator.pipeline.runner import Runner
from edatasheets_creator.pipeline.task import Task
from edatasheets_creator.pipeline.parser import Parser
from edatasheets_creator.utility.path_utilities import get_relative_path, validateRealPath


class DatasheetCreatorApp:
    """
        The DatasheetCreatorApp class implements the mechanics for the datasheet generator.
        To understand the way the app works, read the documentation for the :meth:`run` method.
    """

    def __init__(self, appArgs: list = []):
        """Set up the application

        Args:
           :param --f [Input File Name]:  the input file
           :param --m [Map File Name]:  the map file
           :param --o [Output File Name]:  optional output file name.  Defaults to input file prefix with a JSON extension if blank
           :param --t [Target Specification]: names the desired output file. To activate type run after this parameter/
           :param --vocab [Target Specification]: Path to a vocabulary file to use for translation
           :param --p [Pipeline job file name]: Path to the Job.json file to automate execution of multiple tasks/plug-ins
        """
        try:
            # Class arguments to hold argument data from the console
            self._inputFileName = ""
            self._outputFileName = ""
            self._mapFileName = ""
            self._diffFileToCompare1 = ""
            self._diffFileToCompare2 = ""
            self._vocabulary = ""
            self._translationInputFileName = ""
            self._targetGenerationFile = ""

            # Array of tasks to process if execution is not from the pipeline
            self._tasksToExecute = []

            # Class arguments to define if it it is a pipeline execution
            self._isPipelineExecution = False
            self._isPipelineSym = False

            # Runner or plugin argumets flag
            argumentsPresent = False

            # Runner instance for plug-in execution
            self._runner = Runner()

            # # If this is running in the debugger, generate a debug.txt file that will appear in the main source tree
            # for frame in inspect.stack():
            #     if frame[1].__contains__(g.VSCODE_DEBUG_INDICATOR):
            #         sys.stdout = open(g.DEBUGGER_OUTPUT_FILE_NAME, 'w')

            # Validate if valid plug-in arguments are being called with the execution
            if appArgs != []:
                argumentsPresent = True

                # Help messages for the console arguments
                diffArgMsg = t(diff.DIFF_HELP_ARGUMENT)
                compareFile1 = t(diff.DIFF1_HELP_ARGUMENT)
                compareFile2 = t(diff.DIFF2_HELP_ARGUMENT)
                inputFileMsg = t(coreconstants.INPUT_FILE_HELP_ARGUMENT)
                inputMapMsg = t(coreconstants.MAP_HELP_ARGUMET)
                outputFileMsg = t(coreconstants.OUTPUT_HELP_ARGUMENT)
                targetOutputMsg = t(coreconstants.TARGET_HELP_ARGUMENT)
                vocabularyMsg = t(tc.VOCABULARY_HELP_ARGUMENT)
                inputJobMessage = t(runnerconstants.JOB_HELP_ARGUMENT)
                fixup_message = t(coreconstants.FIXUP_HELP_ARGUMENT)
                ccg_pdg_checker_message = t(coreconstants.CCG_PDG_CHECKER_HELP_ARGUMENT)
                dcai_pdg_checker_message = t(coreconstants.DCAI_PDG_CHECKER_HELP_ARGUMENT)
                directory_listing_message = t(coreconstants.DIRECTORY_LISTING_HELP_ARGUMENT)
                power_sequence_message = t(coreconstants.POWER_SEQUENCE_HELP_ARGUMENT)

                # Adding arguments
                parser = argparse.ArgumentParser()
                parser.add_argument(coreconstants.INPUT_FILE_ARGUMENT, help=inputFileMsg)
                parser.add_argument(coreconstants.MAP_ARGUMENT, help=inputMapMsg)
                parser.add_argument(coreconstants.OUTPUT_ARGUMENT, help=outputFileMsg)
                parser.add_argument(coreconstants.TARGET_ARGUMENT, help=targetOutputMsg)
                parser.add_argument(coreconstants.CCG_PDG_CHECKER_ARGUMENT, help=ccg_pdg_checker_message)
                parser.add_argument(coreconstants.DCAI_PDG_CHECKER_ARGUMENT, help=dcai_pdg_checker_message)
                parser.add_argument(coreconstants.POWER_SEQUENCE_ARGUMENT, help=power_sequence_message)
                parser.add_argument(runnerconstants.JOB_ARGUMENT, help=inputJobMessage)
                parser.add_argument(tc.PLUGINARGUMENT, help=vocabularyMsg)
                parser.add_argument(diff.PLUGINARGUMENT, help=diffArgMsg)
                parser.add_argument(diff.PLUGIN_ARGUMENT_FILE1, help=compareFile1)
                parser.add_argument(diff.PLUGIN_ARGUMENT_FILE2, help=compareFile2)
                parser.add_argument(coreconstants.FIXUP_ARGUMENT, help=fixup_message)
                parser.add_argument(coreconstants.DIRECTORY_LISTING_ARGUMENT, help=directory_listing_message)
                args = parser.parse_args()

                # Checks if the execution comes from a job pipeline
                if (((args.p is not None) and (len(args.p) > 0))):
                    self._isPipelineExecution = True
                    if (not validateRealPath(args.p)):
                        self._isPipelineSym = True
                        # Do not continue with execution if a symlink is found
                        error_object = {
                            "message": 'Job file is a symlink',
                            "exception": "SymlinkFound"
                        }
                        ExceptionLogger.logError(__name__, "", error_object)
                        return
                    # Get the job pipeline file name
                    self._inputFileName = pathlib.Path(os.path.realpath(args.p).strip())

                    # Run parse the pipeline file and sets the type of execution
                    self._runner.parseRunnerJob(str(self._inputFileName))

                else:
                    # Plug-ins will be defined by parameter
                    # Call the parsing of command arguments
                    fileExtensions = self._parseCommandArguments(args)
                    inputFileExtension = fileExtensions[0]
                    outputFileExtension = fileExtensions[1]

                    # Create the tasks that will be executed
                    self._tasksToExecute = self._createRunnerTasks(args, inputFileExtension, outputFileExtension, argumentsPresent)

            else:
                # if no plugins, use the default
                ExceptionLogger.logInformation(__name__, "", t("No plugins so will use the default..."))

                # Create the default task that will be executed
                self._tasksToExecute = self._createRunnerTasks(0, 0, argumentsPresent)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def __del__(self):

        sys.stdout.close()

    # Initialization
    def run(self):
        """
            This method, depending on the type of execution, launches the execution process of Jobs or Tasks on
            the Runner instance.
        """

        try:

            ExceptionLogger.logInformation(__name__, "", t("Core application running"))

            # Check the type of execution
            if (self._isPipelineExecution):
                # Validate if pipe was a symlink
                if (not self._isPipelineSym):
                    # Start the execution of jobs in the pipeline
                    self._runner.runJobs()

            else:
                # Start the execution of tasks created in argument processing
                numberOfTasksPresent = len(self._tasksToExecute)
                if (numberOfTasksPresent >= 1):
                    self._runner.runTasks(self._tasksToExecute)
                else:
                    error_object = {
                        "message": 'Input arguments do not comply with any task structure',
                        "exception": "Parameter Error"
                    }
                    ExceptionLogger.logError(__name__, "", error_object)

            ExceptionLogger.logInformation(__name__, "", t("\nFinished core"))
            print()

        except AttributeError as ae:
            ExceptionLogger.logError(__name__, "", ae)

        except TypeError as te:
            ExceptionLogger.logError(__name__, "", te)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def _parseCommandArguments(self, arguments):
        """
            Populates class arguments with information from the command line

        Args:
           arguments: Arguments from the invocation command

        Returns:
           array: Extensions of the input and output files
        """
        inputFileExtension = ''
        outputFileExtension = ''
        try:
            # Check if input file parameter is present
            if (arguments.f is not None):
                real_path = os.path.realpath(arguments.f)
                self._inputFileName = pathlib.Path(real_path.strip())
                inputFileExtension = pathlib.Path(real_path).suffix.lower()

            # Check if processing is for ccg pdg checker
            if (arguments.fpdg is not None):
                real_path = os.path.realpath(arguments.fpdg)
                self._inputFileName = pathlib.Path(real_path.strip())
                inputFileExtension = pathlib.Path(real_path).suffix.lower()

            if (arguments.pow is not None):
                real_path = os.path.realpath(arguments.pow)
                self._inputFileName = pathlib.Path(real_path.strip())
                inputFileExtension = pathlib.Path(real_path).suffix.lower()

            # Check if processing is for dcai pdg checker
            if (arguments.fdcai is not None):
                real_path = os.path.realpath(arguments.fdcai)
                self._inputFileName = pathlib.Path(real_path.strip())
                inputFileExtension = pathlib.Path(real_path).suffix.lower()

            # Check if map file parameter is present
            if (arguments.m is not None):
                real_path = os.path.realpath(arguments.m)
                self._mapFileName = pathlib.Path(real_path.strip())

            # Check if the vocabulary parameter is present
            if (arguments.vocabulary is not None):
                real_path = os.path.realpath(arguments.vocabulary)
                self._vocabulary = pathlib.Path(real_path.strip())

            # Check if difference file 1 parameter is present
            if (arguments.diff1 is not None):
                real_path = os.path.realpath(arguments.diff1)
                self._diffFileToCompare1 = pathlib.Path(real_path.strip())

            # Check if difference file 2 parameter is present
            if (arguments.diff2 is not None):
                real_path = os.path.realpath(arguments.diff2)
                self._diffFileToCompare2 = pathlib.Path(real_path.strip())

            # Check if target parameter is present
            if (arguments.t is not None):
                # real_path = os.path.realpath(arguments.t)
                self._targetGenerationFile = arguments.t.strip()
            # Check if fixup file parameter is present
            if (arguments.fixup is not None):
                real_path = os.path.realpath(arguments.fixup)
                self.fixup_map = pathlib.Path(real_path.strip())
            # Check if input directory for listing files is present
            if (arguments.d is not None):
                real_path = os.path.realpath(arguments.d)
                self._directoryInput = str(pathlib.Path(real_path.strip()))
            # Check if output file parameter is present
            if (arguments.o is not None):
                # if an output file was passed, use it
                real_path = os.path.realpath(arguments.o)
                self._outputFileName = pathlib.Path(real_path.strip())
                outputFileExtension = pathlib.Path(real_path).suffix.lower()
                self._translationInputFileName = self._outputFileName
            else:
                if (len(str(self._inputFileName)) > 0):
                    # No output file passed so use the inputfilename
                    fileDetails = os.path.splitext(self._inputFileName)

                    if self.__isJSON(inputFileExtension):
                        # If input file is a JSON file and no output file was specified, then this is probably a translation.
                        # Generate a unique identifier so that the input file name does not get overwritten
                        if arguments.vocabulary is not None:
                            # This is a translation
                            self._translationInputFileName = self._inputFileName
                            self._outputFileName = fileDetails[0] + tc.PLUGIN_TYPE_OUTPUT_DESIGNATOR + \
                                '.' + serializationconstants.JSON_FILE_EXTENSION
                        else:
                            self._outputFileName = fileDetails[0] + '.' + serializationconstants.JSON_FILE_EXTENSION
                            self._translationInputFileName = self._outputFileName
                    else:
                        self._outputFileName = fileDetails[0] + '.' + serializationconstants.JSON_FILE_EXTENSION

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return [inputFileExtension, outputFileExtension]

    def _createRunnerTasks(self, args, inputFileExtension, outputFileExtension, argumentsPresent):
        """
            Creates and sets tasks to the runner to execute

        Args:
           args: Arguments from the invocation command
           inputFileExtension: Extension string of the input file
           outputFileExtension: Extension string of the output file
           argumentsPresent: Flag that indicates if the invocation command had arguments

        Returns:
           Array: Array of tasks objects to be executed on Runner
        """
        # Array that will store the tasks created depending on the command parameters
        tasksToExecute = []
        # Initial task id
        taskID = 1

        try:
            # Parse the Plug-in configuration file
            jobParser = Parser()
            pluginList = jobParser.getDictionary(get_relative_path(runnerconstants.PLUGIN_CFG_PATH))

            # Check if the invocation command had parameters
            if argumentsPresent:
                # validate input parameter
                if ((args.f is not None) and (len(args.f) > 0)):

                    if (len(args.f) > 0):
                        # Load the plugin for the specified file type

                        # Validate if is intended to do an spreadsheet format parsing
                        if (outputFileExtension == '.xlsx'):
                            # xls to xlsx
                            if (inputFileExtension == '.xls'):
                                # Get the xls -> xlsx plugin data
                                xlstoxlsxPlugIn = self._runner.findObject(
                                    pluginList, pluginconstants.XLS_TO_XLSX_INDEX, runnerconstants.PLUGIN_OBJECT)

                                # Create a new spreadsheet task and append to the task array
                                xlstoxlsxTask = self._newTask(taskID,
                                                              xlstoxlsxPlugIn[runnerconstants.PLUGIN_DESCRIPTION],
                                                              xlstoxlsxPlugIn[runnerconstants.PLUGINGUIDTAG],
                                                              str(self._mapFileName),
                                                              str(self._vocabulary),
                                                              str(self._inputFileName),
                                                              str(self._diffFileToCompare2),
                                                              str(self._outputFileName))
                                tasksToExecute.append(xlstoxlsxTask)

                                # Increment the task ID
                                taskID += 1

                            # xlsm to xlsx
                            elif (inputFileExtension == '.xlsm'):
                                # Get the xls -> xlsx plugin data
                                xlsmtoxlsxPlugIn = self._runner.findObject(
                                    pluginList, pluginconstants.XLSM_TO_XLSX_INDEX, runnerconstants.PLUGIN_OBJECT)

                                # Create a new spreadsheet task and append to the task array
                                xlsmtoxlsxTask = self._newTask(taskID,
                                                               xlsmtoxlsxPlugIn[runnerconstants.PLUGIN_DESCRIPTION],
                                                               xlsmtoxlsxPlugIn[runnerconstants.PLUGINGUIDTAG],
                                                               str(self._mapFileName),
                                                               str(self._vocabulary),
                                                               str(self._inputFileName),
                                                               str(self._diffFileToCompare2),
                                                               str(self._outputFileName))
                                tasksToExecute.append(xlsmtoxlsxTask)

                                # Increment the task ID
                                taskID += 1

                            elif (inputFileExtension == '.json'):
                                # Get the xlsx -> json plugin data
                                jsonToXlsxPlugIn = self._runner.findObject(
                                    pluginList, pluginconstants.DATASHEET_TO_XLSX, runnerconstants.PLUGIN_OBJECT)

                                # Create a new spreadsheet task and append to the task array
                                jsonToXlsxTask = self._newTask(taskID,
                                                               jsonToXlsxPlugIn[runnerconstants.PLUGIN_DESCRIPTION],
                                                               jsonToXlsxPlugIn[runnerconstants.PLUGINGUIDTAG],
                                                               str(self._mapFileName),
                                                               str(self._vocabulary),
                                                               str(self._inputFileName),
                                                               str(self._diffFileToCompare2),
                                                               str(self._outputFileName))
                                tasksToExecute.append(jsonToXlsxTask)

                                # Increment the task ID
                                taskID += 1
                        elif (inputFileExtension == ".xml"):
                            dita_to_json_plugin = self._runner.findObject(pluginList, pluginconstants.DITA_TO_JSON, runnerconstants.PLUGIN_OBJECT)
                            dita_to_json_task = self._newTask(taskID,
                                                              dita_to_json_plugin[runnerconstants.PLUGIN_DESCRIPTION],
                                                              dita_to_json_plugin[runnerconstants.PLUGINGUIDTAG],
                                                              str(self._mapFileName),
                                                              str(self._vocabulary),
                                                              str(self._inputFileName),
                                                              str(self._diffFileToCompare2),
                                                              str(self._outputFileName))
                            tasksToExecute.append(dita_to_json_task)
                            taskID += 1

                        elif (inputFileExtension == '.html'):
                            # Get the html plugin data
                            htmlPlugIn = self._runner.findObject(pluginList, pluginconstants.HTML_TO_JSON, runnerconstants.PLUGIN_OBJECT)

                            # Create a new html task and append to the task array
                            htmlTask = self._newTask(taskID,
                                                     htmlPlugIn[runnerconstants.PLUGIN_DESCRIPTION],
                                                     htmlPlugIn[runnerconstants.PLUGINGUIDTAG],
                                                     str(self._mapFileName),
                                                     str(self._vocabulary),
                                                     str(self._inputFileName),
                                                     str(self._diffFileToCompare2),
                                                     str(self._outputFileName))
                            tasksToExecute.append(htmlTask)

                            # Increment the task ID
                            taskID += 1

                        elif (inputFileExtension == '.pptx'):
                            # Get the html plugin data
                            pptxPlugIn = self._runner.findObject(pluginList, pluginconstants.PPTX_TO_JSON, runnerconstants.PLUGIN_OBJECT)

                            # Create a new html task and append to the task array
                            pptxTask = self._newTask(taskID,
                                                     pptxPlugIn[runnerconstants.PLUGIN_DESCRIPTION],
                                                     pptxPlugIn[runnerconstants.PLUGINGUIDTAG],
                                                     str(self._mapFileName),
                                                     str(self._vocabulary),
                                                     str(self._inputFileName),
                                                     str(self._diffFileToCompare2),
                                                     str(self._outputFileName))
                            tasksToExecute.append(pptxTask)

                            # Increment the task ID
                            taskID += 1

                        # NO parsing needed, load the Spreadsheet plug-in
                        elif (self.__isSpreadsheet(inputFileExtension)):
                            # Get the spreadsheet plugin data
                            spreadsheetPlugIn = self._runner.findObject(pluginList, pluginconstants.SPREADSHEET_INDEX, runnerconstants.PLUGIN_OBJECT)

                            # Create a new spreadsheet task and append to the task array
                            spreadsheetTask = self._newTask(taskID, spreadsheetPlugIn[runnerconstants.PLUGIN_DESCRIPTION], spreadsheetPlugIn[runnerconstants.PLUGINGUIDTAG],
                                                            str(self._mapFileName), str(self._vocabulary), str(self._inputFileName), str(self._diffFileToCompare2), str(self._outputFileName))
                            tasksToExecute.append(spreadsheetTask)

                            # Increment the task ID
                            taskID += 1

                        # Translation
                        if (args.vocabulary is not None):
                            # Get the translator plugin data
                            translatorPlugIn = self._runner.findObject(pluginList, pluginconstants.TRANSLATOR_INDEX, runnerconstants.PLUGIN_OBJECT)

                            # Create a new translator task and append to the task array
                            translatorTask = self._newTask(taskID,
                                                           translatorPlugIn[runnerconstants.PLUGIN_DESCRIPTION],
                                                           translatorPlugIn[runnerconstants.PLUGINGUIDTAG],
                                                           str(self._mapFileName),
                                                           str(self._vocabulary),
                                                           str(self._inputFileName),
                                                           str(self._diffFileToCompare2),
                                                           str(self._outputFileName))
                            tasksToExecute.append(translatorTask)

                            # Increment the task ID
                            taskID += 1
                if (args.fixup is not None):
                    fixup_plugin = self._runner.findObject(pluginList, pluginconstants.FIXUP_INDEX, runnerconstants.PLUGIN_OBJECT)
                    fixup_task = self._newTask(taskID, fixup_plugin[runnerconstants.PLUGIN_DESCRIPTION], fixup_plugin[runnerconstants.PLUGINGUIDTAG],
                                               str(self._mapFileName), str(self._vocabulary), str(self._inputFileName), str(self.fixup_map),
                                               str(self._outputFileName))
                    tasksToExecute.append(fixup_task)
                    taskID += 1

                if (args.fpdg is not None):
                    dita_to_json_plugin_2 = self._runner.findObject(pluginList, pluginconstants.DITA_TO_JSON_CCG, runnerconstants.PLUGIN_OBJECT)
                    dita_to_json_task_2 = self._newTask(taskID,
                                                        dita_to_json_plugin_2[runnerconstants.PLUGIN_DESCRIPTION],
                                                        dita_to_json_plugin_2[runnerconstants.PLUGINGUIDTAG],
                                                        str(self._mapFileName),
                                                        str(self._vocabulary),
                                                        str(self._inputFileName),
                                                        str(self._diffFileToCompare2),
                                                        str(self._outputFileName))
                    tasksToExecute.append(dita_to_json_task_2)
                    taskID += 1

                if (args.fdcai is not None):
                    dita_to_json_plugin_3 = self._runner.findObject(pluginList, pluginconstants.DITA_TO_JSON_DCAI, runnerconstants.PLUGIN_OBJECT)
                    dita_to_json_task_3 = self._newTask(taskID,
                                                        dita_to_json_plugin_3[runnerconstants.PLUGIN_DESCRIPTION],
                                                        dita_to_json_plugin_3[runnerconstants.PLUGINGUIDTAG],
                                                        str(self._mapFileName),
                                                        str(self._vocabulary),
                                                        str(self._inputFileName),
                                                        str(self._diffFileToCompare2),
                                                        str(self._outputFileName))
                    tasksToExecute.append(dita_to_json_task_3)
                if (args.pow is not None):
                    power_sequencing_plugin = self._runner.findObject(pluginList, pluginconstants.POWER_SEQUENCING, runnerconstants.PLUGIN_OBJECT)
                    power_sequencing_plugin = self._newTask(taskID,
                                                            power_sequencing_plugin[runnerconstants.PLUGIN_DESCRIPTION],
                                                            power_sequencing_plugin[runnerconstants.PLUGINGUIDTAG],
                                                            str(self._mapFileName),
                                                            str(self._vocabulary),
                                                            str(self._inputFileName),
                                                            str(self._diffFileToCompare2),
                                                            str(self._outputFileName))
                    tasksToExecute.append(power_sequencing_plugin)
                    taskID += 1
                # Target configuration plugin (CLANG)
                if (args.t is not None):
                    # Validate if a header file is required
                    if (self._targetGenerationFile == coreconstants.TARGET_FILE_HEADER):
                        # Get the clang header plugin data
                        clangHeaderPlugIn = self._runner.findObject(pluginList, pluginconstants.CLANG_HEADER_INDEX, runnerconstants.PLUGIN_OBJECT)

                        # Create a new clang headertask and append to the task array
                        clangHeaderTask = self._newTask(taskID,
                                                        clangHeaderPlugIn[runnerconstants.PLUGIN_DESCRIPTION],
                                                        clangHeaderPlugIn[runnerconstants.PLUGINGUIDTAG],
                                                        str(self._mapFileName),
                                                        str(self._vocabulary),
                                                        str(self._inputFileName),
                                                        str(self._diffFileToCompare2),
                                                        str(self._outputFileName))
                        tasksToExecute.append(clangHeaderTask)

                        # Increment the task ID
                        taskID += 1

                    elif (self._targetGenerationFile == coreconstants.TARGET_FILE_C):
                        # C file will be generated
                        clangFilePlugIn = self._runner.findObject(pluginList, pluginconstants.CLANG_FILE_INDEX, runnerconstants.PLUGIN_OBJECT)

                        # Create a new clang file and append to the task array
                        clangFileTask = self._newTask(taskID,
                                                      clangFilePlugIn[runnerconstants.PLUGIN_DESCRIPTION],
                                                      clangFilePlugIn[runnerconstants.PLUGINGUIDTAG],
                                                      str(self._mapFileName),
                                                      str(self._vocabulary),
                                                      str(self._inputFileName),
                                                      str(self._diffFileToCompare2),
                                                      str(self._outputFileName))
                        tasksToExecute.append(clangFileTask)

                        # Increment the task ID
                        taskID += 1
                if (args.d is not None):
                    # Get the Directory Listing plugin data
                    directoryListPlugin = self._runner.findObject(pluginList, pluginconstants.DIRECTORY_LISTING, runnerconstants.PLUGIN_OBJECT)
                    # Create a new diff task and append to the task array
                    directoryListTask = self._newTask(taskID, directoryListPlugin[runnerconstants.PLUGIN_DESCRIPTION], directoryListPlugin[runnerconstants.PLUGINGUIDTAG],
                                                      str(self._mapFileName), str(self._vocabulary), str(self._directoryInput),
                                                      str(self._diffFileToCompare2), str(self._outputFileName), directoryInput=self._directoryInput)
                    tasksToExecute.append(directoryListTask)

                    # Increment the task ID
                    taskID += 1
                # Difference File Comparison Plugin
                if (args.diff1 is not None):
                    # Get the diff plugin data
                    diffPlugIn = self._runner.findObject(pluginList, pluginconstants.DIFF_INDEX, runnerconstants.PLUGIN_OBJECT)

                    # Create a new diff task and append to the task array
                    diffTask = self._newTask(taskID, diffPlugIn[runnerconstants.PLUGIN_DESCRIPTION], diffPlugIn[runnerconstants.PLUGINGUIDTAG],
                                             str(self._mapFileName), str(self._vocabulary), str(
                                                 self._diffFileToCompare1), str(self._diffFileToCompare2),
                                             str(self._outputFileName))
                    tasksToExecute.append(diffTask)

                    # Increment the task ID
                    taskID += 1
            else:
                # Create a default plugin task to execute
                defaultPlugIn = self._runner.findObject(pluginList, pluginconstants.DEFAULT_INDEX, runnerconstants.PLUGIN_OBJECT)

                # Create a new default task and append to the task array
                defaultTask = self._newTask(taskID, defaultPlugIn[runnerconstants.PLUGIN_DESCRIPTION], defaultPlugIn[runnerconstants.PLUGINGUIDTAG],
                                            str(self._mapFileName), str(self._vocabulary), str(
                                                self._diffFileToCompare1), str(self._diffFileToCompare2),
                                            str(self._outputFileName))
                tasksToExecute.append(defaultTask)

            """
                As we assume that the all tasks will have a next task while in creation,
                it is needed to fix the last element to not have a nextTask element
            """
            # Get the index of the last task
            lastElementIndex = len(tasksToExecute) - 1
            # Check if the index is a valid positive number
            if (lastElementIndex >= 0):
                # Get the last task
                lastTask = tasksToExecute[lastElementIndex]
                # Replace the next property
                lastTask.setNextTask(None)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return tasksToExecute

    def _newTask(self, taskId, taskDesc, taskGUID, taskMap, taskVocab, taskArg1, taskArg2, taskOutput, **kwargs):
        """
            Creates and sets tasks to the runner to execute

        Args:
           taskId: ID of the task that will be created
           taskDesc: Description of the task that will be created
           taskGUID: Plug-in guid of the task that will be created
           taskMap: Map of the task that will be created
           taskVocab: Vocabulary of the task that will be created
           taskArg1: Input file name 1 of the task that will be created
           taskArg2: Input file name 2 of the task that will be created
           taskOutput: Output file of the task that will be created

        Returns:
           Task: Object task with the parameter information
        """
        # Assume that we will have a next task with an incremental ID
        nextTask = taskId + 1
        # Create and return the new object
        newTask = Task(taskId, taskDesc, taskGUID, taskMap, taskVocab, taskArg1,
                       taskArg2, taskOutput, nextTask, **kwargs)
        return newTask

    # Check spreadsheet type
    def __isSpreadsheet(self, ext):
        """
            Indicates if the extension is a valid spreadsheet type

        Args:
           ext: String containing the extension of the input file

        Returns:
           Boolean: Flag indicating if the extension is a valid spreadsheet type
        """
        bln = False

        try:
            bln = ext in spreadsheettypes.spreadsheetExtensions.values()

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return bln

    # Check JSON type
    def __isJSON(self, ext):
        """
            Indicates if the extension is a valid JSON type

        Args:
           ext: String containing the extension of the input file

        Returns:
           Boolean: Flag indicating if the extension is a valid JSON type
        """
        bln = False

        try:
            bln = ext.lower() in jsontypes.fileExtensions.values()

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return bln

    def getFormats(self, format):
        """
            Selects the plug-in name to execute depending on the format input

        Args:
           format: String containing the extension of the input file

        Returns:
           String: Name of the selected plug-in
        """
        switch = {
            'json': spreadsheettypes.PLUGIN,
            'header': clangtypes.PLUGIN,
            "c": ctypes.PLUGIN,
            "xlsx": xlsxtypes.PLUGIN
        }

        return switch.get(format, 1)
