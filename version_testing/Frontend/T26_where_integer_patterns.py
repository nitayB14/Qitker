"""Verify integer conditions and their fixed-width binary interpretation.

An integer condition must be equivalent to its zero-padded binary string in
Qitker's left-to-right register order.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit.quantum_info import Operator

from frontend_test_helpers import export_to_qiskit
from qitker import circuit, qubit


def build_where(condition):
    """Build a four-control X operation for one condition representation."""
    circ = circuit()
    controls = [qubit(circ) for _ in range(4)]
    target = qubit(circ)
    target.flipIf(controls, where=condition)
    return circ


def test_where_integer_patterns():
    """Compare representative integers with their exact four-bit strings."""
    cases = {
        0: "0000",
        1: "0001",
        2: "0010",
        8: "1000",
        15: "1111",
    }

    for integer, bitstring in cases.items():
        integer_unitary = Operator(export_to_qiskit(build_where(integer)))
        string_unitary = Operator(export_to_qiskit(build_where(bitstring)))
        assert integer_unitary.equiv(string_unitary)


if __name__ == "__main__":
    test_where_integer_patterns()
    print("T26_where_integer_patterns: PASS")
