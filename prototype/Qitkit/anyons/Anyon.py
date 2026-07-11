from enum import Enum

"""
1 × 1 = 1
1 × τ = τ
τ × 1 = τ
τ × τ = 1 + τ
"""

"""
class Anyon - Represents a Fibonacci anyon and its topological charge.

"""


class Charge(Enum):   
    # Defines the allowed topological charges of a Fibonacci anyon.
    VACUUM = "1"
    TAU = "τ"

class Anyon:
    # Represents a single Fibonacci anyon in the system.
    VALID_CHARGES = {Charge.TAU, Charge.VACUUM}
        
    # Creates an anyon with a unique ID and topological charge.
    def __init__(self, anyon_id, charge = Charge.TAU):
        
        if charge not in self.VALID_CHARGES:
            raise ValueError(f"Invalid charge: {charge}")
        

        self.anyon_id = anyon_id
        self.charge = charge
    ##############################################################    
    def get_id(self):                   # Returns the unique identifier of the anyon.
        return self.anyon_id

    def get_charge(self):               # Returns the topological charge of the anyon.
        return self.charge.value
    
    def is_vacuum(self) -> bool:        # Returns True if the anyon has vacuum charge.
        return self.charge == Charge.VACUUM

    def is_tau(self) -> bool:           # Returns True if the anyon has tau charge.
        return self.charge == Charge.TAU

    def __str__(self):
        return f"{self.anyon_id}:{self.charge.value}"
    
    def __repr__(self):
        return f"{self.anyon_id}:{self.charge.value}"



