#==============================================
#        Fibonacci Anyons Quantum DSL 
#==============================================
#creator: Nitay Bahliker
#Date: 23/06/2026
#Rule: Independent researcher
#
#
#
from qitker.compiler.operations import operation
from qitker.compiler import circuit
from qitker.compiler import validation

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
            self._index = self._quantumCircuit.getIndex(self)

            if initialize == 0:
                pass #already initialize to 0s
            elif initialize == 1:
                self.flip() #apply not gate to initialize as 1
            else:
                print("number too big throw exception")

        else:
            print("throw error")
    
    def getIndex(self):
        return self._index

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
    """ Call operation class to add T gate to circuit """
    def rotateX(self, angle):
        op.apply_rotate_X(self, angle=angle, circuit=self._quantumCircuit)

    def RX(self, angle):
        op.apply_rotate_X(self, angle=angle, circuit=self._quantumCircuit)

    ################################################################
    def rotateY(self, angle):
        op.apply_rotate_Y(self, angle=angle, circuit=self._quantumCircuit)

    def RY(self, angle):
        op.apply_rotate_Y(self, angle=angle, circuit=self._quantumCircuit)

    ################################################################
    def rotateZ(self, angle):
        op.apply_rotate_Z(self, angle=angle, circuit=self._quantumCircuit)

    def RZ(self, angle):
        op.apply_rotate_Z(self, angle=angle, circuit=self._quantumCircuit)

    ################################################################




    """ Call operation class to add controlled gate to circuit """



    def _checkItems(self, control, where):
        from qitker.compiler.qRegister import qRegister

        if isinstance(control, qRegister):
            control = control[::]
        if isinstance(where, qRegister):
            where = where[::]

        return control, where




    def flipIf(self, control, where=None):
        control, where = self._checkItems(control, where)
        self._controlledGate(control, "X", where)

    def flipPhaseIf(self, control, where=None):
        control, where = self._checkItems(control, where)
        self._controlledGate(control, "Y", where)

    def phaseIf(self, control, where=None):
        control, where = self._checkItems(control, where)
        self._controlledGate(control, "Z", where)

    def halfPhaseIf(self, control, where=None):
        control, where = self._checkItems(control, where)
        self._controlledGate(control, "S", where)

    def quarterPhaseIf(self, control, where=None):
        control, where = self._checkItems(control, where)
        self._controlledGate(control, "T", where)
    
    ###########################################################################
    def _controlledGate(self, control, oType, where=None):
        comparison_requested = isinstance(where, (qubit, list))

        controls, condition = validation.validate_controlled_gate(
            self,
            control,
            where,
            allow_comparison=True,
        )

        if comparison_requested:
            references = condition

            same_operands = all(
                current_control is reference
                for current_control, reference in zip(
                    controls,
                    references,
                )
            )

            if same_operands:
                if(oType == "X"):
                    self.flip()
                elif(oType == "Y"):
                    self.flipPhase()
                elif(oType == "Z"):
                    self.phase()
                elif(oType == "S"):
                    self.halfPhase()
                elif(oType == "T"):
                    self.quarterPhase()
                
                return

            comparison_pairs = list(zip(controls, references))

            # Compute the bitwise differences into the reference side.
            for current_control, reference in comparison_pairs:
                reference.cx(current_control)

            # All computed differences are zero exactly when both operands
            # represent the same computational-basis value.
            if(oType == "X"):
                self._controlledGate(references, "X", where=0)
            elif(oType == "Y"):
                    self._controlledGate(references, "Y", where=0)
            elif(oType == "Z"):
                    self._controlledGate(references, "Z", where=0)
            elif(oType == "S"):
                    self._controlledGate(references, "S", where=0)
            elif(oType == "T"):
                    self._controlledGate(references, "T", where=0)
                   

            
            # Restore every reference qubit to its original state.
            for current_control, reference in reversed(comparison_pairs):
                reference.cx(current_control)

            return

        pattern = condition

        active_controls = []
        zero_controls = []

        for current_control, state in zip(controls, pattern):
            if state == "x":
                continue

            active_controls.append(current_control)

            if state == "0":
                zero_controls.append(current_control)

        for current_control in zero_controls:
            current_control.flip()

        if active_controls:
            if(oType == "X"):
                op.apply_Controlled_X(self,active_controls,self._quantumCircuit,)
            elif(oType == "Y"):
                op.apply_Controlled_Y(self,active_controls,self._quantumCircuit,)
            elif(oType == "Z"):
                op.apply_Controlled_Z(self,active_controls,self._quantumCircuit,)
            elif(oType == "S"):
                op.apply_Controlled_S(self,active_controls,self._quantumCircuit,)
            elif(oType == "T"):
                op.apply_Controlled_T(self,active_controls,self._quantumCircuit,)
                
        else:
            if(oType == "X"):
                self.flip()
            elif(oType == "Y"):
                    self.flipPhase()
            elif(oType == "Z"):
                    self.phase()
            elif(oType == "S"):
                    self.halfPhase()
            elif(oType == "T"):
                    self.quarterPhase()


        for current_control in reversed(zero_controls):
            current_control.flip()


    #################################################################
    def cx(self, control):
        self.flipIf(control)
    def cy(self, control):
        self.flipPhaseIf(control)
    def cz(self, control):
        self.phaseIf(control)
    def cs(self, control):
        self.halfPhaseIf(control)
    def ct(self, control):
        self.quarterPhaseIf(control)

    def CX(self, control):
        self.flipIf(control)
    def CY(self, control):
        self.flipPhaseIf(control)
    def CZ(self, control):
        self.phaseIf(control)
    def CS(self, control):
        self.halfPhaseIf(control)
    def CT(self, control):
        self.quarterPhaseIf(control)
    #################################################################
    """ Create swap by adding 3 cx """
    
    def swap(self, control):
        if not isinstance(control, qubit):
            raise TypeError("control must be a qubit")

        self.flipIf(control)
        control.flipIf(self)
        self.flipIf(control)

    #################################################################
    
    def __str__(self):
        return f"index: {self._quantumCircuit.getIndex(self)}, is to measure?: {self._measured}"


    def __repr__(self):
        return self.__str__()





