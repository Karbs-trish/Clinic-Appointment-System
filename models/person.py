from abc import ABC


class Person(ABC):
    """
    Base class for every person in the clinic.

    Invariants:
    - id > 0
    - name is not empty
    """

    def __init__(self, name: str, person_id: int, **kwargs: str):
        if not name or not name.strip():
            raise ValueError("Name cannot be empty.")

        if person_id <= 0:
            raise ValueError("Person ID must be positive.")

        self._name = name.strip()
        self._id = person_id
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    def __str__(self) -> str:
        return f"{self._name} (ID: {self._id})"