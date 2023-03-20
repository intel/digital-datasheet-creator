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


from datetime import datetime, timezone
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger


def get_current_utc_datetime(_format: str = None) -> str:
    """
    Get the current UTC now, if format is not provided use %Y-%m-%dT%H:%M:%S as default

    Args:
        _format (string) : format to be used in the output

    Returns:
        string: current utc datetime
    """
    try:
        default_format = "%Y-%m-%dT%H:%M:%S"
        now = datetime.now(tz=timezone.utc)
        _format = default_format if not _format else _format
        return now.strftime(_format)

    except Exception as e:
        ExceptionLogger.logError(__name__, "", e)
