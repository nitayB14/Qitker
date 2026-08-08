from qitker.anyons.Anyon import Anyon, Charge
import numpy as np


class AnyonicQubit:
    """
    Represents one logical qubit encoded by four Fibonacci anyons.
    """

    def __init__(self, qubit_id: int, anyons: list[Anyon]):

        if not isinstance(qubit_id, int):
            raise TypeError("qubit_id must be an integer.")

        if len(anyons) != 4:
            raise ValueError(
                f"An AnyonicQubit requires exactly 4 anyons, "
                f"received {len(anyons)}."
            )

        if not all(isinstance(anyon, Anyon) for anyon in anyons):
            raise TypeError(
                "All elements in anyons must be Anyon objects."
            )

        self.qubit_id = qubit_id
        self.anyons = anyons
#############################################################################
    def get_left_pair(self):
        return self.anyons[0], self.anyons[1]


    def get_middle_pair(self):
        return self.anyons[1], self.anyons[2]


    def get_right_pair(self):
        return self.anyons[2], self.anyons[3]

    #return information about the logical anyon qubit
    def __repr__(self):
        return (
            f"AnyonicQubit("
            f"qubit_id={self.qubit_id}, "
            f"anyons={self.anyons}"
            f")"
        )




    

"""
    Represents a logical qubit encoded using four Fibonacci anyons.       
    
    def __init__(self):
        self.movmentList = np.array([])
        self.movmentList = np.append(self.movmentList, f"Start             {(self.tree.structure)}") 


    # Applies the specified braid generator (σi or σi⁻¹).       
    def sigma(self, index, state, hilbertOp):
        navigate each sigma operation to the function that apply it
        
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

        state = hilbertOp.sigma(index, state)
        return state
    
    def leftSwitchPositive(self):                 # R
        Applies a positive braid exchange on the left anyon pair
        
        first, second = self.tree.getLeftId()
        self.tree.RMove(first,second)
        self.movmentList = np.append(self.movmentList, f"12|R              {(self.tree.structure)}") 


    def middleSwitchPositive(self):              # FFRF^-1F^-1
        
        Applies a positive braid exchange on the middle anyon pair.
        

        first, second = self.tree.getMiddleId()
        self.tree.FMove()
        self.tree.RMove(first, second)
        self.tree.undoFmove()
        self.movmentList = np.append(self.movmentList, f"23|FRF^(-1)       {self.tree.structure}") 


    def rightSwitchPositive(self):              #R
        
        Applies a positive braid exchange on the right anyon pair.
        

        first, second = self.tree.getRightId()
        self.tree.RMove(first, second)
        self.movmentList = np.append(self.movmentList, f"34|R              {self.tree.structure}")


    def leftSwitchNegative(self):               # R^-1
        
        Applies the inverse braid exchange on the left anyon pair.
        

        first, second = self.tree.getLeftId()
        self.tree.undoRMove(first,second)
        self.movmentList = np.append(self.movmentList, f"12|R^(-1)         {self.tree.structure}")
    

    def middleSwitchNegative(self):            #FFR^(-1)F^(-1)F^(-1)
        Applies the inverse braid exchange on the middle anyon pair. 
        
        first, second = self.tree.getMiddleId()
        self.tree.FMove()
        self.tree.undoRMove(first, second)
        self.tree.undoFmove()
        self.movmentList = np.append(self.movmentList, f"23|FR^(-1)F^(-1)  {self.tree.structure}")
        

    def rightSwitchNegative(self):             #R^-1
        Applies the inverse braid exchange on the right anyon pair. 
        
        first, second = self.tree.getRightId()
        self.tree.undoRMove(first, second)
        self.movmentList = np.append(self.movmentList, f"34|R^(-1)         {self.tree.structure}")
#################################################################################

    #return movment list
    def getReportList(self):
        return self.movmentList
    """




