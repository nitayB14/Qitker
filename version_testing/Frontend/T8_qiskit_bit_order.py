"""Verify the display-order boundary between Qitker and Qiskit.

The exported circuit keeps direct qubit indexes. Qiskit displays basis states
from its highest index to its lowest, while Qitker displays them from index 0
upward. Reversing only the displayed key must recover the Qitker bitstring.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit.quantum_info import Statevector

from frontend_test_helpers import export_to_qiskit, to_qitker_bit_order
from qitker import circuit, qRegister


def test_qiskit_bit_order():
    """Check several asymmetric states so an accidental match is impossible."""
    qitker_states = ("0001", "0010", "0100", "1000", "1011")

    for expected_qitker_state in qitker_states:
        circ = circuit()
        qRegister(circ, initialize=expected_qitker_state)

        qiskit_probabilities = Statevector.from_instruction(
            export_to_qiskit(circ)
        ).probabilities_dict()
        qiskit_state = max(qiskit_probabilities, key=qiskit_probabilities.get)

        converted = to_qitker_bit_order({qiskit_state: 1})
        actual_qitker_state = next(iter(converted))

        assert qiskit_state == expected_qitker_state[::-1]
        assert actual_qitker_state == expected_qitker_state


if __name__ == "__main__":
    test_qiskit_bit_order()
    print("T8_qiskit_bit_order: PASS")
