#==============================================
#        Fibonacci Anyons Quantum DSL 
#==============================================
#creator: Nitay Bahliker
#Date: 12/08/2026
#Rule: Independent researcher
#
#
#
from qitker.compiler.operations import operation
from qitker.compiler import circuit
from qitker.compiler.qubit import qubit, EqualityCondition

op = operation.operation() #class operation - to add operations to qubit


class qRegister:
    """
    Represents list of qubits
    
    Attributes:
        - quantumCircuit: circuit
            The circuit of the qubit
        - initialize: int/str
            Control qubit initialize (can be num or string)
        - size: int
           Number of qubits 
        - measured: bool
            is the register to measure
    """

    #initialize class
    def __init__(self, quantumCircuit, size=None, initialize=0, measured=True):
        """Create a register, optionally inferring its size from initialize."""

        # Validate the circuit.
        if not isinstance(quantumCircuit, circuit.circuit):
            raise TypeError("quantumCircuit must be a circuit")

        # Normalize the initial value and its minimum required size.
        if isinstance(initialize, bool):
            raise TypeError("initialize must be an int or a binary string")

        if isinstance(initialize, int):
            if initialize < 0:
                raise ValueError("initialize cannot be negative")

            initialize_value = initialize
            minimum_size = max(1, initialize.bit_length())

        elif isinstance(initialize, str):
            if not initialize or any(bit not in "01" for bit in initialize):
                raise ValueError("initialize must be a non-empty binary string")

            initialize_value = int(initialize, 2)
            minimum_size = len(initialize)

        else:
            raise TypeError("initialize must be an int or a binary string")

        # Use the requested size, or infer it from initialize.
        if size is None:
            register_size = minimum_size
        else:
            if isinstance(size, bool) or not isinstance(size, int):
                raise TypeError("size must be an int")

            if size <= 0:
                raise ValueError("size must be greater than zero")

            if size < minimum_size:
                raise ValueError("initialize does not fit inside the register")

            register_size = size

        # Pad on the left like an ordinary binary number.
        bitstring = format(initialize_value, f"0{register_size}b")

        

        self._size = register_size
        self._initialize = bitstring
        self._quantumCircuit = quantumCircuit

        # Index zero represents the rightmost, least-significant bit.
        self._reg = [
            qubit(
                quantumCircuit,
                initialize=int(bit),
                measured=measured,
            )
            for bit in bitstring
        ]

        #self._reg.reverse()

    

    def getIndex(self):
        return [i.getIndex() for i in self._reg]

    def getBitstring(self):
        return "".join(
            str(regQubit.getValue())
            for regQubit in self._reg
        )

    def getValue(self):
        return int(self.getBitstring(), 2)


    def isToMeasure(self):
        return [i.isToMeasure() for i in self._reg]

    def getQubit(self, index):
        return self._reg[index]
    ###########################################################################
    """
    Apply gate on qubit

    Args:
        - None

    Returns:
        - None
    """
    ##############################################
    """ Call every qubit in the register and apply H gate """
    def H(self):
        for regQubit in self._reg:
            regQubit.H()
    
    def h(self):
        self.H()

    def superPosition(self):
        self.H()

    def mix(self):
        self.H()
    ##############################################
    """ Call every qubit in the register and apply X gate """
    def X(self):
        for regQubit in self._reg:
            regQubit.X()

    def x(self):
        self.X()

    def flip(self):
        self.X()
