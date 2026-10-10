"""Register of circuit qubits with elementwise gates and conditional operations."""

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
    """Represent an ordered group of qubits in one circuit.

    Index zero is the leftmost, most-significant bit. Gate methods record
    the same operation on each qubit; they do not execute the circuit.

    Attributes:
        _quantumCircuit (circuit): Circuit containing the register's qubits.
        _size (int): Number of qubits in the register.
        _initialize (str): Initial bitstring, padded to the register size.
        _reg (list[qubit]): Qubits in left-to-right register order.
    """

    #initialize class
    def __init__(self, quantumCircuit, size=None, initialize=0, measured=True):
        """Create new qubits in the circuit and initialize the register.

        If `size` is omitted, an integer uses its minimum binary width
        (at least one bit), while a binary string keeps its full width.
        A larger explicit size pads the value with zeros on the left.
        Each 1 bit records an X gate on the corresponding new qubit.

        Args:
            quantumCircuit (circuit): Circuit to receive the new qubits.
            size (int | None): Positive register width, or None to infer it.
            initialize (int | str): Non-negative integer or non-empty binary
                string. Defaults to 0.
            measured (bool): Measurement flag for every new qubit.
                Defaults to True.

        Raises:
            TypeError: If an argument has an unsupported type.
            ValueError: If the size or initial value is invalid or does not fit.
        """

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

        # Index zero is the leftmost, most-significant bit of the bitstring.
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
        """Return the circuit-wide index of each qubit in register order.

        Returns:
            list[int]: One circuit index per register qubit.
        """
        return [i.getIndex() for i in self._reg]

    def getBitstring(self):
        """Return this register's bits from the selected measurement outcome.

        Measure the circuit and select an outcome first. Every register
        qubit must be marked for measurement. Bits follow register order,
        with index zero on the left.

        Returns:
            str: The selected register bitstring.

        Raises:
            RuntimeError: If there is no measurement or selected outcome.
            ValueError: If a register qubit is not marked for measurement.
        """
        return "".join(
            str(regQubit.getValue())
            for regQubit in self._reg
        )

    def getValue(self):
        """Return the selected register bitstring as a base-two integer.

        Requires a selected measurement outcome and measured register qubits;
        it does not read the initial value or the current quantum state.

        Returns:
            int: The measured value of the register.
        """
        return int(self.getBitstring(), 2)


    def isToMeasure(self):
        """Return the measurement flag of every qubit in register order.

        Returns:
            list[bool]: One flag per register qubit.
        """
        return [i.isToMeasure() for i in self._reg]

    def getQubit(self, index):
        """Return an existing qubit at a register index.

        Python list indexing applies, including negative indexes.

        Args:
            index (int): Position in the register.

        Returns:
            qubit: The qubit at that position.

        Raises:
            IndexError: If the index is out of range.
        """
        return self._reg[index]
    ###########################################################################
    ##############################################
    def H(self):
        """Record a Hadamard gate on every qubit in the register."""
        for regQubit in self._reg:
            regQubit.H()
    
    def h(self):
        """Alias for `H`; acts on every register qubit."""
        self.H()

    def superPosition(self):
        """Alias for `H`; acts on every register qubit."""
        self.H()

    def mix(self):
        """Alias for `H`; acts on every register qubit."""
        self.H()
    ##############################################
    def X(self):
        """Record a Pauli-X gate on every qubit in the register."""
        for regQubit in self._reg:
            regQubit.X()

    def x(self):
        """Alias for `X`; acts on every register qubit."""
        self.X()

    def flip(self):
        """Alias for `X`; acts on every register qubit."""
        self.X()
