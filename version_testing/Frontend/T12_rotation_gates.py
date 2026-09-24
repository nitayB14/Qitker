"""Verify single-qubit rotations for several representative angles.

Positive, negative, zero, and full-turn angles exercise both parameter storage
and the RX/RY/RZ dispatch performed by the Qiskit exporter.
"""

import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit


def test_rotation_gates():
    """Compare rotateX/Y/Z and RX/RY/RZ with Qiskit."""
    methods = {
        "rx": ("rotateX", "RX"),
        "ry": ("rotateY", "RY"),
        "rz": ("rotateZ", "RZ"),
    }
    angles = (0, math.pi / 4, math.pi / 2, math.pi, -math.pi / 3, 2 * math.pi)

    for qiskit_gate, method_names in methods.items():
        for method_name in method_names:
            for angle in angles:
                circ = circuit()
                target = qubit(circ)
                target.H()
                getattr(target, method_name)(angle)

                expected = QuantumCircuit(1)
                expected.h(0)
                getattr(expected, qiskit_gate)(angle, 0)

                assert_same_state(circ, expected)


if __name__ == "__main__":
    test_rotation_gates()
    print("T12_rotation_gates: PASS")
