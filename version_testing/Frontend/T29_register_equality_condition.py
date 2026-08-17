"""Verify coherent equality comparison between two qRegisters.

The expected circuit explicitly computes bitwise XORs into the reference,
checks that every XOR is zero, and reverses the computation afterward.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_unitary
from qitker import circuit, qubit, qRegister


def build_expected_equality(width):
    """Build the manual Qiskit equality operation for the requested width."""
    expected = QuantumCircuit((2 * width) + 1)
    controls = list(range(width))
    references = list(range(width, 2 * width))
    target = 2 * width

    for control, reference in zip(controls, references):
        expected.cx(control, reference)
    for reference in references:
        expected.x(reference)

    expected.mcx(references, target)

    for reference in reversed(references):
        expected.x(reference)
    for control, reference in reversed(list(zip(controls, references))):
        expected.cx(control, reference)

    return expected


def test_register_equality_condition():
    """Compare two- and three-bit Qitker equality with explicit Qiskit circuits."""
    for width in (2, 3):
        circ = circuit()
        left = qRegister(circ, size=width)
        right = qRegister(circ, size=width)
        target = qubit(circ)
        target.flipIf(left, where=right)

        assert_same_unitary(circ, build_expected_equality(width))


if __name__ == "__main__":
    test_register_equality_condition()
    print("T29_register_equality_condition: PASS")
