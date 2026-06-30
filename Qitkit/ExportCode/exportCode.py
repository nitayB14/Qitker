from qiskit import *


class exportCode():
    
    def exportToQiskit(AnyonCircuit):

        qc = QuantumCircuit(AnyonCircuit.getQubitsNumber(), AnyonCircuit.getQubitsNumber())
        vector = AnyonCircuit.getOperationVector()
        
        for op in vector:
            #print("OP:", op, "NAME:", repr(op.getName()), "TARGET:", op.getTarget())
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