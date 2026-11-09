# Software FJ Management System

A desktop application for managing customers, hourly services, and reservations. It is built with Python 3, object-oriented design, and Tkinter/ttk. Customer, service, and reservation data stay in memory; the only file written by the application is its event and error log.

## Project objective

The project demonstrates abstraction, inheritance, encapsulation, polymorphism, optional-parameter cost calculations, input validation, and controlled exception handling in a cross-platform desktop application.

## Architecture

| Module | Responsibility |
| --- | --- |
| `models/entity.py` | Abstract base entity |
| `models/customer.py` | Encapsulated customer data and validation |
| `models/service.py` | Abstract service and room, equipment, and consulting service types |
| `models/reservation.py` | Reservation details and lifecycle state |
| `services/system_manager.py` | In-memory collections, coordination, search, availability, and operations |
| `exceptions/errors.py` | Application-specific exception types |
| `utils/logger.py` | Timestamped file logging |
| `utils/simulation.py` | Repeatable 15-scenario operation demonstration and isolated simulation state |
| `gui/main_window.py` | Tkinter interface and user actions |
| `tests/` | Standard-library `unittest` suite |

### Object-oriented design

`Entity` is an abstract class implemented by `Customer` and `Service`. The three concrete service subclasses override their category and description. The interface and manager operate on the shared `Service` type, demonstrating polymorphism. Customer fields use properties for validation and encapsulation.

`Service.calculate_cost(duration, tax=0.0, discount=0.0)` is Python's optional-parameter approach to method overloading: callers can request a base cost, tax, discount, or both. Tax and discount are decimal rates from `0` to `1`; the discount is applied before tax.

### Exception handling and logging

The application defines specific exceptions for invalid or duplicate customers, unavailable services, invalid or duplicate reservations, prohibited operations, missing parameters, and calculation errors. Expected failures are caught at operation boundaries, logged with their operation and exception type, and presented as visible messages in the interface. The manager demonstrates `try`/`except`/`else`/`finally`; missing reservation lookups use exception chaining (`raise ... from ...`). The demonstration catches expected errors and continues to later scenarios.

The log is written to `logs/software_fj.log`. The System Logs section displays its contents and provides a confirmed **Clear Logs** action. The Simulation section includes a confirmed **Reset Simulation** action that clears simulation results only; it does not modify customers, services, or reservations. No database or data-persistence file is used.

## Project structure

```text
.
├── main.py
├── requirements.txt
├── README.md
├── exceptions/
├── gui/
├── logs/
├── models/
├── services/
├── tests/
└── utils/
```

## Requirements

- Python 3.10 or later.
- Tkinter (included with standard Windows Python installations; install the Debian package if missing).
- No third-party Python packages are required.

## Installation and execution

### Windows

1. Install Python 3.10 or later from [python.org](https://www.python.org/downloads/), ensuring the Tcl/Tk option is included.
2. From the project directory, create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Start the application:

   ```powershell
   python main.py
   ```

### Debian Linux

Install Python and Tkinter if they are not already installed:

```bash
sudo apt update
sudo apt install python3 python3-tk
```

Then, from the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python main.py
```

`requirements.txt` is intentionally dependency-free. The application uses the Python standard library only.

## Using the application

- **Dashboard:** view live totals and recent log activity.
- **Customers:** register, search, and list customers. Duplicate IDs, documents, and email addresses are rejected.
- **Services:** create and search room, equipment, and consulting services. Rates are hourly.
- **Reservations:** create reservations, calculate their costs, search, confirm, and cancel. A service can have only one active reservation per date.
- **Simulation:** run or rerun 15 scenarios and review each expected result, actual result, and status. Reset clears only the simulation results.
- **System Logs:** view or refresh the event and error file, or clear its history after confirmation.
- **Settings:** view the interface language, theme, selected fonts, storage policy, and log file location.

## Run the tests

On Windows:

```powershell
python -m unittest discover -v
```

On Debian:

```bash
python3 -m unittest discover -v
```

The suite covers object creation, abstract classes, inheritance, polymorphism, validation, cost calculations, custom exceptions, exception chaining, logging, reservation lifecycle, recovery after errors, and the 15-scenario demonstration.

## Windows and Debian font compatibility

The interface selects an installed font from Arial, Liberation Sans, or Verdana and falls back to Tk's system font. Monospace text prefers Courier New, Liberation Mono, or DejaVu Sans Mono, then falls back to the selected system font. It does not download fonts or bundle font files.

On Debian, `fonts-liberation` can provide compatible Arial-style fonts when desired:

```bash
sudo apt install fonts-liberation
```

The GUI remains usable with system fallback fonts if those optional fonts are not installed.

