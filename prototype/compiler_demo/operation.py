import circuit


"""
class operation - responsible on the logic gates
                  adding operation ot circuit

"""
class operation:
    
    def __init__(self):
        pass

    
    def applyHadamard(self, qubit, circuit):
        circuit.addOperationToVercot(f"Hadamard on qubit: {circuit.getIndex(qubit)}")
    #############################################################################################################################################################################################    

    def applyNOT(self, qubit, circuit):
        circuit.addOperationToVercot(f"NOT on qubit: {circuit.getIndex(qubit)}")
    
    def applyCNOT(self, control, target, circuit):
        circuit.addOperationToVercot(f"CNOT on qubits; control: {circuit.getIndex(control)}, target: {circuit.getIndex(target)}")

    def applyCCNOT(self, control1, control2, target, circuit):
        circuit.addOperationToVercot(f"CCNOT on qubits; control: {circuit.getIndex(control1)}, control: {circuit.getIndex(control2)}, target: {circuit.getIndex(target)}")
    #############################################################################################################################################################################################
    
    def applyY(self, qubit, circuit):
        circuit.addOperationToVercot(f"Y gate on qubit: {circuit.getIndex(qubit)}")
    
    def applyCY(self, control, target, circuit):
        circuit.addOperationToVercot(f"CY gate on qubits; control: {circuit.getIndex(control)}, target: {circuit.getIndex(target)}")

    def applyCCY(self, control1, control2, target, circuit):
        circuit.addOperationToVercot(f"CCY gate on qubits; control: {circuit.getIndex(control1)}, control: {circuit.getIndex(control2)}, target: {circuit.getIndex(target)}")
    #############################################################################################################################################################################################
    
    def applyZ(self, qubit, circuit):
        circuit.addOperationToVercot(f"Z gate on qubit: {circuit.getIndex(qubit)}")
    
    def applyCZ(self, control, target, circuit):
        circuit.addOperationToVercot(f"CZ gate on qubits; control: {circuit.getIndex(control)}, target: {circuit.getIndex(target)}")

    def applyCCZ(self, control1, control2, target, circuit):
        circuit.addOperationToVercot(f"CCZ gate on qubits; control: {circuit.getIndex(control1)}, control: {circuit.getIndex(control2)}, target: {circuit.getIndex(target)}")
    #############################################################################################################################################################################################
    
    def applyS(self, qubit, circuit):
        circuit.addOperationToVercot(f"S gate on qubit: {circuit.getIndex(qubit)}")
    
    def applyCS(self, control, target, circuit):
        circuit.addOperationToVercot(f"CS gate on qubits; control: {circuit.getIndex(control)}, target: {circuit.getIndex(target)}")

    def applyCCS(self, control1, control2, target, circuit):
        circuit.addOperationToVercot(f"CCS gate on qubits; control: {circuit.getIndex(control1)}, control: {circuit.getIndex(control2)}, target: {circuit.getIndex(target)}")
    #############################################################################################################################################################################################
    
    def applyT(self, qubit, circuit):
        circuit.addOperationToVercot(f"T gate on qubit: {circuit.getIndex(qubit)}")
    
    def applyCT(self, control, target, circuit):
        circuit.addOperationToVercot(f"CT gate on qubits; control: {circuit.getIndex(control)}, target: {circuit.getIndex(target)}")

    def applyCCT(self, control1, control2, target, circuit):
        circuit.addOperationToVercot(f"CCT gate on qubits; control: {circuit.getIndex(control1)}, control: {circuit.getIndex(control2)}, target: {circuit.getIndex(target)}")
    #############################################################################################################################################################################################
    
