class ApplicationError(Exception):
    """Base class for expected application errors."""


class InvalidCustomerError(ApplicationError):
    pass


class DuplicateCustomerError(ApplicationError):
    pass


class ServiceUnavailableError(ApplicationError):
    pass


class InvalidReservationError(ApplicationError):
    pass


class DuplicateReservationError(ApplicationError):
    pass


class OperationNotAllowedError(ApplicationError):
    pass


class MissingParameterError(ApplicationError):
    pass


class CalculationError(ApplicationError):
    pass
