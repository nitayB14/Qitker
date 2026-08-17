"""Verify the final-measurement metadata produced by the frontend.

Measured quantum indexes may contain gaps, but their classical destinations
must always be consecutive and preserve Qitker's qubit creation order.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from frontend_test_helpers import export_to_qiskit
from qitker import circuit, qubit


def test_measurement_selection():
    """Select alternating qubits and verify their classical-bit mapping."""
    circ = circuit()
    qubit(circ, measured=True)
    qubit(circ, measured=False)
    qubit(circ, measured=True)
    qubit(circ, measured=False)
    qubit(circ, measured=True)

    quantum_indexes, classical_indexes = circ.getMeasuredLists()

    assert circ.getQubitsNumberToMeasure() == 3
    assert quantum_indexes == [0, 2, 4]
    assert classical_indexes == [0, 1, 2]

    # Export allocates the classical register but intentionally leaves the
    # user free to decide when to add Qiskit measurement instructions.
    exported = export_to_qiskit(circ)
    assert exported.num_qubits == 5
    assert exported.num_clbits == 3
    assert exported.count_ops().get("measure", 0) == 0


if __name__ == "__main__":
    test_measurement_selection()
    print("T7_measurement_selection: PASS")
