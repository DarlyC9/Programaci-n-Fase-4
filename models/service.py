from abc import abstractmethod
from math import isfinite

from exceptions.errors import CalculationError, MissingParameterError
from models.entity import Entity


class Service(Entity):
    category = "General"

    def __init__(
        self,
        identifier: str,
        name: str,
        hourly_rate: float,
        available: bool = True,
    ) -> None:
        super().__init__(identifier, name)
        if not self.identifier or not self.name:
            raise MissingParameterError("Service identifier and name are required.")
        self.hourly_rate = self._validate_rate(hourly_rate)
        self.available = bool(available)

    @staticmethod
    def _validate_rate(value: float) -> float:
        try:
            rate = float(value)
        except (TypeError, ValueError) as error:
            raise CalculationError("The service rate must be a number.") from error
        if not isfinite(rate) or rate <= 0:
            raise CalculationError("The service rate must be a positive finite number.")
        return rate

    @abstractmethod
    def description(self) -> str:
        """Describe this service category."""

    def summary(self) -> str:
        return f"{self.name} — {self.category} — ${self.hourly_rate:.2f}/hour"

    def __str__(self) -> str:
        return self.summary()

    def calculate_cost(
        self,
        duration: float,
        tax: float = 0.0,
        discount: float = 0.0,
    ) -> float:
        """Calculate a base, taxed, discounted, or combined price."""
        try:
            hours = float(duration)
            tax_rate = float(tax)
            discount_rate = float(discount)
        except (TypeError, ValueError) as error:
            raise CalculationError("Duration, tax, and discount must be numbers.") from error
        if not all(isfinite(value) for value in (hours, tax_rate, discount_rate)):
            raise CalculationError("Cost parameters must be finite numbers.")
        if hours <= 0 or not 0 <= tax_rate <= 1 or not 0 <= discount_rate <= 1:
            raise CalculationError(
                "Duration must be positive; tax and discount must be between 0 and 1."
            )
        return round(self.hourly_rate * hours * (1 - discount_rate) * (1 + tax_rate), 2)


class RoomService(Service):
    category = "Room"

    def description(self) -> str:
        return "Reservation of a room for the requested number of hours."


class EquipmentService(Service):
    category = "Equipment"

    def description(self) -> str:
        return "Rental of equipment for the requested number of hours."


class ConsultingService(Service):
    category = "Consulting"

    def description(self) -> str:
        return "Specialized consulting billed by the hour."
