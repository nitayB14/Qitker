"""Shared helpers for concise frontend correctness tests."""

from qiskit.quantum_info import Operator, Statevector


def export_to_qiskit(qitker_circuit):
    """Export a Qitker circuit and fail clearly if export returns nothing."""
    exported = qitker_circuit.exportCircuit("qiskit")
    assert exported is not None, "Qiskit export returned None"
    return exported


def assert_same_state(qitker_circuit, expected_qiskit_circuit):
    """Assert equal output states, allowing an irrelevant global phase."""
    actual = Statevector.from_instruction(export_to_qiskit(qitker_circuit))
    expected = Statevector.from_instruction(expected_qiskit_circuit)
    assert actual.equiv(expected), f"actual={actual}, expected={expected}"


def assert_same_unitary(qitker_circuit, expected_qiskit_circuit):
    """Assert equal unitaries, allowing an irrelevant global phase."""
    actual = Operator(export_to_qiskit(qitker_circuit))
    expected = Operator(expected_qiskit_circuit)
    assert actual.equiv(expected), f"actual={actual}, expected={expected}"


def to_qitker_bit_order(qiskit_counts):
    """Return Qiskit counts displayed in Qitker's left-to-right qubit order."""
    return {
        bitstring[::-1]: count
        for bitstring, count in qiskit_counts.items()
    }
