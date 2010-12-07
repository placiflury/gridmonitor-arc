from gridmonitor.model.errors.handler import HandlerException

class CacheHandlerError(HandlerException):
    """ 
    Exception raised for Cache errors.
    Attributes:
        expression -- input expression in which error occurred
        message -- explanation of error 
    """
    def __init__(self, expression, message):
        HandlerException.__init__(expression,message)

