import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from gui.main_window import MainWindow
from models.customer import Customer
from models.reservation import Reservation, ReservationStatus
from models.service import RoomService
from services.system_manager import SystemManager
from utils.logger import EventLogger


class FakeVariable:
    def __init__(self, value: str) -> None:
        self.value = value

    def get(self) -> str:
        return self.value

    def set(self, value: str) -> None:
        self.value = value


class FakeTree:
    def __init__(self, selected: tuple[str, ...]) -> None:
        self.selected = selected
        self.removed: tuple[str, ...] = ()

    def selection(self) -> tuple[str, ...]:
        return self.selected

    def selection_remove(self, *items: str) -> None:
        self.removed = items
        self.selected = ()


class ReservationFormTests(unittest.TestCase):
    def test_clear_form_resets_inputs_and_selection_without_changing_live_data(self) -> None:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        manager = SystemManager(
            EventLogger(Path(temporary_directory.name) / "events.log")
        )
        customer = manager.register_customer(
            Customer("C-1", "Alex Morgan", "ID-1", "alex@example.com", "5550100")
        )
        service = manager.add_service(RoomService("S-1", "Conference Room", 50))
        reservation = manager.create_reservation(
            Reservation("R-1", customer, service, 2, "2030-05-10")
        )
        stored_data = (manager.customers, manager.services, manager.reservations)
        stored_status = reservation.status

        fields = [FakeVariable("draft") for _ in range(3)]
        customer_selection = FakeVariable("C-1")
        service_selection = FakeVariable("S-1")
        search = FakeVariable("R-1")
        status = FakeVariable("Error: previous validation message")
        tree = FakeTree(("reservation-row",))
        refresh_calls: list[bool] = []
        form = SimpleNamespace(
            reservation_fields=fields,
            reservation_customer=customer_selection,
            reservation_service=service_selection,
            reservation_search=search,
            reservation_tree=tree,
            status=status,
            _clear_fields=lambda variables: [
                variable.set("") for variable in variables
            ],
            _refresh_reservations=lambda: refresh_calls.append(True),
        )

        MainWindow._clear_reservation_form(form)

        self.assertEqual([field.get() for field in fields], ["", "", ""])
        self.assertEqual(customer_selection.get(), "")
        self.assertEqual(service_selection.get(), "")
        self.assertEqual(search.get(), "")
        self.assertEqual(tree.removed, ("reservation-row",))
        self.assertEqual(status.get(), "Ready.")
        self.assertEqual(refresh_calls, [True])
        self.assertEqual(
            (manager.customers, manager.services, manager.reservations), stored_data
        )
        self.assertIs(reservation.status, stored_status)
        self.assertEqual(reservation.status, ReservationStatus.PENDING)


if __name__ == "__main__":
    unittest.main()
