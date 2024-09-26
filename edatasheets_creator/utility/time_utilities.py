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
