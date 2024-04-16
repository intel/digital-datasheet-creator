# Task model class
import edatasheets_creator.constants.parserconstants as p


class Task:
    """
    Task class that provides the model to save a task information
    """

    def __init__(self, taskID: int = 0, description: str = "", taskGUID: str = "", map: str = "", vocabulary: str = "",
                 arg1: str = "", arg2: str = "", output: str = "", nextTask: int = 0, **kwargs) -> None:
        """
        Class initialization
        """
        self._taskID: int = taskID
        self._description: str = description
        self._taskGUID: str = taskGUID
        self._map: str = map
        self._vocabulary: str = vocabulary
        self._arg1: str = arg1
        self._arg2: str = arg2
        self._output: str = output
        self._nextTask: int = nextTask
        # Define extra arguments without input validation step
        for name, value in kwargs.items():
            self.__setattr__(name, value)

    def __repr__(self) -> str:
        """
            Method to print a string representation of the task object

            Returns:
                string : Json representation of the class
        """
        return f'''{{
          "{p.TASK_ID}" : {self._taskID},
          "{p.TASK_DESCRIPTION}": {self._description},
          "{p.TASK_GUID}": {self._taskGUID},
          "{p.TASK_MAP}": {self._map},
          "{p.TASK_VOCABULARY}":{self._vocabulary},
          "{p.TASK_ARGUMENT_1}": {self._arg1},
          "{p.TASK_ARGUMENT_2}: {self._arg2},
          "{p.TASK_OUTPUT}": {self._output},
          "{p.NEXT_TASK}": {self._nextTask},
        }}'''

    # Getters

    def getTaskID(self) -> int:
        """
        Returns the taskID (task identifier) of the task object

        Returns:
            int: taskID
        """
        return self._taskID

    def getDescription(self) -> str:
        """
        Returns the description of the task object

        Returns:
            string: description
        """
        return self._description

    def getTaskGUID(self) -> str:
        """
        Returns the taskGUID (indentifier for each plugin at internal level) of the task object

        Returns:
            string: taskGUID
        """
        return self._taskGUID

    def getMap(self) -> str:
        """
        Returns the map attribute of the task object

        Returns:
            string: map
        """
        return self._map

    def getVocabulary(self) -> str:
        """
        Returns the vocabulary attribute of the task object

        Returns:
            string: vocabulary
        """
        return self._vocabulary

    def getArg1(self) -> str:
        """
        Returns the first argument (arg1) of the task object

        Returns:
            string: arg1
        """
        return self._arg1

    def getArg2(self) -> str:
        """
        Returns the second argument (arg2) of the task object

        Returns:
            string: arg2
        """
        return self._arg2

    def getOutput(self) -> str:
        """
        Returns the output path of the task object

        Returns:
            string: codeGenerationTarget
        """
        return self._output

    def getNextTask(self) -> int:
        """
        Returns the identifier of the next task object

        Returns:
            string: nextTask
        """
        return self._nextTask

    # Setters

    def setTaskID(self, taskID: int) -> None:
        """
        Set the task identifier of the task object

        Args:
            taskID(int): task identifier

        Returns:
            None
        """
        self._taskID: int = taskID

    def setDescription(self, description: str) -> None:
        """
        Set the description of the task object

        Args:
            description(string): description of the task

        Returns:
            None
        """
        self._description: str = description

    def setTaskGUID(self, taskGUID: str) -> None:
        """
        Set the taskGUID (unique plugin identifier for internal use) of the task object

        Args:
            taskGUID(string): task global unique identifier

        Returns:
            None
        """
        self._taskGUID: str = taskGUID

    def setMap(self, mapStr: str) -> None:
        """
        Set the map attribute of the task object

        Args:
            map(string): map attribute of the task

        Returns:
            None
        """
        self._map: str = mapStr

    def setVocabulary(self, vocabulary: str) -> None:
        """
        Set the vocabulary attribute of the task object

        Args:
            vocabulary(string): vocabulary attribute of the task

        Returns:
            None
        """
        self._vocabulary: str = vocabulary

    def setArg1(self, arg1: str) -> None:
        """
        Set the first argument of the task object

        Args:
            arg1(string): first argument of the task object

        Returns:
            None
        """
        self._arg1: str = arg1

    def setArg2(self, arg2: str) -> None:
        """
        Set the second argument of the task object

        Args:
            arg2(string): first second of the task object

        Returns:
            None
        """
        self._arg2: str = arg2

    def setOutput(self, output: str) -> None:
        """
        Set the output path of the task object

        Args:
            output(string): output path of the task object

        Returns:
            None
        """
        self._output: str = output

    def setNextTask(self, nextTask: int) -> None:
        """
        Set the next task id

        Args:
            nextTask(int): next task unique identifier

        Returns:
            None
        """
        self._nextTask: int = nextTask
