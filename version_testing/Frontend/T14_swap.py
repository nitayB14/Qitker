"""Verify Qitker's three-CNOT implementation of the SWAP operation.

Basis states check the visible exchange, while a complex superposition checks
that the operation preserves amplitudes and phases as a true quantum SWAP.
"""

import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit


def test_swap_basis_states():
    """Compare SWAP on all two-qubit computational-basis inputs."""
    for first_value in (0, 1):
        for second_value in (0, 1):
            circ = circuit()
            first = qubit(circ, initialize=first_value)
            second = qubit(circ, initialize=second_value)
            first.swap(second)

            expected = QuantumCircuit(2)
            if first_value:
                expected.x(0)
            if second_value:
                expected.x(1)
            expected.swap(0, 1)

            assert_same_state(circ, expected)


def test_swap_superposition():
    """Compare SWAP when both qubits carry nontrivial quantum states."""
    circ = circuit()
    first = qubit(circ)
    second = qubit(circ)
    first.H()
    second.rotateY(math.pi / 3)
    second.rotateZ(math.pi / 5)
    first.swap(second)

    expected = QuantumCircuit(2)
    expected.h(0)
    expected.ry(math.pi / 3, 1)
    expected.rz(math.pi / 5, 1)
    expected.swap(0, 1)

    assert_same_state(circ, expected)


if __name__ == "__main__":
    test_swap_basis_states()
    test_swap_superposition()
    print("T14_swap: PASS")
