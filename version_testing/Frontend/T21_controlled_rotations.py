"""Verify controlled RX, RY, and RZ with one or multiple controls.

The full unitary is compared for positive, negative, and zero angles, covering
both frontend parameter storage and controlled-rotation export to Qiskit.
"""

import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit
from qiskit.circuit.library import RXGate, RYGate, RZGate

from frontend_test_helpers import assert_same_unitary
from qitker import circuit, qubit


def test_controlled_rotations():
    """Compare every controlled rotation across control widths and angles."""
    cases = (
        ("rotateXif", RXGate),
        ("rotateYif", RYGate),
        ("rotateZif", RZGate),
    )
    angles = (0, math.pi / 3, -math.pi / 4, math.pi)

    for controls_number in (1, 2, 3):
        for qitker_method, gate_type in cases:
            for angle in angles:
                circ = circuit()
                controls = [qubit(circ) for _ in range(controls_number)]
                target = qubit(circ)
                control_argument = controls[0] if controls_number == 1 else controls
                getattr(target, qitker_method)(control_argument, angle)

                expected = QuantumCircuit(controls_number + 1)
                expected.append(
                    gate_type(angle).control(controls_number),
                    list(range(controls_number + 1)),
                )

                assert_same_unitary(circ, expected)


if __name__ == "__main__":
    test_controlled_rotations()
    print("T21_controlled_rotations: PASS")
