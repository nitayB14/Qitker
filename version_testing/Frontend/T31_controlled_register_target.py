"""Verify controlled operations applied to an entire target qRegister.

Each register method must apply the requested gate once to every target qubit
under the same condition, including fixed, phase, and rotation operations.
"""

import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit
from qiskit.circuit.library import RZGate

from frontend_test_helpers import assert_same_unitary
from qitker import circuit, qubit, qRegister


def test_controlled_register_x_on_zero():
    """Apply X to every target when the control is in state |0>."""
    circ = circuit()
    control = qubit(circ)
    targets = qRegister(circ, size=3)
    targets.flipIf(control, where=0)

    expected = QuantumCircuit(4)
    expected.x(0)
    for target in (1, 2, 3):
        expected.cx(0, target)
    expected.x(0)

    assert_same_unitary(circ, expected)


def test_controlled_register_phase_and_rotation():
    """Check controlled Z and RZ across all register targets."""
    cases = (
        ("phaseIf", None, "cz"),
        ("rotateZif", math.pi / 3, "crz"),
    )

    for qitker_method, angle, operation_type in cases:
        circ = circuit()
        control = qubit(circ)
        targets = qRegister(circ, size=3)

        if angle is None:
            getattr(targets, qitker_method)(control)
        else:
            getattr(targets, qitker_method)(control, angle)

        expected = QuantumCircuit(4)
        for target in (1, 2, 3):
            if operation_type == "cz":
                expected.cz(0, target)
            else:
                expected.append(RZGate(angle).control(1), [0, target])

        assert_same_unitary(circ, expected)


if __name__ == "__main__":
    test_controlled_register_x_on_zero()
    test_controlled_register_phase_and_rotation()
    print("T31_controlled_register_target: PASS")
