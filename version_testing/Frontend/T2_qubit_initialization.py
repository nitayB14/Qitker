"""Verify that a qubit can be initialized to either basis state.

The test checks the exported quantum state rather than inspecting Qitker's
internal operation list, so it validates the observable frontend behavior.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit


def test_qubit_initialization():
    """Compare Qitker's |0> and |1> initialization with Qiskit."""
    for initial_value in (0, 1):
        circ = circuit()
        qubit(circ, initialize=initial_value)

        expected = QuantumCircuit(1)
        if initial_value == 1:
            expected.x(0)

        assert_same_state(circ, expected)


if __name__ == "__main__":
    test_qubit_initialization()
    print("T2_qubit_initialization: PASS")
