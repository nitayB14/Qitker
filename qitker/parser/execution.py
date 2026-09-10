import json
import numpy as np

from qitker.parser.sequenceOperation import sequenceOperation
from qitker.anyons.FusionSystem import FusionSystem

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
        """
        Create new operation sequence and add to the logical qubit
    
        Args:
            - opType (opType):
                operation obj

        Returns:
            - None
        """
        
        name = opType.getName()
        target = opType.getTarget()

        seq = seqOp.getSeq(name)
        
        self.applySequence(target, seq)
        


            
    def applySequence(self, qubitTarget, seq):
        """
        Apply sequence of sigma(x) on the anyons     
        
        Args:
            - qubitTarget (int):
                id of logical qubit
            - seq (list):
                sigma operation (1, -1, 2, -2, 3, -3...)

        Returns:
            - None
        """
        
        for i in seq:
            self._braidsNumber += 1
            self._fusionSystem.sigma(qubit_id=qubitTarget, index=i)




            
    def getFidelity(self):
        """
        Return Fidelity (how close our matrix to idial matrix)

        Args:
            - None

        Returns:
            - (float) : fidelity
        """
        return f"{self._fusionSystem.hilbertSpace.gate_fidelity() * 100:.4f}%"



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
            
    #returning string with basic information on the execution
    def __repr__(self):
        output = "Execution:\nNumber of braids: " + str(self._braidsNumber)
        
        return output



