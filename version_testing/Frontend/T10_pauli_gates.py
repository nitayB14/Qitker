"""Verify the X, Y, and Z gates together with their public aliases.

The input starts in |+> so phase differences created by Y and Z remain visible
to the statevector comparison instead of disappearing from probabilities.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit


def test_pauli_gates():
    """Compare every Pauli alias with its equivalent Qiskit gate."""
    aliases = {
        "X": ("X", "x", "flip"),
        "Y": ("Y", "y", "flipPhase"),
        "Z": ("Z", "z", "phase"),
    }

    for qiskit_gate, method_names in aliases.items():
        for method_name in method_names:
            circ = circuit()
            target = qubit(circ)
            target.H()
            getattr(target, method_name)()

            expected = QuantumCircuit(1)
            expected.h(0)
            getattr(expected, qiskit_gate.lower())(0)

            assert_same_state(circ, expected)


if __name__ == "__main__":
    test_pauli_gates()
    print("T10_pauli_gates: PASS")
