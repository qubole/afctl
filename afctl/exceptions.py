class AfctlException(Exception):
    """
        Base class for AfctlExcetions.
        All exception classes must inherit this class.
    """

class AfctlParserException(AfctlException):
    """
        Exceptions caused while parsing the commands.
    """