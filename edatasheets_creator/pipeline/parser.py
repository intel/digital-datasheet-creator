# Parser class

import json

from edatasheets_creator.pipeline.job import Job
from edatasheets_creator.pipeline.task import Task
from edatasheets_creator.constants import parserconstants as p
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


class Parser():
    """
    Parser in charge of processing the JSON input file and creating Jobs and Tasks.
    """

    def __init__(self):
        """
        Class initialization
        """
        self._dictionary = {}
        self._jobs = []
        self._pipelineDescription = ""

    def getDictionary(self, inputFile):
        """
        Opens the file and loads it into a Python dictionary

        Args:
            inputFileName: Input file name

        Returns:
            dictionary(dict): dictionary of objects
        """
        try:
            with open(inputFile, 'r') as f:
                # Open file and load it as JSON
                dictionary = json.load(f)
                return dictionary

        except Exception as e:
            ExceptionLogger.logError(__name__, e)

    def parseJSON(self, inputFileName):
        """
        Opens the file and loads it into a Python dictionary

        Args:
            inputFileName: Input file name

        Returns:
            arrays: Array of Job objects
        """
        ExceptionLogger.logInformation(__name__, "", "Opening file: " + inputFileName)

        pipeline = self.getDictionary(inputFileName)
        self._dictionary = pipeline

        # Get pipeline description
        self._pipelineDescription = pipeline[p.PIPELINE_DESCRIPTION]

        # Start the parsing of jobs
        self._jobs = self.__parseJobs(pipeline)

        return self._jobs

    def getDescription(self):
        """
        Opens the file and loads it into a Python dictionary

        Returns:
            string: Description for pipeline
        """
        return self._pipelineDescription

    def __parseJobs(self, pipeline):
        # Retrieve the jobs and the actual amount from the file
        jobs = pipeline[p.PIPELINE_JOBS]
        amountOfJobs = len(jobs)
        parsedJobs = []

        if (amountOfJobs > 0):
            for job in jobs:
                # Create a new job object and populate it
                newJob = Job()
                newJob.setDescription(job[p.JOB_DESCRIPTION])
                newJob.setJobID(job[p.JOB_ID])
                listOfTasks = self.__parseTasks(job)
                newJob.setTasks(listOfTasks)

                # Add next job if present
                if p.NEXT_JOB in job:
                    newJob.setNextJob(job[p.NEXT_JOB])
                else:
                    newJob.setNextJob(None)

                # Adding new job to return array
                parsedJobs.append(newJob)

        return parsedJobs

    def __parseTasks(self, job):
        tasks = job[p.JOB_TASKS]
        amountOfTasks = len(tasks)
        parsedTasks = []

        if (amountOfTasks > 0):
            for task in tasks:
                # Create a new task object and populate it
                newTask = Task(**task)

                # Add next task if present
                if p.NEXT_TASK in task:
                    newTask.setNextTask(task[p.NEXT_TASK])
                else:
                    newTask.setNextTask(None)

                # Adding new task to return array
                parsedTasks.append(newTask)

        return parsedTasks
