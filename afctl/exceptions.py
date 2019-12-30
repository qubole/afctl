class AfctlException(Exception):
    """
        Base class for AfctlExcetions.
        All exception classes must inherit this class.
    """

class AfctlParserException(AfctlException):
    """
        Exceptions caused while parsing the commands.
    """

class AfctlUtilsException(AfctlException):
    """
        Exceptions cause while running the utils.
    """

class AfctlDeploymentException(AfctlException):
    """
        Exceptions caused while running deployment code.
    """