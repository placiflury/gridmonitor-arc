""" Contains the Exception(s) that will be thrown on ACL DB access errors."""

class ACLError(Exception):  
    """
    Exception raised for ACL errors.
    Attributes:
        expression -- input expression in which error occurred
        message -- explanation of error 
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class ACLInsertError(ACLError):  
    """
    Exception raised for ACL Insert errors.
    Attributes:
        expression -- input expression in which error occurred
        message -- explanation of error 
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class ACLNoRecError(ACLError):  
    """
    Exception raised for missing ACL entry. 
    Attributes:
        expression -- input expression in which error occurred
        message -- explanation of error 
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
