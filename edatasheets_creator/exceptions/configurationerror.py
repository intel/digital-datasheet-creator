class ConfigurationError(Exception):
    """
    ConfigurationError exception definition.

    Args:
        Exception (object): base class.
    """

    def __init__(self, msg, details):
        """
        Class initializer.

        Args:
            msg (string): an error message.
            details (string): error message details.
        """
        self.message = msg
        self.details = details
        s = self.message + ':  ' + self.details
        super().__init__(s)
