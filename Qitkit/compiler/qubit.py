
from compiler import operation
from compiler import circuit

op = operation.operation() #class operation - to add operations to qubit


class qubit:
    """
    Represents single qubit
    
    Attributes:
        - quantumCircuit: circuit
            The circuit of the qubit
        - initialize: int
            Control qubit initialize (can be 0 or 1 and if not apply H instantly)
    """


    #initialize class
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
    


    """
    Apply gate on qubit

    Args:
        - None

    Returns:
        - None
    """
    ##############################################
    """ Call operation class to add H gate to circuit """
    def H(self):
        op.apply_H(self, self.quantumCircuit)
    
    def h(self):
        self.H()
    ##############################################
    """ Call operation class to add X gate to circuit """
    def X(self):
        op.apply_X(self, self.quantumCircuit)

    def x(self):
        self.X()

    def flip(self):
        self.X()
    ##############################################
    """ Call operation class to add Y gate to circuit """
    def Y(self):
        op.apply_Y(self, self.quantumCircuit)

    def y(self):
        self.Y()
    ##############################################
    """ Call operation class to add Z gate to circuit """
    def Z(self):
        op.apply_Z(self, self.quantumCircuit)
    
    def z(self):
        self.Z()

    def phase(self):
        self.Z()
    ##############################################
    """ Call operation class to add S gate to circuit """
    def S(self):
        op.apply_S(self, self.quantumCircuit)

    def s(self):
        self.S()
    ##############################################
    """ Call operation class to add T gate to circuit """
    def T(self):
        op.apply_T(self, self.quantumCircuit)

    def t(self):
        self.T()
    ##############################################

    #returning string with basic information on the qubit
    def __str__(self):
        return f"index: {self.quantumCircuit.getIndex(self)}, is initialize?: {self.initialize}"
    