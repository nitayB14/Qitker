"""Operation records stored in a quantum circuit."""




class opType:
    """Store an operation name, including a barrier name."""

    def __init__(self, gateName):
        """Initialize the record with its operation name."""
        self._gateName = gateName
    
    def getName(self):
        """
        Return name of operation
        """

        return self._gateName
    
        #returning string with basic information on the operation
    def __str__(self):
        """Return the operation name as a readable string."""
        return f"operation -> {self._gateName}"


##################################################################################


class gateOpType(opType):
    """
    Store a gate name and its target's circuit index.

    Attributes:
        - _gateName (str): Name of the gate.
        - _target (int): Target qubit's index in the circuit.
    """

    def __init__(self, gateName, target):
        """Initialize the gate name and target index."""
        super().__init__(gateName)
        self._target = target
   

    def getTarget(self):
        """
        Return index of qubit we apply operation on
        """

        return self._target

    #returning string with basic information on the operation
    def __str__(self):
        """Return the target index and gate name as a readable string."""
        return f"index: {self._target} -> {self._gateName}"
#######################################################################################################

class controlledOpType(gateOpType):
    """
    Store a controlled gate and its circuit qubit indexes.

    Attributes:
        - _gateName (str): Name of the gate.
        - _target (int): Target qubit's index in the circuit.
        - _controllers (list[int]): Control qubits' circuit indexes.
    """

    def __init__(self, gateName, target, controllers):
        """Initialize the gate, target index, and control indexes."""
        super().__init__(gateName, target)
        self._controllers = controllers

    def getControllers(self):
        """Return the list of control qubit indexes."""
        return self._controllers

    #returning string with basic information on the operation
    def __str__(self):
        """Return the gate, target, and controls as a readable string."""
        return f"Controlled {self._gateName}  -->  Target: {self._target}, Controllers: {self._controllers}"



#######################################################################################################
class rotateOpType(gateOpType):
    """
    Store a rotation gate, its target index, and angle.

    Attributes:
        - _gateName (str): Name of the rotation gate.
        - _target (int): Target qubit's index in the circuit.
        - _angle: Rotation angle in radians.
    """

    def __init__(self, gateName, target, angle=0):
        """Initialize the rotation; the angle defaults to zero."""
        super().__init__(gateName, target)
        self._angle = angle

    def getAngle(self):
        """Return the rotation angle in radians."""
        return self._angle

   

    #returning string with basic information on the operation
    def __str__(self):
        """Return the gate, target, and angle as a readable string."""
        return f"index: {self._target} -> {self._gateName} :: angle: {self._angle}"



#######################################################################################################
class controlledRotateOpType(rotateOpType):
    """
    Store a controlled rotation with its target, controls, and angle.

    Attributes:
        - _gateName (str): Name of the rotation gate.
        - _target (int): Target qubit's index in the circuit.
        - _controllers (list[int]): Control qubits' circuit indexes.
        - _angle: Rotation angle in radians.
    """

    def __init__(self, gateName, target,controllers, angle=0):
        """Initialize the rotation; the angle defaults to zero."""
        super().__init__(gateName, target, angle)
        self._controllers = controllers

    def getControllers(self):
        """Return the list of control qubit indexes."""
        return self._controllers

   

    #returning string with basic information on the operation
    def __str__(self):
        """Return the gate, target, controls, and angle as a string."""
        return f"Controlled {self._gateName}  -->  Target: {self._target}, Controllers: {self._controllers}, angle: {self._angle}"

