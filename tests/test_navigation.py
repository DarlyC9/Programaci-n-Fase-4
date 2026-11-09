import unittest
import inspect
from types import SimpleNamespace

from gui.main_window import MainWindow, NAVIGATION_SECTIONS


class FakePage:
    def __init__(self) -> None:
        self.packed = False
        self.forgotten = False

    def pack_forget(self) -> None:
        self.forgotten = True
        self.packed = False

    def pack(self, **_kwargs: object) -> None:
        self.packed = True


class FakeButton:
    def __init__(self) -> None:
        self.style = ""

    def configure(self, *, style: str) -> None:
        self.style = style


class NavigationTests(unittest.TestCase):
    def test_sidebar_switches_all_sections_and_marks_active_item(self) -> None:
        pages = {key: FakePage() for key, _title in NAVIGATION_SECTIONS}
        buttons = {key: FakeButton() for key, _title in NAVIGATION_SECTIONS}
        window = SimpleNamespace(
            pages=pages,
            nav_buttons=buttons,
            current_page=pages["dashboard"],
            current_section="dashboard",
        )

        for key, _title in NAVIGATION_SECTIONS:
            MainWindow._show_section(window, key)
            self.assertIs(window.current_page, pages[key])
            self.assertTrue(pages[key].packed)
            self.assertEqual(buttons[key].style, "NavActive.TButton")
            for other_key, button in buttons.items():
                if other_key != key:
                    self.assertEqual(button.style, "Nav.TButton")

    def test_navigation_has_no_redundant_notebook(self) -> None:
        self.assertEqual(
            tuple(key for key, _title in NAVIGATION_SECTIONS),
            (
                "dashboard",
                "customers",
                "services",
                "reservations",
                "simulation",
                "logs",
                "settings",
            ),
        )
        self.assertNotIn("ttk.Notebook", inspect.getsource(MainWindow))


if __name__ == "__main__":
    unittest.main()
