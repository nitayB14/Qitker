from compiler import circuit


"""
class operation - responsible on the logic gates
                  adding operation ot circuit

"""


class opType:
    def __init__(self, gateName, target):
        self.gateName = gateName
        self.target = target
    
    def getName(self):
        return self.gateName
    
    def getTarget(self):
        return self.target

    def __str__(self):
        return f"index: {self.target} -> {self.gateName}"


class operation:
    
    
    def apply_H(self, qubit, circuit):
        op = opType(gateName="H",
                    target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    #############################################################################################################################################################################################

    def apply_X(self, qubit, circuit):
        op = opType(gateName="X",
                    target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    #############################################################################################################################################################################################

    def apply_Y(self, qubit, circuit):
        op = opType(gateName="Y",
                    target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    #############################################################################################################################################################################################

    def apply_Z(self, qubit, circuit):
        op = opType(gateName="Z",
                    target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    #############################################################################################################################################################################################

    def apply_S(self, qubit, circuit):
        op = opType(gateName="S",
                    target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    #############################################################################################################################################################################################

    def apply_T(self, qubit, circuit):
        op = opType(gateName="T",
                    target=circuit.getIndex(qubit))
        circuit.addOperation(op)
    #############################################################################################################################################################################################



