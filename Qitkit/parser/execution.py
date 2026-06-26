import json
import numpy as np

from anyons import logicalQubit
from parser.sequenceOperation import sequenceOperation
from QuantumMath.HilbertSpace import hilbertSpace

"""
class execute - integration layer between compiler <-> anyons
                
"""

seqOp = sequenceOperation()

class execution:

    #initialize execution class
    def __init__(self, circuit):      
        self.anyonCircuit = []
        self.braidsNumber = 0
        for i in circuit.qubitsArray:
            self.anyonCircuit.append(logicalQubit.logicalQubit())
        
        self.hilbertOp = hilbertSpace()
        self.state = np.array([1,0], dtype=complex)  
        self.convert(circuit)

    #convert quantum operation(gate) to braids  
    def convert(self, circuit):
        op = circuit.getOperationVector()
        for i in op:
            self.applyGate(i)

    #create new operation sequence and add to the logical qubit
    def applyGate(self, opType):
        name = opType.getName()
        
        if name == "H":
            seq = seqOp.H_seq()
            self.applySequence(opType.getTarget(), seq)
        if name == "X":
            seq = seqOp.X_seq()
            self.applySequence(opType.getTarget(), seq)
        if name == "Y":
            seq = seqOp.Y_seq()
            self.applySequence(opType.getTarget(), seq)
        if name == "Z":
            seq = seqOp.Z_seq()
            self.applySequence(opType.getTarget(), seq)
        if name == "S":
            seq = seqOp.S_seq()
            self.applySequence(opType.getTarget(), seq)
        if name == "T":
            seq = seqOp.T_seq()
            self.applySequence(opType.getTarget(), seq)

            
    #apply sequence of sigma(x) on the anyons     
    def applySequence(self, qubitTarget, seq):
        for i in seq:
            self.braidsNumber += 1
            self.state = self.anyonCircuit[qubitTarget].sigma(i, self.state, self.hilbertOp)


    def measure(self, shots):
        return self.hilbertOp.run_measurements(self.state, shots)
    
    def getMatrix(self):
        return self.state

    def __repr__(self):
        output = ""
        for index, qubit in enumerate(self.anyonCircuit):
            output += f"{index}: {qubit}\n"

        return output