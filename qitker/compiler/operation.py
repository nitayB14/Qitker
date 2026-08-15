


class opType:
    def __init__(self, gateName):
        self._gateName = gateName
    
    def getName(self):
        """
        Return name of operation
        """

        return self._gateName
    
        #returning string with basic information on the operation
    def __str__(self):
        return f"operation -> {self._gateName}"


##################################################################################


class gateOpType(opType):
    """
    The class save index of qubit and gate name
    
    Attributes:
        - gateName: string
            Name of quantum gate
        - target: int
            index of qubit
    """

    def __init__(self, gateName, target):
        super().__init__(gateName)
        self._target = target
   

    def getTarget(self):
        """
        Return index of qubit we apply operation on
        """

        return self._target

    #returning string with basic information on the operation
    def __str__(self):
        return f"index: {self._target} -> {self._gateName}"
#######################################################################################################

class controlledOpType(gateOpType):
    """
    The class save index of target qubit, controlled qubits and gate name
    
    Attributes:
        - gateName: string
            Name of quantum gate
        - target: int
            index of qubit
        - controlled: list 
              list of qubits
    """

    def __init__(self, gateName, target, controllers):
        super().__init__(gateName, target)
        self._controllers = controllers

    def getControllers(self):
        return self._controllers

    #returning string with basic information on the operation
    def __str__(self):
        return f"Controlled {self._gateName}  -->  Target: {self._target}, Controllers: {self._controllers}"




#####################################################################################################
class operation:
    """
    The class connect between the operation on qubit to the circuit vector
    Responsible to create object of opType and add it to the circuit
    
    Attributes:
        - None
    """

    ####################################################

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
