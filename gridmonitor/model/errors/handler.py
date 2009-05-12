
class HandlerException(Exception):
    """ 
    Exception raised for Handler errors.
    Attributes:
        expression -- input expression in which error occurred
        message -- explanation of error 
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class CREATE_ERROR(HandlerException):
    """Exception raised if handler could not be created.
    """
    pass

class ACCESS_ERROR(HandlerException):
    """Exception raised if handler could not be accessed.
    """
    pass

