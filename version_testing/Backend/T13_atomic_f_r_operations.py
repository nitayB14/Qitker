"""Section 13: verify that F/R update the whole physical system atomically."""

import sys
from pathlib import Path

import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent)
)

from qitker.anyons.FusionSystem import FusionSystem


def assert_raises(expected_exception, function):
    """Verify that calling function raises the expected exception."""
    try:
        function()
    except expected_exception:
        return

    raise AssertionError(
        f"Expected {expected_exception.__name__} to be raised."
    )


def assert_coherent(fusion_system):
    """Check the shared tree, basis, and HilbertSpace invariants."""
    fusion_system._validate_system_coherence()
    assert fusion_system.basis.tree_signature == (
        fusion_system.tree.to_ids()
    )
    assert fusion_system.hilbertSpace.basis is fusion_system.basis
    assert fusion_system.hilbertSpace.dimension == len(
        fusion_system.basis.states
    )
    assert fusion_system.hilbertSpace.state_vector.shape == (
        fusion_system.hilbertSpace.dimension,
    )


def normalized_physical_state(dimension):
    """Create a deterministic normalized complex statevector."""
    state = np.arange(1, dimension + 1, dtype=complex)
    state += 1j * np.arange(dimension, dtype=complex)
    return state / np.linalg.norm(state)


def test_public_r_move_commits_and_records():
    """Check that public R updates the full system and records one step."""
    fusion_system = FusionSystem(2)
    initial_basis = fusion_system.basis
    initial_norm = np.linalg.norm(
        fusion_system.hilbertSpace.state_vector
    )

    result = fusion_system.apply_r_move(3, 4)

    assert result is None
    assert fusion_system.basis is not initial_basis
    assert fusion_system.get_current_anyon_order() == (
        1, 2, 4, 3, 5, 6, 7, 8,
    )
    assert np.isclose(
        np.linalg.norm(fusion_system.hilbertSpace.state_vector),
        initial_norm,
    )
    assert len(fusion_system.operation_history) == 1

    operation = fusion_system.operation_history[0]
    assert operation.operation_type == "R_MOVE"
    assert operation.inverse is False
    assert operation.parameters["first_id"] == 3
    assert operation.parameters["second_id"] == 4
    assert "R | anyons: 3, 4" in (
        fusion_system.get_operation_history()
    )
    assert_coherent(fusion_system)


def test_public_f_move_commits_and_records():
    """Check that public F updates the full system and records one step."""
    fusion_system = FusionSystem(2)
    initial_basis = fusion_system.basis

    result = fusion_system.apply_f_move((), "right")

    assert result is None
    assert fusion_system.basis is not initial_basis
    assert fusion_system.basis.classify_logical is False
    assert len(fusion_system.operation_history) == 1

    operation = fusion_system.operation_history[0]
    assert operation.operation_type == "F_MOVE"
    assert operation.parameters["path"] == ()
    assert operation.parameters["direction"] == "right"
    assert "F | path: () | direction: right" in (
        fusion_system.get_operation_history()
    )
    assert_coherent(fusion_system)


def test_failed_public_operation_restores_history_and_state():
    """Check rollback of tree, basis, vector, and history on failure."""
    fusion_system = FusionSystem(2)
    fusion_system.apply_r_move(1, 2)

    tree_before = fusion_system.tree.to_ids()
    basis_before = fusion_system.basis
    state_before = fusion_system.hilbertSpace.state_vector.copy()
    history_before = fusion_system.operation_history.copy()

    assert_raises(
        ValueError,
        lambda: fusion_system.apply_r_move(4, 5),
    )

    assert fusion_system.tree.to_ids() == tree_before
    assert fusion_system.basis is basis_before
    assert fusion_system.hilbertSpace.basis is basis_before
    assert np.array_equal(
        fusion_system.hilbertSpace.state_vector,
        state_before,
    )
    assert fusion_system.operation_history == history_before
    assert_coherent(fusion_system)


