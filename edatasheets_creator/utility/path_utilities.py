import os
from pathlib import Path
from os.path import isfile, islink, join


def get_relative_path(filename) -> str:
    """Get the relative path, for frozen application (executable binaries)
    or the relative path for local execution.

    Args:
        filename (str): filepath to include

    Returns:
        str: relative path founded
    """
    datadir = Path(os.path.dirname(__file__)).parent
    return join(datadir, filename)


def validateRealPath(pathToFile: str) -> bool:
    """This will check if the path corresponds to a symlink or not

    Args:
        pathToFile (str): Path to the file

    Returns:
        bool: Boolean indicating is the path is a file and not a symlink
    """
    isValidFile = False
    fileExist = False
    # Is link will return true if file is a symlink, negate it to only accept actual files
    isValidFile = not islink(pathToFile)
    fileExist = isfile(pathToFile)
    return isValidFile and fileExist
