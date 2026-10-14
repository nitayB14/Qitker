from enum import Enum

class Charge(Enum):   
    """Topological charges in the Fibonacci anyon model.

    VACUUM is the trivial charge (1); TAU is the nontrivial charge (τ).
    """
    VACUUM = "1"
    TAU = "τ"


def fusion_outcomes(
    left_charge: Charge,
    right_charge: Charge,
) -> tuple[Charge, ...]:
    """Return the possible outcomes of fusing two Fibonacci charges.

    Fusing VACUUM with any charge leaves that charge unchanged.
    Fusing TAU with TAU returns VACUUM and TAU, in that order.

    Args:
        left_charge: The first charge.
        right_charge: The second charge.

    Returns:
        A tuple of the allowed resulting charges.

    Raises:
        TypeError: If either argument is not a Charge value.
    """
    if not isinstance(left_charge, Charge):
        raise TypeError(
            "left_charge must be a Charge value."
        )

    if not isinstance(right_charge, Charge):
        raise TypeError(
            "right_charge must be a Charge value."
        )

    if left_charge is Charge.VACUUM:
        return (right_charge,)

    if right_charge is Charge.VACUUM:
        return (left_charge,)

    return (
        Charge.VACUUM,
        Charge.TAU,
    )



class Anyon:
    """Represent an anyon by its integer ID and topological charge."""

    VALID_CHARGES = {Charge.TAU, Charge.VACUUM}
        
    #initialize class
    def __init__(self, anyon_id: int, charge: Charge = Charge.TAU):
        """Create an anyon with the given ID and charge.

        Args:
            anyon_id: Integer identifier of the anyon.
            charge: Topological charge; defaults to Charge.TAU.

        Raises:
            TypeError: If anyon_id is not an integer.
            ValueError: If charge is not a supported charge.
        """

        if not isinstance(anyon_id, int):
            raise TypeError("anyon_id must be an integer.")
        
        if charge not in self.VALID_CHARGES:
            raise ValueError(f"Invalid charge: {charge}")
        
        self.anyon_id = anyon_id
        self.charge = charge
    
    
    def get_id(self) -> int:      
        """
        Return id of anyon

        Returns:
            int: anyon id
        """
        return self.anyon_id


    def get_charge(self):               
        """
        Return charge of anyon

        Returns:
            Charge: anyon charge
        """
        return self.charge
    

    def is_vacuum(self) -> bool:
        """
        Return is anyon is vaccum

        Returns:
            bool: True if charge is vacuum
        """
        return self.charge is Charge.VACUUM


    def is_tau(self) -> bool:           
        """
        Return is anyon is tau

        Returns:
            bool: True if charge is tau
        """
        return self.charge is Charge.TAU


    #returning string with basic information on the circuit
    def __str__(self):
        return f"{self.anyon_id}:{self.charge.value}"
    
    #returning string with basic information on the circuit
    def __repr__(self) -> str:
        return (
            f"Anyon("
            f"id={self.anyon_id}, "
            f"charge={self.charge.value})"
        )