def test_history_failure_rolls_back_completed_move():
    """Check rollback when history recording fails after a physical move."""
    fusion_system = FusionSystem(1)
    tree_before = fusion_system.tree.to_ids()
    basis_before = fusion_system.basis
    state_before = fusion_system.hilbertSpace.state_vector.copy()

    def fail_record(operation):
        # Fail after mutation to verify that the outer transaction also
        # restores history, rather than only the physical state.
        fusion_system.operation_history.append(operation)
        raise RuntimeError("Forced history failure.")

    fusion_system.record_operation = fail_record

    assert_raises(
        RuntimeError,
        lambda: fusion_system.apply_r_move(1, 2),
    )

    assert fusion_system.tree.to_ids() == tree_before
    assert fusion_system.basis is basis_before
    assert fusion_system.hilbertSpace.basis is basis_before
    assert np.array_equal(
        fusion_system.hilbertSpace.state_vector,
        state_before,
    )
    assert fusion_system.operation_history == []
    assert_coherent(fusion_system)


def test_r_inside_temporary_f_basis():
    """Check that R remains physical while logical classification is absent."""
    fusion_system = FusionSystem(1)

    # These rotations expose anyons 2 and 3 as siblings. During this
    # recoupling the tree no longer represents a logical four-anyon block.
    fusion_system.apply_f_move((), "right")
    fusion_system.apply_f_move((1,), "left")

    assert fusion_system.tree.is_siblings(2, 3)
    assert fusion_system.basis.classify_logical is False

    fusion_system.apply_r_move(2, 3)

    assert fusion_system.basis.classify_logical is False
    assert fusion_system.get_current_anyon_order() == (1, 3, 2, 4)
    assert np.isclose(
        np.linalg.norm(fusion_system.hilbertSpace.state_vector),
        1.0,
    )
    assert_coherent(fusion_system)


def test_atomic_f_r_sequence_and_inverse_restore_system():
    """Check a composed F/R sequence and its exact inverse."""
    fusion_system = FusionSystem(1)
    initial_tree = fusion_system.tree.to_ids()
    initial_state = normalized_physical_state(2)
    fusion_system.hilbertSpace.state_vector = initial_state.copy()

    fusion_system.apply_f_move((), "right")
    fusion_system.apply_f_move((1,), "left")
    fusion_system.apply_r_move(2, 3)
    fusion_system.apply_r_move(2, 3, inverse=True)
    fusion_system.apply_f_move((1,), "right")
    fusion_system.apply_f_move((), "left")

    assert fusion_system.tree.to_ids() == initial_tree
    assert fusion_system.basis.classify_logical is True
    assert np.allclose(
        fusion_system.hilbertSpace.state_vector,
        initial_state,
    )
    assert len(fusion_system.operation_history) == 6
    assert_coherent(fusion_system)


def test_coherence_validation_detects_mismatch():
    """Check that explicit coherence validation rejects bad metadata."""
    fusion_system = FusionSystem(1)
    fusion_system.hilbertSpace.dimension += 1

    assert_raises(
        RuntimeError,
        fusion_system._validate_system_coherence,
    )


def main():
    """Run all section 13 atomic-operation checks."""
    test_public_r_move_commits_and_records()
    print("Public atomic R: PASS")

    test_public_f_move_commits_and_records()
    print("Public atomic F: PASS")

    test_failed_public_operation_restores_history_and_state()
    print("Operation rollback: PASS")

    test_history_failure_rolls_back_completed_move()
    print("History rollback: PASS")

    test_r_inside_temporary_f_basis()
    print("R in temporary F basis: PASS")

    test_atomic_f_r_sequence_and_inverse_restore_system()
    print("Composed F/R inverse: PASS")

    test_coherence_validation_detects_mismatch()
    print("Coherence validation: PASS")

    print("All section 13 atomic F/R tests passed.")


if __name__ == "__main__":
    main()
