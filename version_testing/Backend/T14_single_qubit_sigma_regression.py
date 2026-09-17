"""Section 14: verify local sigmas and stored single-qubit gate sequences."""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from qitker.QuantumMath.constant import math_constant
from qitker.anyons.FusionSystem import FusionSystem
from qitker.parser.sequenceOperation import sequenceOperation


SIGMA_REFERENCES = {
    1: math_constant.R12,
    -1: math_constant.R12_inv,
    2: math_constant.R23,
    -2: math_constant.R23_inv,
    3: math_constant.R34,
    -3: math_constant.R34_inv,
}


def assert_raises(expected_exception, function):
    """Verify that function raises the expected exception."""
    try:
        function()
    except expected_exception:
        return
    raise AssertionError(
        f"Expected {expected_exception.__name__} to be raised."
    )


def assert_coherent(fusion_system):
    """Check stable tree, basis, and HilbertSpace invariants."""
    fusion_system._validate_system_coherence()
    assert fusion_system.basis.classify_logical is True
    assert fusion_system.basis.tree_signature == fusion_system.tree.to_ids()
    assert fusion_system.hilbertSpace.basis is fusion_system.basis
    assert fusion_system.hilbertSpace.dimension == 2
    assert fusion_system.hilbertSpace.state_vector.shape == (2,)


def effective_matrix(sequence):
    """Build the effective 2x2 matrix of a sigma sequence."""
    columns = []
    # Applying the sequence to each basis vector gives one matrix column.
    for input_index in range(2):
        fusion_system = FusionSystem(1)
        fusion_system.hilbertSpace.state_vector[:] = 0
        fusion_system.hilbertSpace.state_vector[input_index] = 1
        for sigma_index in sequence:
            fusion_system.sigma(0, sigma_index)
        columns.append(fusion_system.hilbertSpace.state_vector.copy())
        assert_coherent(fusion_system)
    return np.column_stack(columns)


def operator_fidelity(actual, expected):
    """Return global-phase-insensitive fidelity of two 2x2 operators."""
    return float(abs(np.trace(expected.conj().T @ actual)) / 2)


def load_braid_database():
    """Load gate sequences and metadata directly from the JSON file."""
    json_path = PROJECT_ROOT / "qitker" / "parser" / "braid_sequences.json"
    with json_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_sigma_reference_matrices():
    """Compare every local generator and inverse with its reference."""
    for sigma_index, expected in SIGMA_REFERENCES.items():
        actual = effective_matrix([sigma_index])
        assert np.allclose(actual, expected)
        assert np.allclose(actual.conj().T @ actual, np.eye(2))


def test_sigma_inverse_restores_system():
    """Check generator/inverse restoration of state, tree, and order."""
    state = np.array([0.3 + 0.4j, -0.2 + 0.842614977j])
    state /= np.linalg.norm(state)

    for sigma_index in (1, 2, 3):
        fusion_system = FusionSystem(1)
        tree_before = fusion_system.tree.to_ids()
        order_before = fusion_system.get_current_anyon_order()
        fusion_system.hilbertSpace.state_vector = state.copy()

        fusion_system.sigma(0, sigma_index)
        fusion_system.sigma(0, -sigma_index)

        assert fusion_system.tree.to_ids() == tree_before
        assert fusion_system.get_current_anyon_order() == order_before
        assert np.allclose(fusion_system.hilbertSpace.state_vector, state)
        assert len(fusion_system.operation_history) == 2
        assert_coherent(fusion_system)


def test_sigma_records_one_operation():
    """Check that sigma2 hides its internal F/R implementation steps."""
    fusion_system = FusionSystem(1)
    fusion_system.sigma(0, 2)

    assert len(fusion_system.operation_history) == 1
    operation = fusion_system.operation_history[0]
    assert operation.operation_type == "SIGMA"
    assert operation.parameters["sigma_index"] == 2
    assert operation.parameters["first_id"] == 2
    assert operation.parameters["second_id"] == 3
    assert "q[0] | Sigma: σ2" in fusion_system.get_operation_history()


