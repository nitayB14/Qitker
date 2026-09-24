"""Verify controlled operations that activate on control state |0>.

Unitary comparison includes superpositions and proves that temporary X gates
used to invert the control are removed before the operation finishes.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_unitary
from qitker import circuit, qubit


def test_where_zero():
    """Compare string and integer zero conditions with a manual Qiskit circuit."""
    expected = QuantumCircuit(2)
    expected.x(0)
    expected.cx(0, 1)
    expected.x(0)

    for condition in ("0", 0):
        circ = circuit()
        control = qubit(circ)
        target = qubit(circ)
        target.flipIf(control, where=condition)

        assert_same_unitary(circ, expected)


if __name__ == "__main__":
    test_where_zero()
    print("T23_where_zero: PASS")
