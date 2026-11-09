import re

from exceptions.errors import InvalidCustomerError
from models.entity import Entity


class Customer(Entity):
    def __init__(
        self,
        identifier: str,
        full_name: str,
        document_id: str,
        email: str,
        phone: str,
    ) -> None:
        normalized_id = identifier.strip() if identifier else ""
        normalized_name = full_name.strip() if full_name else ""
        if not normalized_id or not normalized_name:
            raise InvalidCustomerError("Customer ID and full name are required.")
        super().__init__(normalized_id, normalized_name)
        self.document_id = document_id
        self.email = email
        self.phone = phone

    @property
    def document_id(self) -> str:
        return self._document_id

    @document_id.setter
    def document_id(self, value: str) -> None:
        value = value.strip() if value else ""
        if not value:
            raise InvalidCustomerError("An identification document is required.")
        self._document_id = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        value = value.strip() if value else ""
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise InvalidCustomerError("Enter a valid email address.")
        self._email = value

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        value = value.strip() if value else ""
        if len(re.sub(r"\D", "", value)) < 7:
            raise InvalidCustomerError("The phone number must contain at least 7 digits.")
        self._phone = value

    def summary(self) -> str:
        return f"{self.name} ({self.identifier}) — {self.email}"

    def __str__(self) -> str:
        return self.summary()
