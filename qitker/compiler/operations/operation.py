

from qitker.compiler.operations.opClasses import controlledRotateOpType, opType, gateOpType, controlledOpType, rotateOpType

#####################################################################################################
class operation:
    """
    The class connect between the operation on qubit to the circuit vector
    Responsible to create object of opType and add it to the circuit
    
    Attributes:
        - None
    """

    ####################################################
    def apply_barrier(self, circuit):
        op = opType(gateName="barrier")
        circuit.addOperation(op)


    def apply_H(self, qubit, circuit):
        """
        Add H operation to operationVector in circuit

        Args:
            - qubit (qubit):
                using the qubit to get its index
            - circuit (circuit):
                adding operation to circuit

        Returns:
            - None
        """

        op = gateOpType(gateName="H", target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    ####################################################

    def apply_X(self, qubit, circuit):
        """
        Add X operation to operationVector in circuit

        Args:
            - qubit (qubit):
                using the qubit to get its index
            - circuit (circuit):
                adding operation to circuit

        Returns:
            - None
        """

        op = gateOpType(gateName="X", target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    ####################################################

    def apply_Y(self, qubit, circuit):
        """
        Add Y operation to operationVector in circuit

        Args:
            - qubit (qubit):
                using the qubit to get its index
            - circuit (circuit):
                adding operation to circuit

        Returns:
            - None
        """

        op = gateOpType(gateName="Y", target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    ####################################################

    def apply_Z(self, qubit, circuit):
        """
        Add Z operation to operationVector in circuit

        Args:
            - qubit (qubit):
                using the qubit to get its index
            - circuit (circuit):
                adding operation to circuit

        Returns:
            - None
        """

        op = gateOpType(gateName="Z", target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    ####################################################

    def apply_S(self, qubit, circuit):
        """
        Add S operation to operationVector in circuit

        Args:
            - qubit (qubit):
                using the qubit to get its index
            - circuit (circuit):
                adding operation to circuit

        Returns:
            - None
        """

        op = gateOpType(gateName="S", target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    ####################################################

    def apply_T(self, qubit, circuit):
        """
        Add T operation to operationVector in circuit

        Args:
            - qubit (qubit):
                using the qubit to get its index
            - circuit (circuit):
                adding operation to circuit

        Returns:
            - None
        """

        op = gateOpType(gateName="T",target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    ####################################################
    def apply_Controlled_X(self, targetQubit, controlQubits, circuit):
        """
        Add a controlled-X operation to operationVector.

        Args:
            - targetQubit (qubit):
                Qubit on which X will be applied.
            - controlQubits (qubit or list[qubit]):
                One or more control qubits.
            - circuit (circuit):
                Circuit to which the operation is added.

        Returns:
            - None
        """

        if isinstance(controlQubits, list):
            controllersIndexes = [
                circuit.getIndex(controlQubit)
                for controlQubit in controlQubits
            ]
        else:
            controllersIndexes = [
                circuit.getIndex(controlQubits)
            ]

        op = controlledOpType(
            gateName="X",
            target=circuit.getIndex(targetQubit),
            controllers=controllersIndexes
        )
        circuit.addOperation(op)

    ####################################################
    def apply_Controlled_Y(self, targetQubit, controlQubits, circuit):
        """
        Add a controlled-Y operation to operationVector.

        Args:
            - targetQubit (qubit):
                Qubit on which Y will be applied.
            - controlQubits (qubit or list[qubit]):
                One or more control qubits.
            - circuit (circuit):
                Circuit to which the operation is added.

        Returns:
            - None
        """

        if isinstance(controlQubits, list):
            controllersIndexes = [
                circuit.getIndex(controlQubit)
                for controlQubit in controlQubits
            ]
        else:
            controllersIndexes = [
                circuit.getIndex(controlQubits)
            ]

        op = controlledOpType(
            gateName="Y",
            target=circuit.getIndex(targetQubit),
            controllers=controllersIndexes
        )
        circuit.addOperation(op)

    ####################################################
    def apply_Controlled_Z(self, targetQubit, controlQubits, circuit):
        """
        Add a controlled-Z operation to operationVector.

        Args:
            - targetQubit (qubit):
                Qubit on which Z will be applied.
            - controlQubits (qubit or list[qubit]):
                One or more control qubits.
            - circuit (circuit):
                Circuit to which the operation is added.

        Returns:
            - None
        """

        if isinstance(controlQubits, list):
            controllersIndexes = [
                circuit.getIndex(controlQubit)
                for controlQubit in controlQubits
            ]
        else:
            controllersIndexes = [
                circuit.getIndex(controlQubits)
            ]

        op = controlledOpType(
            gateName="Z",
            target=circuit.getIndex(targetQubit),
            controllers=controllersIndexes
        )
        circuit.addOperation(op)

    def apply_Controlled_S(self, targetQubit, controlQubits, circuit):
        """
        Add a controlled-S operation to operationVector.

        Args:
            - targetQubit (qubit):
                Qubit on which S will be applied.
            - controlQubits (qubit or list[qubit]):
                One or more control qubits.
            - circuit (circuit):
                Circuit to which the operation is added.

        Returns:
            - None
        """

        if isinstance(controlQubits, list):
            controllersIndexes = [
                circuit.getIndex(controlQubit)
                for controlQubit in controlQubits
            ]
        else:
            controllersIndexes = [
                circuit.getIndex(controlQubits)
            ]

        op = controlledOpType(
            gateName="S",
            target=circuit.getIndex(targetQubit),
            controllers=controllersIndexes
        )
        circuit.addOperation(op)

    def apply_Controlled_T(self, targetQubit, controlQubits, circuit):
        """
        Add a controlled-T operation to operationVector.

        Args:
            - targetQubit (qubit):
                Qubit on which T will be applied.
            - controlQubits (qubit or list[qubit]):
                One or more control qubits.
            - circuit (circuit):
                Circuit to which the operation is added.

        Returns:
            - None
        """

        if isinstance(controlQubits, list):
            controllersIndexes = [
                circuit.getIndex(controlQubit)
                for controlQubit in controlQubits
            ]
        else:
            controllersIndexes = [
                circuit.getIndex(controlQubits)
            ]

        op = controlledOpType(
            gateName="T",
            target=circuit.getIndex(targetQubit),
            controllers=controllersIndexes
        )
        circuit.addOperation(op)



    ################################################################################

    def apply_rotate_X(self, targetQubit, angle, circuit):
        op = rotateOpType(gateName="RX", target=circuit.getIndex(targetQubit), angle=angle)
        circuit.addOperation(op)
    
    def apply_rotate_Y(self, targetQubit, angle, circuit):
        op = rotateOpType(gateName="RY", target=circuit.getIndex(targetQubit), angle=angle)
        circuit.addOperation(op)

    def apply_rotate_Z(self, targetQubit, angle, circuit):
        op = rotateOpType(gateName="RZ", target=circuit.getIndex(targetQubit), angle=angle)
        circuit.addOperation(op)

    ################################################################################
        
    def apply_controlled_rotate_X(self, targetQubit, controlQubits, angle, circuit):
        if isinstance(controlQubits, list):
            controllersIndexes = [
                circuit.getIndex(controlQubit)
                for controlQubit in controlQubits
            ]
        else:
            controllersIndexes = [
                circuit.getIndex(controlQubits)
            ]

        op = controlledRotateOpType(
            gateName="RX",
            target=circuit.getIndex(targetQubit),
            controllers=controllersIndexes,
            angle=angle
        )
        circuit.addOperation(op)
    
    def apply_controlled_rotate_Y(self, targetQubit, controlQubits, angle, circuit):
        if isinstance(controlQubits, list):
            controllersIndexes = [
                circuit.getIndex(controlQubit)
                for controlQubit in controlQubits
            ]
        else:
            controllersIndexes = [
                circuit.getIndex(controlQubits)
            ]

        op = controlledRotateOpType(
            gateName="RY",
            target=circuit.getIndex(targetQubit),
            controllers=controllersIndexes,
            angle=angle
        )
        circuit.addOperation(op)
    
    def apply_controlled_rotate_Z(self, targetQubit, controlQubits, angle, circuit):
        if isinstance(controlQubits, list):
            controllersIndexes = [
                circuit.getIndex(controlQubit)
                for controlQubit in controlQubits
            ]
        else:
            controllersIndexes = [
                circuit.getIndex(controlQubits)
            ]

        op = controlledRotateOpType(
            gateName="RZ",
            target=circuit.getIndex(targetQubit),
            controllers=controllersIndexes,
            angle=angle
        )
        circuit.addOperation(op)

