# Clinic Appointment System

## Authors

- Trish Kabudura — R2420408
- Pray P Matombo — R2420401

This project demonstrates a small appointment system with patients, staff,
manual time, logging, and FIFO waiting lists. It also demonstrates inheritance
and polymorphism through staff roles and the `MedicalLecturer` class.

## Run

From the `ClinicAppointmentSystem` directory, run:

```powershell
python main.py
```

The demo pauses at key workflow stages; press Enter to continue.
No third-party packages are required.
The demo writes its event log to `clinic.log` in the project directory.

## Scheduling rules

- Appointment start hours are in the range 0–168.
- A staff member can have one scheduled appointment at a given start hour,
  and a patient can have at most one non-cancelled appointment at that hour.
- Each staff member owns a FIFO waiting list; a conflicting booking is added
  to that staff member's list.
- Cancelling a scheduled appointment promotes the earliest eligible booking
  for an available staff member and hour to `Pending`.
- Confirmed appointments cannot be cancelled less than two hours before they
  start.
- The project uses P = 0: a doctor fee is $40 and a nurse fee is $10.

Run the tests from this directory with:

```powershell
python -m unittest discover
```

## Class diagram

The diagram below reflects the current classes and relationships.
`MedicalLecturer` inherits from both `Doctor` and `Lecturer`. Each `Staff`
instance owns a FIFO list containing appointment requests. These requests are
currently represented by `Appointment` objects with `WAITLISTED` status; when
promoted, the same object changes to `PENDING`.

```text
                   <<abstract>> Person
                         |
             +-----------+-----------+
             |                       |
          Patient              <<abstract>> Staff
                                     |
                    +----------------+----------------+
                    |                |                |
                  Doctor            Nurse         Pharmacist
                     \                           /
                      \                         /
                       +----> MedicalLecturer <+
                      /       (inherits from    \
                     /        both parent classes)
                  Lecturer


+-----------------------------------------------+
|                    Clinic                     |
+-----------------------------------------------+
| -patients : dict[int, Patient]                |
| -staff : dict[int, Staff]                     |
| -appointments : list[Appointment]             |
| -clock : Clock                                |
| -logger : Logger                              |
+-----------------------------------------------+
| +book(patient, staff, start_hour)             |
| +confirm(appointment_id)                      |
| +cancel(appointment_id, reason)               |
| +print_fees()                                 |
+-----------------------------------------------+
       | registers staff/patients; stores appointments
       | uses
       +---------------------> Clock
       +---------------------> Logger
       |
       +---------------------> Appointment

<<abstract>> Clock                    Logger
      |                                  |
 ManualClock                         uses Clock


+-----------------------------------------------+
|                 Appointment                   |
+-----------------------------------------------+
| -appointment_id : int                         |
| -patient : Patient                            |
| -staff : Staff                                |
| -start_hour : int                             |
| -status : AppointmentStatus                   |
| -cancellation_reason : str | None             |
+-----------------------------------------------+
| +confirm(now)                                 |
| +cancel(now, reason)                          |
| +waitlist()                                   |
| +activate()                                   |
+-----------------------------------------------+
       | assigned to one Patient
       +----------------------------------------->
       | assigned to one Staff member
       +----------------------------------------->

Staff owns: waiting_list : list[Appointment] (FIFO)
AppointmentStatus: PENDING | CONFIRMED | WAITLISTED | CANCELLED
```

## Design principles demonstrated

- **Inheritance:** `Patient` and `Staff` inherit common identity fields from
  `Person`; concrete staff roles inherit from `Staff`.
- **Polymorphism:** `Doctor`, `Nurse`, and `Pharmacist` provide their own
  `role()` and `fee()` implementations. `Clinic.print_fees()` calls `fee()`
  without branching on staff type. `MedicalLecturer` inherits the doctor fee.
- **Encapsulation:** `Appointment` validates its own confirmation,
  cancellation, waiting-list, and activation state transitions.
- **Dependency injection:** `Clinic` receives a `Clock`, so tests can use
  `ManualClock` to control time deterministically.
- **Open/closed design:** New `Staff` subclasses can participate in fee
  printing and clinic scheduling through the existing `role()` and `fee()`
  interfaces, without adding role-specific branches to `Clinic`.