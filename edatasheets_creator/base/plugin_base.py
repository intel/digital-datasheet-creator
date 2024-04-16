from edatasheets_creator.utility.dictionary_utilities import DictionaryUtilities
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from marshmallow import Schema


class PluginBase:
    INPUT_SCHEMA = None

    def __init__(self) -> None:
        self.dictionary_utilities = DictionaryUtilities()

    def process(self, **kwargs):
        try:
            raise NotImplementedError(f"Process method has not been implemented for {__name__}")
        except Exception as e:
            ExceptionLogger.logError(__name__, '', e)

    def validate_schema(self, kwargs):
        if self.INPUT_SCHEMA:
            try:
                schema: Schema = self.INPUT_SCHEMA()
                kwargs = schema.load(data=kwargs)
            except Exception as e:
                raise Exception(f"Error validating schema for input args: {e}")
        return kwargs
