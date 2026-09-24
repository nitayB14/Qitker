"""Verify integer initialization and Qitker's register bit order.

For a four-qubit register, Qitker displays index 0 on the left and index 3 on
the right. Therefore integer 1 is represented as ``0001`` in Qitker order.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit.quantum_info import Statevector

from frontend_test_helpers import export_to_qiskit, to_qitker_bit_order
from qitker import circuit, qRegister


def exported_qitker_state(initial_value):
    """Return the single populated basis state in Qitker display order."""
    circ = circuit()
    qRegister(circ, size=4, initialize=initial_value)

    probabilities = Statevector.from_instruction(
        export_to_qiskit(circ)
    ).probabilities_dict()
    qitker_probabilities = to_qitker_bit_order(probabilities)

    # Integer initialization creates a deterministic computational-basis state.
    return max(qitker_probabilities, key=qitker_probabilities.get)


def test_register_integer_initialization():
    """Check representative values including both ends of the valid range."""
    expected_states = {
        0: "0000",
        1: "0001",
        6: "0110",
        15: "1111",
    }

    for initial_value, expected_state in expected_states.items():
        assert exported_qitker_state(initial_value) == expected_state


if __name__ == "__main__":
    test_register_integer_initialization()
    print("T3_register_integer_initialization: PASS")
