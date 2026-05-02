
import qubit
import circuit



def runBasicOperation(myCircuit):
    qubit0 = qubit.qubit(myCircuit, 1)     #create qubit
    qubit1 = qubit.qubit(myCircuit)
    qubit2 = qubit.qubit(myCircuit)
    qubit3 = qubit.qubit(myCircuit, 1)
    qubit4 = qubit.qubit(myCircuit, 0)
    
    qubit2.H()
    qubit2.swap(qubit1)
    qubit2.H()
    
    ~qubit0
    qubit3.flip()
    qubit0.flipIf(qubit1)
    qubit2.flipIf(qubit1, qubit0)
    
    qubit0.flipY()
    qubit4.flipYIf(qubit0)
    qubit1.flipYIf(qubit2, qubit3)
    
    qubit2.flipZ()
    qubit1.flipZIf(qubit3)
    qubit3.flipZIf(qubit1, qubit0)

    qubit0.flipS()
    qubit4.flipSIf(qubit0)
    qubit1.flipSIf(qubit2, qubit3)

    qubit2.flipT()
    qubit0.flipTIf(qubit3)
    qubit4.flipTIf(qubit1, qubit0)
    




def printInformation(myCircuit):
    
    print("show circuit information:\n")
    print(myCircuit)
    print(myCircuit.getOperationList())


def main():

    myCircuit = circuit.circuit()

    runBasicOperation(myCircuit)
    printInformation(myCircuit)




if __name__ == "__main__":
    main()