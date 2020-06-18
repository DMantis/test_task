"""
AppException
| - ControllerException
| - - TransferException
| - - - InvalidAmountError
| - - ClientNotFoundError
| - - InvalidCredentialsErrors
| - - UsernameAlreadyRegisteredError
| - BadPayloadError
| - InsufficientFundError
"""


class AppException(Exception):
    """ Base class for service-defined exceptions. """
    pass


class ControllerException(AppException):
    pass


class TransferException(ControllerException):
    pass


class InvalidAmountError(TransferException):
    pass


class ClientNotFoundError(ControllerException):
    pass


class UsernameAlreadyRegisteredError(ControllerException):
    pass


class InvalidCredentialsError(ControllerException):
    pass


class BadPayloadError(AppException):
    pass


class InsufficientFundsError(AppException):
    pass
