# Software FJ Management System

A cross-platform desktop application for managing customers, hourly services, and reservations, developed with Python 3, object-oriented programming (OOP), and Tkinter/ttk.

The application provides customer management, service administration, reservation scheduling, cost calculations, input validation, exception handling, activity logging, and automated simulation scenarios.

All customer, service, and reservation records are stored in memory. No database or persistent data storage is used. The only file generated at runtime is the application log.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Object-Oriented Design](#object-oriented-design)
- [Project Architecture](#project-architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Application Modules](#application-modules)
- [Simulation](#simulation)
- [Logging System](#logging-system)
- [Running Tests](#running-tests)
- [Data Storage and Limitations](#data-storage-and-limitations)
- [Cross-Platform Compatibility](#cross-platform-compatibility)
- [Technologies Used](#technologies-used)

## Project Overview

Software FJ Management System is an educational desktop application designed to demonstrate fundamental and intermediate object-oriented programming concepts through a practical management system.

The project integrates a graphical user interface with a modular architecture, custom exceptions, input validation, service cost calculations, and automated testing.

Its design emphasizes code organization, maintainability, reusability, and controlled error handling.

## Features

### Dashboard
- Display live system totals.
- Show recent system activity.
- Provide an overview of application operations.

### Customer Management
- Register new customers.
- Search and list registered customers.
- Validate customer information.
- Prevent duplicate IDs, documents, and email addresses.

### Service Management
- Create and search services.
- Support three service categories:
  - Room services.
  - Equipment services.
  - Consulting services.
- Manage hourly service rates.

### Reservation Management
- Create and search reservations.
- Calculate reservation costs.
- Confirm and cancel reservations.
- Prevent multiple active reservations for the same service on the same date.

### Simulation
- Execute 15 predefined operation scenarios.
- Display expected results and actual results.
- Identify successful and unsuccessful scenarios.
- Rerun simulations.
- Reset simulation results without modifying customers, services, or reservations.

### System Logs
- Record application events and errors.
- Display log contents.
- Refresh the log viewer.
- Clear log history after user confirmation.

### Settings
- Display interface language and theme.
- Show selected fonts.
- Display storage policy.
- Show the log file location.

## Object-Oriented Design

The application demonstrates the following OOP principles:

| Concept | Implementation |
|---|---|
| Abstraction | Abstract `Entity` and `Service` classes |
| Inheritance | `Customer` and `Service` inherit from `Entity` |
| Polymorphism | Concrete service subclasses override shared methods |
| Encapsulation | Customer attributes use properties and validation |
| Exception handling | Application-specific exception classes |
| Reusability | Shared service interfaces and centralized management |

### Service Cost Calculation

The method:

```python
calculate_cost(duration, tax=0.0, discount=0.0)
```

Uses optional parameters to provide flexible cost calculations.

- `duration`: Service duration in hours.
- `tax`: Tax rate expressed as a decimal between 0 and 1.
- `discount`: Discount rate expressed as a decimal between 0 and 1.

The discount is applied before tax.

This approach demonstrates flexible method behavior using optional parameters.

## Project Architecture

The project follows a modular structure that separates models, business logic, graphical interface, utilities, exceptions, and tests.

```text
Software-FJ-Management-System/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── exceptions/
│   └── errors.py
│
├── gui/
│   └── main_window.py
│
├── models/
│   ├── entity.py
│   ├── customer.py
│   ├── service.py
│   └── reservation.py
│
├── services/
│   └── system_manager.py
│
├── tests/
│   └── ...
│
└── utils/
    ├── logger.py
    └── simulation.py
```

The `logs/` directory is generated automatically at runtime and is not included in the repository.

## Requirements

- Python 3.10 or later.
- Tkinter and ttk.
- Python standard library.
- No third-party Python packages are required.

## Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
```

Replace `YOUR_REPOSITORY_URL` with the actual GitHub repository URL.

### 2. Enter the project directory

```bash
cd Software-FJ-Management-System
```

### 3. Create a virtual environment

**Windows:**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**Debian Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Running the Application

### Windows

Install Python 3.10 or later from:

https://www.python.org/downloads/

Ensure Tcl/Tk support is included during installation.

Run:

```powershell
python main.py
```

### Debian Linux

Install Python and Tkinter:

```bash
sudo apt update
sudo apt install python3 python3-tk
```

Run:

```bash
python3 main.py
```

## Application Modules

| Module | Description |
|---|---|
| `models/entity.py` | Defines the abstract base entity |
| `models/customer.py` | Manages customer information and validation |
| `models/service.py` | Defines abstract and concrete service types |
| `models/reservation.py` | Manages reservation information and lifecycle |
| `services/system_manager.py` | Coordinates application operations and in-memory collections |
| `exceptions/errors.py` | Defines custom application exceptions |
| `utils/logger.py` | Handles timestamped event and error logging |
| `utils/simulation.py` | Executes the 15 predefined simulation scenarios |
| `gui/main_window.py` | Implements the Tkinter graphical interface |
| `tests/` | Contains automated unit tests |

## Simulation

The application includes a demonstration of 15 predefined scenarios covering normal operations and expected error conditions.

Each scenario displays:

- Expected result.
- Actual result.
- Execution status.

The simulation can be executed repeatedly.

The **Reset Simulation** action clears simulation results only. It does not modify registered customers, services, or reservations.

## Logging System

Application events and errors are recorded in:

```text
logs/software_fj.log
```

The log directory and file are automatically created when the application starts.

Log entries include timestamps and relevant operation and exception information.

The System Logs interface allows users to view, refresh, and clear the log history after confirmation.

Log files are excluded from version control through `.gitignore`.

## Running Tests

The project uses Python's built-in `unittest` framework.

Run the complete test suite from the project root directory.

**Windows:**

```powershell
python -m unittest discover -v
```

**Debian Linux:**

```bash
python3 -m unittest discover -v
```

The test suite covers:

- Object creation.
- Abstract classes.
- Inheritance.
- Polymorphism.
- Data validation.
- Cost calculations.
- Custom exceptions.
- Exception chaining.
- Logging.
- Reservation lifecycle.
- Recovery after errors.
- The 15-scenario demonstration.

## Data Storage and Limitations

The application uses in-memory storage for customers, services, reservations, and simulation results.

Consequently, these records are available only while the application is running. All records are lost when the application closes.

The log file is the only automatically generated file. It records application events and errors but does not provide data persistence.

No database, external storage service, or third-party dependency is required.

This project is intended as an educational demonstration of object-oriented programming, desktop application development, validation, and exception handling.

## Cross-Platform Compatibility

The application is designed to run on Windows and Debian Linux.

The interface selects an available font from the following options:

- Arial.
- Liberation Sans.
- Verdana.

For monospace text, it prefers:

- Courier New.
- Liberation Mono.
- DejaVu Sans Mono.

If these fonts are unavailable, the application uses the system font fallback.

On Debian, compatible fonts can optionally be installed with:

```bash
sudo apt install fonts-liberation
```

No fonts are downloaded or bundled with the application.

## Technologies Used

- **Python 3.10+** — Main programming language.
- **Tkinter** — Desktop graphical interface.
- **ttk** — Interface widgets and styling.
- **OOP** — Object-oriented programming principles.
- **unittest** — Automated testing.
- **logging** — Event and error recording.
- **Git and GitHub** — Version control and repository management.

---

## License

No license has been specified for this project yet. All rights are reserved by the author unless a license is added to the repository.

---

**Software FJ Management System**  
Python Desktop Application | Object-Oriented Programming
