from enum import Enum




class Charge(Enum):   
    """ 
    Defines the allowed topological charges of a Fibonacci anyon.
    
    Atrributes:
        - VACUUM  ("1") : Vacuum charge.
        - TAU:    ("τ") : Fibonacci anyon charge
    
    """

    VACUUM = "1"
    TAU = "τ"



class Anyon:
    """
    Represents a single Fibonacci anyon in the system.

    Attributes:
        - anyon_id: int
            number of anyon
        - charge : Charge
            charge of anyon (can be 1 or tau)
         
    """
    
    VALID_CHARGES = {Charge.TAU, Charge.VACUUM}
        

    #initialize class
    def __init__(self, anyon_id, charge = Charge.TAU):
        
        if charge not in self.VALID_CHARGES:
            raise ValueError(f"Invalid charge: {charge}")
        
        self.anyon_id = anyon_id
        self.charge = charge
    
    
    def get_id(self):                   
        """
        Returns the unique identifier of the anyon.

        Args:
            - None

        Returns:
            - (int) : anyon id
        """

        return self.anyon_id


    def get_charge(self):               
        """
        Returns the topological charge of the anyon.

        Args:
            - None

        Returns:
            - (Charge) : anyon charge
        """

        return self.charge.value
    

    def is_vacuum(self) -> bool:        
        """
        Returns True if the anyon has vacuum charge.

        Args:
            - None

        Returns:
            - (bool) : if vacuum -> True
        """

        return self.charge == Charge.VACUUM


    def is_tau(self) -> bool:           
        """
        Returns True if the anyon has tau charge.

        Args:
            - None

        Returns:
            - (bool) : if tau -> True
        """

        return self.charge == Charge.TAU


    #returning string with basic information on the circuit
    def __str__(self):
        return f"{self.anyon_id}:{self.charge.value}"
    
    #returning string with basic information on the circuit
    def __repr__(self):
        return f"{self.anyon_id}:{self.charge.value}"



"""
1 × 1 = 1
1 × τ = τ
τ × 1 = τ
τ × τ = 1 + τ
"""

"""
class Anyon - Represents a Fibonacci anyon and its topological charge.

"""