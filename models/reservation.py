from datetime import date as Date
from enum import Enum
from math import isfinite

from exceptions.errors import OperationNotAllowedError, InvalidReservationError
from models.customer import Customer
from models.service import Service


class ReservationStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"


class Reservation:
    def __init__(
        self,
        identifier: str,
        customer: Customer,
        service: Service,
        duration: float,
        reservation_date: str,
    ) -> None:
        if not identifier or not identifier.strip():
            raise InvalidReservationError("A reservation identifier is required.")
        if not isinstance(customer, Customer) or not isinstance(service, Service):
            raise InvalidReservationError("A valid customer and service are required.")
        try:
            parsed_date = Date.fromisoformat(reservation_date.strip())
        except (AttributeError, ValueError) as error:
            raise InvalidReservationError("Date must use the YYYY-MM-DD format.") from error
        try:
            duration = float(duration)
        except (TypeError, ValueError) as error:
            raise InvalidReservationError("Duration must be a positive number.") from error
        if not isfinite(duration) or duration <= 0:
            raise InvalidReservationError("Duration must be a positive finite number.")
        self.identifier = identifier.strip()
        self.customer = customer
        self.service = service
        self.duration = duration
        self.date = parsed_date.isoformat()
        self.status = ReservationStatus.PENDING
        self.cost = service.calculate_cost(duration)

    def confirm(self) -> None:
        if self.status is not ReservationStatus.PENDING:
            raise OperationNotAllowedError("Only pending reservations can be confirmed.")
        self.status = ReservationStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status is ReservationStatus.CANCELLED:
            raise OperationNotAllowedError("This reservation is already cancelled.")
        self.status = ReservationStatus.CANCELLED

    def summary(self) -> str:
        return (
            f"{self.identifier} — {self.customer.name} — {self.service.name} — "
            f"{self.date} — {self.status.value} — ${self.cost:.2f}"
        )

    def __str__(self) -> str:
        return self.summary()
