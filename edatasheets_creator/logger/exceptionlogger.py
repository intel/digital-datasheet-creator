import inspect
import sys
import logging
import traceback
import os
from inspect import getframeinfo


# Determine if the script is running as a PyInstaller binary
if getattr(sys, 'frozen', False):
    # If running as a PyInstaller binary, get the executable path
    executable_path = os.path.dirname(sys.executable)
else:
    # If running as a script, get the script path
    executable_path = os.path.dirname(os.path.abspath(__file__))

# Create a log file in the user's home directory
home_directory = os.path.expanduser('~')
log_file = os.path.join(home_directory, 'ddc-application.log')


# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the log level to DEBUG to capture all log levels

# Create handlers
file_handler = logging.FileHandler(log_file)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler_error = logging.StreamHandler(sys.stderr)


# Set log levels for handlers
file_handler.setLevel(logging.DEBUG)
stream_handler.setLevel(logging.INFO)
stream_handler_error.setLevel(logging.ERROR)

# Create formatters and add them to handlers
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_format = logging.Formatter('%(message)s')
stream_error_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler.setFormatter(file_format)
stream_handler.setFormatter(stream_format)
stream_handler_error.setFormatter(stream_error_format)

# Add filters to handlers to avoid duplicate logging
stream_handler.addFilter(lambda record: record.levelno == logging.INFO)
stream_handler_error.addFilter(lambda record: record.levelno >= logging.ERROR)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.addHandler(stream_handler_error)


class ExceptionLogger:
    """
    Provides logging mechanism for information, warning, error and debug messages.
    """

    def __init__(self, excptn, type, value, traceback, method):
        """
        Class initializer.

        Args:
            excptn (Exception): the exception object.
            type (object): exception type.
            value (object): exception details.
            traceback (object): caller information.
            method (string): calling method.
        """
        try:
            self._type = type
            self._value = value
            self._traceback = traceback
            self._exception = excptn
            self._method = method

            self.log_exception()

        except Exception as e:
            logger.error("Failed to initialize ExceptionLogger: %s", str(e))
            #print(f"Failed to initialize ExceptionLogger: {e}")


    def logException(self):
        """
        Logs the exception information to a file and prints it.
        """
        try:
            # Determine error details
            if hasattr(self._value, 'strerror'):
                details = f"Error: {self._value.strerror}"
            else:
                details = f"Error: {str(self._value)}"
            
            # Construct the message
            msg = f"{self._method}: {details}"
            
            # Log the exception
            exc_info = (self._type, self._value, self._traceback)
            logger.error(msg, exc_info=exc_info)

        except Exception as e:
            # Handle any exceptions that occur during logging
            if hasattr(e, 'strerror'):
                details = f"Error: {e.strerror}"
            else:
                details = f"Error: {str(e)}"
            
            # Construct the error message
            error_msg = f"{self._method}: {details}"
            
            
            # Log the error
            logger.error("Failed to log exception: %s", str(e))



    @staticmethod
    @staticmethod
    def logError(callingClassName, message='', obj=None):
        """
        Logs an error message

        Args:
            callingClassName (string): the calling class name.
            message (str, optional): an error message. Defaults to ''.
            obj (object, optional): additional error details. Defaults to None.
        """
        try:
            # Get full stack trace
            stack_trace = ''.join(traceback.format_stack())

            # Construct origin string with full stack trace
            full_stacktrace = f"{callingClassName}, stack trace: {stack_trace}"

            # Get calling method and line number
            stack = inspect.stack()
            callingMethod = stack[1][0].f_code.co_name
            callerFrameInfo = getframeinfo(stack[1][0])
            lineNumber = callerFrameInfo.lineno

            # Construct origin string
            origin = f"{callingClassName}.{callingMethod}, line ({lineNumber}): "

            # Determine error message and exception type
            if isinstance(obj, dict):
                error_message = obj.get("message", "")
                error_exception = obj.get("exception", "")
            elif isinstance(obj, Exception):
                error_message = str(obj)
                error_exception = obj
                full_stacktrace = ''.join(traceback.format_exception(type(obj), obj, obj.__traceback__))
                while obj.__cause__:
                    obj = obj.__cause__
                    error_message = str(obj)
                    full_stacktrace += ''.join(traceback.format_exception(type(obj), obj, obj.__traceback__))
            elif message != '':
                error_message = message
                error_exception = type(message).__name__
            else:
                error_message = str(obj)
                error_exception = type(obj).__name__

            # Log the error message
            logger.error(f"{origin}{error_message}")
            logger.debug(f"{full_stacktrace}{error_message}")

        except Exception as e:
            logger.error("Failed to log error: %s", str(e))


    @staticmethod
    def logDebug(className, strMsg="", obj=None):
        """
        Logs a debug message with the line number of the caller for software debugging purposes.

        Args:
            className (string): the calling class name.
            strMsg (str, optional): a debug message. Defaults to ''.
            obj (object, optional): additional details. Defaults to None.
        """
        try:
            # Get calling method and line number
            stack = inspect.stack()
            callingMethod = stack[1][0].f_code.co_name
            callerFrameInfo = getframeinfo(stack[1][0])
            lineNumber = callerFrameInfo.lineno

            # Construct origin string
            origin = f"{className}.{callingMethod}, line ({lineNumber}): "


            # Log the debug message
            logger.debug(f"{origin}{strMsg}")
            if obj is not None:
                logger.debug(f"Additional details: {obj}")

        except Exception as ex:
            logger.error("Failed to log debug message: %s", str(ex))


    @staticmethod
    def logInformation(className, strMsg="", obj=None):
        """
        Logs an information message.

        Args:
            className (string): the calling class name.
            strMsg (str, optional): an information message. Defaults to ''.
            obj (object, optional): additional details. Defaults to None.
        """
        try:
            # Get calling method and line number
            stack = inspect.stack()
            callingMethod = stack[1][0].f_code.co_name
            callerFrameInfo = getframeinfo(stack[1][0])
            lineNumber = callerFrameInfo.lineno

            # Construct origin string
            origin = f"{className}.{callingMethod}, line ({lineNumber}): "

            # Log the information message
            logger.info(f"{strMsg}")
            logger.debug(f"{origin}{strMsg}")
            if obj is not None:
                logger.debug(f"Additional details: {obj}")

        except Exception as ex:
            logger.error("Failed to log information: %s", str(ex))

