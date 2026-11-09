from dataclasses import dataclass
from typing import Callable

from exceptions.errors import (
    DuplicateCustomerError,
    InvalidCustomerError,
    CalculationError,
    InvalidReservationError,
    ServiceUnavailableError,
    ApplicationError,
)
from models.customer import Customer
from models.reservation import Reservation
from models.service import Service, ConsultingService, EquipmentService, RoomService
from services.system_manager import SystemManager


@dataclass(frozen=True)
class ScenarioResult:
    scenario: str
    expected: str
    actual: str
    status: str


def run_demonstration(manager: SystemManager) -> list[ScenarioResult]:
    """Run 15 repeatable scenarios against an isolated in-memory system."""
    demo = SystemManager(manager.logger)
    results: list[ScenarioResult] = []
    customers: dict[str, Customer] = {}
    services: dict[str, Service] = {}

    def run(
        name: str,
        expected: str,
        action: Callable[[], object],
        expected_error: type[ApplicationError] | None = None,
    ) -> object | None:
        operation = f"demo:{name}"
        try:
            value = action()
        except ApplicationError as error:
            actual = f"Controlled {type(error).__name__}: {error}"
            status = "CONTROLLED ERROR" if (
                expected_error is not None and isinstance(error, expected_error)
            ) else "FAILED"
            if status == "CONTROLLED ERROR":
                demo.logger.warning(operation, actual, error)
            else:
                demo.logger.error(operation, error)
            results.append(ScenarioResult(name, expected, actual, status))
            return None
        else:
            actual = str(value) if value is not None else "Completed successfully."
            status = "SUCCESSFUL" if expected_error is None else "FAILED"
            results.append(ScenarioResult(name, expected, actual, status))
            demo.logger.event(operation, f"Scenario result: {status}.")
            return value
        finally:
            demo.logger.event(operation, "Scenario execution finished.")

    def register_customer(key: str, *args: str) -> Customer:
        customer = Customer(*args)
        customers[key] = demo.register_customer(customer)
        return customer

    def add_service(key: str, service: Service) -> Service:
        services[key] = demo.add_service(service)
        return service

    def make_reservation(key: str, customer: str, service: str, date: str) -> Reservation:
        reservation = Reservation(f"R-{key}", customers[customer], services[service], 2, date)
        return demo.create_reservation(reservation)

    run(
        "Register first customer",
        "Customer is registered.",
        lambda: register_customer(
            "first", "C-001", "Alex Morgan", "ID-1001", "alex@example.com", "555-0101"
        ),
    )
    run(
        "Register second customer",
        "A different customer is registered.",
        lambda: register_customer(
            "second", "C-002", "Jordan Lee", "ID-1002", "jordan@example.com", "555-0102"
        ),
    )
    run(
        "Reject duplicate customer",
        "Duplicate is rejected with a controlled error.",
        lambda: demo.register_customer(
            Customer("C-001", "Alex Morgan", "ID-1001", "alex@example.com", "555-0101")
        ),
        DuplicateCustomerError,
    )
    run(
        "Reject invalid email",
        "Invalid email is rejected with a controlled error.",
        lambda: Customer("C-003", "Taylor Kim", "ID-1003", "not-an-email", "555-0103"),
        InvalidCustomerError,
    )
    run(
        "Create room service",
        "Room service is available at its configured rate.",
        lambda: add_service(
            "room", RoomService("S-ROOM", "Conference Room", 50)
        ),
    )
    run(
        "Create equipment service",
        "Equipment service is available at its configured rate.",
        lambda: add_service(
            "equipment", EquipmentService("S-EQUIP", "Projector", 20)
        ),
    )
    run(
        "Create consulting service",
        "Consulting service is available at its configured rate.",
        lambda: add_service(
            "consulting", ConsultingService("S-CONSULT", "Technical Consulting", 80)
        ),
    )
    run(
        "Reject invalid service parameters",
        "A zero service rate is rejected with a controlled error.",
        lambda: RoomService("S-BAD", "Invalid Room", 0),
        CalculationError,
    )
    run(
        "Create reservation",
        "A pending reservation is created and priced.",
        lambda: make_reservation("main", "first", "room", "2030-05-10"),
    )
    run(
        "Confirm reservation",
        "The pending reservation is confirmed.",
        lambda: demo.confirm_reservation("R-main"),
    )
    run(
        "Cancel reservation",
        "The reservation is cancelled.",
        lambda: demo.cancel_reservation("R-main"),
    )
    unavailable = RoomService("S-OFF", "Unavailable Room", 40, available=False)
    run(
        "Reject unavailable service",
        "An unavailable service cannot be reserved.",
        lambda: create_unavailable_reservation(demo, customers["first"], unavailable),
        ServiceUnavailableError,
    )
    run(
        "Reject invalid reservation",
        "A reservation with zero duration is rejected.",
        lambda: Reservation(
            "R-BAD", customers["first"], services["equipment"], 0, "2030-05-11"
        ),
        InvalidReservationError,
    )
    run(
        "Calculate cost with tax",
        "Two hours plus 19% tax are calculated correctly.",
        lambda: assert_cost(services["consulting"].calculate_cost(2, tax=0.19), 190.4),
    )
    run(
        "Calculate cost with discount",
        "Two hours with a 10% discount are calculated correctly.",
        lambda: assert_cost(services["consulting"].calculate_cost(2, discount=0.10), 144),
    )
    return results


def create_unavailable_reservation(
    manager: SystemManager, customer: Customer, service: RoomService
) -> Reservation:
    manager.add_service(service)
    reservation = Reservation("R-OFF", customer, service, 1, "2030-05-12")
    return manager.create_reservation(reservation)


def assert_cost(actual: float, expected: float) -> float:
    if actual != expected:
        raise CalculationError(f"Expected ${expected:.2f}, received ${actual:.2f}.")
    return actual


class SimulationSession:
    def __init__(self, manager: SystemManager) -> None:
        self.manager = manager
        self.results: list[ScenarioResult] = []

    def run(self) -> list[ScenarioResult]:
        self.results = run_demonstration(self.manager)
        return list(self.results)

    def reset(self) -> None:
        self.results.clear()
        self.manager.logger.event(
            "reset_simulation",
            "Simulation results reset; customer, service, and reservation data were preserved.",
        )
