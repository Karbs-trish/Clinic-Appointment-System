from models.staff import Staff


# Invariant:
#   - Inherits Staff invariants (non-empty name, id > 0, fee > 0)
#   - fee is always 5
class Pharmacist(Staff):
    """
    Represents a pharmacist in the clinic.
    """

    def __init__(self, name: str, person_id: int):
        super().__init__(name, person_id)

    def role(self) -> str:
        return "Pharmacist"

    def fee(self) -> float:
        return 5
