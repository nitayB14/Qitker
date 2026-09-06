from qitker.QuantumMath.constant import math_constant
import numpy as np

from qitker.anyons.FusionBasis import FusionBasis
from qitker.anyons.Anyon import Charge

fibonacciConst = math_constant()

class HilbertSpace:

    def __init__(self, basis: FusionBasis):

        self.basis = basis
        self.qubits_num = basis.qubits_num
        self.dimension = len(basis.states)

        initial_label = "0" * self.qubits_num
        initial_index = (self.basis.logical_to_physical[initial_label])

        self.state_vector = np.zeros(self.dimension, dtype=complex,)
        self.state_vector[initial_index] = 1



        self.local_braid_operators = [fibonacciConst.I.copy() for _ in range(self.qubits_num)]
        self.local_ideal_operators = [fibonacciConst.I.copy() for _ in range(self.qubits_num)]

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


    def state_vector_in_basis(self, new_basis: FusionBasis, state_vector: np.ndarray | None = None,) -> np.ndarray:
        """
        Return the current statevector reindexed into new_basis.

        This method does not modify the HilbertSpace.
        """

        source_state_vector = (self.state_vector if state_vector is None else state_vector)

        if not isinstance(source_state_vector, np.ndarray):
            raise TypeError("state_vector must be a NumPy array.")

        if source_state_vector.shape != (self.dimension,):
            raise ValueError(
                "state_vector shape does not match "
                "the current fusion basis."
            )

        reindex_map = self.basis.get_reindex_map(
            new_basis
        )

        new_state_vector = np.zeros(
            len(new_basis.states),
            dtype=complex,
        )

        for old_index, new_index in enumerate(reindex_map):
            new_state_vector[new_index] = (
                source_state_vector[old_index]
            )

        return new_state_vector

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
    
    def computational_probability(self) -> float:
        probabilities = self.probs()
        return float(probabilities[self.basis.computational_indices].sum())
    
    def leakage_probability(self) -> float:
        probabilities = self.probs()
        return float(probabilities[self.basis.leakage_indices].sum())
    
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
            raise TypeError(
                "shots must be an integer."
            )

        if shots < 1:
            raise ValueError(
                "shots must be at least 1."
            )

        results = {}

        for _ in range(shots):
            physical_index = self.measure_once()

            result = self._decode_measurement(
                physical_index
            )

            results[result] = (
                results.get(result, 0) + 1
            )

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
    
    def _decode_measurement(self,physical_index: int,) -> str:
        if physical_index in (self.basis.physical_to_logical):
            return self.basis.physical_to_logical[physical_index]

        return "LEAKAGE"
    def get_state_vector(self):
        #Returns the current quantum state.
        return self.state_vector

    def state_vector_after_r(self, parent_path: tuple, inverse: bool = False,) -> np.ndarray:
        """
        Return the statevector after applying an R-symbol
        at a sibling-parent fusion channel.

        This method does not modify the HilbertSpace.
        """

        if not isinstance(parent_path, tuple):
            raise TypeError(
                "parent_path must be a tuple."
            )

        if not isinstance(inverse, bool):
            raise TypeError(
                "inverse must be a boolean."
            )

        new_state_vector = np.zeros(
            self.dimension,
            dtype=complex,
        )

        for index, state in enumerate(self.basis.states):
            if parent_path not in state["labels"]:
                raise ValueError(
                    "parent_path is not an internal fusion node "
                    "in the current basis."
                )

            parent_charge = state["labels"][parent_path]

            if parent_charge is Charge.VACUUM:
                phase = fibonacciConst.R_VACUUM
            elif parent_charge is Charge.TAU:
                phase = fibonacciConst.R_TAU
            else:
                raise ValueError(
                    "Unsupported fusion channel for R-move."
                )

            if inverse:
                phase = np.conjugate(phase)

            new_state_vector[index] = (
                phase * self.state_vector[index]
            )

        return new_state_vector

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
