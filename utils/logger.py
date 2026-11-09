import logging
from pathlib import Path


class EventLogger:
    def __init__(self, path: str | Path = "logs/software_fj.log") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"software_fj.{self.path.resolve()}")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        if not self.logger.handlers:
            handler = logging.FileHandler(self.path, encoding="utf-8")
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(levelname)s | operation=%(operation)s | "
                    "%(message)s | error_type=%(error_type)s"
                )
            )
            self.logger.addHandler(handler)
        self._file_handler = next(
            handler
            for handler in self.logger.handlers
            if isinstance(handler, logging.FileHandler)
        )

    def event(self, operation: str, description: str) -> None:
        self.logger.info(
            description,
            extra={"operation": operation, "error_type": "-"},
        )

    def warning(
        self, operation: str, description: str, error: Exception | None = None
    ) -> None:
        self.logger.warning(
            description,
            extra={
                "operation": operation,
                "error_type": type(error).__name__ if error is not None else "-",
            },
        )

    def error(self, operation: str, error: Exception) -> None:
        self.logger.error(
            str(error),
            extra={"operation": operation, "error_type": type(error).__name__},
        )

    def read(self) -> str:
        if not self.path.exists():
            return ""
        return self.path.read_text(encoding="utf-8")

    def clear_logs(self) -> None:
        handler = self._file_handler
        handler.acquire()
        try:
            stream = handler.stream
            if stream is None:
                raise OSError("The system log file is not open.")
            stream.flush()
            stream.seek(0)
            stream.truncate(0)
            stream.flush()
        except (OSError, ValueError) as error:
            raise OSError(f"Unable to clear the system log: {error}") from error
        finally:
            handler.release()
        self.event("clear_logs", "System logs cleared by user.")
