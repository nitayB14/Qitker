import json
import numpy as np

from qitker.parser.sequenceOperation import sequenceOperation
from qitker.anyons.FusionSystem import FusionSystem
from qitker.parser import routing


seqOp = sequenceOperation()

class execution:
    """
    Integration layer between compiler <-> anyons
    
    Attributes:
        - braidsNumber : int
            number of braids in circuit      
        - circuit : circuit
            our circuit
        - fusionSystem : FusionSystem
            represent the physic of anyons
    """


    # initialize execution class
    def __init__(self, circuit):
       
        self._braidsNumber = 0
        
        self._circuit = circuit
        self._fusionSystem = FusionSystem(self._circuit.getQubitsNumber())



  
    def convert(self):
        """
        Convert quantum operation(gate) to braids 
        Call fidelity function

        Args:
            - circuit (circuit):
                circuit of user

        Returns:
            - None
        """
        
        op = self._circuit.getOperationVector()

        for i in op:
            self._fusionSystem.addOperationToIdealMatrix(i)
            self.applyGate(i) #apply each gate appear in operation vector


    
    def applyGate(self, opType):
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
        """
        Measures the quantum state multiple times.

        Args:
            - shots (int): 
                Number of measurement repetitions.

        Returns:
            (dict[int, int]): Measurement counts for each basis state.
        """

        return self._fusionSystem.hilbertSpace.run_measurements(shots=shots)
    
    def getLeakageProbability(self):
        probability = (
            self._fusionSystem
            .hilbertSpace
            .leakage_probability()
        )

        return probability




    def build_sequence(self, gate_key: str,) -> dict:
        """
        Search for or construct a physical braid sequence for a gate
        that is not present in the saved sequence database.
        """

        raise NotImplementedError(
            f"Automatic braid synthesis for {gate_key} "
            "is not implemented yet."
        )
            
    #returning string with basic information on the execution
    def __repr__(self):
        output = "Execution:\nNumber of braids: " + str(self._braidsNumber)
        
        return output



