import tempfile
import unittest
from pathlib import Path

from exceptions.errors import DuplicateCustomerError
from models.customer import Customer
from models.reservation import Reservation
from models.service import RoomService
from services.system_manager import SystemManager
from utils.logger import EventLogger
from utils.simulation import SimulationSession, run_demonstration


class ExceptionAndSimulationTests(unittest.TestCase):
    def test_failed_operation_is_logged_and_does_not_stop_later_work(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            logger = EventLogger(Path(directory) / "events.log")
            manager = SystemManager(logger)
            customer = Customer(
                "C-1", "Alex Morgan", "ID-1", "alex@example.com", "5550100"
            )
            manager.register_customer(customer)
            with self.assertRaises(DuplicateCustomerError):
                manager.register_customer(
                    Customer(
                        "C-1", "Alex Morgan", "ID-1", "alex@example.com", "5550100"
                    )
                )
            manager.register_customer(
                Customer("C-2", "Jordan Lee", "ID-2", "jordan@example.com", "5550101")
            )
            log = logger.read()
            self.assertIn("DuplicateCustomerError", log)
            self.assertIn("register_customer", log)
            self.assertEqual(len(manager.customers), 2)

    def test_reproducible_demo_runs_all_15_scenarios_without_failures(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = SystemManager(EventLogger(Path(directory) / "events.log"))
            first = run_demonstration(manager)
            second = run_demonstration(manager)
            self.assertEqual(len(first), 15)
            self.assertEqual([item.status for item in first], [item.status for item in second])
            self.assertNotIn("FAILED", {item.status for item in first})
            self.assertIn("CONTROLLED ERROR", {item.status for item in first})
            self.assertTrue(all(item.actual for item in first))
            log = manager.logger.read()
            self.assertIn("| WARNING |", log)
            self.assertIn("error_type=DuplicateCustomerError", log)

    def test_reset_clears_only_simulation_results_and_allows_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = SystemManager(EventLogger(Path(directory) / "events.log"))
            customer = manager.register_customer(
                Customer("C-1", "Alex Morgan", "ID-1", "alex@example.com", "5550100")
            )
            service = manager.add_service(RoomService("S-1", "Room", 50))
            reservation = manager.create_reservation(
                Reservation("R-1", customer, service, 1, "2030-05-10")
            )
            simulation = SimulationSession(manager)

            first_results = simulation.run()
            self.assertEqual(len(first_results), 15)
            simulation.reset()

            self.assertEqual(simulation.results, [])
            self.assertEqual(manager.customers, (customer,))
            self.assertEqual(manager.services, (service,))
            self.assertEqual(manager.reservations, (reservation,))
            self.assertIn("reset_simulation", manager.logger.read())
            self.assertEqual(len(simulation.run()), 15)


if __name__ == "__main__":
    unittest.main()
