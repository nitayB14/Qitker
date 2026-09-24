"""Verify binary-string initialization, including leading zeroes.

The string is treated as a left-to-right Qitker register representation and
must keep its original width instead of being reduced to an integer's width.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit.quantum_info import Statevector

from frontend_test_helpers import export_to_qiskit, to_qitker_bit_order
from qitker import circuit, qRegister


def test_register_string_initialization():
    """Check that each input string produces the same Qitker-order state."""
    for expected_state in ("0001", "1010", "0000", "1111"):
        circ = circuit()
        register = qRegister(circ, initialize=expected_state)

        probabilities = Statevector.from_instruction(
            export_to_qiskit(circ)
        ).probabilities_dict()
        actual_state = max(
            to_qitker_bit_order(probabilities),
            key=to_qitker_bit_order(probabilities).get,
        )

        assert len(register[::]) == len(expected_state)
        assert actual_state == expected_state


if __name__ == "__main__":
    test_register_string_initialization()
    print("T4_register_string_initialization: PASS")
