"""Verify multi-qubit ``where`` patterns as a complete truth table.

For every selected pattern, all eight three-bit inputs are tested. A pattern
matches when every 0/1 position agrees; positions containing ``x`` are ignored.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit.quantum_info import Statevector

from frontend_test_helpers import export_to_qiskit, to_qitker_bit_order
from qitker import circuit, qubit


def pattern_matches(bits, pattern):
    """Return the classical truth value defined by a Qitker where pattern."""
    return all(expected == "x" or actual == expected for actual, expected in zip(bits, pattern))


def output_state(bits, pattern):
    """Run one deterministic pattern case and return it in Qitker bit order."""
    circ = circuit()
    controls = [qubit(circ, initialize=int(bit)) for bit in bits]
    target = qubit(circ)
    target.flipIf(controls, where=pattern)

    probabilities = Statevector.from_instruction(export_to_qiskit(circ)).probabilities_dict()
    qitker_probabilities = to_qitker_bit_order(probabilities)
    return max(qitker_probabilities, key=qitker_probabilities.get)


def test_where_bitstring_patterns():
    """Check fixed, mixed, and all-don't-care patterns."""
    patterns = ("000", "001", "101", "1x0", "x11", "0xx", "xxx")

    for pattern in patterns:
        for value in range(8):
            bits = format(value, "03b")
            expected_target = "1" if pattern_matches(bits, pattern) else "0"
            assert output_state(bits, pattern) == bits + expected_target


if __name__ == "__main__":
    test_where_bitstring_patterns()
    print("T25_where_bitstring_patterns: PASS")
