from qitker.compiler import circuit



class opType:
    """
    The class save index of qubit and gate name
    
    Attributes:
        - gateName: string
            Name of quantum gate
        - target: int
            index of qubit
    """

    def __init__(self, gateName, target):
        self.gateName = gateName
        self.target = target
    
    def getName(self):
        """
        Return name of operation

        Args:
            - None

        Returns:
            - (string) : operation name
        """

        return self.gateName
    

    def getTarget(self):
        """
        Return index of qubit we apply operation on

        Args:
            - None

        Returns:
            - (int) : qubit index
        """

        return self.target

    #returning string with basic information on the operation
    def __str__(self):
        return f"index: {self.target} -> {self.gateName}"




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

        op = opType(gateName="H",
                    target=circuit.getIndex(qubit))
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

        op = opType(gateName="X",
                    target=circuit.getIndex(qubit))
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

        op = opType(gateName="Y",
                    target=circuit.getIndex(qubit))
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

        op = opType(gateName="Z",
                    target=circuit.getIndex(qubit))
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

        op = opType(gateName="S",
                    target=circuit.getIndex(qubit))
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

        op = opType(gateName="T",
                    target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    ####################################################



