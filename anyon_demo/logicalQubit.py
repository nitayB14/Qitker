from anyon import Anyon, Charge
from FusionTree import FusionTree


class logicalQubit():

    def __init__(self):
    
        anyons = [
        Anyon(1, Charge.VACUUM),
        Anyon(2),
        Anyon(3),
        Anyon(4)
        ]

        self.tree = FusionTree(
            anyons=anyons,
            total_charge=Charge.VACUUM
        )
        
    def sigma(self, index):
        if(index > 0):
            if index % 4 == 1:
                first, second = self.tree.getLeftId()
                self.tree.RMove(first,second)
                print(f"sigma {index}: R")
            elif index % 4 == 2:
                first, second = self.tree.getMiddleId()
                self.tree.FMove()
                self.tree.RMove(first, second)
                self.tree.undoFmove()
                print(f"sigma {index}: FFRF^(-1)F^(-1)")
            elif index % 4 == 3:
                first, second = self.tree.getRightId()
                self.tree.RMove(first, second)
                print(f"sigma {index}: R")
        elif(index < 0):
            if index % -4 == -1:
                first, second = self.tree.getLeftId()
                self.tree.RMove(first,second)
                print(f"sigma {index}: R^(-1)")
            elif index % -4 == -2:
                first, second = self.tree.getMiddleId()
                self.tree.FMove()
                self.tree.RMove(first, second)
                self.tree.undoFmove()
                print(f"sigma {index}: FFR^(-1)F^(-1)F^(-1)")
            elif index % -4 == -3:
                first, second = self.tree.getRightId()
                self.tree.RMove(first, second)
                print(f"sigma {index}: R^(-1)")
        else:
            raise ValueError("For 4 anyons, sigma cannot be 0 ")



    def operationList(self, operations):

        for item in operations:
            self.sigma(item)


    def __repr__(self):
        return f"{self.tree}"

