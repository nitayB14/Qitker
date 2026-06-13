from anyon import Anyon, Charge
from FusionTree import FusionTree
from logicalQubit import logicalQubit


def main():


    qubit1 = logicalQubit()
    print("starting qubit")
    print(qubit1)
    qubit1.sigma(1)
    print(qubit1)
    qubit1.sigma(3)
    print(qubit1)
    qubit1.sigma(-3)
    print(qubit1)
    qubit1.sigma(2)
    print(qubit1)
    qubit1.sigma(-1)
    print(qubit1)
    qubit1.sigma(-2)
    print(qubit1)
    print("###########################################")
    qubit2 = logicalQubit()
    print("starting qubit")
    print(qubit2)
    qubit2.operationList([1,3,3,2,-1,-2])
    print(qubit2)

    





if __name__ == "__main__":
    main()