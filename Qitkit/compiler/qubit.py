
from compiler import operation
from compiler import circuit

op = operation.operation()
"""
class qubit - responsible on the qubit itself, calls to operation and manage the qubit
              locate the qubit to a circuit, initialize with |0> or |1> or with H gate

"""
class qubit:

    def __init__(self, quantumCircuit, initialize = None):

        if(type(quantumCircuit) == circuit.circuit):
            self.quantumCircuit = quantumCircuit
            self.quantumCircuit.addQubit(self)
            self.initialize = initialize
            if initialize == None: #if user have not choose to initialize we apply H gate
                self.H_gate()
            elif initialize == 0:
                pass #already initialize to 0s
            elif initialize == 1:
                self.X_gate() #apply not gate to initialize as 1
            else:
                print("number too big throw exception")

        else:
            print("throw error")
    #####################################################################################

    def H_gate(self):
        op.apply_H(self, self.quantumCircuit)

    def X_gate(self):
        op.apply_X(self, self.quantumCircuit)

    def Y_gate(self):
        op.apply_Y(self, self.quantumCircuit)

    def Z_gate(self):
        op.apply_Z(self, self.quantumCircuit)
    
    def S_gate(self):
        op.apply_S(self, self.quantumCircuit)

    def T_gate(self):
        op.apply_T(self, self.quantumCircuit)


    def __str__(self):
        return f"index: {self.quantumCircuit.getIndex(self)}, is initialize?: {self.initialize}"
    