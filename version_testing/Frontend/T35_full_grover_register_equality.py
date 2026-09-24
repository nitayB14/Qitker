"""Run a complete two-qubit Grover search using register equality.

The search register begins in uniform superposition. A quantum reference
register stores ``10``; the oracle marks equality through compute/phase/
uncompute, and one Grover diffusion step must recover ``10`` with certainty.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from frontend_test_helpers import assert_same_state, export_to_qiskit, to_qitker_bit_order
from qitker import circuit, qubit, qRegister


def apply_manual_equality_oracle(expected):
    """Mark search==reference and restore both reference qubits afterward."""
    expected.cx(0, 2)
    expected.cx(1, 3)
    expected.x(2)
    expected.x(3)
    expected.mcx([2, 3], 4)
    expected.x(3)
    expected.x(2)
    expected.cx(1, 3)
    expected.cx(0, 2)
    expected.z(4)

    # Repeating the equality computation uncomputes the marker after phase use.
    expected.cx(0, 2)
    expected.cx(1, 3)
    expected.x(2)
    expected.x(3)
    expected.mcx([2, 3], 4)
    expected.x(3)
    expected.x(2)
    expected.cx(1, 3)
    expected.cx(0, 2)


def build_grover_circuit():
    """Build the Qitker equality oracle followed by two-qubit diffusion."""
    circ = circuit()
    search = qRegister(circ, size=2)
    reference = qRegister(circ, size=2, initialize="10", measured=False)
    marker = qubit(circ, measured=False)

    search.superPosition()

    marker.flipIf(search, where=reference)
    marker.phase()
    marker.flipIf(search, where=reference)

    search.H()
    search.X()
    search[1].phaseIf(search[0])
    search.X()
    search.H()

    return circ


def build_expected_grover_circuit():
    """Build the same algorithm directly in Qiskit as an independent reference."""
    expected = QuantumCircuit(5)
    expected.x(2)  # Qitker reference string "10" sets its leftmost qubit.
    expected.h(0)
    expected.h(1)
    apply_manual_equality_oracle(expected)
    expected.h(0)
    expected.h(1)
    expected.x(0)
    expected.x(1)
    expected.cz(0, 1)
    expected.x(0)
    expected.x(1)
    expected.h(0)
    expected.h(1)
    return expected


def test_full_grover_register_equality():
    """Verify the complete state, clean workspace, and final search result."""
    circ = build_grover_circuit()
    assert_same_state(circ, build_expected_grover_circuit())

    state = Statevector.from_instruction(export_to_qiskit(circ))
    qitker_probabilities = to_qitker_bit_order(state.probabilities_dict())

    # Full Qitker order is search(10), reference(10), marker(0).
    assert qitker_probabilities.get("10100", 0) > 1 - 1e-12
    assert circ.getMeasuredLists() == ([0, 1], [0, 1])


if __name__ == "__main__":
    test_full_grover_register_equality()
    print("T35_full_grover_register_equality: PASS")
