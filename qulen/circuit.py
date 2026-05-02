import numpy as np
import qubit

"""
class circuit - responsible on the quantum circuit
                count qubits number and locate them to this circuit
                buld vector of operations and add/erase logic gates
                
"""
class circuit:

    #initialize class
    def __init__(self):
        self.operationVector = np.array([])
        self.qubitsArray = []
        self.qubitsNumber = 0
    

    #adding qubit to circuit
    def addQubit(self, qubit):
        self.qubitsNumber += 1
        self.qubitsArray.append(qubit)


    #adding operation to operation vector
    def addOperationToVercot(self, strOperation):
        self.operationVector = np.append(self.operationVector, strOperation)

    
    #return qubit index
    def getIndex(self, qubit):
        return self.qubitsArray.index(qubit)

    #returning string with basic information on the circuit
    def __str__(self):
        y = ""
        for j in self.qubitsArray:
            y += f"{j}\n"

        return f"number of qubits: {self.qubitsNumber}\n{y}"

    #returning all the operations we added to the circuit
    def getOperationList(self):
        x = ""
        for i in self.operationVector:
            x += f"{i}\n"
        
        return f"operations list: \n{x}"

