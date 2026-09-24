"""Verify the ``==`` frontend syntax for qubits and registers.

The existing ``where`` tests cover the underlying controlled operations. This
test checks that equality expressions reach those operations as conditions.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_unitary
from qitker import circuit, qubit, qRegister


def test_qubit_equality_operator():
    """A qubit comparison must control on equal values in superposition."""
    circ = circuit()
    left = qubit(circ)
    right = qubit(circ)
    target = qubit(circ)
    target.flipIf(left == right)

    expected = QuantumCircuit(3)
    expected.cx(0, 1)
    expected.x(1)
    expected.cx(1, 2)
    expected.x(1)
    expected.cx(0, 1)
    assert_same_unitary(circ, expected)

    same_circ = circuit()
    value = qubit(same_circ)
    same_target = qubit(same_circ)
    same_target.flipIf(value == value)

    same_expected = QuantumCircuit(2)
    same_expected.x(1)
    assert_same_unitary(same_circ, same_expected)


def test_register_equality_operator():
    """Whole-register equality must compute, control, and uncompute."""
    for width in (2, 3):
        circ = circuit()
        left = qRegister(circ, size=width)
        right = qRegister(circ, size=width)
        target = qubit(circ)
        target.flipIf(left == right)

        expected = QuantumCircuit((2 * width) + 1)
        references = list(range(width, 2 * width))
        for control, reference in enumerate(references):
            expected.cx(control, reference)
        for reference in references:
            expected.x(reference)
        expected.mcx(references, 2 * width)
        for reference in reversed(references):
            expected.x(reference)
        for control, reference in reversed(list(enumerate(references))):
            expected.cx(control, reference)

        assert_same_unitary(circ, expected)


def test_register_pattern_equality_operator():
    """Register equality with a string or integer must use the same bit order."""
    string_circ = circuit()
    string_register = qRegister(string_circ, size=3)
    string_target = qubit(string_circ)
    string_target.flipIf(string_register == "1x1")

    string_expected = QuantumCircuit(4)
    string_expected.mcx([0, 2], 3)
    assert_same_unitary(string_circ, string_expected)

    integer_circ = circuit()
    integer_register = qRegister(integer_circ, size=3)
    integer_target = qubit(integer_circ)
    integer_target.flipIf(integer_register == 5)  # Three-bit pattern 101.

    integer_expected = QuantumCircuit(4)
    integer_expected.x(1)
    integer_expected.mcx([0, 1, 2], 3)
    integer_expected.x(1)
    assert_same_unitary(integer_circ, integer_expected)


if __name__ == "__main__":
    test_qubit_equality_operator()
    test_register_equality_operator()
    test_register_pattern_equality_operator()
    print("T36_equality_operator: PASS")
