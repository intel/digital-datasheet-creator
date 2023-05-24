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
import json
import sys

from inspect import getframeinfo
from edatasheets_creator.constants import validation_constants as validatorconstants
from edatasheets_creator.functions import t


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

        except Exception:

            if hasattr(self._value, 'strerror'):
                details = t('Error') + self._value.strerror
            else:
                details = t('Error') + str(self._exception)
            msg = self._method + ':  ' + details
            print(msg)

    def logException(self):
        """
        Not used.
        """

        try:

            if hasattr(self._value, 'strerror'):
                details = t('Error') + self._value.strerror
            else:
                details = t('Error') + str(self._exception)
            msg = self._method + ':  ' + details
            print(msg)

        except Exception as e:
            if hasattr(self._value, 'strerror'):
                details = t('Error') + self._value.strerror
            else:
                details = t('Error') + str(e)
            msg = self._method + ':  ' + details
            print(msg)

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
            exc_type, exc_obj, exc_tb = sys.exc_info()

            callingClass = callingClassName

            stack = inspect.stack()
            callingMethod = stack[1][0].f_code.co_name
            origin = callingClass + '.' + callingMethod + ':  '
            callerFrameInfo = getframeinfo(stack[1][0])
            lineNumber = callerFrameInfo.lineno

            # if exc_tb is not None:
            #     lineNumber = exc_tb.tb_lineno
            # else:
            #     lineNumber = callerFrameInfo.lineno

            origin = callingClass + '.' + callingMethod + ', line (' + str(lineNumber) + '):  '
            error_message = ""
            error_exception = ""
            # Validate if the error message and type is specified
            if (validatorconstants.DICTIONARY == type(obj).__name__):
                error_message = obj.get("message")
                error_exception = obj.get("exception")
            else:
                error_message = str(obj)
                error_exception = type(obj).__name__
            print(origin + message, flush=True, end='')

            if obj is not None:
                print(obj, flush=True)
                err_output = {
                    "message": error_message,
                    "exception": error_exception,
                    "type": "Error"
                }
                print(json.dumps(err_output), file=sys.stderr)

        except Exception as ex:
            print(ex)

    @staticmethod
    def logDebug(className, strMsg="", obj=None):
        """
        Logs an debug message with the line number of the caller for software debugging purposes.

        Args:
            callingClassName (string): the calling class name.
            strMsg (str, optional): an error message. Defaults to ''.
            obj (object, optional): additional error details. Defaults to None.
        """

        try:
            stack = inspect.stack()
            callingMethod = stack[1][0].f_code.co_name
            callerFrameInfo = getframeinfo(stack[1][0])
            lineNumber = callerFrameInfo.lineno

            msg = "\nDEBUG - " + className + '.' + callingMethod + ' line ' + str(lineNumber) + ':  ' + strMsg
            print(msg, flush=True, end='')
            if obj is not None:
                print(obj, flush=True)
            print('\n')

        except Exception as ex:
            print(ex)

    @staticmethod
    def logInformation(className, str="", obj=None):
        """
        Logs an information message.

        Args:
            callingClassName (string): the calling class name.
            strMsg (str, optional): an error message. Defaults to ''.
            obj (object, optional): additional error details. Defaults to None.
        """
        # stack = inspect.stack()
        # callingMethod = stack[1][0].f_code.co_name
        # callerFrameInfo = getframeinfo(stack[1][0])
        # lineNumber = callerFrameInfo.lineno

        try:
            msg = str
            print(msg, flush=True, end='')
            if obj is not None:
                print(obj, flush=True)

        except Exception as ex:
            print(ex)
