#==============================================
#        Fibonacci Anyons Quantum DSL 
#==============================================
#creator: Nitay Bahliker
#Date: 23/06/2026
#Rule: Independent researcher
#
#
#
from qitker.compiler import operation
from qitker.compiler import circuit

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
    def __init__(self, quantumCircuit, initialize=0, measured=True):

        if(type(quantumCircuit) == circuit.circuit):
            self._quantumCircuit = quantumCircuit
            self._quantumCircuit.addQubit(self)
            self._initialize = initialize
            self._measured = measured

            if initialize == 0:
                pass #already initialize to 0s
            elif initialize == 1:
                self.X_gate() #apply not gate to initialize as 1
            else:
                print("number too big throw exception")

        else:
            print("throw error")
    
    def getIndex(self):
        return self._quantumCircuit.getIndex(self)
    def isToMeasure(self):
        return self._measured


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
        op.apply_H(self, self._quantumCircuit)
    
    def h(self):
        self.H()

    def superPosition(self):
        self.H()
    ##############################################
    """ Call operation class to add X gate to circuit """
    def X(self):
        op.apply_X(self, self._quantumCircuit)

    def x(self):
        self.X()

    def flip(self):
        self.X()
    ##############################################
    """ Call operation class to add Y gate to circuit """
    def Y(self):
        op.apply_Y(self, self._quantumCircuit)

    def y(self):
        self.Y()

    def flipPhase(self):
        self.Y()
    ##############################################
    """ Call operation class to add Z gate to circuit """
    def Z(self):
        op.apply_Z(self, self._quantumCircuit)
    
    def z(self):
        self.Z()

    def phase(self):
        self.Z()
    ##############################################
    """ Call operation class to add S gate to circuit """
    def S(self):
        op.apply_S(self, self._quantumCircuit)

    def s(self):
        self.S()

    def halfPhase(self):
        self.S()
    ##############################################
    """ Call operation class to add T gate to circuit """
    def T(self):
        op.apply_T(self, self._quantumCircuit)

    def t(self):
        self.T()

    def quarterPhase(self):
        self.T()
    ##############################################

    #returning string with basic information on the qubit
    def __str__(self):
        return f"index: {self._quantumCircuit.getIndex(self)}, is to measure?: {self._measured}"
    