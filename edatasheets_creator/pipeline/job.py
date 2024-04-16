# Job class

class Job():
    """
    Job class handles and stores jobs properties and the list of tasks assigned to it.
    """

    def __init__(self):
        """
        Class initialization
        """
        self._description = ""
        self._jobID = 0
        self._nextJob = 0
        self._jobTasks = []

    def getDescription(self):
        """
        Returns current job description

        Returns:
            string: Job description
        """
        return self._description

    def getJobID(self):
        """
        Returns current job identification

        Returns:
            int: Job identification
        """
        return self._jobID

    def getNextJob(self):
        """
        Returns next job to execute

        Returns:
            int: next job identification
        """
        return self._nextJob

    def getJobTasks(self):
        """
        Returns current job tasks

        Returns:
            array: tasks
        """
        return self._jobTasks

    def setDescription(self, description):
        """
        Adds a new description for the job
        """
        self._description = description

    def setJobID(self, jobID):
        """
        Assigns an ID to the job
        """
        self._jobID = jobID

    def setNextJob(self, nextJob):
        """
        Assigns the next job to be executed
        """
        self._nextJob = nextJob

    def setTasks(self, tasks):
        """
        Sets a new task list to the task array for the job
        """
        self._jobTasks = tasks
