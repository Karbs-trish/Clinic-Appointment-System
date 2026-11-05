from models.staff import Staff


class Doctor(Staff):
    """
    Represents a doctor.
    """

    def role(self) -> str:
        """
        Return the staff role.
        """
        return "Doctor"

    def fee(self) -> float:
        """
        Doctor consultation fee.

        P = 0
        Fee = 40 + 5(P mod 5)

        40 + 5(0 mod 5)
        = 40
        """
        return 40.0