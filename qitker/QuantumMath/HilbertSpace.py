from qitker.QuantumMath.constant import math_constant
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

        self.local_braid_operators = [fibonacciConst.I.copy() for _ in range(qubits_num)]
        self.local_ideal_operators = [fibonacciConst.I.copy() for _ in range(qubits_num)]

        self.ideal_operations = []







    #########################################################

    def _get_sigma_matrix(self, index: int) -> np.ndarray:

        if index not in fibonacciConst.SIGMA_MATRICES:
            raise ValueError(
                "sigma index must be one of: "
                "1, -1, 2, -2, 3, -3."
            )

        return fibonacciConst.SIGMA_MATRICES[index]
    #########################################################
    def _apply_single_qubit_operator(self,operator: np.ndarray,qubit_id: int) -> None:
        if not isinstance(operator, np.ndarray):
            raise TypeError("operator must be a NumPy array.")

        if operator.shape != (2, 2):
            raise ValueError("operator must have shape (2, 2).")

        if not isinstance(qubit_id, int):
            raise TypeError("qubit_id must be an integer.")

        if qubit_id < 0 or qubit_id >= self.qubits_num:
            raise ValueError(f"Qubit {qubit_id} does not exist.")

        stride = 2 ** (self.qubits_num - qubit_id - 1)
        blocks = self.state_vector.reshape(-1, 2, stride)

        zero_amplitudes = blocks[:, 0, :].copy()
        one_amplitudes = blocks[:, 1, :].copy()

        blocks[:, 0, :] = (
            operator[0, 0] * zero_amplitudes
            + operator[0, 1] * one_amplitudes
        )
        blocks[:, 1, :] = (
            operator[1, 0] * zero_amplitudes
            + operator[1, 1] * one_amplitudes
        )

        self.state_vector = blocks.reshape(self.dimension)




    def sigma(self, qubit_id: int, index: int):
        if not isinstance(index, int):
            raise TypeError("sigma index must be an integer.")

        local_operator = self._get_sigma_matrix(index)

        self._apply_single_qubit_operator(operator=local_operator, qubit_id=qubit_id)

        self.local_braid_operators[qubit_id] = (local_operator @ self.local_braid_operators[qubit_id])

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

    
    def add_ideal_operation(self, gate_name: str, qubit_id: int) -> None:

        if not isinstance(qubit_id, int):
            raise TypeError("qubit_id must be an integer.")

        if qubit_id < 0 or qubit_id >= self.qubits_num:
            raise ValueError(
                f"Qubit {qubit_id} does not exist."
            )

        local_gate = self._get_gate_matrix(gate_name)
        self.local_ideal_operators[qubit_id] = (local_gate @ self.local_ideal_operators[qubit_id])

        self.ideal_operations.append({
            "gate": gate_name,
            "target": qubit_id
        })

    

    def _get_gate_matrix(self, gate_name: str) -> np.ndarray:
        if not isinstance(gate_name, str):
            raise TypeError("gate_name must be a string.")



        gate_name = gate_name.upper()

        if gate_name not in fibonacciConst.GATE_MATRICES:
            raise ValueError(
                f"Unsupported gate: {gate_name}"
            )

        return fibonacciConst.GATE_MATRICES[gate_name]


    def gate_fidelity(self) -> float:
        fidelity = 1.0

        for ideal_operator, braid_operator in zip(
            self.local_ideal_operators,
            self.local_braid_operators
        ):
            local_overlap = abs(
                np.trace(
                    ideal_operator.conj().T
                    @ braid_operator
                )
            ) / 2

            fidelity *= local_overlap

        return float(fidelity)
    
    
    def get_state_vector(self):
        #Returns the current quantum state.
        return self.state_vector


    def __str__(self):
        return (
            f"HilbertSpace(\n"
            f"    qubits = {self.qubits_num},\n"
            f"    dimension = {self.dimension},\n"
            f"    state_vector_shape = {self.state_vector.shape},\n"
            f")"
        )


    def __repr__(self):
        return self.__str__()

