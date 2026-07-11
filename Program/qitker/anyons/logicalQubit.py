from qitker.anyons.Anyon import Anyon, Charge
from qitker.anyons.FusionTree import FusionTree
import numpy as np



#: Default Fibonacci anyon configuration for a logical qubit.
#:
#: Creates four anyons with the standard initial charges:
#:     Anyon 1 : Vacuum (1)
#:     Anyon 2 : Tau (τ)
#:     Anyon 3 : Tau (τ)
#:     Anyon 4 : Tau (τ)
#:
#: This configuration is used as the starting state before any
#: braiding or fusion operations are applied.
anyons_default = [
        Anyon(1, Charge.VACUUM),
        Anyon(2),
        Anyon(3),
        Anyon(4)
        ]





# 
class logicalQubit():
    """
    Represents a logical qubit encoded using four Fibonacci anyons.
    
    Attributes:
        - movmentList : np.array
            contain all braids movments
        - tree : FusionTree
            structure of the logical anyon qubit          
    """
    def __init__(self):
        
        self.tree = FusionTree(
            anyons=anyons_default,
            total_charge=Charge.VACUUM
        )

        self.movmentList = np.array([])
        self.movmentList = np.append(self.movmentList, f"Start             {(self.tree.structure)}") 


    # Applies the specified braid generator (σi or σi⁻¹).       
    def sigma(self, index, state, hilbertOp):
        """
        navigate each sigma operation to the function that apply it

        Args:
            - index (int):
                represent sigma op [for one qubit can be 1, -1, 2, -2, 3, -3]
            - state (np.array([1,0], dtype=complex))
                represent the state vector
            - hilbertOp (hilbertSpace)
                object of the mathematical operations
        Returns:
            - (np.array([1,0], dtype=complex)) - state
        """
        
        state = hilbertOp.sigma(index, state)
        if(index > 0):
            if index % 4 == 1:
                self.leftSwitchPositive()
            elif index % 4 == 2:
                self.middleSwitchPositive()
            elif index % 4 == 3:
                self.rightSwitchPositive()
        elif(index < 0):
            if index % -4 == -1:
                self.leftSwitchNegative()
            elif index % -4 == -2:
                self.middleSwitchNegative()
            elif index % -4 == -3:
                self.rightSwitchNegative()
        else:
            raise ValueError("For 4 anyons, sigma cannot be 0 ")

        return state

#############################################################################

    def leftSwitchPositive(self):                 # R
        """
        Applies a positive braid exchange on the left anyon pair

        Args:
            - None 
        Returns:
            - None
        """

        first, second = self.tree.getLeftId()
        self.tree.RMove(first,second)
        self.movmentList = np.append(self.movmentList, f"12|R              {(self.tree.structure)}") 


    def middleSwitchPositive(self):              # FFRF^-1F^-1
        """
        Applies a positive braid exchange on the middle anyon pair.

        Args:
            - None 
        Returns:
            - None
        """

        first, second = self.tree.getMiddleId()
        self.tree.FMove()
        self.tree.RMove(first, second)
        self.tree.undoFmove()
        self.movmentList = np.append(self.movmentList, f"23|FRF^(-1)       {self.tree.structure}") 


    def rightSwitchPositive(self):              #R
        """
        Applies a positive braid exchange on the right anyon pair.

        Args:
            - None 
        Returns:
            - None
        """

        first, second = self.tree.getRightId()
        self.tree.RMove(first, second)
        self.movmentList = np.append(self.movmentList, f"34|R              {self.tree.structure}")


    def leftSwitchNegative(self):               # R^-1
        """
        Applies the inverse braid exchange on the left anyon pair.

        Args:
            - None 
        Returns:
            - None
        """

        first, second = self.tree.getLeftId()
        self.tree.undoRMove(first,second)
        self.movmentList = np.append(self.movmentList, f"12|R^(-1)         {self.tree.structure}")
    

    def middleSwitchNegative(self):            #FFR^(-1)F^(-1)F^(-1)
        """
        Applies the inverse braid exchange on the middle anyon pair. 

        Args:
            - None 
        Returns:
            - None
        """

        first, second = self.tree.getMiddleId()
        self.tree.FMove()
        self.tree.undoRMove(first, second)
        self.tree.undoFmove()
        self.movmentList = np.append(self.movmentList, f"23|FR^(-1)F^(-1)  {self.tree.structure}")
        

    def rightSwitchNegative(self):             #R^-1
        """
        Applies the inverse braid exchange on the right anyon pair. 

        Args:
            - None 
        Returns:
            - None
        """

        first, second = self.tree.getRightId()
        self.tree.undoRMove(first, second)
        self.movmentList = np.append(self.movmentList, f"34|R^(-1)         {self.tree.structure}")
#################################################################################

    #return movment list
    def getReportList(self):
        return self.movmentList

    #return information about the logical anyon qubit
    def __repr__(self):
        return f"{self.tree}"

