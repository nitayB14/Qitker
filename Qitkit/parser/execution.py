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
        
        self.U = np.eye(2, dtype=complex)
        self.matrix = None
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
        self.fidelityMatrix(op)
        for i in op:
            self.applyGate(i)
    
    def fidelityMatrix(self, opType):
        for num, op in enumerate(opType):
            if num == 0:
                self.matrix = self.hilbertOp.getMatrix(op.getName())
            else:
                self.matrix = self.matrix @ self.hilbertOp.getMatrix(op.getName())
    
            

    #create new operation sequence and add to the logical qubit
    def applyGate(self, opType):
        name = opType.getName()
        target = opType.getTarget()

        seq = seqOp.getSeq(name)
        self.applySequence(target, seq)
        


            
    #apply sequence of sigma(x) on the anyons     
    def applySequence(self, qubitTarget, seq):
        for i in seq:
            self.braidsNumber += 1
            self.state = self.anyonCircuit[qubitTarget].sigma(i, self.state, self.hilbertOp)
            self.U = self.anyonCircuit[qubitTarget].sigma(i, self.U, self.hilbertOp)


            
    def getFidelity(self):
        return f"{self.hilbertOp.gate_fidelity(self.matrix, self.U)*100:.4f}%"

    def measure(self, shots):
        return self.hilbertOp.run_measurements(self.state, shots)
    
    def getMatrix(self):
        return self.U
   
    def getMoveList(self):
        myList = []
        for i in self.anyonCircuit:
            myList.append(i.getReportList())
        return myList
        
            

    def __repr__(self):
        output = ""
        for index, qubit in enumerate(self.anyonCircuit):
            output += f"{index}: {qubit}\n"

        return output