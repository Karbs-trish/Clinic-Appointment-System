from abc import ABC


# Invariant:
#   - module_name is a non-empty string
class Lecturer(ABC):
    """
    Represents a lecturer with a module name.
    In Python, this is an abstract class mixed into MedicalLecturer.
    (In Java this would need to be an interface since Java has no
    multiple class inheritance — restructuring would be needed there.)
    """

    def __init__(self, module_name: str, **kwargs: str):
        if not module_name.strip():
            raise ValueError("Module name cannot be empty.")
        super().__init__(**kwargs)
        self._module_name = module_name.strip()

    @property
    def module_name(self) -> str:
        return self._module_name