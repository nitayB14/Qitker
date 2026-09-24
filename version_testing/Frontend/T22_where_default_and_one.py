"""Verify that an omitted condition means a control on state |1>.

The default, string ``"1"``, and integer ``1`` forms must all produce the
same controlled-X unitary as Qiskit's CNOT gate.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_unitary
from qitker import circuit, qubit


def build_condition(condition_supplied, condition=None):
    """Build one controlled-X form while preserving an actually omitted arg."""
    circ = circuit()
    control = qubit(circ)
    target = qubit(circ)

    if condition_supplied:
        target.flipIf(control, where=condition)
    else:
        target.flipIf(control)

    return circ


def test_where_default_and_one():
    """Compare all representations of a positive control with Qiskit."""
    expected = QuantumCircuit(2)
    expected.cx(0, 1)

    for supplied, condition in ((False, None), (True, "1"), (True, 1)):
        assert_same_unitary(build_condition(supplied, condition), expected)


if __name__ == "__main__":
    test_where_default_and_one()
    print("T22_where_default_and_one: PASS")
