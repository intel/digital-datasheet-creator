# Runner class

from os.path import isdir
from os import listdir
from edatasheets_creator.base.plugin_base import PluginBase

from edatasheets_creator.pipeline.parser import Parser
from edatasheets_creator.pipeline.task import Task
from edatasheets_creator.functions import t
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger

from edatasheets_creator.constants import runnerconstants as r
from edatasheets_creator.constants import pluginconstants as p
from edatasheets_creator.constants import parserconstants as pc

from edatasheets_creator.utility.filevalidation import filesExistsOnPath, outputPathExists, validateJson
from edatasheets_creator.utility.path_utilities import get_relative_path, validateRealPath

import importlib


class Runner():
    """
    Runner in charge of executing parsed Jobs and Tasks from the pipeline
    """

    def __init__(self):
        """
        Initializes Runner parameters

        """
        try:
            # Hold plugins and jobs data
            self._plugins = []
            self._jobsInPipeline = []

            # Flag that defines if the pipeline job file exists
            self._jobExists = True

            # Loading plugin config file
            self._jobParser = Parser()
            self._pluginList = self._jobParser.getDictionary(get_relative_path(r.PLUGIN_CFG_PATH))

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def parseRunnerJob(self, jobFile):
        """
            Executes the 2 parsing processes for the runner.
             * Parses the dictionary of plug-ins
             * Parses the job pipeline file

        Args:
           jobFile: path of the job file
        """
        try:
            # Validate that the path corresponds to an actual existing file
            if (validateRealPath(jobFile)):
                # Creates a parser and triggers the JSON parsing
                ExceptionLogger.logInformation(__name__, "", f'Executing jobs in file: {jobFile}')
                isValid = validateJson(get_relative_path(r.PIPELINE_SCHEMA), "", jobFile, ["xlsx"])

                if (not isValid):
                    error_object = {
                        "message": f'File does not comply with the schema for pipeline files: {jobFile}',
                        "exception": "Schema Error"
                    }
                    ExceptionLogger.logError(__name__, "", error_object)
                    self._jobExists = False
                else:
                    self._jobsInPipeline = self._jobParser.parseJSON(jobFile)

            else:
                # No file found
                error_object = {
                    "message": f'File not found: {jobFile}',
                    "exception": "FileNotFound"
                }
                ExceptionLogger.logError(__name__, "", error_object)
                self._jobExists = False

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def runJobs(self):
        """
            Runs the jobs present on the array in the order specified
            between the jobs and their IDs.

        """
        try:
            # Start with job 1
            nextJob = r.INITIAL_JOB_ID

            # If the job file does not exist
            if (not self._jobExists):
                return

            if (len(self._jobsInPipeline) < 1):
                # There are no jobs in the pipeline, cannot execute
                error_object = {
                    "message": 'There are no jobs present in the pipeline file',
                    "exception": "Schema Error"
                }
                ExceptionLogger.logError(__name__, "", error_object)
                return

            # Start the execution of jobs
            while (nextJob != r.NO_NEXT_JOB_ID):
                # Look for the job to execute
                jobToRun = self.findObject(self._jobsInPipeline, nextJob, r.JOB_OBJECT)

                # Execute tasks from the job
                self.runTasks(jobToRun.getJobTasks())

                # Sets the next job to execute
                currentJob = nextJob
                nextJob = jobToRun.getNextJob()

                # validate for circular dependency that might get in a loop
                if ((nextJob != r.NO_NEXT_JOB_ID) and (currentJob >= nextJob)):
                    # Stop the execution as we are going backwards on the pipeline
                    error_object = {
                        "message": f'Job number {currentJob} points back to job number {nextJob}',
                        "exception": "Infinite loop"
                    }
                    ExceptionLogger.logError(__name__, "", error_object)
                    nextJob = r.NO_NEXT_JOB_ID

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def runTasks(self, tasks):
        """
            Runs the tasks present on the array in the order specified
            between the tasks and their IDs.

        Args:
           tasks: Tasks array from the job
        """
        try:
            # Start with task 1
            nextTask = r.INITIAL_TASK_ID

            if (len(tasks) < 1):
                # There are no tasks in the job, cannot execute
                error_object = {
                    "message": 'The current job does not contain tasks to execute',
                    "exception": "Schema Error"
                }
                ExceptionLogger.logError(__name__, "", error_object)
                return

            # Start the execution of tasks
            while (nextTask != r.NO_NEXT_TASK_ID):
                # Look for the task to execute
                taskToRun = self.findObject(tasks, nextTask, r.TASK_OBJECT)
                pluginDict: dict = self.findObject(self._pluginList, taskToRun.getTaskGUID(), r.PLUGIN_OBJECT)
                validateFilesFlag = pluginDict.get(r.PLUGIN_VALIDATE_INPUTS, True)
                if (validateFilesFlag):
                    # Check if the input for the task is a directory
                    if (isdir(taskToRun.getArg1())):
                        # It is a directory
                        self.__executeTaskInDirectory(taskToRun)
                    elif (validateRealPath(taskToRun.getArg1())):
                        # Execute task for one file
                        self.__processTask(taskToRun)
                    else:
                        # Argument 1 does not exist
                        error_object = {
                            "message": f'File in argument with value {taskToRun.getArg1()} could not be found in task {taskToRun.getTaskID()}',
                            "exception": "FileNotFound"
                        }
                        ExceptionLogger.logError(__name__, "", error_object)
                else:
                    self.__processTask(taskToRun)

                # Sets the next task to execute
                currentTask = nextTask
                nextTask = taskToRun.getNextTask()

                # validate for circular dependency that might get in a loop
                if ((nextTask != r.NO_NEXT_TASK_ID) and (currentTask >= nextTask)):
                    # Stop the execution as we are going backwards on the pipeline
                    error_object = {
                        "message": f'Task number {currentTask} points back to task number {nextTask}',
                        "exception": "Infinite loop"
                    }
                    ExceptionLogger.logError(__name__, "", error_object)
                    nextTask = r.NO_NEXT_TASK_ID

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def findObject(self, objects, objectId, objectType):
        """
            Returns the job for the specific jobId.

        Args:
           objects: objects array from the parser
           objectId: Identification of the object that is needed
           objectType: Type of the object

        Returns:
            object: The object that corresponds to the objectId
        """
        try:
            for object in objects:
                if (objectType == r.JOB_OBJECT):
                    if (object.getJobID() == objectId):
                        # Job with the ID was found
                        return object
                elif (objectType == r.TASK_OBJECT):
                    if (object.getTaskID() == objectId):
                        # Task with the ID was found
                        return object
                elif (objectType == r.PLUGIN_OBJECT):
                    # Plug-in with the GUID was found
                    pluginGUID = object[r.PLUGINGUIDTAG]
                    if (pluginGUID == objectId):
                        return object
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return None

    def __executeTaskInDirectory(self, task):
        """
            Executes a defined task for the files in a directory.
            Only executes the plug-in with a valid input type.

        Args:
           task: Task that will be executed

        """
        try:
            # Get the path that contains the files
            workPath = task.getArg1()
            # Retrieve the content of the path
            directoryFiles = listdir(workPath)
            # Retrieve the input file formats for the task plug-in
            plugInData = self.findObject(self._pluginList, task.getTaskGUID(), r.PLUGIN_OBJECT)
            pluginFormats = plugInData[r.PLUGIN_INPUT_FORMATS]

            # Check each one of the elements in the directory
            for fileName in directoryFiles:
                # Get the name and extension in different index
                fileData = fileName.split(".")
                # As thename is divided by ".", it may have 2 or more elements depending on the name
                dataElementsCount = len(fileData)

                # Get the filename without extension and extension
                fileExtension = fileData[dataElementsCount - 1]
                fileNameNoExtension = fileName.replace("." + fileExtension, "")

                # Paths to validate if it is a file or folder
                newFolderPath = workPath + fileName + "/"
                inputFile = workPath + fileName

                # Valdate if it is a sub-folder
                if (isdir(newFolderPath)):
                    # Create a new Task to valdate sub-folder
                    newTask = Task(1, task.getDescription(), task.getTaskGUID(), task.getMap(),
                                   task.getVocabulary(), newFolderPath, task.getArg2(),
                                   task.getOutput(), None)
                    # Do a recursive call to execute sub-directory
                    self.__executeTaskInDirectory(newTask)

                elif (validateRealPath(inputFile)):
                    # It is a valid file name with extension
                    # Check if the file extension is supported by the plug-in
                    if (fileExtension in pluginFormats):
                        # Will store if the task requires a map or vocabulary file
                        auxiliaryFileType = plugInData[r.PLUGIN_ARGUMENTS][2]
                        mapToUse = ""
                        vocabularyToUse = ""
                        auxiliaryPaths = ['', '']
                        # Get the path to the corresponding map or vocabulary file
                        mapToUse = task.getMap()
                        vocabulary = task.getVocabulary()

                        if validateRealPath(mapToUse):
                            auxiliaryPaths[0] = mapToUse

                        elif validateRealPath(vocabulary):
                            auxiliaryPaths[1] = vocabulary
                        else:
                            auxiliaryPaths = self.__getAuxiliaryFilePath(fileNameNoExtension, task.getMap(), task.getVocabulary(), auxiliaryFileType)

                        outputFile = task.getOutput() + fileNameNoExtension + "." + plugInData[r.PLUGIN_OUTPUT_FORMAT]
                        # Check that the auxiliaryFile exist
                        if (None not in auxiliaryPaths):
                            # Assign the complete auxiliary file path
                            mapToUse = auxiliaryPaths[0]
                            vocabularyToUse = auxiliaryPaths[1]
                        else:
                            # Either the map or vocabulary was not found
                            error_object = {
                                "message": 'Vocabulary or map file is not present on indicated path',
                                "exception": "FileNotFound"
                            }
                            ExceptionLogger.logError(__name__, "", error_object)

                        # Either the map or vocabulary was found
                        newTask = Task(1, task.getDescription(), task.getTaskGUID(), mapToUse,
                                       vocabularyToUse, inputFile, task.getArg2(),
                                       outputFile, None)
                        # Execute the task newly created
                        self.__processTask(newTask)
                else:
                    ExceptionLogger.logError(__name__, f'Not a valid file or directory: {inputFile}\n\n')

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def __processTask(self, task):
        """
            Executes the plugins of each task

        Args:
           task: Task object selected to run
        """
        try:
            # Retrieve the GUID to define which plug in to call
            taskGUID = task.getTaskGUID()

            # Retrieve the plugin
            pluginDict: dict = self.findObject(self._pluginList, taskGUID, r.PLUGIN_OBJECT)
            importPluginName = p.PLUGIN_DIRECTORY + pluginDict[r.PLUGINNAME]
            validateFilesFlag = pluginDict.get(r.PLUGIN_VALIDATE_INPUTS, True)
            caseFormats = pluginDict.get(r.PLUGIN_CASE_FORMATS, {})

            # Imports the plug is to execute
            self._plugins = []
            self._plugins.append(importlib.import_module(importPluginName) .Plugin())

            # if there was an error in initializing the plugins, there will not be a "_plugins" attribute so don't try to process
            if hasattr(self, '_plugins'):
                # Check the arguments the pluf in requires to execute
                pluginArguments = pluginDict[r.PLUGIN_ARGUMENTS]
                if (validateFilesFlag):

                    arg1 = self.__getArgumentValue(task, pluginArguments[0])
                    arg2 = self.__getArgumentValue(task, pluginArguments[1])
                    arg3 = self.__getArgumentValue(task, pluginArguments[2])

                    # Validate if the inputs exists depending on the argument type
                    argumentValues = [arg1, arg2, arg3]
                    inputFormat = pluginDict[r.PLUGIN_INPUT_FORMATS]
                    inputFilesExist = filesExistsOnPath(argumentValues, pluginArguments, inputFormat, True)

                    # Validate that the output path exists
                    outputPathExist = outputPathExists(argumentValues, pluginArguments)
                    if (inputFilesExist and outputPathExist):
                        # Execute the plug in
                        for plugin in self._plugins:
                            plugin.process(arg1, arg2, arg3)
                else:
                    arguments: dict = {}
                    for plugin_arg in pluginArguments:
                        value = self.__getArgumentValue(task, plugin_arg)
                        if not value and caseFormats:
                            arg_case = caseFormats.get(plugin_arg, {})
                            value = arg_case.get(r.CASE_FORMAT_DEFAULT, '')
                        arguments[plugin_arg] = value

                    plugin: PluginBase
                    for plugin in self._plugins:
                        arguments = plugin.validate_schema(arguments)
                        plugin.process(**arguments)

            ExceptionLogger.logInformation(__name__, "", t("\nFinished processing the plugin"))
            print()

        except AttributeError as ae:
            ExceptionLogger.logError(__name__, "", ae)

        except TypeError as te:
            ExceptionLogger.logError(__name__, "", te)

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def __getAuxiliaryFilePath(self, fileName, taskMapPath, taskVocabularyPath, auxiliaryFileType):
        """
            Searches for the paths for vocabularies.

        Args:
           fileName: String that holds the name of the input file without extension
           taskMapPath: Path to where the map is located
           taskVocabularyPath: Path to where the vocabulary is located
           auxiliaryFileType: String that defines if the file to look is a map or vocabulary

        Returns:
            Array: List of map and vocabulary containing the updated output path
        """
        mapFilePath = ""
        vocabularyFilePath = ""

        try:
            # Validate if it is needed a map or vocabulary
            if (auxiliaryFileType == pc.TASK_MAP):
                # Build the map file path
                mapPath = taskMapPath + fileName + r.MAP_SUFFIX
                # Validate if the file exists in the directory
                if (validateRealPath(mapPath)):
                    mapFilePath = mapPath
                else:
                    # The file does not exist
                    mapFilePath = None

            elif (auxiliaryFileType == pc.TASK_VOCABULARY):
                # Build the vocabulary file path
                vocabularyPath = taskVocabularyPath + fileName + r.VOCABULARY_SUFFIX
                # Validate if the file exists in the directory
                if (validateRealPath(vocabularyPath)):
                    vocabularyFilePath = vocabularyPath
                else:
                    # The file does not exist
                    vocabularyFilePath = None

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

        return [mapFilePath, vocabularyFilePath]

    def __getArgumentValue(self, task, argToCheck):
        """
            Gets the value from the task objet of the selected argument

        Args:
           task: task object that is being executed
           argToCheck: argument from the task that needs to be retrieved

        Returns:
            string: The value of the argument for the task object
        """
        value = ''
        try:
            taskId = task.getTaskID()
            # Check for the type of argument and invokes the corresponding task method
            if (argToCheck == pc.TASK_MAP):
                value = task.getMap()

            elif (argToCheck == pc.TASK_VOCABULARY):
                value = task.getVocabulary()

            elif (argToCheck == pc.TASK_ARGUMENT_1):
                value = task.getArg1()

            elif (argToCheck == pc.TASK_ARGUMENT_2):
                value = task.getArg2()

            elif (argToCheck == pc.TASK_CODE_GENERATION_TARGET):
                value = task.getCodeGenerationTarget()

            elif (argToCheck == pc.TASK_OUTPUT):
                value = task.getOutput()
            else:
                value = getattr(task, argToCheck, '')
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
        if value is None:
            msg = f"Not found argument: '{argToCheck}' in taskID {taskId} definition, using empty string instead.\n"
            ExceptionLogger.logInformation(__name__, msg)
        return value
