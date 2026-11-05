from models.person import Person


class Patient(Person):
    """
    Represents a clinic patient.
    """

    def __init__(self, name: str, person_id: int):
        super().__init__(name, person_id)

    def __str__(self) -> str:
        return f"Patient: {self.name} (ID: {self.id})"