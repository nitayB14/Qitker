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


class EqualityCondition:
    """Hold operands for a condition passed to a controlled gate.

    The condition describes a comparison within the circuit; creating it
    does not measure either operand. Its Python truth value checks only
    whether both operands are the same object.
    """

    def __init__(self, left, right):
        """Store the left and right operands of the condition.

        Args:
            left: The control-side operand.
            right: The value or reference to compare against.
        """
        self.left = left
        self.right = right

    def __bool__(self):
        """Return whether the operands are the same Python object.

        This does not evaluate quantum equality or measure the circuit.
        """
        return self.left is self.right


class qubit:
    """Represent a qubit that belongs to a circuit.

    Gate methods record operations on the owning circuit. Whether this qubit
    appears in measurement results is controlled by `measured`.

    Attributes:
        _quantumCircuit (circuit): The circuit that owns this qubit.
        _initialize (int): Requested initial basis value, 0 or 1.
        _measured (bool): Whether to include this qubit in measurements.
        _index (int): The qubit's zero-based index in the circuit.
    """


    #initialize class
    def __init__(self, quantumCircuit, initialize=0, measured=True):
        """Create a qubit and add it to the given circuit.

        A qubit initialized to 1 records an X operation after being added
        to the circuit.

        Args:
            quantumCircuit (circuit): The circuit to add the qubit to.
            initialize (int): Initial basis value, 0 or 1. Defaults to 0.
            measured (bool): Whether to include the qubit in measurements.
                Defaults to True.

        Raises:
            TypeError: If an argument has the wrong type.
            ValueError: If `initialize` is neither 0 nor 1.
        """

        if not isinstance(quantumCircuit, circuit.circuit):
            raise TypeError("quantumCircuit must be a circuit")
        if isinstance(initialize, bool) or not isinstance(initialize, int):
            raise TypeError("initialize must be an integer, either 0 or 1")
        if initialize not in (0, 1):
            raise ValueError("initialize must be 0 or 1")
        if not isinstance(measured, bool):
            raise TypeError("measured must be a boolean")

        self._quantumCircuit = quantumCircuit
        self._initialize = initialize
        self._measured = measured
        self._quantumCircuit.addQubit(self)
        self._index = self._quantumCircuit.getIndex(self)

        if initialize == 1:
            self.flip()
    

    def getIndex(self):
        """
        Return index number of qubit

        Returns:
            int: index of qubit
        """
        
        return self._index


    def isToMeasure(self):
        """
        Return if the qubit is to measure

        Returns:
            bool: True if need to be measured ,else False
        """
        
        return self._measured


    def getValue(self):
        """Return this qubit's bit from the selected measurement outcome.

        Measure the circuit and select an outcome from its report first.
        This method does not read the qubit's current quantum state.

        Returns:
            int: The selected bit, either 0 or 1.

        Raises:
            RuntimeError: If the circuit has not been measured or no outcome
                has been selected.
            ValueError: If this qubit is not marked for measurement.
        """

        return self._quantumCircuit.getSelectedValue(self)

    
    ##############################################
    def H(self):
        """Record a Hadamard gate on this qubit in the circuit."""
        op.apply_H(self, self._quantumCircuit)
    
    def h(self):
        """Alias for `H`."""
        self.H()

    def superPosition(self):
        """Alias for `H`."""
        self.H()

    def mix(self):
        """Alias for `H`."""
        self.H()

    ##############################################
    def X(self):
        """Record a Pauli-X gate on this qubit in the circuit."""
        op.apply_X(self, self._quantumCircuit)

    def x(self):
        """Alias for `X`."""
        self.X()

    def flip(self):
        """Alias for `X`."""
        self.X()
    ##############################################
    def Y(self):
        """Record a Pauli-Y gate on this qubit in the circuit."""
        op.apply_Y(self, self._quantumCircuit)

    def y(self):
        """Alias for `Y`."""
        self.Y()

    def flipPhase(self):
        """Alias for `Y`."""
        self.Y()
    ##############################################
    def Z(self):
        """Record a Pauli-Z gate on this qubit in the circuit."""
        op.apply_Z(self, self._quantumCircuit)
    
    def z(self):
        """Alias for `Z`."""
        self.Z()

    def phase(self):
        """Alias for `Z`."""
        self.Z()
    ##############################################
    def S(self):
        """Record an S phase gate on this qubit in the circuit."""
        op.apply_S(self, self._quantumCircuit)

    def s(self):
        """Alias for `S`."""
        self.S()

    def halfPhase(self):
        """Alias for `S`."""
        self.S()
    ##############################################
    def T(self):
        """Record a T phase gate on this qubit in the circuit."""
        op.apply_T(self, self._quantumCircuit)

    def t(self):
        """Alias for `T`."""
        self.T()

    def quarterPhase(self):
        """Alias for `T`."""
        self.T()
    ##############################################


    def _checkItems(self, control, where):
        """Normalize the control and condition for a controlled gate.

        An `EqualityCondition` is split into its left and right operands.
        A `qRegister` supplied as either operand is converted to a list of
        qubits. Other values pass through for later validation.

        Args:
            control: A control qubit, list, register, or equality condition.
            where: An optional activation condition.

        Returns:
            tuple: The normalized `(control, where)` pair.

        Raises:
            TypeError: If `where` is supplied alongside an equality condition.
        """

        from qitker.compiler.qRegister import qRegister
        if isinstance(control, EqualityCondition):
            if where is not None:
                raise TypeError(
                    "where cannot be used together with an equality condition"
                )

            control, where = control.left, control.right
        
        if isinstance(control, qRegister):
            control = control[::]
        if isinstance(where, qRegister):
            where = where[::]

        return control, where




    def flipIf(self, control, where=None):
        """Record an X gate on this qubit when the control condition matches.

        `control` may be a qubit, a list of qubits, a qRegister, or an equality
        condition. By default, the gate activates when all controls are 1.
        `where` may instead specify an integer, a pattern of 0, 1, and x
        (where x means "don't care"), or qubits to compare for equality.

        Args:
            control: The qubit or qubits that control the gate.
            where: The activation condition. Defaults to None, meaning all 1s.

        Raises:
            TypeError: If an unsupported condition is supplied or `where` is
                combined with an equality condition.
            ValueError: If the controls or condition are invalid.
        """

        control, where = self._checkItems(control, where)
        self._controlledGate(control, "X", where)


    def flipPhaseIf(self, control, where=None):
        """Record a conditional Pauli-Y gate on this qubit.

        `control` and `where` have the same meaning as in `flipIf`.
        """
        
        control, where = self._checkItems(control, where)
        self._controlledGate(control, "Y", where)


    def phaseIf(self, control, where=None):
        """Record a conditional Pauli-Z gate on this qubit.

        `control` and `where` have the same meaning as in `flipIf`.
        """
        
        control, where = self._checkItems(control, where)
        self._controlledGate(control, "Z", where)


    def halfPhaseIf(self, control, where=None):
        """Record a conditional S phase gate on this qubit.

        `control` and `where` have the same meaning as in `flipIf`.
        """
        
        control, where = self._checkItems(control, where)
        self._controlledGate(control, "S", where)


    def quarterPhaseIf(self, control, where=None):
        """Record a conditional T phase gate on this qubit.

        `control` and `where` have the same meaning as in `flipIf`.
        """
        
        control, where = self._checkItems(control, where)
        self._controlledGate(control, "T", where)
    
    ###########################################################################
    def _controlledGate(self, control, oType, where=None):
        """Record a gate under a static condition or a qubit comparison.

        A static condition uses one ``0``, ``1``, or ``x`` per control;
        ``x`` ignores that control. A comparison applies the gate when
        corresponding control and reference qubits have equal values.
        This method records the required gates without executing the circuit.

        Args:
            control (qubit | list[qubit]): The control qubit or qubits.
            oType (str): The gate to record: ``X``, ``Y``, ``Z``, ``S``, or ``T``.
            where: A static condition or qubit comparison reference. If None,
                all controls must be 1.

        Raises:
            TypeError: If a control or condition has an unsupported type.
            ValueError: If the controls, references, or condition are invalid.
        """

        # Validation returns either a bit pattern or reference qubits.
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

            # An operand always equals itself, so no controls are needed.
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

            # XOR each control into its reference qubit to compute differences.
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
                   

            
            # Undo the XOR gates in reverse order after the conditional gate.
            for current_control, reference in reversed(comparison_pairs):
                reference.cx(current_control)

            return

        # Ignore ``x`` positions and remember ``0`` controls for X wrappers.
        pattern = condition

        active_controls = []
        zero_controls = []

        for current_control, state in zip(controls, pattern):
            if state == "x":
                continue

            active_controls.append(current_control)

            if state == "0":
                zero_controls.append(current_control)

        # Invert zero-controls so the recorded gate can use positive controls.
        for current_control in zero_controls:
            current_control.flip()

        # An all-``x`` pattern has no active controls: record a plain gate.
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


        # Remove the temporary inversions from the zero-controls.
        for current_control in reversed(zero_controls):
            current_control.flip()


    #################################################################
    def cx(self, control):
        """Alias for `flipIf(control)`; activates when all controls are 1."""
        self.flipIf(control)
    
    def cy(self, control):
        """Alias for `flipPhaseIf(control)`; activates when all controls are 1."""
        self.flipPhaseIf(control)
    
    def cz(self, control):
        """Alias for `phaseIf(control)`; activates when all controls are 1."""
        self.phaseIf(control)

    def cs(self, control):
        """Alias for `halfPhaseIf(control)`; activates when all controls are 1."""
        self.halfPhaseIf(control)

    def ct(self, control):
        """Alias for `quarterPhaseIf(control)`; activates when all controls are 1."""
        self.quarterPhaseIf(control)


    def CX(self, control):
        """Alias for `flipIf(control)`; activates when all controls are 1."""
        self.flipIf(control)

    def CY(self, control):
        """Alias for `flipPhaseIf(control)`; activates when all controls are 1."""
        self.flipPhaseIf(control)

    def CZ(self, control):
        """Alias for `phaseIf(control)`; activates when all controls are 1."""
        self.phaseIf(control)

    def CS(self, control):
        """Alias for `halfPhaseIf(control)`; activates when all controls are 1."""
        self.halfPhaseIf(control)

    def CT(self, control):
        """Alias for `quarterPhaseIf(control)`; activates when all controls are 1."""
        self.quarterPhaseIf(control)
    #################################################################
    def rotateX(self, angle):
        """Record a rotation around the X axis.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.

        Args:
            angle: Rotation angle in radians.
        """
        op.apply_rotate_X(self, angle=angle, circuit=self._quantumCircuit)

    def RX(self, angle):
        """Record an X-axis rotation, equivalent to `rotateX(angle)`.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.
        """
        op.apply_rotate_X(self, angle=angle, circuit=self._quantumCircuit)

    ################################################################
    def rotateY(self, angle):
        """Record a rotation around the Y axis.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.

        Args:
            angle: Rotation angle in radians.
        """
        op.apply_rotate_Y(self, angle=angle, circuit=self._quantumCircuit)

    def RY(self, angle):
        """Record a Y-axis rotation, equivalent to `rotateY(angle)`.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.
        """
        op.apply_rotate_Y(self, angle=angle, circuit=self._quantumCircuit)

    ################################################################
    def rotateZ(self, angle):
        """Record a rotation around the Z axis.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.

        Args:
            angle: Rotation angle in radians.
        """
        op.apply_rotate_Z(self, angle=angle, circuit=self._quantumCircuit)

    def RZ(self, angle):
        """Record a Z-axis rotation, equivalent to `rotateZ(angle)`.

        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.
        """
        op.apply_rotate_Z(self, angle=angle, circuit=self._quantumCircuit)

    ################################################################
    def rotateXif(self, control, angle=0, where=None):
        """Record an X-axis rotation when the control condition matches.

        `control` and `where` follow the same rules as in `flipIf`.
        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.

        Args:
            control: The qubit or qubits controlling the rotation.
            angle: Rotation angle in radians. Defaults to 0.
            where: The activation condition. Defaults to all controls being 1.
        """
        control, where = self._checkItems(control, where)
        self._controlledRotateGate(control, angle, "RX", where)

    def rotateYif(self, control, angle=0, where=None):
        """Record a Y-axis rotation when the control condition matches.

        `control` and `where` follow the same rules as in `flipIf`.
        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.

        Args:
            control: The qubit or qubits controlling the rotation.
            angle: Rotation angle in radians. Defaults to 0.
            where: The activation condition. Defaults to all controls being 1.
        """
        control, where = self._checkItems(control, where)
        self._controlledRotateGate(control, angle, "RY", where)

    def rotateZif(self, control, angle=0, where=None):
        """Record a Z-axis rotation when the control condition matches.

        `control` and `where` follow the same rules as in `flipIf`.
        The current anyonic backend cannot execute parameterized rotations;
        export the circuit to Qiskit for simulation.

        Args:
            control: The qubit or qubits controlling the rotation.
            angle: Rotation angle in radians. Defaults to 0.
            where: The activation condition. Defaults to all controls being 1.
        """
        control, where = self._checkItems(control, where)
        self._controlledRotateGate(control, angle, "RZ", where)

    #################################################################

    def _controlledRotateGate(self, control, angle, oType, where=None):
        """Record a rotation under a static condition or qubit comparison.

        A static condition uses one ``0``, ``1``, or ``x`` per control;
        ``x`` ignores that control. A comparison rotates the target when
        corresponding control and reference qubits have equal values.
        This method records operations without executing the circuit.

        Args:
            control (qubit | list[qubit]): The control qubit or qubits.
            angle: Rotation angle in radians.
            oType (str): The rotation to record: ``RX``, ``RY``, or ``RZ``.
            where: A static condition or qubit comparison reference. If None,
                all controls must be 1.

        Raises:
            TypeError: If a control or condition has an unsupported type.
            ValueError: If the controls, references, or condition are invalid.
        """

        # Validation returns either a bit pattern or reference qubits.
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

            # An operand always equals itself: record an ordinary rotation.
            if same_operands:
                if(oType == "RX"):
                    self.rotateX(angle)
                elif(oType == "RY"):
                    self.rotateY(angle)
                elif(oType == "RZ"):
                    self.rotateZ(angle)
                return

            comparison_pairs = list(zip(controls, references))

            # XOR each control into its reference qubit to compute differences.
            for current_control, reference in comparison_pairs:
                reference.cx(current_control)

            # All computed differences are zero exactly when both operands
            # represent the same computational-basis value.
            if(oType == "RX"):
                self._controlledRotateGate(references, angle, "RX", where=0)
            elif(oType == "RY"):
                    self._controlledRotateGate(references, angle, "RY", where=0)
            elif(oType == "RZ"):
                    self._controlledRotateGate(references, angle, "RZ", where=0)
            

            # Undo the XOR gates in reverse order after the rotation.
            for current_control, reference in reversed(comparison_pairs):
                reference.cx(current_control)

            return

        # Ignore ``x`` positions and remember ``0`` controls for X wrappers.
        pattern = condition

        active_controls = []
        zero_controls = []

        for current_control, state in zip(controls, pattern):
            if state == "x":
                continue

            active_controls.append(current_control)

            if state == "0":
                zero_controls.append(current_control)

        # Invert zero-controls so the rotation can use positive controls.
        for current_control in zero_controls:
            current_control.flip()

        # An all-``x`` pattern has no active controls: record a plain rotation.
        if active_controls:
            if(oType == "RX"):
                op.apply_controlled_rotate_X(self,active_controls,angle,self._quantumCircuit,)
            elif(oType == "RY"):
                op.apply_controlled_rotate_Y(self,active_controls,angle,self._quantumCircuit,)
            elif(oType == "RZ"):
                op.apply_controlled_rotate_Z(self,active_controls,angle,self._quantumCircuit,)
                
        else:
            if(oType == "RX"):
                self.rotateX(angle)
            elif(oType == "RY"):
                    self.rotateY(angle)
            elif(oType == "RZ"):
                    self.rotateZ(angle)

        # Remove the temporary inversions from the zero-controls.
        for current_control in reversed(zero_controls):
            current_control.flip()


    #################################################################
    def swap(self, control):
        """Record a SWAP with another qubit as three controlled-X gates.

        Args:
            control (qubit): The other qubit to exchange with this one.

        Raises:
            TypeError: If `control` is not a qubit.
            ValueError: If `control` is this qubit or belongs to another circuit.
        """
        if not isinstance(control, qubit):
            raise TypeError("control must be a qubit")

        self.flipIf(control)
        control.flipIf(self)
        self.flipIf(control)

    #################################################################
    def __eq__(self, other):
        """Create a qubit equality condition for a controlled gate.

        Use the returned condition as an argument to methods such as
        `flipIf`. To check whether two variables refer to the same qubit
        object in Python, use `is`.

        Args:
            other: The qubit to compare with this qubit.

        Returns:
            EqualityCondition: A condition for two qubits.
            Returns NotImplemented if `other` is not a qubit.
        """
        
        if not isinstance(other, qubit):
            return NotImplemented

        return EqualityCondition(self, other)

    __hash__ = object.__hash__


    def __str__(self):
        """Return the qubit's circuit index and measurement flag as text."""
        return f"index: {self._quantumCircuit.getIndex(self)}, is to measure?: {self._measured}"


    def __repr__(self):
        """Return the same qubit description as `__str__`."""
        return self.__str__()





