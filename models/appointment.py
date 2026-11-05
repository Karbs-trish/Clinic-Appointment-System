from models.patient import Patient
from models.staff import Staff
from utils.enums import AppointmentStatus


class Appointment:
    """
    Represents a one-hour appointment between a patient and a staff member.

    Invariants:
    - appointment_id > 0
    - patient is not None
    - staff is not None
    - start_hour is in range [0, 168]
    - status transitions:
        PENDING -> CONFIRMED
        PENDING -> CANCELLED
        PENDING -> WAITLISTED
        WAITLISTED -> PENDING
        WAITLISTED -> CANCELLED
        CONFIRMED -> CANCELLED
    - CANCELLED appointments cannot change state again.
    """

    def __init__(
        self,
        appointment_id: int,
        patient: Patient,
        staff: Staff,
        start_hour: int,
    ):
        if appointment_id <= 0:
            raise ValueError("Appointment ID must be positive.")

        if patient is None:
            raise ValueError("Patient cannot be None.")

        if staff is None:
            raise ValueError("Staff member cannot be None.")

        if not (0 <= start_hour <= 168):
            raise ValueError("Start hour must be between 0 and 168.")

        self._appointment_id = appointment_id
        self._patient = patient
        self._staff = staff
        self._start_hour = start_hour
        self._status = AppointmentStatus.PENDING
        self._cancellation_reason = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def id(self) -> int:
        return self._appointment_id

    @property
    def appointment_id(self) -> int:
        return self._appointment_id

    @property
    def patient(self) -> Patient:
        return self._patient

    @property
    def staff(self) -> Staff:
        return self._staff

    @property
    def start_hour(self) -> int:
        return self._start_hour

    @property
    def status(self) -> AppointmentStatus:
        return self._status

    @property
    def cancellation_reason(self) -> str | None:
        return self._cancellation_reason

    # ------------------------------------------------------------------
    # State Transitions
    # ------------------------------------------------------------------

    def confirm(self, now: int) -> None:
        """
        Confirm a pending appointment.

        Raises:
            ValueError if:
            - appointment is already confirmed
            - appointment is cancelled
            - appointment has already started
        """

        if self._status == AppointmentStatus.CANCELLED:
            raise ValueError(
                f"Appointment #{self.id} has been cancelled and cannot be confirmed."
            )

        if self._status == AppointmentStatus.WAITLISTED:
            raise ValueError(
                f"Appointment #{self.id} is waitlisted and cannot be confirmed."
            )

        if self._status == AppointmentStatus.CONFIRMED:
            raise ValueError(
                f"Appointment #{self.id} is already confirmed."
            )

        if now >= self._start_hour:
            raise ValueError(
                f"Appointment #{self.id} has already started."
            )

        self._status = AppointmentStatus.CONFIRMED

    def waitlist(self) -> None:
        if self._status != AppointmentStatus.PENDING:
            raise ValueError(
                f"Appointment #{self.id} cannot be added to the waiting list."
            )
        self._status = AppointmentStatus.WAITLISTED

    def activate(self) -> None:
        if self._status != AppointmentStatus.WAITLISTED:
            raise ValueError(
                f"Appointment #{self.id} is not waitlisted."
            )
        self._status = AppointmentStatus.PENDING

    def cancel(self, now: int, reason: str | None = None) -> None:
        """
        Cancel an appointment.

        Rules:
        - A cancelled appointment cannot be cancelled again.
        - A started appointment cannot be cancelled.
        - A confirmed appointment cannot be cancelled
          within two hours of its start time.
        """

        if self._status == AppointmentStatus.CANCELLED:
            raise ValueError(
                f"Appointment #{self.id} is already cancelled."
            )

        if now >= self._start_hour:
            raise ValueError(
                f"Cannot cancel appointment #{self.id}: appointment has already started."
            )

        if (
            self._status == AppointmentStatus.CONFIRMED
            and (self._start_hour - now) < 2
        ):
            raise ValueError(
                f"Cannot cancel appointment #{self.id}: less than two hours before start."
            )

        self._status = AppointmentStatus.CANCELLED
        self._cancellation_reason = reason

    # ------------------------------------------------------------------
    # String Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"Appointment #{self.id} | "
            f"Patient: {self.patient.name} | "
            f"Staff: {self.staff.name} ({self.staff.role()}) | "
            f"Hour: {self.start_hour} | "
            f"Status: {self.status.value}"
        )