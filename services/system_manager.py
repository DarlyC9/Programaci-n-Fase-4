from pathlib import Path

from exceptions.errors import (
    DuplicateCustomerError,
    InvalidCustomerError,
    OperationNotAllowedError,
    DuplicateReservationError,
    InvalidReservationError,
    ServiceUnavailableError,
)
from models.customer import Customer
from models.reservation import ReservationStatus, Reservation
from models.service import Service
from utils.logger import EventLogger


class SystemManager:
    def __init__(self, logger: EventLogger | None = None) -> None:
        self._customers: list[Customer] = []
        self._services: list[Service] = []
        self._reservations: list[Reservation] = []
        default_log = Path(__file__).resolve().parents[1] / "logs" / "software_fj.log"
        self.logger = logger or EventLogger(default_log)
        self.logger.event("startup", "Software FJ management system started.")

    @property
    def customers(self) -> tuple[Customer, ...]:
        return tuple(self._customers)

    @property
    def services(self) -> tuple[Service, ...]:
        return tuple(self._services)

    @property
    def reservations(self) -> tuple[Reservation, ...]:
        return tuple(self._reservations)

    def register_customer(self, customer: Customer) -> Customer:
        operation = "register_customer"
        try:
            if not isinstance(customer, Customer):
                raise InvalidCustomerError("A valid customer object is required.")
            if any(
                current.identifier.casefold() == customer.identifier.casefold()
                or current.document_id.casefold() == customer.document_id.casefold()
                or current.email.casefold() == customer.email.casefold()
                for current in self._customers
            ):
                raise DuplicateCustomerError(
                    "A customer with this identifier, document, or email already exists."
                )
            self._customers.append(customer)
        except (DuplicateCustomerError, InvalidCustomerError) as error:
            self.logger.error(operation, error)
            raise
        else:
            self.logger.event(operation, f"Customer registered: {customer.identifier}.")
            return customer
        finally:
            self.logger.event(operation, "Customer registration attempt completed.")

    def add_service(self, service: Service) -> Service:
        operation = "create_service"
        try:
            if not isinstance(service, Service):
                raise ServiceUnavailableError("A valid service object is required.")
            if any(
                current.identifier.casefold() == service.identifier.casefold()
                for current in self._services
            ):
                raise OperationNotAllowedError(
                    f"Service identifier {service.identifier} already exists."
                )
            self._services.append(service)
        except (ServiceUnavailableError, OperationNotAllowedError) as error:
            self.logger.error(operation, error)
            raise
        else:
            self.logger.event(operation, f"Service created: {service.identifier}.")
            return service

    def create_reservation(self, reservation: Reservation) -> Reservation:
        operation = "create_reservation"
        try:
            if not isinstance(reservation, Reservation):
                raise InvalidReservationError("A valid reservation object is required.")
            if any(
                current.identifier.casefold() == reservation.identifier.casefold()
                for current in self._reservations
            ):
                raise DuplicateReservationError(
                    f"Reservation identifier {reservation.identifier} already exists."
                )
            if reservation.customer not in self._customers:
                raise InvalidReservationError("The customer is not registered in this system.")
            if reservation.service not in self._services:
                raise InvalidReservationError("The service is not registered in this system.")
            if not reservation.service.available:
                raise ServiceUnavailableError(
                    f"Service {reservation.service.identifier} is unavailable."
                )
            conflict = any(
                existing.service is reservation.service
                and existing.date == reservation.date
                and existing.status is not ReservationStatus.CANCELLED
                for existing in self._reservations
            )
            if conflict:
                raise ServiceUnavailableError(
                    "This service already has an active reservation on that date."
                )
            self._reservations.append(reservation)
        except (
            DuplicateReservationError,
            InvalidReservationError,
            ServiceUnavailableError,
        ) as error:
            self.logger.error(operation, error)
            raise
        else:
            self.logger.event(operation, f"Reservation created: {reservation.identifier}.")
            return reservation

    def confirm_reservation(self, identifier: str) -> Reservation:
        reservation = self._find_reservation(identifier)
        try:
            reservation.confirm()
        except OperationNotAllowedError as error:
            self.logger.error("confirm_reservation", error)
            raise
        self.logger.event("confirm_reservation", f"Reservation confirmed: {identifier}.")
        return reservation

    def cancel_reservation(self, identifier: str) -> Reservation:
        reservation = self._find_reservation(identifier)
        try:
            reservation.cancel()
        except OperationNotAllowedError as error:
            self.logger.error("cancel_reservation", error)
            raise
        self.logger.event("cancel_reservation", f"Reservation cancelled: {identifier}.")
        return reservation

    def process_reservation(self, identifier: str) -> Reservation:
        return self.confirm_reservation(identifier)

    def find_customers(self, query: str) -> list[Customer]:
        normalized = query.strip().casefold()
        return [
            customer
            for customer in self._customers
            if normalized in customer.identifier.casefold()
            or normalized in customer.name.casefold()
            or normalized in customer.document_id.casefold()
            or normalized in customer.email.casefold()
        ]

    def find_services(self, query: str) -> list[Service]:
        normalized = query.strip().casefold()
        return [
            service
            for service in self._services
            if normalized in service.identifier.casefold()
            or normalized in service.name.casefold()
            or normalized in service.category.casefold()
        ]

    def find_reservations(self, query: str) -> list[Reservation]:
        normalized = query.strip().casefold()
        return [
            reservation
            for reservation in self._reservations
            if normalized in reservation.identifier.casefold()
            or normalized in reservation.customer.name.casefold()
            or normalized in reservation.service.name.casefold()
            or normalized in reservation.status.value.casefold()
        ]

    def _find_reservation(self, identifier: str) -> Reservation:
        try:
            return next(
                reservation
                for reservation in self._reservations
                if reservation.identifier.casefold() == identifier.strip().casefold()
            )
        except (AttributeError, StopIteration) as error:
            self.logger.error("find_reservation", error)
            raise InvalidReservationError(
                f"Reservation {identifier!r} was not found."
            ) from error
