"""Verify controlled-X for basis states and coherent superposition.

The basis cases check the truth table, while the Bell-state case proves that
the control remains quantum and becomes correctly entangled with the target.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit

from frontend_test_helpers import assert_same_state
from qitker import circuit, qubit


def test_controlled_x_basis_states():
    """Compare Qitker CNOT with Qiskit on all computational-basis inputs."""
    for control_value in (0, 1):
        for target_value in (0, 1):
            circ = circuit()
            control = qubit(circ, initialize=control_value)
            target = qubit(circ, initialize=target_value)
            target.flipIf(control)

            expected = QuantumCircuit(2)
            if control_value:
                expected.x(0)
            if target_value:
                expected.x(1)
            expected.cx(0, 1)

            assert_same_state(circ, expected)


def test_controlled_x_entanglement():
    """Create a Bell state and compare its full statevector with Qiskit."""
    circ = circuit()
    control = qubit(circ)
    target = qubit(circ)
    control.H()
    target.cx(control)

    expected = QuantumCircuit(2)
    expected.h(0)
    expected.cx(0, 1)

    assert_same_state(circ, expected)


if __name__ == "__main__":
    test_controlled_x_basis_states()
    test_controlled_x_entanglement()
    print("T16_controlled_x: PASS")
