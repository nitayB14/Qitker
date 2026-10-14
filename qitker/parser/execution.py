import json
import numpy as np

from qitker.parser.sequenceOperation import sequenceOperation
from qitker.anyons.FusionSystem import FusionSystem
from qitker.parser import routing


seqOp = sequenceOperation()

class execution:
    """Connect a circuit's recorded operations to the anyonic backend.

    Supported gates are converted to braid sequences and applied to a
    FusionSystem when convert() is called.

    Attributes:
        _circuit: The circuit whose operations will be executed.
        _fusionSystem: The anyonic system used for this execution.
        _braidsNumber: Number of braids applied, including routing braids.
    """

    # initialize execution class
    def __init__(self, circuit):
        """Prepare a fresh anyonic system for the given circuit.

        Creates a FusionSystem for the circuit's qubits and sets the
        braid count to zero. No gates are applied until convert() is called.

        Args:
            circuit: The circuit to execute.
        """

        self._braidsNumber = 0
        
        self._circuit = circuit
        self._fusionSystem = FusionSystem(self._circuit.getQubitsNumber())



  
    def convert(self):
        """Apply the circuit's recorded gates to the anyonic system.

        Processes operations in order and skips barriers. For each gate,
        updates the ideal logical state and then applies its physical
        braid sequence through applyGate().

        Raises:
            NotImplementedError: If a gate has more than two controls,
                or a required braid sequence has not been implemented.
        """
        
        op = self._circuit.getOperationVector()

        for operation in op:
            if operation.getName() == "barrier":
                continue

            controllers = (
                tuple(operation.getControllers())
                if hasattr(operation, "getControllers")
                else ()
            )

            if len(controllers) > 2:
                gate_name = (
                    ("C" * len(controllers))
                    + operation.getName().upper()
                )

                raise NotImplementedError(
                    f"{gate_name} exceeds Qitker V1's 3-qubit gate limit. "
                    "Export the circuit to use another backend."
                )

            self._fusionSystem.addOperationToIdealMatrix(operation)
            self.applyGate(operation)


    
    def applyGate(self, opType):
        """Apply one gate using a stored braid sequence.

        An uncontrolled gate's sequence is shifted to its target qubit.
        For a controlled gate, the participating qubits are routed into
        the order expected by the sequence and routed back afterward.

        Args:
            opType: Gate record containing a name, target, and optional controls.

        Raises:
            NotImplementedError: If no stored sequence exists for the gate;
                automatic sequence construction is not implemented.
        """

        name = opType.getName().upper()
        target = opType.getTarget()

        controllers = (
            tuple(opType.getControllers())
            if hasattr(opType, "getControllers")
            else ()
        )

        gate_key = ("C" * len(controllers)) + name

        if gate_key in seqOp.sequences:
            gate_sequence = seqOp.getSeq(gate_key)
        else:
            record = self.build_sequence(gate_key)
            gate_sequence = record["sequence"]

        qubits_num = self._fusionSystem.qubits_num

        if not controllers:
            execution_sequence = routing.shift_sequence(
                sequence=gate_sequence,
                start_slot=target,
                qubits_num=qubits_num,
            )

        else:
            required_order = routing.get_required_order(
                target=target,
                controllers=controllers,
            )

            route_sequence = routing.get_routing_sequence(
                required_order=required_order,
                qubits_num=qubits_num,
            )

            physical_gate_sequence = routing.shift_sequence(
                sequence=gate_sequence,
                start_slot=0,
                qubits_num=qubits_num,
            )

            unroute_sequence = routing.invert_sequence(
                route_sequence
            )

            execution_sequence = (
                route_sequence
                + physical_gate_sequence
                + unroute_sequence
            )

        self.applySequence(execution_sequence)
        


            
    def applySequence(self, seq):
        """
        Apply sigma on each index of sequence
        """
        for index in seq:
            self._fusionSystem.sigma_global(index)
            self._braidsNumber += 1




            
    def getFidelity(self):
        """
        Return the fidelity between the ideal logical
        output state and the actual physical output state.

        Leakage is included in the fidelity because the
        ideal state has zero amplitude in leakage states.
        """

        fidelity = (
            self._fusionSystem
            .hilbertSpace
            .state_fidelity()
        )

        return f"{fidelity * 100:.6f}%"



    def measure(self, shots):
        """Sample the current state and count the decoded outcomes.

        Args:
            shots (int): Number of samples; must be at least 1.

        Returns:
            dict[str, int]: Counts by logical bitstring, with a "LEAKAGE"
            entry if leakage was sampled.
        """

        return self._fusionSystem.hilbertSpace.run_measurements(shots=shots)
    

    def getLeakageProbability(self):
        """Return the probability of leakage from the computational subspace.

        Returns:
            float: Total probability in physical leakage states, from 0 to 1.

        Raises:
            RuntimeError: If the current fusion basis cannot classify
                computational and leakage states.
        """

        probability = (
            self._fusionSystem
            .hilbertSpace
            .leakage_probability()
        )

        return probability




    def build_sequence(self, gate_key: str,) -> dict:
        """Reject automatic braid synthesis for a gate without a stored sequence.

        Args:
            gate_key: Key identifying the gate, such as "CX".

        Raises:
            NotImplementedError: Always; automatic synthesis is not implemented.
        """

        raise NotImplementedError(
            f"Automatic braid synthesis for {gate_key} "
            "is not implemented yet."
        )
            
    #returning string with basic information on the execution
    def __repr__(self):
        output = "Execution:\nNumber of braids: " + str(self._braidsNumber)
        
        return output



