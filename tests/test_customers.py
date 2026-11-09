import tempfile
import unittest
from pathlib import Path

from exceptions.errors import DuplicateCustomerError, InvalidCustomerError
from models.customer import Customer
from services.system_manager import SystemManager
from utils.logger import EventLogger


class CustomerTests(unittest.TestCase):
    def test_customer_creation_and_encapsulation(self) -> None:
        customer = Customer(
            "C-1", "Alex Morgan", "ID-1", "alex@example.com", "+1 555 0100"
        )
        self.assertEqual(customer.name, "Alex Morgan")
        self.assertEqual(customer.email, "alex@example.com")
        with self.assertRaises(AttributeError):
            customer.name = "Changed"  # type: ignore[misc]

    def test_invalid_customer_fields_are_rejected(self) -> None:
        with self.assertRaises(InvalidCustomerError):
            Customer("", "Alex Morgan", "ID-1", "alex@example.com", "5550100")
        with self.assertRaises(InvalidCustomerError):
            Customer("C-1", "Alex Morgan", "ID-1", "invalid", "5550100")
        with self.assertRaises(InvalidCustomerError):
            Customer("C-1", "Alex Morgan", "ID-1", "alex@example.com", "123")

    def test_duplicate_identifier_document_or_email_is_prevented(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = SystemManager(EventLogger(Path(directory) / "events.log"))
            manager.register_customer(
                Customer("C-1", "Alex Morgan", "ID-1", "alex@example.com", "5550100")
            )
            duplicate = Customer(
                "C-2", "Jordan Lee", "ID-2", "alex@example.com", "5550101"
            )
            with self.assertRaises(DuplicateCustomerError):
                manager.register_customer(duplicate)
            self.assertEqual(len(manager.customers), 1)


if __name__ == "__main__":
    unittest.main()
