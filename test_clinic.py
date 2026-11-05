import tempfile
import unittest
from pathlib import Path

from models.doctor import Doctor
from models.medical_lecturer import MedicalLecturer
from models.nurse import Nurse
from models.patient import Patient
from models.pharmacist import Pharmacist
from services.clinic import Clinic
from utils.clock import ManualClock
from utils.enums import AppointmentStatus


class ClinicTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        log_path = Path(self._temporary_directory.name) / "clinic.log"
        self.clock = ManualClock()
        self.clinic = Clinic(self.clock, str(log_path))
        self.patient1 = Patient("Patient One", 1)
        self.patient2 = Patient("Patient Two", 2)
        self.patient3 = Patient("Patient Three", 3)
        self.doctor = Doctor("Doctor One", 10)
        self.clinic.register_patient(self.patient1)
        self.clinic.register_patient(self.patient2)
        self.clinic.register_patient(self.patient3)
        self.clinic.register_staff(self.doctor)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_p_zero_fees(self) -> None:
        self.assertEqual(self.doctor.fee(), 40.0)
        self.assertEqual(Nurse("Nurse One", 11).fee(), 10.0)
        self.assertEqual(Pharmacist("Pharmacist One", 12).fee(), 5.0)

    def test_waitlist_is_fifo_and_promotes_after_cancellation(self) -> None:
        scheduled = self.clinic.book(self.patient1, self.doctor, 10)
        first_waitlisted = self.clinic.book(self.patient2, self.doctor, 10)
        second_waitlisted = self.clinic.book(self.patient3, self.doctor, 10)

        self.assertEqual(first_waitlisted.status, AppointmentStatus.WAITLISTED)
        self.assertEqual(second_waitlisted.status, AppointmentStatus.WAITLISTED)
        self.assertEqual(self.clinic.waiting_list, (first_waitlisted, second_waitlisted))

        self.clinic.cancel(scheduled.id, "Slot opened")

        self.assertEqual(first_waitlisted.status, AppointmentStatus.PENDING)
        self.assertEqual(second_waitlisted.status, AppointmentStatus.WAITLISTED)
        self.assertEqual(self.doctor.waiting_list, (second_waitlisted,))

    def test_waitlisted_appointment_cannot_be_confirmed(self) -> None:
        self.clinic.book(self.patient1, self.doctor, 10)
        waitlisted = self.clinic.book(self.patient2, self.doctor, 10)

        with self.assertRaisesRegex(ValueError, "waitlisted"):
            self.clinic.confirm(waitlisted.id)

    def test_appointment_string_has_space_after_status_colon(self) -> None:
        appointment = self.clinic.book(self.patient1, self.doctor, 10)

        self.assertIn("Status: Pending", str(appointment))

    def test_patient_cannot_book_two_non_cancelled_appointments_at_same_hour(self) -> None:
        nurse = Nurse("Nurse One", 11)
        self.clinic.register_staff(nurse)
        appointment = self.clinic.book(self.patient1, self.doctor, 10)

        with self.assertRaisesRegex(ValueError, "already has a non-cancelled appointment"):
            self.clinic.book(self.patient1, nurse, 10)

        self.assertEqual(self.clinic.appointments, (appointment,))
        self.assertEqual(nurse.waiting_list, ())

    def test_waiting_list_is_owned_by_staff_and_cancelled_entries_are_removed(self) -> None:
        nurse = Nurse("Nurse One", 11)
        self.clinic.register_staff(nurse)
        scheduled = self.clinic.book(self.patient1, self.doctor, 10)
        waitlisted = self.clinic.book(self.patient2, self.doctor, 10)

        self.assertEqual(self.doctor.waiting_list, (waitlisted,))
        self.assertEqual(nurse.waiting_list, ())
        self.clinic.cancel(waitlisted.id)
        self.assertEqual(self.doctor.waiting_list, ())
        self.assertEqual(scheduled.status, AppointmentStatus.PENDING)

    def test_confirmed_appointment_cannot_be_cancelled_too_late(self) -> None:
        appointment = self.clinic.book(self.patient1, self.doctor, 10)
        self.clinic.confirm(appointment.id)
        self.clock.set_time(9)

        with self.assertRaisesRegex(ValueError, "less than two hours"):
            self.clinic.cancel(appointment.id)

    def test_medical_lecturer_initializes_both_parent_classes(self) -> None:
        lecturer = MedicalLecturer("Doctor Lecturer", 50, "Programming")

        self.assertEqual(lecturer.name, "Doctor Lecturer")
        self.assertEqual(lecturer.module_name, "Programming")
        self.assertEqual(lecturer.role(), "Doctor and Lecturer")
        self.assertEqual(lecturer.fee(), 40.0)


if __name__ == "__main__":
    unittest.main()
