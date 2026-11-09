import unittest
from abc import ABC

from exceptions.errors import CalculationError
from models.entity import Entity
from models.service import Service, ConsultingService, EquipmentService, RoomService


class ServiceTests(unittest.TestCase):
    def test_entity_and_service_are_abstract(self) -> None:
        self.assertTrue(issubclass(Entity, ABC))
        with self.assertRaises(TypeError):
            Entity("1", "Abstract")  # type: ignore[abstract]
        with self.assertRaises(TypeError):
            Service("1", "Abstract", 10)  # type: ignore[abstract]

    def test_service_categories_override_description(self) -> None:
        room = RoomService("S-1", "Room", 50)
        equipment = EquipmentService("S-2", "Equipment", 20)
        consulting = ConsultingService("S-3", "Consulting", 80)
        services = (room, equipment, consulting)
        self.assertEqual([item.category for item in services], ["Room", "Equipment", "Consulting"])
        self.assertEqual(len({item.description() for item in services}), 3)
        self.assertTrue(all(isinstance(item, Service) for item in services))

    def test_calculation_supports_optional_tax_and_discount(self) -> None:
        service = ConsultingService("S-1", "Consulting", 100)
        self.assertEqual(service.calculate_cost(2), 200)
        self.assertEqual(service.calculate_cost(2, tax=0.19), 238)
        self.assertEqual(service.calculate_cost(2, discount=0.1), 180)
        self.assertEqual(
            service.calculate_cost(2, tax=0.19, discount=0.1), 214.2
        )

    def test_invalid_rates_and_calculation_parameters_raise_custom_error(self) -> None:
        with self.assertRaises(CalculationError):
            RoomService("S-1", "Room", 0)
        with self.assertRaises(CalculationError):
            RoomService("S-1", "Room", 50).calculate_cost(0)
        with self.assertRaises(CalculationError):
            RoomService("S-1", "Room", 50).calculate_cost(1, tax=1.5)


if __name__ == "__main__":
    unittest.main()
