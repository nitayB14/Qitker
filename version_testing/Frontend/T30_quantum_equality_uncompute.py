"""Verify equality comparison and uncomputation on phase-sensitive states.

Both operands are placed in different superpositions before comparison. The
full statevector comparison catches leftover XOR garbage, lost phases, or an
incorrect relationship between the reference register and target qubit.
"""

import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit, qRegister


def test_quantum_equality_uncompute():
    """Compare a phase-sensitive register equality with its manual Qiskit form."""
    circ = circuit()
    left = qRegister(circ, size=2)
    right = qRegister(circ, size=2)
    target = qubit(circ)

    left[0].H()
    left[1].rotateY(math.pi / 3)
    right[0].rotateX(math.pi / 4)
    right[1].H()
    right[1].phase()
    target.flipIf(left, where=right)

    expected = QuantumCircuit(5)
    expected.h(0)
    expected.ry(math.pi / 3, 1)
    expected.rx(math.pi / 4, 2)
    expected.h(3)
    expected.z(3)

    expected.cx(0, 2)
    expected.cx(1, 3)
    expected.x(2)
    expected.x(3)
    expected.mcx([2, 3], 4)
    expected.x(3)
    expected.x(2)
    expected.cx(1, 3)
    expected.cx(0, 2)

    assert_same_state(circ, expected)


if __name__ == "__main__":
    test_quantum_equality_uncompute()
    print("T30_quantum_equality_uncompute: PASS")
