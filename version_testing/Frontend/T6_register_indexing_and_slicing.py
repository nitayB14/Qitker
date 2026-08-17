"""Verify that qRegister indexing and slicing follow normal list order.

Index 0 is the leftmost Qitker bit. Slices must return references to the
original qubit objects rather than creating or copying qubits.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qitker import circuit, qRegister


def test_register_indexing_and_slicing():
    """Check positive, negative, forward, and reversed register access."""
    circ = circuit()
    register = qRegister(circ, size=4, initialize="0001")
    all_qubits = register[::]

    assert register[0] is all_qubits[0]
    assert register[-1] is all_qubits[3]
    assert register[0:2] == all_qubits[0:2]
    assert register[2:4] == all_qubits[2:4]
    assert register[::-1] == list(reversed(all_qubits))

    # Reading a slice must not allocate additional qubits in the circuit.
    assert circ.getQubitsNumber() == 4
    assert [q.getIndex() for q in register[0:2]] == [0, 1]
    assert [q.getIndex() for q in register[2:4]] == [2, 3]


if __name__ == "__main__":
    test_register_indexing_and_slicing()
    print("T6_register_indexing_and_slicing: PASS")
