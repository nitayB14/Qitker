"""Verify that qRegister operations act once on every contained qubit.

The comparison uses asymmetric initial states and phases so missing, repeated,
or incorrectly ordered applications are visible in the final statevector.
"""

import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qRegister


def build_qitker_register(method_name, argument=None):
    """Build one element-wise Qitker register operation."""
    circ = circuit()
    register = qRegister(circ, size=3, initialize="101")

    if argument is None:
        getattr(register, method_name)()
    else:
        getattr(register, method_name)(argument)

    return circ


def build_expected_register(qiskit_gate, argument=None):
    """Build the equivalent direct Qiskit circuit in Qitker index order."""
    expected = QuantumCircuit(3)
    expected.x(0)
    expected.x(2)

    for index in range(3):
        gate = getattr(expected, qiskit_gate)
        if argument is None:
            gate(index)
        else:
            gate(argument, index)

    return expected


def test_register_elementwise_gates():
    """Check representative fixed and parameterized register operations."""
    cases = (
        ("H", "h", None),
        ("X", "x", None),
        ("Z", "z", None),
        ("rotateY", "ry", math.pi / 3),
    )

    for qitker_method, qiskit_gate, argument in cases:
        actual = build_qitker_register(qitker_method, argument)
        expected = build_expected_register(qiskit_gate, argument)
        assert_same_state(actual, expected)


if __name__ == "__main__":
    test_register_elementwise_gates()
    print("T13_register_elementwise_gates: PASS")
