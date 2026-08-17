"""Verify controlled-Y and controlled-Z operations.

Superposition on both qubits makes amplitudes and relative phases observable,
which is necessary because basis-state probabilities cannot fully test Y/Z.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit


def test_controlled_pauli_gates():
    """Compare descriptive and short aliases with Qiskit's CY and CZ."""
    cases = (
        ("flipPhaseIf", "cy"),
        ("cy", "cy"),
        ("phaseIf", "cz"),
        ("cz", "cz"),
    )

    for qitker_method, qiskit_gate in cases:
        circ = circuit()
        control = qubit(circ)
        target = qubit(circ)
        control.H()
        target.H()
        getattr(target, qitker_method)(control)

        expected = QuantumCircuit(2)
        expected.h(0)
        expected.h(1)
        getattr(expected, qiskit_gate)(0, 1)

        assert_same_state(circ, expected)


if __name__ == "__main__":
    test_controlled_pauli_gates()
    print("T17_controlled_pauli_gates: PASS")
