"""Verify the S and T phase gates and their descriptive aliases.

Phase gates are applied to |+>, where their relative phase is observable in
the statevector even though measurement probabilities remain unchanged.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit


def test_phase_gates():
    """Compare S/T and their aliases with Qiskit's exact states."""
    aliases = {
        "s": ("S", "s", "halfPhase"),
        "t": ("T", "t", "quarterPhase"),
    }

    for qiskit_gate, method_names in aliases.items():
        for method_name in method_names:
            circ = circuit()
            target = qubit(circ)
            target.H()
            getattr(target, method_name)()

            expected = QuantumCircuit(1)
            expected.h(0)
            getattr(expected, qiskit_gate)(0)

            assert_same_state(circ, expected)


if __name__ == "__main__":
    test_phase_gates()
    print("T11_phase_gates: PASS")
