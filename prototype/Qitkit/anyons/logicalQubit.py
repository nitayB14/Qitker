from anyons.Anyon import Anyon, Charge
from anyons.FusionTree import FusionTree
import numpy as np




anyons_default = [
        Anyon(1, Charge.VACUUM),
        Anyon(2),
        Anyon(3),
        Anyon(4)
        ]

# Represents a logical qubit encoded using four Fibonacci anyons.
class logicalQubit():
    # Initializes a logical qubit in the vacuum fusion sector.    
    def __init__(self):
        self.reportList = np.array([])
        self.tree = FusionTree(
            anyons=anyons_default,
            total_charge=Charge.VACUUM
        )

        self.reportList = np.append(self.reportList, f"Start             {(self.tree.structure)}") 

    # Applies the specified braid generator (σi or σi⁻¹).       
    def sigma(self, index, state, hilbertOp):
        state = hilbertOp.sigma(index, state)
        if(index > 0):
            if index % 4 == 1:
                self.leftSwitchPositive(index)
            elif index % 4 == 2:
                self.middleSwitchPositive(index)
            elif index % 4 == 3:
                self.rightSwitchPositive(index)
        elif(index < 0):
            if index % -4 == -1:
                self.leftSwitchNegative(index)
            elif index % -4 == -2:
                self.middleSwitchNegative(index)
            elif index % -4 == -3:
                self.rightSwitchNegative(index)
        else:
            raise ValueError("For 4 anyons, sigma cannot be 0 ")

        return state
    # Executes a sequence of braid operations.
    def operationList(self, operations):
        for item in operations:
            self.sigma(item)
            
#############################################################################
    # Applies a positive braid exchange on the left anyon pair.   
    def leftSwitchPositive(self, index):                 # R
        first, second = self.tree.getLeftId()
        self.tree.RMove(first,second)
        self.reportList = np.append(self.reportList, f"12|R              {(self.tree.structure)}") 

    # Applies a positive braid exchange on the middle anyon pair.
    def middleSwitchPositive(self, index):              # FFRF^-1F^-1
        first, second = self.tree.getMiddleId()
        self.tree.FMove()
        self.tree.RMove(first, second)
        self.tree.undoFmove()
        self.reportList = np.append(self.reportList, f"23|FRF^(-1)       {self.tree.structure}") 

    # Applies a positive braid exchange on the right anyon pair.
    def rightSwitchPositive(self, index):              #R
        first, second = self.tree.getRightId()
        self.tree.RMove(first, second)
        self.reportList = np.append(self.reportList, f"34|R              {self.tree.structure}")

    # Applies the inverse braid exchange on the left anyon pair.
    def leftSwitchNegative(self, index):               # R^-1
        first, second = self.tree.getLeftId()
        self.tree.undoRMove(first,second)
        self.reportList = np.append(self.reportList, f"12|R^(-1)         {self.tree.structure}")
    
    # Applies the inverse braid exchange on the middle anyon pair.    
    def middleSwitchNegative(self, index):            #FFR^(-1)F^(-1)F^(-1)
        first, second = self.tree.getMiddleId()
        self.tree.FMove()
        self.tree.undoRMove(first, second)
        self.tree.undoFmove()
        self.reportList = np.append(self.reportList, f"23|FR^(-1)F^(-1)  {self.tree.structure}")
        
    # Applies the inverse braid exchange on the right anyon pair.    
    def rightSwitchNegative(self, index):             #R^-1
        first, second = self.tree.getRightId()
        self.tree.undoRMove(first, second)
        self.reportList = np.append(self.reportList, f"34|R^(-1)         {self.tree.structure}")
#################################################################################
    def getReportList(self):
        return self.reportList

    def __repr__(self):
        return f"{self.tree}"

