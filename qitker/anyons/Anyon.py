from enum import Enum

class Charge(Enum):   
    VACUUM = "1"
    TAU = "τ"


def fusion_outcomes(
    left_charge: Charge,
    right_charge: Charge,
) -> tuple[Charge, ...]:
    """Return the allowed outcomes of fusing two Fibonacci charges."""

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
    
    VALID_CHARGES = {Charge.TAU, Charge.VACUUM}
        
    #initialize class
    def __init__(self, anyon_id: int, charge: Charge = Charge.TAU):
        
        if not isinstance(anyon_id, int):
            raise TypeError("anyon_id must be an integer.")
        
        if charge not in self.VALID_CHARGES:
            raise ValueError(f"Invalid charge: {charge}")
        
        self.anyon_id = anyon_id
        self.charge = charge
    
    
    def get_id(self) -> int:                         
        return self.anyon_id


    def get_charge(self):               
        return self.charge
    

    def is_vacuum(self) -> bool:        
        return self.charge is Charge.VACUUM


    def is_tau(self) -> bool:           
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

