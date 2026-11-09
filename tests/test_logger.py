import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from utils.logger import EventLogger


class EventLoggerTests(unittest.TestCase):
    def test_clear_logs_records_the_clear_and_logger_continues_working(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.log"
            logger = EventLogger(path)
            logger.event("before_clear", "Existing log entry.")

            logger.clear_logs()
            cleared_content = logger.read()
            self.assertNotIn("Existing log entry.", cleared_content)
            self.assertIn("System logs cleared by user.", cleared_content)

            logger.event("after_clear", "Logging continued.")
            self.assertIn("Logging continued.", logger.read())

    def test_clear_logs_reports_file_stream_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            logger = EventLogger(Path(directory) / "events.log")
            with patch.object(logger._file_handler, "stream", None):
                with self.assertRaises(OSError):
                    logger.clear_logs()


if __name__ == "__main__":
    unittest.main()
