from qiskit import *


class exportCode():
    """
    Export circuit to other quantum lenguage

    Responsibilities:
        - Qiskit Export
    """
    def exportToQiskit(AnyonCircuit):
        """
        Running all over the circuit and convert it to qiskit

        Args:
            - AnyonCircuit (circuit):
                contains information about the circuit
            
        Returns:
            - qc (qiskit circuit):
                converted circuit to qiskit
        """

        
        qc = QuantumCircuit(AnyonCircuit.getQubitsNumber(), AnyonCircuit.getQubitsNumber()) #creating qiskit circuit
        vector = AnyonCircuit.getOperationVector()
        
        #loop over operation vector
        for op in vector:
            if(op.getName() == "H"):
                qc.h(op.getTarget())
            elif(op.getName() == "X"):
                qc.x(op.getTarget())
            elif(op.getName() == "Y"):
                qc.y(op.getTarget())
            elif(op.getName() == "Z"):
                qc.z(op.getTarget())
            elif(op.getName() == "S"):
                qc.s(op.getTarget())
            elif(op.getName() == "T"):
                qc.t(op.getTarget())
            else:
                pass

        return qc