##############################################
    def Y(self):
        """Record a Pauli-Y gate on every qubit in the register."""
        for regQubit in self._reg:
            regQubit.Y()

    def y(self):
        """Alias for `Y`; acts on every register qubit."""
        self.Y()

    def flipPhase(self):
        """Alias for `Y`; acts on every register qubit."""
        self.Y()
    ##############################################
    def Z(self):
        """Record a Pauli-Z gate on every qubit in the register."""
        for regQubit in self._reg:
            regQubit.Z()
    
    def z(self):
        """Alias for `Z`; acts on every register qubit."""
        self.Z()

    def phase(self):
        """Alias for `Z`; acts on every register qubit."""
        self.Z()
    ##############################################
    def S(self):
        """Record an S phase gate on every qubit in the register."""
        for regQubit in self._reg:
            regQubit.S()

    def s(self):
        """Alias for `S`; acts on every register qubit."""
        self.S()

    def halfPhase(self):
        """Alias for `S`; acts on every register qubit."""
        self.S()
    ##############################################
    def T(self):
        """Record a T phase gate on every qubit in the register."""
        for regQubit in self._reg:
            regQubit.T()

    def t(self):
        """Alias for `T`; acts on every register qubit."""
        self.T()

    def quarterPhase(self):
        """Alias for `T`; acts on every register qubit."""
        self.T()
    ################################################################
    def shiftLeft(self, amount=1):
        """Record a cyclic left shift of the register's quantum contents.

        The shift uses SWAP gates and leaves the Python qubit order in
        `_reg` unchanged. The amount is taken modulo the register size;
        a one-qubit register or a full-width shift records no gates.

        Args:
            amount (int): Positions to shift left. Defaults to 1.
        """
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
        """Record a cyclic right shift without reordering the qubit objects.

        Args:
            amount (int): Positions to shift right. Defaults to 1.
        """
        self.shiftLeft(-amount)
    ################################################################

    def flipIf(self,control, where=None, ancilla=None):
        """Record a conditional X gate on every qubit in the register.

        Each target uses the same control condition; controls are not paired
        with targets by position. `control` and `where` follow the rules of
        `qubit.flipIf`, including ``0``, ``1``, and ``x`` patterns. With an
        ancilla, the condition is computed once, used for all targets, and
        uncomputed. The ancilla must start in |0>, belong to the same
        circuit, and be separate from controls, references, and targets.

        Args:
            control: Control qubit, list, register, or equality condition.
            where: Optional activation condition; None means all controls 1.
            ancilla (qubit | None): Optional workspace qubit, initially |0>.

        Raises:
            TypeError: If the ancilla or condition has an unsupported type.
            ValueError: If the ancilla is a target or the condition is invalid.
        """
        self._controlledGate(control, "X", where, ancilla)

    def flipPhaseIf(self,control, where=None, ancilla=None):
        """Record a conditional Pauli-Y gate on every register qubit.

        `control`, `where`, and `ancilla` follow the rules of `flipIf`.
        """
        self._controlledGate(control, "Y", where, ancilla)
    
    def phaseIf(self,control, where=None, ancilla=None):
        """Record a conditional Pauli-Z gate on every register qubit.

        `control`, `where`, and `ancilla` follow the rules of `flipIf`.
        """
        self._controlledGate(control, "Z", where, ancilla)
    
    def halfPhaseIf(self,control, where=None, ancilla=None):
        """Record a conditional S phase gate on every register qubit.

        `control`, `where`, and `ancilla` follow the rules of `flipIf`.
        """
        self._controlledGate(control, "S", where, ancilla)
    
    def quarterPhaseIf(self,control, where=None, ancilla=None):
        """Record a conditional T phase gate on every register qubit.

        `control`, `where`, and `ancilla` follow the rules of `flipIf`.
        """
        self._controlledGate(control, "T", where, ancilla)

    ################################################################
    

    def _controlledGate(self, control, opType, where=None, ancilla=None):
        """Record the same conditional fixed gate on every target qubit.

        Without an ancilla, each target receives the full condition.
        With one, a conditional X computes the condition into the ancilla,
        each target uses that qubit as its control, and a final X uncomputes
        it. This method only records operations in the circuit.

        Args:
            control: Control operand passed to the qubit gate methods.
            opType (str): One of ``X``, ``Y``, ``Z``, ``S``, or ``T``.
            where: Optional activation condition.
            ancilla (qubit | None): Optional workspace qubit.

        Raises:
            TypeError: If `ancilla` is neither a qubit nor None.
            ValueError: If the ancilla is also a register target.
        """
        if isinstance(ancilla, qubit):
            # Compute the shared condition into the workspace qubit.
            if any(ancilla is target for target in self._reg):
                raise ValueError(
                    "ancilla cannot also be a target qubit"
                )
            ancilla.flipIf(control, where)

            # Use the workspace as a single control for every target.
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

            # Restore the workspace by undoing the condition computation.
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
    def rotateX(self, angle):
        """Record an X-axis rotation on every register qubit.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.

        Args:
            angle: Rotation angle in radians.
        """
        for regQubit in self._reg:
            regQubit.rotateX(angle)

    def RX(self, angle):
        """Alias for `rotateX(angle)` on every register qubit.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.
        """
        self.rotateX(angle)

    ################################################################
    def rotateY(self, angle):
        """Record a Y-axis rotation on every register qubit.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.

        Args:
            angle: Rotation angle in radians.
        """
        for regQubit in self._reg:
            regQubit.rotateY(angle)

    def RY(self, angle):
        """Alias for `rotateY(angle)` on every register qubit.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.
        """
        self.rotateY(angle)

    ################################################################
    def rotateZ(self, angle):
        """Record a Z-axis rotation on every register qubit.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.

        Args:
            angle: Rotation angle in radians.
        """
        for regQubit in self._reg:
            regQubit.rotateZ(angle)

    def RZ(self, angle):
        """Alias for `rotateZ(angle)` on every register qubit.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.
        """
        self.rotateZ(angle)

    ######################################################################
    def rotateXif(self,control, angle, where=None, ancilla=None):
        """Record a conditional X-axis rotation on every register qubit.

        `control`, `where`, and `ancilla` follow the rules of `flipIf`.
        The angle is required and measured in radians. The current anyonic
        backend cannot execute parameterized rotations; use Qiskit export.

        Args:
            control: Shared control condition for every target qubit.
            angle: Rotation angle in radians.
            where: Optional activation condition; None means all controls 1.
            ancilla (qubit | None): Optional workspace qubit, initially |0>.
        """
        self._controlledRotateGate(control, angle, "RX", where, ancilla)

    def rotateYif(self,control, angle, where=None, ancilla=None):
        """Record a conditional Y-axis rotation on every register qubit.

        `control`, `where`, and `ancilla` follow the rules of `rotateXif`.
        The current anyonic backend cannot execute parameterized rotations;
        use Qiskit export.

        Args:
            control: Shared control condition for every target qubit.
            angle: Rotation angle in radians.
            where: Optional activation condition; None means all controls 1.
            ancilla (qubit | None): Optional workspace qubit, initially |0>.
        """
        self._controlledRotateGate(control, angle, "RY", where, ancilla)
    
    def rotateZif(self,control, angle, where=None, ancilla=None):
        """Record a conditional Z-axis rotation on every register qubit.

        `control`, `where`, and `ancilla` follow the rules of `rotateXif`.
        The current anyonic backend cannot execute parameterized rotations;
        use Qiskit export.

        Args:
            control: Shared control condition for every target qubit.
            angle: Rotation angle in radians.
            where: Optional activation condition; None means all controls 1.
            ancilla (qubit | None): Optional workspace qubit, initially |0>.
        """
        self._controlledRotateGate(control, angle, "RZ", where, ancilla)
    
    ########################################################################

    def _controlledRotateGate(self, control, angle, opType, where=None, ancilla=None):
        """Record the same conditional rotation on every target qubit.

        With an ancilla, compute the shared condition into it, use it as
        a single control for each target, and uncompute it. Without one,
        each target receives the full condition. The method records gates
        without executing the circuit.

        Args:
            control: Control operand passed to the qubit rotation methods.
            angle: Rotation angle in radians.
            opType (str): One of ``RX``, ``RY``, or ``RZ``.
            where: Optional activation condition.
            ancilla (qubit | None): Optional workspace qubit.

        Raises:
            TypeError: If `ancilla` is neither a qubit nor None.
            ValueError: If the ancilla is also a register target.
        """
        if isinstance(ancilla, qubit):
            # Compute the shared condition into the workspace qubit.
            if any(ancilla is target for target in self._reg):
                raise ValueError(
                    "ancilla cannot also be a target qubit"
                )
            ancilla.flipIf(control, where)

            # Use the workspace as a single control for every target.
            for regQubit in self._reg:
                if(opType == "RX"):
                    regQubit.rotateXif(ancilla, angle)
                if(opType == "RY"):
                    regQubit.rotateYif(ancilla, angle)
                if(opType == "RZ"):
                    regQubit.rotateZif(ancilla, angle)
                
            # Restore the workspace by undoing the condition computation.
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
        """Return existing qubits by index or a list of them by slice.

        Index zero is the leftmost register bit. A slice returns a Python
        list of references; it does not create another register or gates.

        Args:
            key (int | slice): Index or slice in register order.

        Returns:
            qubit | list[qubit]: The selected qubit or qubits.
        """
        return self._reg[key]

    ################################################################
    def __eq__(self, other):
        """Create a condition for a controlled gate, not a measured boolean.

        A register can be compared with another register, a binary pattern,
        or an integer. Pass the resulting `EqualityCondition` to a controlled
        method such as `flipIf`. Use `is` for Python object identity.

        Args:
            other (qRegister | str | int): Operand to compare against.

        Returns:
            EqualityCondition: A deferred gate condition, or NotImplemented
            for an unsupported operand type.
        """
        if not isinstance(other, (qRegister, str, int)):
            return NotImplemented

        return EqualityCondition(self, other)

    __hash__ = object.__hash__

    def __str__(self):
        """Print each qubit and return their descriptions concatenated.

        The returned text has no separator between qubit descriptions.
        """
        info = ""
        for i in self._reg:
            print(i)
            info = info + str(i)


        return info

    def __repr__(self):
        """Return the same description as `__str__`, including its printing."""
        return self.__str__()
