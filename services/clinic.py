from models.appointment import Appointment
from models.patient import Patient
from models.staff import Staff
from services.logger import Logger
from utils.clock import Clock
from utils.enums import AppointmentStatus


class Clinic:
    """Coordinates clinic registration, appointments, and staff waiting lists."""

    def __init__(self, clock: Clock, log_path: str):
        self._clock = clock
        self._logger = Logger(log_path, clock)
        self._patients: dict[int, Patient] = {}
        self._staff: dict[int, Staff] = {}
        self._appointments: list[Appointment] = []
        self._next_appointment_id = 1

    @property
    def appointments(self) -> tuple[Appointment, ...]:
        return tuple(self._appointments)

    @property
    def waiting_list(self) -> tuple[Appointment, ...]:
        return tuple(
            sorted(
                (
                    appointment
                    for staff in self._staff.values()
                    for appointment in staff.waiting_list
                ),
                key=lambda appointment: appointment.id,
            )
        )

    def register_patient(self, patient: Patient) -> None:
        if patient.id in self._patients:
            raise ValueError(f"Patient ID {patient.id} is already registered.")
        self._patients[patient.id] = patient
        self._logger.log(f"Registered {patient}.")

    def register_staff(self, staff: Staff) -> None:
        if staff.id in self._staff:
            raise ValueError(f"Staff ID {staff.id} is already registered.")
        self._staff[staff.id] = staff
        self._logger.log(f"Registered {staff}.")

    def print_fees(self) -> None:
        for staff in self._staff.values():
            print(f"{staff}: ${staff.fee():.2f}")

    def book(
        self,
        patient: Patient,
        staff: Staff,
        start_hour: int,
    ) -> Appointment:
        with self._logger.session():
            self._require_registered_patient(patient)
            self._require_registered_staff(staff)
            if start_hour < self._clock.now():
                raise ValueError("Cannot book an appointment in the past.")

            patient_has_appointment = any(
                existing.patient.id == patient.id
                and existing.start_hour == start_hour
                and existing.status != AppointmentStatus.CANCELLED
                for existing in self._appointments
            )
            if patient_has_appointment:
                raise ValueError(
                    f"Patient {patient.id} already has a non-cancelled appointment "
                    f"at hour {start_hour}."
                )

            appointment = Appointment(
                self._next_appointment_id,
                patient,
                staff,
                start_hour,
            )
            self._next_appointment_id += 1

            occupied = any(
                existing.staff.id == staff.id
                and existing.start_hour == start_hour
                and existing.status != AppointmentStatus.CANCELLED
                for existing in self._appointments
            )
            if occupied:
                staff.add_to_waiting_list(appointment)
                self._logger.log(
                    f"Added {patient.name} to the waiting list for "
                    f"{staff.role()} at hour {start_hour}."
                )
            else:
                self._logger.log(
                    f"Booked {patient.name} with {staff.role()} at hour {start_hour}."
                )

            self._appointments.append(appointment)
            return appointment

    def confirm(self, appointment_id: int) -> None:
        with self._logger.session():
            appointment = self._find_appointment(appointment_id)
            appointment.confirm(self._clock.now())
            self._logger.log(f"Confirmed appointment #{appointment.id}.")

    def cancel(self, appointment_id: int, reason: str | None = None) -> None:
        with self._logger.session():
            appointment = self._find_appointment(appointment_id)
            was_scheduled = appointment.status != AppointmentStatus.WAITLISTED
            appointment.cancel(self._clock.now(), reason)
            self._logger.log(f"Cancelled appointment #{appointment.id}.")
            if was_scheduled:
                self._promote_waitlisted()
            else:
                appointment.staff.remove_from_waiting_list(appointment)

    def _find_appointment(self, appointment_id: int) -> Appointment:
        for appointment in self._appointments:
            if appointment.id == appointment_id:
                return appointment
        raise ValueError(f"Appointment #{appointment_id} was not found.")

    def _require_registered_patient(self, patient: Patient) -> None:
        if self._patients.get(patient.id) is not patient:
            raise ValueError(f"Patient {patient.id} is not registered at this clinic.")

    def _require_registered_staff(self, staff: Staff) -> None:
        if self._staff.get(staff.id) is not staff:
            raise ValueError(f"Staff member {staff.id} is not registered at this clinic.")

    def _promote_waitlisted(self) -> None:
        for staff in self._staff.values():
            considered_hours: set[int] = set()
            for appointment in staff.waiting_list:
                if appointment.start_hour in considered_hours:
                    continue
                considered_hours.add(appointment.start_hour)

                staff_slot_occupied = any(
                    existing is not appointment
                    and existing.staff.id == staff.id
                    and existing.start_hour == appointment.start_hour
                    and existing.status
                    in (AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED)
                    for existing in self._appointments
                )
                patient_slot_occupied = any(
                    existing is not appointment
                    and existing.patient.id == appointment.patient.id
                    and existing.start_hour == appointment.start_hour
                    and existing.status != AppointmentStatus.CANCELLED
                    for existing in self._appointments
                )
                if staff_slot_occupied or patient_slot_occupied:
                    continue

                appointment.activate()
                staff.remove_from_waiting_list(appointment)
                self._logger.log(
                    f"Promoted appointment #{appointment.id} from the waiting list."
                )