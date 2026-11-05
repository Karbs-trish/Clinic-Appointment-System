from models.doctor import Doctor
from models.lecturer import Lecturer


# Invariant:
#   - Inherits Doctor invariants (non-empty name, id > 0, fee > 0)
#   - module_name is a non-empty string
#   - Person.__init__ is called exactly once through cooperative initialization
class MedicalLecturer(Doctor, Lecturer):
    """
    A doctor who is also a lecturer.
    Demonstrates multiple inheritance: MedicalLecturer inherits from both
    Doctor and Lecturer, but shares exactly one Person base via Python's MRO.
    """

    def __init__(self, name: str, person_id: int, module_name: str):
        super().__init__(
            name=name,
            person_id=person_id,
            module_name=module_name,
        )

    def role(self) -> str:
        return "Doctor and Lecturer"

    # fee() is inherited from Doctor.