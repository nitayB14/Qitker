import numpy as np
from compiler import qubit
from parser import execution
from compiler.circuitReporter import circuitReporter




class circuit:
    """
    Represents a quantum circuit
    
    Attributes:
        - operationVector : vector
            the vector contain all the operations
        - qubitsArray : array
            all qubits list
        - qubitsNumber : int
            number of qubits
        - ex : execution
            executer to Anyon backend                
    """


    #initialize class
    def __init__(self):
        print(circuitReporter.getHeadLine())        
        self.operationVector = np.array([])
        self.qubitsArray = []
        self.qubitsNumber = 0
        self.ex = None
        
    
    def addQubit(self, qubit):
        """
        Adding qubit to circuit

        Args:
            - qubit (qubit):
                Qubit object we add to circuit

        Returns:
            - None
        """
        
        self.qubitsNumber += 1
        self.qubitsArray.append(qubit)
    

    def getQubitsNumber(self):
        """
        Return how many qubits circuit contain

        Args:
            - None

        Returns:
            - (int) : number of qubits
        """
        
        return self.qubitsNumber


    def addOperation(self, op):
        """
        Adding operation to circuit

        Args:
            - op (opType):
                operation object we add to the vector of operation

        Returns:
            - None
        """
        
        self.operationVector = np.append(self.operationVector, op)
    

    def getIndex(self, qubit):
        """
        Return qubit index

        Args:
            - None

        Returns:
            - (int) : index of qubit
        """
        
        return self.qubitsArray.index(qubit)


    def getOperationVector(self):
        """
        Return vector of operations

        Args:
            - None

        Returns:
            - (vector) : operation vector
        """
        
        return self.operationVector
    

    def details(self):
        """
        Print details on the circuit

        Args:
            - None

        Returns:
            - None
        """

        print("\n[Circuit]")
        print("----------------------------------------------")
        print(f"Qubits:             : {circuitReporter.getNumberOfQubits(self)}\n")
        print(circuitReporter.getCircuitDraw(self))
        
        

    def execute(self):
        """
        Execute circuit to Anyon backend

        Args:
            - None

        Returns:
            - None
        """
        
        self.ex = execution.execution(self)


    def measure(self, shots=1000, debug=False):
        """
        Responsible to measure circuit and create details as strings

        Args:
            - shots (int):
                number of shots to run
            - debug (bool):
                In debug mode the function print extra details on circuit
        Returns:
            - compilation (string):
                The string contains every compilation details on circuit
            - resultReport (string):
                The string contains every measure result of circuit
        """
        
        self.shots = shots

        
        if debug:
            print("[Debug]\n----------------------------------------------")
            circuitReporter.printAnyonMove(self.ex.getMoveList())
            circuitReporter.printFinalMatrix(self.ex)
        
        compilation = "\n[Compilation]\n----------------------------------------------\n"
        compilation += f"Total gates:        : {circuitReporter.getTotalGates(self)}\n"
        compilation += f"Total braids:       : {circuitReporter.getTotalBraids(self.ex)}\n"
        compilation += f"Shots number:       : {shots}\n"
        compilation += f"Fidelity:           : {circuitReporter.getFidelity(self.ex)}"


        resultsReport = "\n[Results]\n----------------------------------------------\n"
        resultsReport += str(circuitReporter.getPercentage(self.ex.measure(self.shots)))
        
        return compilation, resultsReport
                 


    
    #returning string with basic information on the circuit
    def __str__(self):
        y = ""
        for j in self.qubitsArray:
            y += f"{j}\n"

        return f"number of qubits: {self.qubitsNumber}\n{y}"