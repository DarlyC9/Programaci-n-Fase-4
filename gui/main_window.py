import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font as tkfont
from collections.abc import Callable

from exceptions.errors import ApplicationError
from models.customer import Customer
from models.reservation import Reservation
from models.service import Service, ConsultingService, EquipmentService, RoomService
from services.system_manager import SystemManager
from utils.simulation import ScenarioResult, SimulationSession


BACKGROUND = "#0B0B0F"
PANEL = "#15151D"
SURFACE = "#20202A"
RED = "#B51224"
BRIGHT_RED = "#FF334F"
DARK_RED = "#65101C"
TEXT = "#E8E8EC"
MUTED = "#92929D"
GREEN = "#66D19E"
WARNING = "#F0B44D"

NAVIGATION_SECTIONS = (
    ("dashboard", "Dashboard"),
    ("customers", "Customers"),
    ("services", "Services"),
    ("reservations", "Reservations"),
    ("simulation", "Simulation"),
    ("logs", "System Logs"),
    ("settings", "Settings"),
)


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Software FJ | Management Console")
        self.geometry("1180x760")
        self.minsize(940, 620)
        self.configure(background=BACKGROUND)
        self.manager = SystemManager()
        self.simulation = SimulationSession(self.manager)
        self.simulation_summary = tk.StringVar(
            value="Successful: 0  |  Controlled errors: 0  |  Failed: 0"
        )
        self._configure_style()
        self._build_layout()
        self._refresh_all()

    def _configure_style(self) -> None:
        available = {family.casefold(): family for family in tkfont.families(self)}
        self.font_family = next(
            (
                available[name.casefold()]
                for name in ("Arial", "Liberation Sans", "Verdana")
                if name.casefold() in available
            ),
            tkfont.nametofont("TkDefaultFont").actual("family"),
        )
        self.mono_family = next(
            (
                available[name.casefold()]
                for name in ("Courier New", "Liberation Mono", "DejaVu Sans Mono")
                if name.casefold() in available
            ),
            self.font_family,
        )
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            ".",
            background=PANEL,
            foreground=TEXT,
            fieldbackground=SURFACE,
            font=(self.font_family, 10),
        )
        style.configure("TFrame", background=PANEL)
        style.configure("TLabel", background=PANEL, foreground=TEXT)
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("Title.TLabel", font=(self.font_family, 20, "bold"))
        style.configure("Section.TLabel", font=(self.font_family, 13, "bold"))
        style.configure(
            "TButton",
            background=RED,
            foreground=TEXT,
            borderwidth=0,
            padding=(10, 7),
        )
        style.map(
            "TButton",
            background=[("active", BRIGHT_RED), ("pressed", DARK_RED)],
            foreground=[("disabled", MUTED)],
        )
        style.configure(
            "TEntry",
            fieldbackground=SURFACE,
            foreground=TEXT,
            insertcolor=TEXT,
            padding=6,
        )
        style.configure(
            "TCombobox",
            fieldbackground=SURFACE,
            foreground=TEXT,
            padding=5,
        )
        style.map("TCombobox", fieldbackground=[("readonly", SURFACE)])
        style.configure(
            "Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=TEXT,
            rowheight=27,
            bordercolor=DARK_RED,
        )
        style.configure(
            "Treeview.Heading",
            background=RED,
            foreground=TEXT,
            font=(self.font_family, 10, "bold"),
            padding=7,
        )
        style.map("Treeview", background=[("selected", DARK_RED)])
        style.configure(
            "Nav.TButton",
            background=PANEL,
            foreground=MUTED,
            anchor="w",
            padding=(12, 10),
        )
        style.map("Nav.TButton", background=[("active", SURFACE)])
        style.configure(
            "NavActive.TButton",
            background=DARK_RED,
            foreground=TEXT,
            anchor="w",
            padding=(12, 10),
        )
        style.map("NavActive.TButton", background=[("active", RED)])

    def _build_layout(self) -> None:
        header = ttk.Frame(self, padding=(18, 12))
        header.pack(fill="x")
        ttk.Label(header, text="SOFTWARE FJ", style="Title.TLabel").pack(side="left")
        ttk.Label(
            header,
            text="SYSTEM STATUS  ●  ONLINE",
            foreground=GREEN,
            font=(self.mono_family, 10, "bold"),
        ).pack(side="right")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        sidebar = ttk.Frame(body, padding=(8, 12), width=180)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="NAVIGATION", foreground=MUTED).pack(
            anchor="w", padx=8, pady=(0, 8)
        )

        self.content_area = ttk.Frame(body)
        self.content_area.pack(side="right", fill="both", expand=True)
        self.pages: dict[str, ttk.Frame] = {}
        self.nav_buttons: dict[str, ttk.Button] = {}
        for key, title in NAVIGATION_SECTIONS:
            page = ttk.Frame(self.content_area, padding=14)
            self.pages[key] = page
            button = ttk.Button(
                sidebar,
                text=title,
                style="Nav.TButton",
                command=lambda section=key: self._show_section(section),
            )
            button.pack(fill="x", pady=2)
            self.nav_buttons[key] = button

        self._build_dashboard()
        self._build_customers()
        self._build_services()
        self._build_reservations()
        self._build_simulation()
        self._build_logs()
        self._build_settings()
        self.status = tk.StringVar(value="Ready.")
        ttk.Label(
            self,
            textvariable=self.status,
            anchor="w",
            padding=(18, 7),
            foreground=MUTED,
        ).pack(fill="x")
        self.current_section = ""
        self.current_page: ttk.Frame | None = None
        self._show_section("dashboard")

    def _show_section(self, section: str) -> None:
        page = self.pages.get(section)
        if page is None:
            raise ValueError(f"Unknown application section: {section}")
        if self.current_page is not None:
            self.current_page.pack_forget()
        page.pack(fill="both", expand=True)
        self.current_page = page
        self.current_section = section
        for key, button in self.nav_buttons.items():
            button.configure(style="NavActive.TButton" if key == section else "Nav.TButton")

    def _build_dashboard(self) -> None:
        page = self.pages["dashboard"]
        ttk.Label(page, text="Operations dashboard", style="Title.TLabel").pack(
            anchor="w", pady=(0, 14)
        )
        metrics = ttk.Frame(page)
        metrics.pack(fill="x")
        self.metric_values: dict[str, tk.StringVar] = {}
        for key, label in (
            ("customers", "CUSTOMERS"),
            ("services", "SERVICES"),
            ("reservations", "RESERVATIONS"),
            ("confirmed", "CONFIRMED"),
            ("cancelled", "CANCELLED"),
        ):
            card = ttk.Frame(metrics, padding=12, relief="solid")
            card.pack(side="left", fill="both", expand=True, padx=(0, 8))
            ttk.Label(card, text=label, foreground=MUTED).pack(anchor="w")
            variable = tk.StringVar(value="0")
            self.metric_values[key] = variable
            ttk.Label(card, textvariable=variable, style="Title.TLabel").pack(
                anchor="w", pady=(7, 0)
            )
        ttk.Label(page, text="Recent activity", style="Section.TLabel").pack(
            anchor="w", pady=(22, 8)
        )
        self.activity = tk.Text(
            page,
            height=12,
            background=SURFACE,
            foreground=TEXT,
            insertbackground=TEXT,
            font=(self.mono_family, 9),
            relief="flat",
            wrap="word",
        )
        self.activity.pack(fill="both", expand=True)
        self.activity.configure(state="disabled")
        controls = ttk.Frame(page)
        controls.pack(fill="x", pady=(12, 0))
        ttk.Button(controls, text="Refresh dashboard", command=self._refresh_all).pack(
            side="left"
        )

    def _build_customers(self) -> None:
        page = self.pages["customers"]
        ttk.Label(page, text="Customer management", style="Title.TLabel").pack(
            anchor="w", pady=(0, 12)
        )
        form = ttk.LabelFrame(page, text="Register customer", padding=10)
        form.pack(fill="x", pady=(0, 10))
        self.customer_fields = self._form_fields(
            form,
            ("Customer ID", "Full name", "Identification document", "Email", "Phone"),
            columns=5,
        )
        ttk.Button(form, text="Register customer", command=self._add_customer).grid(
            row=2, column=0, columnspan=5, sticky="w", pady=(8, 0)
        )
        self.customer_search = tk.StringVar()
        ttk.Label(page, text="Search by ID, name, document, or email").pack(anchor="w")
        search_row = ttk.Frame(page)
        search_row.pack(fill="x", pady=5)
        ttk.Entry(search_row, textvariable=self.customer_search).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(search_row, text="Search", command=self._refresh_customers).pack(
            side="left", padx=6
        )
        ttk.Button(search_row, text="Show all", command=self._show_all_customers).pack(
            side="left"
        )
        self.customer_tree = self._tree(
            page,
            ("id", "name", "document", "email", "phone"),
            ("Customer ID", "Full name", "Document", "Email", "Phone"),
        )

    def _build_services(self) -> None:
        page = self.pages["services"]
        ttk.Label(page, text="Service management", style="Title.TLabel").pack(
            anchor="w", pady=(0, 12)
        )
        form = ttk.LabelFrame(page, text="Create service", padding=10)
        form.pack(fill="x", pady=(0, 10))
        self.service_fields = self._form_fields(
            form, ("Service ID", "Service name", "Hourly rate"), columns=3
        )
        ttk.Label(form, text="Category").grid(row=0, column=3, sticky="w", padx=5)
        self.service_category = tk.StringVar(value="Room")
        ttk.Combobox(
            form,
            textvariable=self.service_category,
            values=("Room", "Equipment", "Consulting"),
            state="readonly",
            width=18,
        ).grid(row=1, column=3, sticky="ew", padx=5)
        ttk.Button(form, text="Create service", command=self._add_service).grid(
            row=2, column=0, columnspan=4, sticky="w", pady=(8, 0)
        )
        self.service_search = tk.StringVar()
        search_row = ttk.Frame(page)
        search_row.pack(fill="x", pady=5)
        ttk.Entry(search_row, textvariable=self.service_search).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(search_row, text="Search", command=self._refresh_services).pack(
            side="left", padx=6
        )
        ttk.Button(search_row, text="Show all", command=self._show_all_services).pack(
            side="left"
        )
        self.service_tree = self._tree(
            page,
            ("id", "name", "category", "rate", "availability", "description"),
            ("Service ID", "Name", "Category", "Rate / hour", "Availability", "Description"),
        )

    def _build_reservations(self) -> None:
        page = self.pages["reservations"]
        ttk.Label(page, text="Reservation management", style="Title.TLabel").pack(
            anchor="w", pady=(0, 12)
        )
        form = ttk.LabelFrame(page, text="Create reservation", padding=10)
        form.pack(fill="x", pady=(0, 10))
        self.reservation_fields = self._form_fields(
            form,
            ("Reservation ID", "Duration (hours)", "Date (YYYY-MM-DD)"),
            columns=3,
        )
        ttk.Label(form, text="Customer").grid(row=0, column=3, sticky="w", padx=5)
        self.reservation_customer = tk.StringVar()
        self.customer_combo = ttk.Combobox(
            form, textvariable=self.reservation_customer, state="readonly", width=18
        )
        self.customer_combo.grid(row=1, column=3, sticky="ew", padx=5)
        ttk.Label(form, text="Service").grid(row=0, column=4, sticky="w", padx=5)
        self.reservation_service = tk.StringVar()
        self.service_combo = ttk.Combobox(
            form, textvariable=self.reservation_service, state="readonly", width=18
        )
        self.service_combo.grid(row=1, column=4, sticky="ew", padx=5)
        ttk.Button(form, text="Create reservation", command=self._add_reservation).grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Button(form, text="Clear Form", command=self._clear_reservation_form).grid(
            row=2, column=1, sticky="w", padx=5, pady=(8, 0)
        )
        ttk.Button(form, text="Confirm selected", command=self._confirm_reservation).grid(
            row=2, column=2, sticky="w", padx=5, pady=(8, 0)
        )
        ttk.Button(form, text="Cancel selected", command=self._cancel_reservation).grid(
            row=2, column=3, sticky="w", padx=5, pady=(8, 0)
        )
        self.reservation_search = tk.StringVar()
        search_row = ttk.Frame(page)
        search_row.pack(fill="x", pady=5)
        ttk.Entry(search_row, textvariable=self.reservation_search).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(search_row, text="Search", command=self._refresh_reservations).pack(
            side="left", padx=6
        )
        ttk.Button(
            search_row, text="Show all", command=self._show_all_reservations
        ).pack(side="left")
        self.reservation_tree = self._tree(
            page,
            ("id", "customer", "service", "duration", "date", "status", "cost"),
            ("Reservation ID", "Customer", "Service", "Hours", "Date", "Status", "Cost"),
        )

    def _build_simulation(self) -> None:
        page = self.pages["simulation"]
        header = ttk.Frame(page)
        header.pack(fill="x")
        ttk.Label(header, text="Operation simulation", style="Title.TLabel").pack(
            side="left"
        )
        ttk.Label(
            header,
            textvariable=self.simulation_summary,
            foreground=MUTED,
        ).pack(side="right")
        ttk.Label(
            page,
            text="Run all 15 scenarios against an isolated in-memory system. Simulation results are separate from live application data.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 10))
        controls = ttk.Frame(page)
        controls.pack(fill="x", pady=(0, 8))
        ttk.Button(
            controls, text="Run Simulation", command=self._run_demo
        ).pack(side="left")
        ttk.Button(
            controls, text="Reset Simulation", command=self._reset_simulation
        ).pack(side="left", padx=8)
        self.demo_tree = self._tree(
            page,
            ("scenario", "expected", "actual", "status"),
            ("Scenario", "Expected result", "Actual result", "Status"),
        )
        self.demo_tree.column("scenario", width=200)
        self.demo_tree.column("expected", width=300)
        self.demo_tree.column("actual", width=300)

    def _build_logs(self) -> None:
        page = self.pages["logs"]
        top = ttk.Frame(page)
        top.pack(fill="x")
        ttk.Label(top, text="System logs", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="Clear Logs", command=self._clear_logs).pack(side="right")
        ttk.Button(top, text="Refresh", command=self._refresh_log).pack(
            side="right", padx=(0, 8)
        )
        ttk.Label(
            page,
            text=f"Log file: {self.manager.logger.path.resolve()}",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=8)
        self.log_text = tk.Text(
            page,
            background=SURFACE,
            foreground=TEXT,
            insertbackground=TEXT,
            font=(self.mono_family, 9),
            relief="flat",
            wrap="none",
        )
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")

    def _build_settings(self) -> None:
        page = self.pages["settings"]
        ttk.Label(page, text="Settings", style="Title.TLabel").pack(
            anchor="w", pady=(0, 14)
        )
        settings = ttk.LabelFrame(page, text="Application configuration", padding=14)
        settings.pack(fill="x", anchor="n")
        details = (
            ("Interface language", "English"),
            ("Color theme", "Dark red administration theme"),
            ("Primary font", self.font_family),
            ("Monospace font", self.mono_family),
            ("Data storage", "In-memory only; no database"),
            ("System log", str(self.manager.logger.path.resolve())),
        )
        for row, (label, value) in enumerate(details):
            ttk.Label(settings, text=label, foreground=MUTED).grid(
                row=row, column=0, sticky="nw", padx=(0, 18), pady=5
            )
            ttk.Label(settings, text=value, wraplength=560).grid(
                row=row, column=1, sticky="nw", pady=5
            )
        settings.columnconfigure(1, weight=1)

    def _form_fields(
        self, parent: ttk.LabelFrame, labels: tuple[str, ...], columns: int
    ) -> list[tk.StringVar]:
        fields = []
        for index, label in enumerate(labels):
            column = index % columns
            ttk.Label(parent, text=label).grid(
                row=0, column=column, sticky="w", padx=5, pady=(0, 4)
            )
            variable = tk.StringVar()
            ttk.Entry(parent, textvariable=variable).grid(
                row=1, column=column, sticky="ew", padx=5
            )
            parent.columnconfigure(column, weight=1)
            fields.append(variable)
        return fields

    def _tree(
        self, parent: ttk.Frame, columns: tuple[str, ...], headings: tuple[str, ...]
    ) -> ttk.Treeview:
        wrapper = ttk.Frame(parent)
        wrapper.pack(fill="both", expand=True, pady=(5, 0))
        tree = ttk.Treeview(wrapper, columns=columns, show="headings")
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        for column, heading in zip(columns, headings):
            tree.heading(column, text=heading)
            tree.column(column, width=130, minwidth=80, anchor="w")
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree

    def _guard(self, operation: str, action: Callable[[], None]) -> None:
        try:
            action()
        except (ApplicationError, ValueError) as error:
            self.manager.logger.error(operation, error)
            self.status.set(f"Error: {error}")
            messagebox.showerror("Operation failed", str(error), parent=self)

    def _add_customer(self) -> None:
        def action() -> None:
            customer = Customer(*(field.get() for field in self.customer_fields))
            self.manager.register_customer(customer)
            self._clear_fields(self.customer_fields)
            self._refresh_all()
            self.status.set(f"Customer {customer.identifier} registered.")

        self._guard("register_customer", action)

    def _add_service(self) -> None:
        def action() -> None:
            identifier, name, rate = (field.get() for field in self.service_fields)
            service_types: dict[str, type[Service]] = {
                "Room": RoomService,
                "Equipment": EquipmentService,
                "Consulting": ConsultingService,
            }
            service = service_types[self.service_category.get()](
                identifier, name, float(rate)
            )
            self.manager.add_service(service)
            self._clear_fields(self.service_fields)
            self._refresh_all()
            self.status.set(f"Service {service.identifier} created.")

        self._guard("create_service", action)

    def _add_reservation(self) -> None:
        def action() -> None:
            identifier, duration, date = (
                field.get() for field in self.reservation_fields
            )
            customer_id = self.reservation_customer.get()
            service_id = self.reservation_service.get()
            customer = next(
                (item for item in self.manager.customers if item.identifier == customer_id),
                None,
            )
            service = next(
                (item for item in self.manager.services if item.identifier == service_id),
                None,
            )
            if customer is None or service is None:
                raise ValueError("Select a registered customer and service first.")
            reservation = Reservation(identifier, customer, service, float(duration), date)
            self.manager.create_reservation(reservation)
            self._refresh_all()
            self.status.set(f"Reservation {reservation.identifier} created.")

        self._guard("create_reservation", action)

    def _selected_reservation_id(self) -> str:
        selection = self.reservation_tree.selection()
        if not selection:
            raise ValueError("Select a reservation from the table first.")
        return str(self.reservation_tree.item(selection[0], "values")[0])

    def _confirm_reservation(self) -> None:
        def action() -> None:
            reservation = self.manager.confirm_reservation(self._selected_reservation_id())
            self._refresh_all()
            self.status.set(f"Reservation {reservation.identifier} confirmed.")

        self._guard("confirm_reservation", action)

    def _cancel_reservation(self) -> None:
        def action() -> None:
            reservation = self.manager.cancel_reservation(self._selected_reservation_id())
            self._refresh_all()
            self.status.set(f"Reservation {reservation.identifier} cancelled.")

        self._guard("cancel_reservation", action)

    def _clear_reservation_form(self) -> None:
        self._clear_fields(self.reservation_fields)
        self.reservation_customer.set("")
        self.reservation_service.set("")
        self.reservation_search.set("")
        selection = self.reservation_tree.selection()
        if selection:
            self.reservation_tree.selection_remove(*selection)
        self.status.set("Ready.")
        self._refresh_reservations()

    def _clear_fields(self, fields: list[tk.StringVar]) -> None:
        for field in fields:
            field.set("")

    def _clear_tree(self, tree: ttk.Treeview) -> None:
        tree.delete(*tree.get_children())

    def _show_all_customers(self) -> None:
        self.customer_search.set("")
        self._refresh_customers()

    def _show_all_services(self) -> None:
        self.service_search.set("")
        self._refresh_services()

    def _show_all_reservations(self) -> None:
        self.reservation_search.set("")
        self._refresh_reservations()

    def _refresh_customers(self) -> None:
        self._clear_tree(self.customer_tree)
        query = self.customer_search.get().strip()
        items = self.manager.find_customers(query) if query else self.manager.customers
        for customer in items:
            self.customer_tree.insert(
                "",
                "end",
                values=(
                    customer.identifier,
                    customer.name,
                    customer.document_id,
                    customer.email,
                    customer.phone,
                ),
            )

    def _refresh_services(self) -> None:
        self._clear_tree(self.service_tree)
        query = self.service_search.get().strip()
        items = self.manager.find_services(query) if query else self.manager.services
        for service in items:
            self.service_tree.insert(
                "",
                "end",
                values=(
                    service.identifier,
                    service.name,
                    service.category,
                    f"${service.hourly_rate:.2f}",
                    "Available" if service.available else "Unavailable",
                    service.description(),
                ),
            )

    def _refresh_reservations(self) -> None:
        self._clear_tree(self.reservation_tree)
        query = self.reservation_search.get().strip()
        items = self.manager.find_reservations(query) if query else self.manager.reservations
        for reservation in items:
            self.reservation_tree.insert(
                "",
                "end",
                values=(
                    reservation.identifier,
                    reservation.customer.name,
                    reservation.service.name,
                    f"{reservation.duration:g}",
                    reservation.date,
                    reservation.status.value,
                    f"${reservation.cost:.2f}",
                ),
            )
        self.customer_combo.configure(
            values=tuple(item.identifier for item in self.manager.customers)
        )
        self.service_combo.configure(
            values=tuple(item.identifier for item in self.manager.services)
        )

    def _refresh_dashboard(self) -> None:
        reservations = self.manager.reservations
        counts = {
            "customers": len(self.manager.customers),
            "services": len(self.manager.services),
            "reservations": len(reservations),
            "confirmed": sum(
                item.status.value == "Confirmed" for item in reservations
            ),
            "cancelled": sum(
                item.status.value == "Cancelled" for item in reservations
            ),
        }
        for key, value in counts.items():
            self.metric_values[key].set(str(value))
        lines = self.manager.logger.read().splitlines()[-12:]
        self.activity.configure(state="normal")
        self.activity.delete("1.0", "end")
        self.activity.insert("1.0", "\n".join(lines) or "No activity recorded yet.")
        self.activity.configure(state="disabled")

    def _refresh_log(self) -> None:
        try:
            log_contents = self.manager.logger.read()
        except OSError as error:
            self.status.set(f"Unable to read system logs: {error}")
            messagebox.showerror(
                "Unable to read logs",
                f"The system log could not be opened.\n\n{error}",
                parent=self,
            )
            return
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", log_contents or "No log entries yet.")
        self.log_text.configure(state="disabled")

    def _clear_logs(self) -> None:
        confirmed = messagebox.askyesno(
            "Clear system logs",
            "This will permanently erase the existing system log history. "
            "A new entry will be written to record that the logs were cleared.\n\n"
            "Do you want to continue?",
            icon="warning",
            parent=self,
        )
        if not confirmed:
            return
        try:
            self.manager.logger.clear_logs()
        except (OSError, ValueError) as error:
            self.status.set(f"Unable to clear system logs: {error}")
            messagebox.showerror(
                "Unable to clear logs",
                f"The system log could not be cleared. Check file permissions and try again.\n\n{error}",
                parent=self,
            )
            return
        self._refresh_dashboard()
        self._refresh_log()
        self.status.set("System logs cleared. Logging is active.")

    def _run_demo(self) -> None:
        results = self.simulation.run()
        self._clear_tree(self.demo_tree)
        for result in results:
            self.demo_tree.insert(
                "",
                "end",
                values=(result.scenario, result.expected, result.actual, result.status),
            )
        failures = sum(result.status == "FAILED" for result in results)
        successful = sum(result.status == "SUCCESSFUL" for result in results)
        controlled = sum(result.status == "CONTROLLED ERROR" for result in results)
        self.simulation_summary.set(
            f"Successful: {successful}  |  Controlled errors: {controlled}  |  Failed: {failures}"
        )
        self.status.set(
            f"Demonstration complete: {len(results)} scenarios; {failures} failed."
        )
        self._refresh_dashboard()
        self._refresh_log()

    def _reset_simulation(self) -> None:
        confirmed = messagebox.askyesno(
            "Reset simulation",
            "This will clear the displayed simulation results and counters only. "
            "Registered customers, services, and reservations will not be changed.\n\n"
            "Do you want to continue?",
            icon="warning",
            parent=self,
        )
        if not confirmed:
            return
        try:
            self.simulation.reset()
        except (OSError, ValueError) as error:
            self.status.set(f"Simulation results were reset, but the operation could not be logged: {error}")
            messagebox.showerror(
                "Unable to record simulation reset",
                f"The results were cleared, but the reset event could not be recorded in the system log.\n\n{error}",
                parent=self,
            )
        self._clear_tree(self.demo_tree)
        self.simulation_summary.set(
            "Successful: 0  |  Controlled errors: 0  |  Failed: 0"
        )
        self._refresh_dashboard()
        self._refresh_log()
        if not self.status.get().startswith("Simulation results were reset,"):
            self.status.set("Simulation results cleared. Live application data is unchanged.")

    def _refresh_all(self) -> None:
        self._refresh_customers()
        self._refresh_services()
        self._refresh_reservations()
        self._refresh_dashboard()
        self._refresh_log()
