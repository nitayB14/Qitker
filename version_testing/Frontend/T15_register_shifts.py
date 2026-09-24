"""Verify cyclic left and right shifts of a qRegister.

Shifts move quantum states through SWAP gates; they must not reorder the
Python qubit objects or allocate new qubits in the circuit.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit.quantum_info import Statevector

from frontend_test_helpers import export_to_qiskit, to_qitker_bit_order
from qitker import circuit, qRegister


def shifted_state(direction, amount):
    """Apply one Qitker shift and return its deterministic displayed state."""
    circ = circuit()
    register = qRegister(circ, size=4, initialize="1001")
    original_qubits = register[::]

    getattr(register, direction)(amount)

    probabilities = Statevector.from_instruction(
        export_to_qiskit(circ)
    ).probabilities_dict()
    qitker_probabilities = to_qitker_bit_order(probabilities)
    state = max(qitker_probabilities, key=qitker_probabilities.get)

    # A quantum shift changes states, not the register's Python object order.
    assert register[::] == original_qubits
    assert circ.getQubitsNumber() == 4
    return state


def test_register_shifts():
    """Check direction, amount, modulo behavior, and zero-distance shifts."""
    expected_states = {
        ("shiftLeft", 1): "0011",
        ("shiftRight", 1): "1100",
        ("shiftLeft", 2): "0110",
        ("shiftRight", 2): "0110",
        ("shiftLeft", 4): "1001",
        ("shiftRight", 5): "1100",
    }

    for (direction, amount), expected_state in expected_states.items():
        assert shifted_state(direction, amount) == expected_state


if __name__ == "__main__":
    test_register_shifts()
    print("T15_register_shifts: PASS")
