from models.staff import Staff


# Invariant:
#   - Inherits Staff invariants (non-empty name, id > 0, fee > 0)
#   - P = 0, so the nurse fee is 10
class Nurse(Staff):
    """
    Represents a nurse in the clinic.
    """

    def __init__(self, name: str, person_id: int):
        super().__init__(name, person_id)

    def role(self) -> str:
        return "Nurse"

    def fee(self) -> float:
        return 10.0