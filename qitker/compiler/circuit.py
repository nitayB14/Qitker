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
from qitker.ExportCode.exportCode import export_to
from qitker.compiler.operations.operation import operation
from qitker.compiler.operations.opClasses import opType


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
        #print("""==============================================\n        Fibonacci Anyons Quantum DSL     \n==============================================\nVersion: 1.0.0-alpha\nDate: 24/07/2026\nRule: Independent researcher""")        
        self._operationVector = np.array([])
        self._qubitsArray = []
        self._qubitsNumber = 0
        self._ex = None
        
    
    def addQubit(self, qubit):
        """
        Adding qubit to circuit

        Args:
            - qubit (qubit):
                Qubit object we add to circuit

        Returns:
            - None
        """
        
        self._qubitsNumber += 1
        self._qubitsArray.append(qubit)
    

    def getQubitsNumber(self):
        """
        Return how many qubits circuit contain

        Args:
            - None

        Returns:
            - (int) : number of qubits
        """
        
        return self._qubitsNumber


    def getQubitsNumberToMeasure(self):
        """
        Return how many qubits to measure circuit contain

        Args:
            - None

        Returns:
            - (int) : number of qubits to measure
        """
        num = 0
        for i in self._qubitsArray:
            if i.isToMeasure():
                num += 1
        return num


    def getQubitsArray(self):
        """
        Return the array of qubits

        Args:
            - None

        Returns:
            - (array) : qubits array
        """
        return self._qubitsArray


    def addOperation(self, op):
        """
        Adding operation to circuit

        Args:
            - op (opType):
                operation object we add to the vector of operation

        Returns:
            - None
        """
        
        self._operationVector = np.append(self._operationVector, op)
    

    def getIndex(self, qubit):
        """
        Return qubit index

        Args:
            - None

        Returns:
            - (int) : index of qubit
        """
        
        return self._qubitsArray.index(qubit)


    def getOperationVector(self):
        """
        Return vector of operations

        Args:
            - None

        Returns:
            - (vector) : operation vector
        """
        
        return self._operationVector
    

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
        print(f"Qubits:             : {self._qubitsNumber}\n")
        print(self.getCircuitDraw())
        
    def barrier(self):
        operation().apply_barrier(self)



    def getCircuitDraw(self):
        """
        Return a text representation of the circuit.
        """

        if self._qubitsNumber == 0:
            return ""

        labels = []

        for index, currentQubit in enumerate(self._qubitsArray):
            if currentQubit.isToMeasure():
                labels.append(f"q[{index}]: ")
            else:
                labels.append(f"A[{index}]: ")

        labelWidth = max(len(label) for label in labels)

        rows = [
            label.ljust(labelWidth) + "─"
            for label in labels
        ]

        for operation in self._operationVector:
            if operation.getName() == "barrier":
                for qubitIndex in range(self._qubitsNumber):
                    rows[qubitIndex] += "─@─"

                continue

            target = operation.getTarget()

            # A controlled operation is identified by the additional
            # interface supplied by controlledOpType.
            if hasattr(operation, "getControllers"):
                controllers = operation.getControllers()
                targetGate = operation.getName()

                involvedQubits = controllers + [target]

                firstInvolved = min(involvedQubits)
                lastInvolved = max(involvedQubits)

                cellWidth = max(3, len(targetGate) + 2)

                for qubitIndex in range(self._qubitsNumber):
                    if qubitIndex in controllers:
                        symbol = "●"

                    elif qubitIndex == target:
                        symbol = targetGate

                    elif firstInvolved < qubitIndex < lastInvolved:
                        symbol = "│"

                    else:
                        symbol = None

                    if symbol is None:
                        rows[qubitIndex] += "─" * cellWidth
                    else:
                        rows[qubitIndex] += symbol.center(
                            cellWidth,
                            "─"
                        )
                # Regular single-qubit operation.
            else:
                gateName = operation.getName()
                cellWidth = max(3, len(gateName) + 2)

                for qubitIndex in range(self._qubitsNumber):
                    if qubitIndex == target:
                        rows[qubitIndex] += gateName.center(
                            cellWidth,
                            "─"
                        )
                    else:
                        rows[qubitIndex] += "─" * cellWidth
        return "\n".join(rows)





    def execute(self):
        """
        Execute circuit to Anyon backend

        Args:
            - None

        Returns:
            - None
        """
        if len(self._qubitsArray) == 0:
            raise TypeError("cannot execute algorithm without qubits")

        #if len(self._operationVector) == 0:
        #    raise TypeError("cannot execute algorithm without gates")
        
        self._ex = execution.execution(self)
        self._ex.convert()



    def measure(self, shots=1024):
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

        self.execute()
        
        measureOutput = self._ex.measure(shots)
        filteredOutput = self.filtered(measureOutput)
        

        obj = reporterObject(self._ex._fusionSystem.get_operation_history(),
                             len(self._operationVector),
                             self._ex._braidsNumber,
                             shots,
                             self._ex.getFidelity(),
                             filteredOutput,
                             self._ex._fusionSystem.hilbertSpace.get_state_vector(),
                             self._ex.getLeakageProbability())
        
        return obj




    def filtered(self, measureOutput):
        measuredIndexes = [qubit.getIndex() for qubit in self._qubitsArray if qubit.isToMeasure()]
        filteredOutput = {}

        if not measuredIndexes:
            raise ValueError("Cannot measure circuit: no qubits are marked for measurement.")

        for bitstring, count in measureOutput.items():
            filteredBitstring = "".join(
                bitstring[index]
                for index in measuredIndexes
            )

            filteredOutput[filteredBitstring] = (
                filteredOutput.get(filteredBitstring, 0) + count
            )

        return filteredOutput


    def exportCircuit(self, name):
        """
        export circuit to diffrent quantum lenguage

        Args:
            - name:
                name of quantum lenguage

        Returns:
            - circuit exported from the quantum lenguage
        """

        return export_to(name, self)
    
    def getMeasuredLists(self):
        """
        export circuit to diffrent quantum lenguage

        Args:
            - None

        Returns:
            - returning 2 list of measured qubits indexs
        """

        LogicalRegister = []
        quantumRegister = []
        x = 0
        for i in self._qubitsArray:
            if i.isToMeasure():
                quantumRegister.append(i.getIndex())
                LogicalRegister.append(x)
                x += 1


        return quantumRegister, LogicalRegister



    #returning string with basic information on the circuit
    def __str__(self):
        y = ""
        for j in self._qubitsArray:
            y += f"{j}\n"

        return f"number of qubits: {self._qubitsNumber}\n{y}"

    def __repr__(self):
        return self.__str__()
