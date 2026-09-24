"""Verify every public name for Qitker's Hadamard operation.

Each alias must create the same |+> state as Qiskit's Hadamard gate.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit


def test_h_gate():
    """Check H, h, and superPosition without relying on measurements."""
    for method_name in ("H", "h", "superPosition"):
        circ = circuit()
        target = qubit(circ)
        getattr(target, method_name)()

        expected = QuantumCircuit(1)
        expected.h(0)

        assert_same_state(circ, expected)


if __name__ == "__main__":
    test_h_gate()
    print("T9_h_gate: PASS")
