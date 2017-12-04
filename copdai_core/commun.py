from enum import Enum, unique


@unique
class ReturnCodes(Enum):
    """Errors codes enumeration"""

    FATAL = 0
    SUCCESS = 1
