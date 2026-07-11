#==============================================
#        Fibonacci Anyons Quantum DSL 
#==============================================
#creator: Nitay Bahliker
#Date: 23/06/2026
#Rule: Independent researcher
#
#
#
import numpy as np
from qitker.compiler import qubit
from qitker.parser import execution
from qitker.compiler.reporter.reporterObject import reporterObject



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
        print("""==============================================\n        Fibonacci Anyons Quantum DSL     \n==============================================\nVersion: 1.0.0-alpha\nDate: 23/06/2026\nRule: Independent researcher""")        
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
        print(f"Qubits:             : {self.qubitsNumber}\n")
        print(self.getCircuitDraw())
        

    def getCircuitDraw(self): 
        """
        Returning draw of circuit

        Args:
            - self (circuit):

        Returns:
            - (string) draw of circuit
        """

        s = ""
        for i in range(self.qubitsNumber):
            s += (f"q[{i}]:  ")
            
            for j in self.operationVector:
                s += f"--"                  
                if j.getTarget() == i:
                    s += j.getName()
                else:
                    s += "-"


            s += f"--"              
            s += "\n"
        
        return s    

    def execute(self):
        """
        Execute circuit to Anyon backend

        Args:
            - None

        Returns:
            - None
        """
        
        self.ex = execution.execution(self)

    def getAnyonMove(self, anyonMoveList):
        """
        Printing how anyons move 

        Args:
            - anyonMoveList (List):
                list of anyon places

        Returns:
            - None
        """
        anyonMove = ""
        for i in anyonMoveList:
            for vecId, operation in enumerate(i):
                anyonMove += (f"[{vecId:05d}]:    {operation}\n")

        return anyonMove


    def measure(self, shots=1024, debug=False):
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

        measureOutput = self.ex.measure(shots)

        obj = reporterObject(self.getAnyonMove(self.ex.getMoveList()),
                             self.ex.getMatrix(),
                             len(self.operationVector),
                             self.ex.braidsNumber,
                             shots,
                             self.ex.getFidelity(),
                             measureOutput)
        return obj

        """
        print(f"ss:   {self.ex.measure(shots)}")
        if debug: #in debug mode the function print matrix and anyon move 
            print("[Debug]\n----------------------------------------------")
            circuitReporter.printAnyonMove(self.ex.getMoveList())
            circuitReporter.printFinalMatrix(self.ex)
        
        compilation = "\n[Compilation]\n----------------------------------------------\n"
        compilation += circuitReporter.getTotalGates(self)
        compilation += circuitReporter.getTotalBraids(self.ex)
        compilation += f"Shots number:       : {shots}\n"
        compilation += circuitReporter.getFidelity(self.ex)


        resultsReport = "\n[Results]\n----------------------------------------------\n"
        resultsReport += circuitReporter.getPercentage(self.ex.measure(shots))
        
        return compilation, resultsReport
        """         


    
    #returning string with basic information on the circuit
    def __str__(self):
        y = ""
        for j in self.qubitsArray:
            y += f"{j}\n"

        return f"number of qubits: {self.qubitsNumber}\n{y}"