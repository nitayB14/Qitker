"""Verify a quantum equality condition between two individual qubits.

Qitker computes XOR into the reference, controls on XOR=0, and uncomputes it.
The full unitary proves the comparison works coherently for superpositions.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_unitary
from qitker import circuit, qubit


def test_qubit_equality_condition():
    """Compare Qitker equality with an explicit Qiskit compute/uncompute circuit."""
    circ = circuit()
    left = qubit(circ)
    right = qubit(circ)
    target = qubit(circ)
    target.flipIf(left, where=right)

    expected = QuantumCircuit(3)
    expected.cx(0, 1)  # Compute left XOR right into the reference qubit.
    expected.x(1)      # Equality corresponds to the computed XOR being zero.
    expected.cx(1, 2)
    expected.x(1)
    expected.cx(0, 1)  # Restore the reference qubit.

    assert_same_unitary(circ, expected)


def test_same_qubit_equality_is_always_true():
    """Comparing a qubit with itself must reduce to an unconditional X."""
    circ = circuit()
    value = qubit(circ)
    target = qubit(circ)
    target.flipIf(value, where=value)

    expected = QuantumCircuit(2)
    expected.x(1)

    assert_same_unitary(circ, expected)


if __name__ == "__main__":
    test_qubit_equality_condition()
    test_same_qubit_equality_is_always_true()
    print("T28_qubit_equality_condition: PASS")