##############################################
    """ Call every qubit in the register and apply Y gate """
    def Y(self):
        for regQubit in self._reg:
            regQubit.Y()

    def y(self):
        self.Y()

    def flipPhase(self):
        self.Y()
    ##############################################
    """ Call every qubit in the register and apply Z gate """
    def Z(self):
        for regQubit in self._reg:
            regQubit.Z()
    
    def z(self):
        self.Z()

    def phase(self):
        self.Z()
    ##############################################
    """ Call every qubit in the register and apply S gate """
    def S(self):
        for regQubit in self._reg:
            regQubit.S()

    def s(self):
        self.S()

    def halfPhase(self):
        self.S()
    ##############################################
    """ Call every qubit in the register and apply T gate """
    def T(self):
        for regQubit in self._reg:
            regQubit.T()

    def t(self):
        self.T()

    def quarterPhase(self):
        self.T()
    ################################################################
    def shiftLeft(self, amount=1):
        n = len(self._reg)

        if n <= 1:
            return

        amount %= n

        if amount == 0:
            return

        # We only use this list to calculate the required SWAPs.
        # self._reg itself is NOT reordered here.
        current = list(range(n))
        target = current[amount:] + current[:amount]

        for i in range(n):
            if current[i] == target[i]:
                continue

            j = current.index(target[i], i + 1)

            # Apply the actual quantum SWAP
            self._reg[i].swap(self._reg[j])

            # Keep our classical bookkeeping synchronized
            current[i], current[j] = current[j], current[i]

    def shiftRight(self, amount=1):
        self.shiftLeft(-amount)
    ################################################################

    def flipIf(self,control, where=None, ancilla=None):
        self._controlledGate(control, "X", where, ancilla)

    def flipPhaseIf(self,control, where=None, ancilla=None):
        self._controlledGate(control, "Y", where, ancilla)
    
    def phaseIf(self,control, where=None, ancilla=None):
        self._controlledGate(control, "Z", where, ancilla)
    
    def halfPhaseIf(self,control, where=None, ancilla=None):
        self._controlledGate(control, "S", where, ancilla)
    
    def quarterPhaseIf(self,control, where=None, ancilla=None):
        self._controlledGate(control, "T", where, ancilla)

    ################################################################
    

    def _controlledGate(self, control, opType, where=None, ancilla=None):
        if isinstance(ancilla, qubit):
            # Compute
            if any(ancilla is target for target in self._reg):
                raise ValueError(
                    "ancilla cannot also be a target qubit"
                )
            ancilla.flipIf(control, where)

            # Use
            for regQubit in self._reg:
                if(opType == "X"):
                    regQubit.flipIf(ancilla)
                if(opType == "Y"):
                    regQubit.flipPhaseIf(ancilla)
                if(opType == "Z"):
                    regQubit.phaseIf(ancilla)
                if(opType == "S"):
                    regQubit.halfPhaseIf(ancilla)
                if(opType == "T"):
                    regQubit.quarterPhaseIf(ancilla)

            # Uncompute
            ancilla.flipIf(control, where)

        elif ancilla is None:
            for regQubit in self._reg:
                if(opType == "X"):
                    regQubit.flipIf(control, where)
                if(opType == "Y"):
                    regQubit.flipPhaseIf(control, where)
                if(opType == "Z"):
                    regQubit.phaseIf(control, where)
                if(opType == "S"):
                    regQubit.halfPhaseIf(control, where)
                if(opType == "T"):
                    regQubit.quarterPhaseIf(control, where)

        else:
            raise TypeError("ancilla must be a qubit or None")






    ##############################################
    """ Call operation class to add T gate to circuit """
    def rotateX(self, angle):
        for regQubit in self._reg:
            regQubit.rotateX(angle)

    def RX(self, angle):
        self.rotateX(angle)

    ################################################################
    def rotateY(self, angle):
        for regQubit in self._reg:
            regQubit.rotateY(angle)

    def RY(self, angle):
        self.rotateY(angle)

    ################################################################
    def rotateZ(self, angle):
        for regQubit in self._reg:
            regQubit.rotateZ(angle)

    def RZ(self, angle):
        self.rotateZ(angle)

    ######################################################################
    def rotateXif(self,control, angle, where=None, ancilla=None):
        self._controlledRotateGate(control, angle, "RX", where, ancilla)

    def rotateYif(self,control, angle, where=None, ancilla=None):
        self._controlledRotateGate(control, angle, "RY", where, ancilla)
    
    def rotateZif(self,control, angle, where=None, ancilla=None):
        self._controlledRotateGate(control, angle, "RZ", where, ancilla)
    
    ########################################################################

    def _controlledRotateGate(self, control, angle, opType, where=None, ancilla=None):
        if isinstance(ancilla, qubit):
            # Compute
            if any(ancilla is target for target in self._reg):
                raise ValueError(
                    "ancilla cannot also be a target qubit"
                )
            ancilla.flipIf(control, where)

            # Use
            for regQubit in self._reg:
                if(opType == "RX"):
                    regQubit.rotateXif(ancilla, angle)
                if(opType == "RY"):
                    regQubit.rotateYif(ancilla, angle)
                if(opType == "RZ"):
                    regQubit.rotateZif(ancilla, angle)
                
            # Uncompute
            ancilla.flipIf(control, where)

        elif ancilla is None:
            for regQubit in self._reg:
                if(opType == "RX"):
                    regQubit.rotateXif(control, angle, where)
                if(opType == "RY"):
                    regQubit.rotateYif(control, angle, where)
                if(opType == "RZ"):
                    regQubit.rotateZif(control, angle, where)
                
        else:
            raise TypeError("ancilla must be a qubit or None")

    ####################################################################
    def __getitem__(self, key):
        return self._reg[key]

    ################################################################
    def __eq__(self, other):
        if not isinstance(other, (qRegister, str, int)):
            return NotImplemented

        return EqualityCondition(self, other)

    __hash__ = object.__hash__

    def __str__(self):
        info = ""
        for i in self._reg:
            print(i)
            info = info + str(i)


        return info

    def __repr__(self):
        return self.__str__()
