


def export_to(name, circuit):
    """
    Refering to target function
        - Qiskit
        -
        -

    Args:
        - circuit (circuit):
            contains information about the circuit
        - name (string):
            name of platform to convert the circuit
    Returns:
        - qc (circuit):
            converted circuit
    """

    if (name == "qiskit"):
        qc = exportToQiskit(circuit)
    elif (name == "cirq"):
        print("Comming Soon...")#[error]
    else:
        pass#[error]


    return qc






def exportToQiskit(AnyonCircuit):
    """
    Running all over the circuit and convert it to qiskit

    Args:
        - AnyonCircuit (circuit):
            contains information about the circuit
            
    Returns:
        - qc (qiskit circuit):
            converted circuit to qiskit
    """

    from qiskit import QuantumCircuit    

    qc = QuantumCircuit(AnyonCircuit.getQubitsNumber(), AnyonCircuit.getQubitsNumberToMeasure()) #creating qiskit circuit
    vector = AnyonCircuit.getOperationVector()
        
    #loop over operation vector
    for op in vector:
        if(op.getName() == "H"):
            qc.h(op.getTarget())
        elif(op.getName() == "X"):
            qc.x(op.getTarget())
        elif(op.getName() == "Y"):
            qc.y(op.getTarget())
        elif(op.getName() == "Z"):
            qc.z(op.getTarget())
        elif(op.getName() == "S"):
            qc.s(op.getTarget())
        elif(op.getName() == "T"):
            qc.t(op.getTarget())
        else:
            pass

    return qc