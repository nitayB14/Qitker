#==============================================
#        Fibonacci Anyons Quantum DSL 
#==============================================
#creator: Nitay Bahliker
#Date: 23/06/2026
#Rule: Independent researcher
#
#
#
from ctypes import Structure

import numpy as np
from qitker.compiler import qubit
from qitker.parser import execution
from qitker.compiler.reporter.reporterObject import reporterObject
from qitker.ExportCode.exportCode import export_to
from qitker.compiler.operations.operation import operation
from qitker.compiler.operations.opClasses import opType
import time


class circuit:
    """Represent a quantum circuit and its recorded operations.

    Attributes:
        _operationVector (np.ndarray): Recorded gates and barriers.
        _qubitsArray (list[qubit]): Qubits in circuit order.
        _qubitsNumber (int): Number of qubits in the circuit.
        _ex (execution.execution | None): Most recent backend execution.
        _lastMeasurement (reporterObject | None): Most recent measurement report.
        _selectedOutcome (str | None): Selected measurement bitstring.
        _selectedValues (dict[qubit, int]): Selected bit for each measured qubit.
    """


    def __init__(self):
        """Initialize an empty circuit with no qubits, operations, or measurement result."""
        
        self._operationVector = np.array([])
        self._qubitsArray = []
        self._qubitsNumber = 0
        self._ex = None
        
        self._lastMeasurement = None
        self._selectedOutcome = None
        self._selectedValues = {}
    

    def addQubit(self, qubit):
        """Add a qubit to the circuit.

        Appends the qubit to the circuit's qubit list, increments the qubit
        count, and clears any previous measurement result and selection.

        Args:
            qubit (qubit): The qubit to add.
        """
        
        self._lastMeasurement = None
        self._selectedOutcome = None
        self._selectedValues = {}

        self._qubitsNumber += 1
        self._qubitsArray.append(qubit)
    

    def getQubitsNumber(self):
        """
        Return how many qubits circuit contain

        Returns:
            int: The number of qubits currently in the circuit.
        """
        
        return self._qubitsNumber


    def getQubitsNumberToMeasure(self):
        """
        Return how many qubits to measure circuit contain

        Returns:
            int: number of qubits to measure
        """

        num = 0
        for i in self._qubitsArray:
            if i.isToMeasure():
                num += 1
        return num


    def getQubitsArray(self):
        """
        Return the array of qubits

        Returns:
            array: qubits array
        """
        
        return self._qubitsArray


    def addOperation(self, op):
        """Add an operation to the circuit.

        Appending an operation clears the previous measurement result and any
        selected outcome, because they no longer describe the current circuit.

        Args:
            op (opType): The operation to append.
        """

        self._lastMeasurement = None
        self._selectedOutcome = None
        self._selectedValues = {}

        self._operationVector = np.append(self._operationVector, op)
    

    def getIndex(self, qubit):
        """Return the qubit's index in the circuit.

        Args:
            qubit (qubit): The qubit to locate.

        Returns:
            int: The qubit's zero-based index.

        Raises:
            ValueError: If the qubit is not in the circuit.
        """
        
        return self._qubitsArray.index(qubit)


    def getOperationVector(self):
        """
        Return vector of operations

        Returns:
            vector: operation vector
        """
        
        return self._operationVector
    

    def details(self):
        """Print how many qubits an draw the circuit"""

        print("\n[Circuit]")
        print("----------------------------------------------")
        print(f"Qubits:             : {self._qubitsNumber}\n")
        self.draw() 
        

    def barrier(self):
        """adding barrier to circuit"""
        operation().apply_barrier(self)



    def draw(self):
        """Print a text diagram of the circuit.

        Each row represents a qubit: ``q`` marks a qubit selected for
        measurement, and ``A`` marks one that is not. The diagram shows gate
        names and barriers, but does not show rotation angles.
        """

        if self._qubitsNumber == 0:
            print("")
            return


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
        print("\n".join(rows))
        return





    def execute(self):
        """Execute the circuit's operations on a new anyonic backend.

        Stores the new execution object on the circuit. This method does not
        sample measurement outcomes. The returned structure is captured
        before the recorded operations are applied.

        Returns:
            tuple: A nested tuple of anyon IDs describing the initial fusion tree.

        Raises:
            TypeError: If the circuit has no qubits.
            NotImplementedError: If a gate cannot be executed by this backend.
        """

        if len(self._qubitsArray) == 0:
            raise TypeError("cannot execute algorithm without qubits")

        self._ex = execution.execution(self)
        anyonStructure = self._ex._fusionSystem.tree.to_ids()
        self._ex.convert()
        return anyonStructure


    def getSelectedValue(self, currentQubit):
        """Return a qubit's bit in the selected measurement outcome.

        Args:
            currentQubit (qubit): The qubit whose selected value is requested.

        Returns:
            int: The selected bit, either 0 or 1.

        Raises:
            RuntimeError: If the circuit has not been measured or no outcome
                has been selected.
            ValueError: If the qubit is not marked for measurement.
        """

        if self._lastMeasurement is None:
            raise RuntimeError("The circuit has not been measured yet.")

        if self._selectedOutcome is None:
            raise RuntimeError(
                "No measurement outcome has been selected."
            )

        if not currentQubit.isToMeasure():
            raise ValueError(
                "This qubit was not included in the measurement."
            )

        return self._selectedValues[currentQubit]


    def _selectMeasurementOutcome(self, result, outcome):
        """Set the selected outcome for the circuit's latest measurement.

        Maps the bits in `outcome` to the qubits marked for measurement,
        in their circuit order.

        Args:
            result (reporterObject): The measurement report selecting the outcome.
            outcome (str): A bitstring with one bit per measured qubit.

        Raises:
            RuntimeError: If `result` is not the latest measurement report
                or the bitstring length does not match the measured qubits.
        """

        if result is not self._lastMeasurement:
            raise RuntimeError(
                "This measurement result is no longer the current result."
            )

        measuredQubits = [
            currentQubit
            for currentQubit in self._qubitsArray
            if currentQubit.isToMeasure()
        ]

        if len(outcome) != len(measuredQubits):
            raise RuntimeError(
                "Measurement outcome does not match the measured qubits."
            )

        self._selectedOutcome = outcome
        self._selectedValues = {
            currentQubit: int(bit)
            for currentQubit, bit in zip(measuredQubits, outcome)
        }


    def measure(self, shots=1024):
        """Execute the circuit and sample its measurement outcomes.

        Creates a fresh backend execution, samples the resulting state, and
        keeps counts only for qubits marked for measurement. Any leakage
        outcome is retained separately. A previous measurement result and
        selected outcome are cleared.

        Args:
            shots (int): Number of samples to take. Defaults to 1024.

        Returns:
            reporterObject: A report containing the outcome counts and
            execution details, including fidelity and leakage probability.

        Raises:
            TypeError: If the circuit has no qubits or `shots` is not an integer.
            ValueError: If `shots` is less than 1 or no qubits are marked
                for measurement.
            NotImplementedError: If a recorded gate cannot be executed by
                the anyonic backend.
        """

        self._lastMeasurement = None
        self._selectedOutcome = None
        self._selectedValues = {}
        

        start = time.perf_counter()
        anyonStructure = self.execute()
        measureOutput = self._ex.measure(shots)
        end = time.perf_counter()

        
        filteredOutput = self.filtered(measureOutput)
        

        obj = reporterObject(anyonStructure,
                             self._ex._fusionSystem.get_operation_history(),
                             sum(1 for op in self._operationVector if op.getName() != "barrier"),
                             self._ex._braidsNumber,
                             shots,
                             self._ex.getFidelity(),
                             filteredOutput,
                             self._ex._fusionSystem.hilbertSpace.get_state_vector(),
                             self._ex.getLeakageProbability(),
                             end-start,
                             self,)
        
        self._lastMeasurement = obj

        return obj




    def filtered(self, measureOutput):
        """Keep measurement counts for qubits marked for measurement.

        Removes bits belonging to unmeasured qubits and combines counts
        that become the same bitstring. The `LEAKAGE` count is preserved
        as a separate entry.

        Args:
            measureOutput (dict[str, int]): Counts for full-circuit
                bitstrings, with an optional `LEAKAGE` entry.

        Returns:
            dict[str, int]: Counts keyed by the measured qubits' bitstrings,
            in circuit order, with `LEAKAGE` if present.

        Raises:
            ValueError: If no qubits are marked for measurement.
        """
        
        measuredIndexes = [qubit.getIndex() for qubit in self._qubitsArray if qubit.isToMeasure()]
        filteredOutput = {}

        if not measuredIndexes:
            raise ValueError("Cannot measure circuit: no qubits are marked for measurement.")

        for bitstring, count in measureOutput.items():
            if bitstring == "LEAKAGE":
                filteredOutput["LEAKAGE"] = (
                    filteredOutput.get("LEAKAGE", 0) + count
                )
                continue

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
        Supported lenguages: - Qiskit

        Args:
            name (string): name of quantum lenguage

        Returns:
            circuit exported from the quantum lenguage
        """

        return export_to(name, self)
    

    def getMeasuredLists(self):
        """Return the qubit and classical-bit indexes used for measurement.

        The first list contains the circuit indexes of qubits marked for
        measurement. The second contains their corresponding consecutive
        classical-bit indexes, starting at 0. Both lists follow circuit order.

        Returns:
            tuple[list[int], list[int]]: Qubit indexes and their corresponding
            classical-bit indexes.
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
        """Return the qubit count followed by each qubit's string representation."""
        
        y = ""
        for j in self._qubitsArray:
            y += f"{j}\n"

        return f"number of qubits: {self._qubitsNumber}\n{y}"

    def __repr__(self):
        """Return the same circuit description as `__str__`."""
        return self.__str__()
