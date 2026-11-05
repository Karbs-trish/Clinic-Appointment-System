from pathlib import Path

from services.clinic import Clinic
from utils.clock import ManualClock
from models.patient import Patient
from models.doctor import Doctor
from models.nurse import Nurse
from models.pharmacist import Pharmacist
from models.medical_lecturer import MedicalLecturer


def continue_demo() -> None:
    input("Press Enter to continue...")


def main():

    # ── Setup ──────────────────────────────────────────────────────────────────

    clock = ManualClock(0)

    clinic = Clinic(
        clock=clock,
        log_path=str(Path(__file__).parent / "clinic.log"),
    )

    # ── Register patients ──────────────────────────────────────────────────────

    patient1 = Patient("Trish", 1)
    patient2 = Patient("John", 2)
    patient3 = Patient("Alex", 3)

    clinic.register_patient(patient1)
    clinic.register_patient(patient2)
    clinic.register_patient(patient3)

    # ── Register staff ─────────────────────────────────────────────────────────

    doctor = Doctor("Dr Smith", 10)
    nurse = Nurse("Nurse Mary", 11)
    pharmacist = Pharmacist("Peter", 12)

    clinic.register_staff(doctor)
    clinic.register_staff(nurse)
    clinic.register_staff(pharmacist)

    # ── Part 3: polymorphic fee loop ───────────────────────────────────────────

    print("\n" + "=" * 12 + " Staff Fees (Part 3 - no isinstance) " + "=" * 12)
    clinic.print_fees()
    print()

    # ── Book appointments ──────────────────────────────────────────────────────

    print("=" * 12 + " Booking Appointments " + "=" * 12)
    appointment1 = clinic.book(patient1, doctor, 20)
    appointment2 = clinic.book(patient2, nurse, 25)
    print()

    # ── Confirm ────────────────────────────────────────────────────────────────

    print("=" * 12 + " Confirming Appointment #1 " + "=" * 12)
    clinic.confirm(appointment1.appointment_id)
    print()

    # ── Cancel appointment2 (PENDING, far enough away — succeeds) ─────────────

    print("=" * 12 + " Cancellation Workflow " + "=" * 12)
    print(f"Patient: {appointment2.patient.name}")
    print(f"Appointment: #{appointment2.id} ({appointment2.status.value})")
    print("Step 1: Clinic received the cancellation request.")
    continue_demo()
    print("Step 2: Clinic is checking the cancellation rules.")
    clinic.cancel(appointment2.appointment_id, "Patient requested cancellation")
    print("Step 3: Decision: APPROVED.")
    print(f"Step 4: Appointment status is now {appointment2.status.value}.")
    print("Reason: Patient requested cancellation.")
    print()

    # ── Deliberate failure: cancel confirmed appointment too close to start ────

    print("=" * 12 + " Cancellation Workflow " + "=" * 12)
    clock.set_time(19)      # now at hour 19 — only 1 hour before start at 20
    print(f"Patient: {appointment1.patient.name}")
    print(f"Appointment: #{appointment1.id} ({appointment1.status.value})")
    print(
        f"Step 1: Clinic received a cancellation request at hour {clock.now()} "
        f"for an appointment at hour {appointment1.start_hour}."
    )
    continue_demo()
    print("Step 2: Clinic is checking the cancellation rules.")
    try:
        clinic.cancel(appointment1.appointment_id, "Changed mind")
    except ValueError as error:
        print("Step 3: Decision: REJECTED.")
        print(f"Reason: {error}")
        print(f"Step 4: Appointment remains {appointment1.status.value}.")
    print()

    # ── Conflict and FIFO waiting list demonstration ───────────────────────────

    print("=" * 12 + " Booking Conflicts and FIFO Waiting List " + "=" * 12)
    clock.set_time(0)
    scheduled = clinic.book(patient1, doctor, 40)
    first_waitlisted = clinic.book(patient2, doctor, 40)
    second_waitlisted = clinic.book(patient3, doctor, 40)
    print(
        f"RESULT: Appointment #{scheduled.id} is booked; appointments "
        f"#{first_waitlisted.id} and #{second_waitlisted.id} are added to "
        f"{doctor.name}'s waiting list in that order."
    )
    print(f"\nWaiting List for {doctor.name} (before cancellation):")
    for position, appointment in enumerate(doctor.waiting_list, start=1):
        print(f"{position}. {appointment.patient.name}")

    print(
        f"Request: book {patient2.name} with {nurse.name} at hour "
        f"{first_waitlisted.start_hour} as well."
    )
    try:
        clinic.book(patient2, nurse, 40)
    except ValueError as error:
        print(f"RESULT: Booking rejected because the patient already has an appointment. {error}")

    print(f"\n=== Waiting List Promotion Workflow ===")
    print(f"Request: cancel appointment #{scheduled.id} to open the hour-40 slot.")
    continue_demo()
    print(f"Clinic checks {doctor.name}'s waiting list in FIFO order:")
    for position, appointment in enumerate(doctor.waiting_list, start=1):
        print(f"{position}. {appointment.patient.name}")
    clinic.cancel(scheduled.id, "Opening the slot")
    print(f"Decision: cancellation approved; appointment #{scheduled.id} is cancelled.")
    print(
        f"First eligible patient, {first_waitlisted.patient.name}, is promoted "
        f"to {first_waitlisted.status.value}."
    )
    print(f"\nWaiting List for {doctor.name} (after promotion):")
    for position, appointment in enumerate(doctor.waiting_list, start=1):
        print(f"{position}. {appointment.patient.name}")
    print()

    # ── Part 5: MedicalLecturer — multiple inheritance ─────────────────────────

    print("=" * 12 + " MedicalLecturer (Part 5) " + "=" * 12)
    lecturer = MedicalLecturer(
        name="Dr Brown",
        person_id=50,
        module_name="Object Oriented Programming",
    )

    print(f"Name   : {lecturer.name}")
    print(f"Role   : {lecturer.role()}")
    print(f"Module : {lecturer.module_name}")
    print(f"Fee    : ${lecturer.fee():.2f}")
    print()

    # ── Display all appointments ───────────────────────────────────────────────

    print("=" * 12 + " All Appointments " + "=" * 12)
    for appointment in clinic.appointments:
        print(appointment)


if __name__ == "__main__":
    main()