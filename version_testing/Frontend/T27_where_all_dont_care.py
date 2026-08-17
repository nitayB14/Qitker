"""Verify the edge case where every control is marked as don't-care.

No active controls remain, so the frontend must emit one unconditional target
operation rather than attempting to construct a controlled gate with no controls.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_unitary
from qitker import circuit, qubit


def test_where_all_dont_care():
    """Compare four ignored controls with a single unconditional target X."""
    circ = circuit()
    controls = [qubit(circ) for _ in range(4)]
    target = qubit(circ)
    target.flipIf(controls, where="xxxx")

    expected = QuantumCircuit(5)
    expected.x(4)

    assert_same_unitary(circ, expected)
    assert len(circ.getOperationVector()) == 1


if __name__ == "__main__":
    test_where_all_dont_care()
    print("T27_where_all_dont_care: PASS")
