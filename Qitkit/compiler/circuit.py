import numpy as np
from compiler import qubit
from parser import execution
from compiler.circuitReporter import circuitReporter



"""
class circuit - responsible on the quantum circuit
                count qubits number and locate them to this circuit
                buld vector of operations and add/erase logic gates
                
"""
class circuit:

    #initialize class
    def __init__(self):
        print(circuitReporter.getHeadLine())        
        self.operationVector = np.array([])
        self.qubitsArray = []
        self.qubitsNumber = 0
        self.ex = None
        
    #adding qubit to circuit
    def addQubit(self, qubit):
        self.qubitsNumber += 1
        self.qubitsArray.append(qubit)
    
    def getQubitsNumber(self):
        return self.qubitsNumber

    #adding operation to operation vector
    def addOperation(self, op):
        self.operationVector = np.append(self.operationVector, op)
    
    #return qubit index
    def getIndex(self, qubit):
        return self.qubitsArray.index(qubit)

    #returning string with basic information on the circuit
    def __str__(self):
        y = ""
        for j in self.qubitsArray:
            y += f"{j}\n"

        return f"number of qubits: {self.qubitsNumber}\n{y}"

    
    def getOperationVector(self):
        return self.operationVector
    
    #returning all the operations we added to the circuit
    def getOperationList(self):
        x = ""
        for i in self.operationVector:
            x += f"{i}\n"
        
        return f"operations list: \n{x}"
    
    def details(self):
        
        
        print("\n[Circuit]")
        print("----------------------------------------------")
        
        print(f"Qubits:             : {circuitReporter.getNumberOfQubits(self)}\n")
        print(circuitReporter.getCircuitDraw(self))
        
        

    def execute(self):
        self.ex = execution.execution(self)


    def measure(self, shots=1000, debug=False):
        self.shots = shots

        
        if debug:
            print("[Debug]\n----------------------------------------------")
            circuitReporter.getAnyonMove(self.ex.getMoveList())
            circuitReporter.getFinalMatrix(self.ex)
        
        compilation = "\n[Compilation]\n----------------------------------------------\n"
        compilation += f"Total gates:        : {circuitReporter.getTotalGates(self)}\n"
        compilation += f"Total braids:       : {circuitReporter.getTotalBraids(self.ex)}\n"
        compilation += f"Shots number:       : {shots}\n"
        compilation += f"Fidelity:           : {circuitReporter.getFidelity(self.ex)}"


        resultsReport = "\n[Results]\n----------------------------------------------\n"
        resultsReport += str(circuitReporter.getPercentage(self.ex.measure(self.shots)))
        
        return compilation, resultsReport
                 
