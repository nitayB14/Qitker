from QuantumMath.constant import math_constant
import numpy as np

fibonacciConst = math_constant()


class hilbertSpace():

    
    #########################################################
        #R on 1,2
    def apply_R12(self, state):
        return fibonacciConst.R12 @ state

    def apply_reverseR12(self,state):
        return fibonacciConst.R12_inv @ state

    def apply_R34(self, state):
        return fibonacciConst.R34 @ state

    def apply_reverseR34(self, state):
        return fibonacciConst.R34_inv @ state

    def apply_R23(self, state):
        return fibonacciConst.R23 @ state

    def apply_reverseR23(self, state):
        return fibonacciConst.R23_inv @ state


    #########################################################
    def probs(self, state):
        return np.abs(state) ** 2
    #########################################################

    

    def sigma(self, num, state):
        
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
        p = self.probs(state)
        return np.random.choice([0, 1], p=p)


    def run_measurements(self,state, shots=1000):
        results = {0: 0, 1: 0}

        for _ in range(shots):
            outcome = self.measure_once(state)
            results[outcome] += 1

        return results 

    
    def gate_fidelity(self, U_target, U):
        d = U.shape[0]        
        return abs(np.trace(U_target.conj().T @ U)) / d  
    
    """
    def gate_fidelity(self, U_target, U_actual):
        d = U_target.shape[0]
        overlap = np.trace(U_target.conj().T @ U_actual)
        fidelity = abs(overlap) ** 2 / (d ** 2)
        return float(np.real(fidelity))
    """

    def getMatrix(self, op):
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



    """
    def gate_error_percent(self, U_target, U):
        fidelity = self.gate_fidelity(U_target, U)
        return (1 - fidelity) * 100
    """