def test_sigma2_failure_rolls_back_system():
    """Check full rollback when sigma2 fails at its middle R step."""
    fusion_system = FusionSystem(1)
    tree_before = fusion_system.tree.to_ids()
    basis_before = fusion_system.basis
    state_before = fusion_system.hilbertSpace.state_vector.copy()
    braid_before = fusion_system.hilbertSpace.local_braid_operators[0].copy()

    def fail_r_move(*args, **kwargs):
        # Sigma2 has already performed two F-moves at this point, so the
        # outer sigma transaction must undo more than the failing R call.
        raise RuntimeError("Forced sigma2 R failure.")

    fusion_system._apply_r_move = fail_r_move
    assert_raises(RuntimeError, lambda: fusion_system.sigma(0, 2))

    assert fusion_system.tree.to_ids() == tree_before
    assert fusion_system.basis is basis_before
    assert fusion_system.hilbertSpace.basis is basis_before
    assert np.array_equal(fusion_system.hilbertSpace.state_vector, state_before)
    assert fusion_system.operation_history == []
    assert np.array_equal(
        fusion_system.hilbertSpace.local_braid_operators[0],
        braid_before,
    )
    assert_coherent(fusion_system)


def test_sigma_input_validation():
    """Check invalid IDs, indices, and temporary-basis rejection."""
    fusion_system = FusionSystem(1)

    for value in (True, 1.0, "0"):
        assert_raises(TypeError, lambda value=value: fusion_system.sigma(value, 1))
    for value in (-1, 1):
        assert_raises(ValueError, lambda value=value: fusion_system.sigma(value, 1))
    for value in (True, 1.0, "1"):
        assert_raises(TypeError, lambda value=value: fusion_system.sigma(0, value))
    for value in (-4, 0, 4):
        assert_raises(ValueError, lambda value=value: fusion_system.sigma(0, value))

    fusion_system.apply_f_move((), "right")
    assert_raises(RuntimeError, lambda: fusion_system.sigma(0, 1))


def test_json_gate_sequences():
    """Run all stored one-qubit gates through the physical sigma engine."""
    database = load_braid_database()
    loader = sequenceOperation()

    for gate_name, metadata in database.items():
        if gate_name not in math_constant.GATE_MATRICES:
            continue

        sequence = loader.getSeq(gate_name)
        expected_gate = math_constant.GATE_MATRICES[gate_name]

        assert sequence == metadata["sequence"]
        assert len(sequence) == metadata["braid count"]
        assert all(index in SIGMA_REFERENCES for index in sequence)

        # This matrix comes from physical F/R evolution, while the JSON
        # fidelity describes its logical approximation to the ideal gate.
        actual_gate = effective_matrix(sequence)
        fidelity = operator_fidelity(actual_gate, expected_gate)
        initial_state = np.array([1.0, 0.0], dtype=complex)
        ideal_output = expected_gate @ initial_state
        actual_output = actual_gate @ initial_state
        expected_state_fidelity = abs(
            np.vdot(ideal_output, actual_output)
        ) ** 2

        assert np.isclose(
            fidelity * 100,
            metadata["gate fidelity"],
            atol=0.0001,
        )

        fusion_system = FusionSystem(1)
        fusion_system.hilbertSpace.add_ideal_operation(gate_name, 0)
        for sigma_index in sequence:
            fusion_system.sigma(0, sigma_index)

        assert np.isclose(
            fusion_system.hilbertSpace.state_fidelity(),
            expected_state_fidelity,
        )
        assert len(fusion_system.operation_history) == len(sequence)
        assert np.isclose(
            np.linalg.norm(fusion_system.hilbertSpace.state_vector),
            1.0,
        )
        assert_coherent(fusion_system)


def main():
    """Run all section 14 checks."""
    test_sigma_reference_matrices()
    print("Sigma reference matrices: PASS")
    test_sigma_inverse_restores_system()
    print("Sigma inverse restoration: PASS")
    test_sigma_records_one_operation()
    print("Single SIGMA history entry: PASS")
    test_sigma2_failure_rolls_back_system()
    print("Sigma2 rollback: PASS")
    test_sigma_input_validation()
    print("Sigma input validation: PASS")
    test_json_gate_sequences()
    print("JSON gate sequences and fidelity: PASS")
    print("All section 14 single-qubit sigma tests passed.")


if __name__ == "__main__":
    main()
