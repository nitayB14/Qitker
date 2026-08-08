from QuantumMath.constant import math_constant
import numpy as np

fibonacciConst = math_constant()

class HilbertSpace:

    def __init__(self, qubits_num: int):

        if not isinstance(qubits_num, int):
            raise TypeError("qubits_num must be an integer.")

        if qubits_num < 1:
            raise ValueError("qubits_num must be at least 1.")

        self.qubits_num = qubits_num
        self.dimension = 2 ** qubits_num

        # |00...0⟩
        self.state_vector = np.zeros(self.dimension, dtype=complex)
        self.state_vector[0] = 1

        # Accumulated unitary
        self.unitary = np.eye(self.dimension, dtype=complex)

        # Ideal gate/unitary (filled later by the compiler/execution)
        self.ideal_unitary = np.eye(self.dimension,dtype=complex)
        self.ideal_operations = []


    #########################################################

    def _get_sigma_matrix(self, index: int) -> np.ndarray:

        sigma_matrices = {
            1: fibonacciConst.R12,
            -1: fibonacciConst.R12_inv,

            2: fibonacciConst.R23,
            -2: fibonacciConst.R23_inv,

            3: fibonacciConst.R34,
            -3: fibonacciConst.R34_inv,
        }

        
        if index not in sigma_matrices:
            raise ValueError(
                "sigma index must be one of: "
                "1, -1, 2, -2, 3, -3."
            )

        return sigma_matrices[index]

    def _expand_single_qubit_operator(self,operator: np.ndarray,qubit_id: int) -> np.ndarray:

        if not isinstance(qubit_id, int):
            raise TypeError("qubit_id must be an integer.")

        if qubit_id < 0 or qubit_id >= self.qubits_num:
            raise ValueError(
                f"Qubit {qubit_id} does not exist."
            )

        global_operator = np.array([[1]], dtype=complex)

        for current_qubit in range(self.qubits_num):

            current_operator = (
                operator
                if current_qubit == qubit_id
                else fibonacciConst.I
            )

            global_operator = np.kron(
                global_operator,
                current_operator
            )

        return global_operator

    def sigma(self, qubit_id: int, index: int):
        if not isinstance(index, int):
            raise TypeError("sigma index must be an integer.")

        local_operator = self._get_sigma_matrix(index)

        global_operator = self._expand_single_qubit_operator(
            operator=local_operator,
            qubit_id=qubit_id
        )

        self.state_vector = (global_operator @ self.state_vector)

        if self.unitary is not None:
            self.unitary = (global_operator @ self.unitary)


    def probs(self):
        """
        Computes the measurement probabilities
        of the current quantum state.
        """

        probabilities = np.abs(self.state_vector) ** 2

        return probabilities / probabilities.sum()
    


    def measure_once(self):
        """
        Measures the current quantum state once.

        Returns:
            int: Measured basis-state index.
        """

        probabilities = self.probs()

        return np.random.choice(
            self.dimension,
            p=probabilities
        )


    def run_measurements(self, shots):

        if not isinstance(shots, int):
            raise TypeError("shots must be an integer.")

        if shots < 1:
            raise ValueError("shots must be at least 1.")

        results = {}

        for _ in range(shots):
            outcome = self.measure_once()

            bitstring = format(
                outcome,
                f"0{self.qubits_num}b"
            )

            results[bitstring] = results.get(bitstring, 0) + 1

        return results


    def add_ideal_operation(self, gate_name: str, qubit_id: int):
        local_gate = self._get_gate_matrix(gate_name)

        global_gate = self._expand_single_qubit_operator(
            operator=local_gate,
            qubit_id=qubit_id
        )

        self.ideal_operations.append({
            "gate": gate_name,
            "target": qubit_id
        })

        self.ideal_unitary = (
            global_gate @ self.ideal_unitary
        )


    def _get_gate_matrix(self, gate_name: str) -> np.ndarray:
        if not isinstance(gate_name, str):
            raise TypeError("gate_name must be a string.")

        gate_matrices = {
            "I": fibonacciConst.I,
            "H": fibonacciConst.H,
            "X": fibonacciConst.X,
            "Y": fibonacciConst.Y,
            "Z": fibonacciConst.Z,
            "S": fibonacciConst.S,
            "T": fibonacciConst.T,
        }

        gate_name = gate_name.upper()

        if gate_name not in gate_matrices:
            raise ValueError(
                f"Unsupported gate: {gate_name}"
            )

        return gate_matrices[gate_name]


    def gate_fidelity(self):
        """
        Computes the fidelity between the current implemented
        unitary and the ideal unitary.
        """

        if self.ideal_unitary is None:
            raise ValueError(
                "ideal_unitary has not been initialized."
            )

        d = self.unitary.shape[0]

        return abs(
            np.trace(
                self.ideal_unitary.conj().T @ self.unitary
            )
        ) / d
    
    
    def get_state_vector(self):
        #Returns the current quantum state.
        return self.state_vector

    def get_unitary(self):
        #Returns the braid unitary.
        return self.unitary

    def get_ideal_unitary(self):
        #Returns the target unitary corresponding to the logical circuit.
        return self.ideal_unitary

    def __str__(self):
        return (
            f"HilbertSpace(\n"
            f"    qubits = {self.qubits_num},\n"
            f"    dimension = {self.dimension},\n"
            f"    state_vector_shape = {self.state_vector.shape},\n"
            f"    unitary_shape = {self.unitary.shape},\n"
            f"    ideal_unitary = "
            f"{None if self.ideal_unitary is None else self.ideal_unitary.shape}\n"
            f")"
        )


    def __repr__(self):
        return self.__str__()



   