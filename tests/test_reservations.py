import tempfile
import unittest
from pathlib import Path

from exceptions.errors import (
    OperationNotAllowedError,
    InvalidReservationError,
    ServiceUnavailableError,
)
from models.customer import Customer
from models.reservation import ReservationStatus, Reservation
from models.service import RoomService
from services.system_manager import SystemManager
from utils.logger import EventLogger


class ReservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.manager = SystemManager(
            EventLogger(Path(self.directory.name) / "events.log")
        )
        self.customer = self.manager.register_customer(
            Customer("C-1", "Alex Morgan", "ID-1", "alex@example.com", "5550100")
        )
        self.service = self.manager.add_service(
            RoomService("S-1", "Conference Room", 50)
        )

    def tearDown(self) -> None:
        self.directory.cleanup()

    def test_create_confirm_cancel_and_cost(self) -> None:
        reservation = self.manager.create_reservation(
            Reservation("R-1", self.customer, self.service, 2, "2030-05-10")
        )
        self.assertEqual(reservation.cost, 100)
        self.assertEqual(reservation.status, ReservationStatus.PENDING)
        self.manager.confirm_reservation("R-1")
        self.assertEqual(reservation.status, ReservationStatus.CONFIRMED)
        self.manager.cancel_reservation("R-1")
        self.assertEqual(reservation.status, ReservationStatus.CANCELLED)

    def test_reservation_input_and_transition_validation(self) -> None:
        with self.assertRaises(InvalidReservationError):
            Reservation("R-1", self.customer, self.service, 0, "2030-05-10")
        with self.assertRaises(InvalidReservationError):
            Reservation("R-1", self.customer, self.service, 1, "not-a-date")
        with self.assertRaises(InvalidReservationError):
            self.manager.confirm_reservation("missing")

    def test_unavailable_or_already_booked_service_is_rejected(self) -> None:
        self.manager.create_reservation(
            Reservation("R-1", self.customer, self.service, 2, "2030-05-10")
        )
        with self.assertRaises(ServiceUnavailableError):
            self.manager.create_reservation(
                Reservation("R-2", self.customer, self.service, 1, "2030-05-10")
            )
        self.assertEqual(len(self.manager.reservations), 1)

    def test_failed_reservation_lookup_chains_original_exception(self) -> None:
        with self.assertRaises(InvalidReservationError) as context:
            self.manager.confirm_reservation("missing")
        self.assertIsNotNone(context.exception.__cause__)


if __name__ == "__main__":
    unittest.main()
