"""Verify that ``where='x'`` completely ignores its control qubit.

The resulting operation must be an unconditional X on the target while the
nominal control is preserved for every possible quantum input state.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_unitary
from qitker import circuit, qubit


def test_where_dont_care():
    """Compare a don't-care condition with an unconditional Qiskit X."""
    circ = circuit()
    control = qubit(circ)
    target = qubit(circ)
    target.flipIf(control, where="x")

    expected = QuantumCircuit(2)
    expected.x(1)

    assert_same_unitary(circ, expected)


if __name__ == "__main__":
    test_where_dont_care()
    print("T24_where_dont_care: PASS")
