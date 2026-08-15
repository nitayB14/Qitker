



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




class rotateOpType(gateOpType):
    """
    The class save index of qubit and gate name
    
    Attributes:
        - gateName: string
            Name of quantum gate
        - target: int
            index of qubit
    """

    def __init__(self, gateName, target, angle=0):
        super().__init__(gateName, target)
        self._angle = angle

    def getAngle(self):
        return self._angle

   

    #returning string with basic information on the operation
    def __str__(self):
        return f"index: {self._target} -> {self._gateName} :: angle: {self._angle}"