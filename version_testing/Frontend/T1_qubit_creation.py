"""Verify the basic contract between qubits and their parent circuit.

This test checks that creating qubits registers the same objects in the
circuit, assigns sequential indexes, and preserves their measurement flags.
It also verifies that the exported Qiskit circuit has matching register sizes.
"""

import sys
from pathlib import Path

# Allow this file to be run directly from the Frontend testing directory.
# Three ``parent`` accesses lead from this file back to the repository root.
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from frontend_test_helpers import export_to_qiskit
from qitker import circuit, qubit


def test_qubit_creation():
    """Create three qubits and verify the circuit metadata they produce."""
    circ = circuit()

    # The middle qubit is intentionally excluded from measurement so the test
    # can verify both measured and unmeasured qubits in the same circuit.
    first = qubit(circ)
    second = qubit(circ, measured=False)
    third = qubit(circ)

    # Qubits must remain in creation order and receive matching indexes.
    assert circ.getQubitsNumber() == 3
    assert [q.getIndex() for q in circ.getQubitsArray()] == [0, 1, 2]
    assert circ.getQubitsArray() == [first, second, third]
    assert [q.isToMeasure() for q in circ.getQubitsArray()] == [True, False, True]
    assert circ.getQubitsNumberToMeasure() == 2

    # Quantum indexes 0 and 2 are mapped to consecutive classical bits 0 and 1.
    assert circ.getMeasuredLists() == ([0, 2], [0, 1])

    # Export must preserve the quantum size and allocate classical bits only
    # for qubits that Qitker marks for measurement.
    exported = export_to_qiskit(circ)
    assert exported.num_qubits == 3
    assert exported.num_clbits == 2


if __name__ == "__main__":
    # Keep the test runnable without requiring pytest.
    test_qubit_creation()
    print("T1_qubit_creation: PASS")
