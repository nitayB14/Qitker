"""Export recorded circuit operations to Qiskit."""



def export_to(name, circuit):
    """
    Export a circuit to the requested platform.

    Only the exact name "qiskit" is supported.

    Args:
        name (str): Export target.
        circuit (circuit): Circuit to export.

    Returns:
        qiskit.QuantumCircuit: A new exported circuit.

    Raises:
        TypeError: If name is not a string.
        ValueError: If name is not ``"qiskit"``.
    """

    if not isinstance(name, str):
        raise TypeError("export target must be a string")
    if name != "qiskit":
        raise ValueError(f"Unsupported export target: {name!r}. Supported target: 'qiskit'.")

    return exportToQiskit(circuit)






def exportToQiskit(AnyonCircuit):
    """
    Convert the circuit's recorded operations to a new Qiskit circuit.

    The exported circuit has one qubit per Qitker qubit and one classical
    bit per qubit marked for measurement. No measurement instructions
    are added.

    Args:
        AnyonCircuit (circuit): Circuit to export.

    Returns:
        qiskit.QuantumCircuit: The exported circuit.
    """

    from qiskit import QuantumCircuit    
    from qiskit.circuit.library import (
        YGate,
        ZGate,
        SGate,
        TGate,
        RXGate,
        RYGate,
        RZGate,
    )

    qc = QuantumCircuit(AnyonCircuit.getQubitsNumber(), AnyonCircuit.getQubitsNumberToMeasure()) #creating qiskit circuit
    vector = AnyonCircuit.getOperationVector()
    
    controlled_gates = {
    "Y": YGate,
    "Z": ZGate,
    "S": SGate,
    "T": TGate
}

    controlled_rotation_gates = {
    "RX": RXGate,
    "RY": RYGate,
    "RZ": RZGate
}


    #loop over operation vector
    for op in vector:

        if hasattr(op, "getControllers"):
            controls = op.getControllers()
            target = op.getTarget()
            name = op.getName()

            if name == "X":
                if len(controls) == 1:
                    qc.cx(controls[0], target)
                else:
                    qc.mcx(controls, target)

            elif name in controlled_rotation_gates:
                gate = controlled_rotation_gates[name](op.getAngle())

                qc.append(
                    gate.control(len(controls)),
                    controls + [target]
                )

            elif name in controlled_gates:
                gate = controlled_gates[name]()

                if len(controls) == 1:
                    qc.append(
                        gate.control(1),
                        controls + [target]
                    )
                else:
                    qc.append(
                        gate.control(len(controls)),
                        controls + [target]
                    )
        else:  
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
            elif(op.getName() == "RX"):
                qc.rx(op.getAngle(), op.getTarget())
            elif(op.getName() == "RY"):
                qc.ry(op.getAngle(), op.getTarget())
            elif(op.getName() == "RZ"):
                qc.rz(op.getAngle(), op.getTarget())
            elif(op.getName() == "barrier"):
                qc.barrier()

    return qc
