from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from models.person import Person
from utils.enums import AppointmentStatus

if TYPE_CHECKING:
    from models.appointment import Appointment


class Staff(Person, ABC):
    """
    Abstract base class for all clinic staff.

    Every staff member must provide:
    - role()
    - fee()
    """

    def __init__(self, name: str, person_id: int, **kwargs: str):
        super().__init__(name, person_id, **kwargs)
        self._waiting_list: list[Appointment] = []

    @property
    def waiting_list(self) -> tuple[Appointment, ...]:
        return tuple(self._waiting_list)

    def add_to_waiting_list(self, appointment: Appointment) -> None:
        if appointment.staff is not self:
            raise ValueError("Appointment belongs to a different staff member.")
        if appointment in self._waiting_list:
            raise ValueError(f"Appointment #{appointment.id} is already waitlisted.")

        appointment.waitlist()
        self._waiting_list.append(appointment)

    def remove_from_waiting_list(self, appointment: Appointment) -> None:
        try:
            self._waiting_list.remove(appointment)
        except ValueError as error:
            raise ValueError(
                f"Appointment #{appointment.id} is not on this staff member's waiting list."
            ) from error

    @abstractmethod
    def role(self) -> str:
        """
        Return the role of the staff member.
        """
        pass

    @abstractmethod
    def fee(self) -> float:
        """
        Return the consultation fee.
        """
        pass

    def __str__(self) -> str:
        return f"{self.role()} - {self.name} (ID: {self.id})"