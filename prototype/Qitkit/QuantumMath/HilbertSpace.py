from QuantumMath.constant import math_constant
import numpy as np

fibonacciConst = math_constant()


class hilbertSpace():
    """
    Represents the hilbert space
    Responsible to apply the mathematical operations and measurments
    
    Attributes:
        - None
    """
    
    #########################################################
    """
    Apply matrix multiplication

    Args:
        - state : (np.ndarray (2x2, complex))

    Returns:
        - np.ndarray (2x2, complex)
    """
    #Sigma(1)
    def apply_R12(self, state):
        return fibonacciConst.R12 @ state

    #Sigma(-1)
    def apply_reverseR12(self,state):
        return fibonacciConst.R12_inv @ state

    #Sigma(2)
    def apply_R34(self, state):
        return fibonacciConst.R34 @ state

    #Sigma(-2)
    def apply_reverseR34(self, state):
        return fibonacciConst.R34_inv @ state

    #Sigma(3)
    def apply_R23(self, state):
        return fibonacciConst.R23 @ state

    #Sigma(-3)
    def apply_reverseR23(self, state):
        return fibonacciConst.R23_inv @ state


    #########################################################
    def probs(self, state):
        """
        Computes the measurement probabilities of a quantum state.

        Parameters:
            state (np.ndarray): Quantum state vector.

        Returns:
            np.ndarray: Probability of measuring each basis state.
        """

        return np.abs(state) ** 2
    #########################################################

    

    def sigma(self, num, state):
        """
        Applies the requested braid operation (σ₁, σ₂, σ₃ or their inverses)
        to the given quantum state.

        Parameters:
            num (int): Braid index.
            state (np.ndarray): Quantum state vector.

        Returns:
            np.ndarray: Updated quantum state.
        """

        if num == 1:
            state = self.apply_R12(state)
        elif num == 2:
            state = self.apply_R23(state)
        elif num == 3:
            state = self.apply_R34(state)
        elif num == -1:
            state = self.apply_reverseR12(state)
        elif num == -2:
            state = self.apply_reverseR23(state)
        elif num == -3:
            state = self.apply_reverseR34(state)
        else:
            raise ValueError("bad input")
        return state



    def measure_once(self, state):
        """
        Performs a single measurement of the quantum state.

        The measurement outcome is randomly sampled according to the
        state's probability distribution (Born rule).

        Parameters:
            state (np.ndarray): Quantum state vector.

        Returns:
            int: Measured basis state (0 or 1).
        """

        p = self.probs(state)
        return np.random.choice([0, 1], p=p)


    def run_measurements(self,state, shots=1000):
        """
        Repeatedly measures the quantum state and collects the results.

        Parameters:
            state (np.ndarray): Quantum state vector.
            shots (int, optional): Number of measurement repetitions.
                                   Default is 1000.

        Returns:
            dict[int, int]: Measurement counts for each basis state.
                            Example: {0: 487, 1: 513}
        """
        
        results = {0: 0, 1: 0}

        for i in range(shots):
            outcome = self.measure_once(state)
            results[outcome] += 1

        return results 

    
    def gate_fidelity(self, U_target, U):
        """
        Computes the fidelity between two quantum gate matrices.

        Fidelity measures how closely the implemented gate matches the
        target gate. A value of 1.0 indicates identical operations
        (up to a global phase).

        Parameters:
            U_target (np.ndarray): Reference quantum gate matrix.
            U (np.ndarray): Implemented quantum gate matrix.

        Returns:
            float: Gate fidelity in the range [0, 1].
        """
        d = U.shape[0]        
        return abs(np.trace(U_target.conj().T @ U)) / d  
    

    def getMatrix(self, op):
        """
        Returns the reference matrix for a given quantum gate.

        Parameters:
            op (str): Gate name ("H", "X", "Y", "Z", "S", or "T").

        Returns:
            np.ndarray: Corresponding 2×2 quantum gate matrix.
        """
        if op == "H":
            return fibonacciConst.H
        elif op == "X":
            return fibonacciConst.X
        elif op == "Y":
            return fibonacciConst.Y
        elif op == "Z":
            return fibonacciConst.Z
        elif op == "S":
            return fibonacciConst.S
        elif op == "T":
            return fibonacciConst.T


    #print(f"U target:\n{U_target}")

    """
    def gate_error_percent(self, U_target, U):
        fidelity = self.gate_fidelity(U_target, U)
        return (1 - fidelity) * 100
    
    def gate_fidelity(self, U_target, U_actual):
        d = U_target.shape[0]
        overlap = np.trace(U_target.conj().T @ U_actual)
        fidelity = abs(overlap) ** 2 / (d ** 2)
        return float(np.real(fidelity))
    """
