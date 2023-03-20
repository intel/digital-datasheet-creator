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


class ConfigurationError(Exception):
    """
    ConfigurationError exception definition.

    Args:
        Exception (object): base class.
    """

    def __init__(self, msg, details):
        """
        Claass initializer.

        Args:
            msg (string): an error message.
            details (string): error message details.
        """
        self.message = msg
        self.details = details
        s = self.message + ':  ' + self.details
        super().__init__(s)
