from enum import Enum


# Legal transitions:
#   PENDING   → CONFIRMED
#   PENDING   → CANCELLED
#   PENDING   → WAITLISTED
#   WAITLISTED → PENDING (when a slot opens)
#   WAITLISTED → CANCELLED
#   CONFIRMED → CANCELLED  (only if now < start - 2 hours, and not yet started)
#
# Illegal transitions (must raise an error):
#   CANCELLED → anything   (a cancelled appointment can never return)
#   CONFIRMED → PENDING    (cannot return to pending)
#   any       → CONFIRMED  (once started, cannot confirm again)
class AppointmentStatus(Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    WAITLISTED = "Waitlisted"
    CANCELLED = "Cancelled"