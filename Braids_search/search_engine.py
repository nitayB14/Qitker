"""Preparation and evaluation of braid-search problems (no search algorithm).

Example: braid_searching(2, "X", target=1, controllers=(0,)) describes CNOT.
Logical bitstrings place q[0] on the left. Controls activate on bit value 1.
"""

import sys
from pathlib import Path

import numpy as np

# Allow running/importing this experiment outside the installed package.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from qitker.anyons.FusionSystem import FusionSystem
from qitker.QuantumMath.constant import math_constant


class braid_searching:
    """Compile physical generators once and evaluate arbitrary braid words.

    Supported scope is one to three logical four-anyon qubits. Evaluation
    preserves the entire physical space, including leakage. A nonidentity
    final permutation is reported, rather than silently repaired or rejected.
    """

    def __init__(self, qubits_num, gate, target, controllers=()):
        self.qubits_num = qubits_num
        self.gate = gate
        self.target = target
        self.controllers = controllers
        self._validate_configuration()

        self.logical_dimension = 2 ** self.qubits_num
        self.logical_labels = tuple(
            format(index, f"0{self.qubits_num}b")
            for index in range(self.logical_dimension)
        )
        self.target_matrix = self._build_target_matrix()
        self._prepare_physical_engine()

    def _validate_configuration(self):
        """Reject ambiguous types, unsupported gates and invalid qubit roles."""
        if isinstance(self.qubits_num, bool) or not isinstance(self.qubits_num, int):
            raise TypeError("qubits_num must be an integer.")
        if not 1 <= self.qubits_num <= 3:
            raise ValueError("This search engine supports one to three qubits.")
        if not isinstance(self.gate, str):
            raise TypeError("gate must be a string, for example 'H' or 'X'.")
        self.gate = self.gate.upper()
        if self.gate not in math_constant.GATE_MATRICES:
            raise ValueError("Supported base gates are I, H, X, Y, Z, S and T.")
        if not isinstance(self.controllers, (tuple, list)):
            raise TypeError("controllers must be a tuple or list of qubit indices.")
        self.controllers = tuple(self.controllers)
        for index in (self.target,) + self.controllers:
            if isinstance(index, bool) or not isinstance(index, int):
                raise TypeError("Qubit indices must be integers, not booleans.")
            if not 0 <= index < self.qubits_num:
                raise ValueError("Qubit index is outside the configured system.")
        if len(set(self.controllers)) != len(self.controllers):
            raise ValueError("Controllers must be unique.")
        if self.target in self.controllers:
            raise ValueError("The target cannot also be a controller.")

    def _build_target_matrix(self):
        """Embed the base gate into the logical register, conditioned on controls."""
        base = math_constant.GATE_MATRICES[self.gate]
        result = np.zeros(
            (self.logical_dimension, self.logical_dimension), dtype=complex
        )
        # Matrix columns correspond to input states; rows to output states.
        for column, label in enumerate(self.logical_labels):
            if not all(label[index] == "1" for index in self.controllers):
                result[column, column] = 1
                continue
            input_bit = int(label[self.target])
            for output_bit in (0, 1):
                output = list(label)
                output[self.target] = str(output_bit)
                row = int("".join(output), 2)
                result[row, column] = base[output_bit, input_bit]
        return result

    def _prepare_physical_engine(self):
        """Extract full-space sigma matrices from Qitker's F/R implementation.

        This is the expensive, one-time preparation. Both braid orientations
        exchange endpoint identities. Matrix coordinates follow positional
        fusion labels in the restored tree topology, as in Qitker's basis.
        """
        system = FusionSystem(self.qubits_num)
        self.physical_dimension = system.hilbertSpace.dimension
        self.initial_order = system.get_current_anyon_order()
        self.computational_indices = tuple(
            system.basis.logical_to_physical[label] for label in self.logical_labels
        )
        self.leakage_indices = tuple(system.basis.leakage_indices)
        self.initial_columns = np.zeros(
            (self.physical_dimension, self.logical_dimension), dtype=complex
        )
        self.initial_columns[
            list(self.computational_indices), np.arange(self.logical_dimension)
        ] = 1
        self.generators = {}
        snapshot = system._capture_state_snapshot()
        identity = np.eye(self.physical_dimension)
        for index in range(1, len(self.initial_order)):
            matrix = np.empty_like(identity, dtype=complex)
            for column in range(self.physical_dimension):
                # Restore the same topology and state before extracting each column.
                system._restore_state_snapshot(snapshot)
                # Snapshot restoration shares its history list; keep each probe isolated.
                system.operation_history = []
                system.hilbertSpace.state_vector = identity[:, column].astype(complex)
                system.sigma_global(index)
                matrix[:, column] = system.hilbertSpace.state_vector
            if not np.allclose(matrix.conj().T @ matrix, identity, atol=1e-10, rtol=0):
                raise RuntimeError(f"Compiled sigma {index} is not unitary.")
            matrix.setflags(write=False)
            inverse = matrix.conj().T.copy()
            inverse.setflags(write=False)
            self.generators[index] = matrix
            self.generators[-index] = inverse
        self.initial_columns.setflags(write=False)
        self.target_matrix.setflags(write=False)

    def sigma(self, index, physical_columns):
        """Return one braid applied to physical amplitudes, without mutating input."""
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("sigma index must be an integer.")
        if index not in self.generators:
            raise ValueError("sigma index is outside the configured system.")
        columns = np.asarray(physical_columns, dtype=complex)
        if columns.ndim not in (1, 2) or columns.shape[0] != self.physical_dimension:
            raise ValueError("Amplitudes must have physical_dimension rows.")
        if not np.all(np.isfinite(columns)):
            raise ValueError("Amplitudes must be finite.")
        return self.generators[index] @ columns

    def run_sequence(self, sequence):
        """Start from all logical inputs and return full amplitudes and final order."""
        sequence = tuple(sequence)
        physical = self.initial_columns.copy()
        order = list(self.initial_order)
        for index in sequence:
            physical = self.sigma(index, physical)
            left = abs(index) - 1
            order[left], order[left + 1] = order[left + 1], order[left]
        # Check the full input isometry, not just individually normalized columns.
        if not np.allclose(
            physical.conj().T @ physical,
            np.eye(self.logical_dimension), atol=1e-10, rtol=0,
        ):
            raise RuntimeError("Braid evolution did not preserve the input isometry.")
        return physical, tuple(order)

    def evaluate(self, sequence):
        """Return unconditioned target fidelity (percent) and leakage probabilities."""
        sequence = tuple(sequence)
        physical, final_order = self.run_sequence(sequence)
        logical = physical[list(self.computational_indices), :]
        leaked = physical[list(self.leakage_indices), :]
        # L^dagger L measures loss for arbitrary superpositions of logical inputs.
        # Its diagonal is basis-input leakage; its largest eigenvalue is the
        # actual worst-case leakage, which may exceed every diagonal entry.
        loss = leaked.conj().T @ leaked
        leakage_by_input = np.real(np.diag(loss))
        maximum_leakage = max(0.0, float(np.linalg.eigvalsh(loss)[-1]))
        d = self.logical_dimension
        overlap_squared = float(abs(np.trace(self.target_matrix.conj().T @ logical)) ** 2)
        survival_weight = float(np.vdot(logical, logical).real)
        return {
            "sequence": sequence,
            "logical_labels": self.logical_labels,
            "computational_matrix": logical,
            # No postselection or normalization of the computational block:
            # amplitudes lost to leakage lower both target-overlap metrics.
            # Fidelity is exposed as a percentage for user-facing search output.
            # Leakage remains a 0--1 probability.
            "process_fidelity": 100 * overlap_squared / (d * d),
            "average_gate_fidelity": 100 * (survival_weight + overlap_squared) / (d * (d + 1)),
            "leakage_by_input": dict(zip(self.logical_labels, map(float, leakage_by_input))),
            "average_leakage": float(np.trace(loss).real / d),
            "maximum_basis_leakage": float(np.max(leakage_by_input)),
            "maximum_leakage": maximum_leakage,
            "final_anyon_order": final_order,
            "order_restored": final_order == self.initial_order,
        }

    def verify_with_qitker(self, sequence):
        """Compare all physical amplitudes with independent F/R replay.

        Validates a candidate even when its final permutation is nonidentity;
        accepting that permutation as a logical gate is a separate policy.
        Raises on disagreement and returns the largest amplitude discrepancy.
        """
        sequence = tuple(sequence)
        fast, expected_order = self.run_sequence(sequence)
        maximum_error = 0.0
        for column, label in enumerate(self.logical_labels):
            system = FusionSystem(self.qubits_num)
            system.hilbertSpace.state_vector[:] = 0
            system.hilbertSpace.state_vector[system.basis.logical_to_physical[label]] = 1
            for index in sequence:
                system.sigma_global(index)
            system._validate_system_coherence()
            if system.get_current_anyon_order() != expected_order:
                raise RuntimeError("Fast and Qitker endpoint orders disagree.")
            if tuple(system.basis.logical_to_physical[x] for x in self.logical_labels) != self.computational_indices:
                raise RuntimeError("Final logical basis mapping changed unexpectedly.")
            actual = system.hilbertSpace.state_vector
            error = float(np.max(np.abs(actual - fast[:, column])))
            maximum_error = max(maximum_error, error)
            if not np.allclose(actual, fast[:, column], atol=1e-10, rtol=1e-10):
                raise RuntimeError(f"Physical replay disagrees for input {label}: {error}.")
        return maximum_error
