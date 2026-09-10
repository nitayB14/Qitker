"""Section 12: quantum F-move basis transformations and inverse tests."""

import sys
from pathlib import Path

import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent)
)

from qitker.QuantumMath.constant import math_constant
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


def normalized_physical_state(dimension):
    """Create a deterministic normalized complex statevector for tests."""
    state = np.arange(1, dimension + 1, dtype=complex)
    state += 1j * np.arange(dimension, dtype=complex)
    return state / np.linalg.norm(state)


def test_f_constants_are_unitary():
    """Check that the Fibonacci F matrix is unitary."""
    assert np.allclose(
        math_constant.F @ math_constant.F_inv,
        np.eye(2),
    )
    assert np.allclose(
        math_constant.F.conj().T @ math_constant.F,
        np.eye(2),
    )


def test_temporary_physical_basis():
    """Check behavior when recoupling temporarily removes logical paths."""
    fusion_system = FusionSystem(2)
    step = fusion_system._apply_f_move((), "right")

    assert len(fusion_system.basis.states) == 13
    assert fusion_system.basis.classify_logical is False
    assert fusion_system.basis.qubit_paths == {}
    assert fusion_system.basis.computational_indices == []
    assert fusion_system.basis.leakage_indices == []
    assert_raises(
        RuntimeError,
        fusion_system.hilbertSpace.computational_probability,
    )
    assert_raises(
        RuntimeError,
        fusion_system.hilbertSpace.leakage_probability,
    )
    assert step["type"] == "F"
    assert step["tree_before"] != step["tree_after"]
    assert fusion_system.operation_history == []


def test_f_preserves_norm_and_total_charge():
    """Check that F preserves norm, dimension, and global charge."""
    fusion_system = FusionSystem(2)
    state = normalized_physical_state(13)
    fusion_system.hilbertSpace.state_vector = state.copy()

    fusion_system._apply_f_move((), "right")

    assert np.isclose(
        np.linalg.norm(
            fusion_system.hilbertSpace.state_vector
        ),
        1.0,
    )
    assert len(fusion_system.basis.states) == 13
    assert all(
        basis_state["total"]
        is fusion_system.basis._total_charge
        for basis_state in fusion_system.basis.states
    )
    assert fusion_system.basis.tree_signature == (
        fusion_system.tree.to_ids()
    )
    assert fusion_system.hilbertSpace.basis is fusion_system.basis


def test_nontrivial_f_mixing_occurs():
    """Check that a two-channel F sector mixes its amplitudes."""
    fusion_system = FusionSystem(1)

    # First recoupling is scalar and exposes a three-tau subtree.
    fusion_system._apply_f_move((), "right")
    old_state = fusion_system.hilbertSpace.state_vector.copy()

    fusion_system._apply_f_move((1,), "left")
    new_state = fusion_system.hilbertSpace.state_vector

    assert np.isclose(np.linalg.norm(new_state), 1.0)
    assert np.allclose(
        new_state,
        math_constant.F_inv[:, 0],
    )
    assert not np.allclose(new_state, old_state)


def test_f_sequence_and_inverse_restore_system():
    """Check that an F sequence and its inverse restore tree and state."""
    fusion_system = FusionSystem(2)
    state = normalized_physical_state(13)
    fusion_system.hilbertSpace.state_vector = state.copy()
    initial_tree = fusion_system.tree.to_ids()

    fusion_system._apply_f_move((), "right")
    fusion_system._apply_f_move((1,), "left")
    fusion_system._apply_f_move((1,), "right")
    fusion_system._apply_f_move((), "left")

    assert fusion_system.tree.to_ids() == initial_tree
    assert fusion_system.basis.tree_signature == initial_tree
    assert fusion_system.basis.classify_logical is True
    assert len(fusion_system.basis.computational_indices) == 4
    assert len(fusion_system.basis.leakage_indices) == 9
    assert np.allclose(
        fusion_system.hilbertSpace.state_vector,
        state,
    )


def test_invalid_f_move_rolls_back():
    """Check rollback when F is requested at an invalid subtree."""
    fusion_system = FusionSystem(2)
    tree_before = fusion_system.tree.to_ids()
    basis_before = fusion_system.basis
    state_before = (
        fusion_system.hilbertSpace.state_vector.copy()
    )

    assert_raises(
        ValueError,
        lambda: fusion_system._apply_f_move(
            (0, 0),
            "right",
        ),
    )

    assert fusion_system.tree.to_ids() == tree_before
    assert fusion_system.basis is basis_before
    assert fusion_system.hilbertSpace.basis is basis_before
    assert np.array_equal(
        fusion_system.hilbertSpace.state_vector,
        state_before,
    )
    assert fusion_system.operation_history == []


def test_f_input_validation():
    """Check validation of F paths and rotation directions."""
    fusion_system = FusionSystem(1)

    assert_raises(
        TypeError,
        lambda: fusion_system._apply_f_move(
            [],
            "right",
        ),
    )
    assert_raises(
        ValueError,
        lambda: fusion_system._apply_f_move(
            (),
            "up",
        ),
    )
    assert_raises(
        TypeError,
        lambda: fusion_system.basis.get_charge_at_path(
            fusion_system.basis.states[0],
            [],
        ),
    )


def main():
    """Run all section 12 quantum F-move checks."""
    test_f_constants_are_unitary()
    print("F constants: PASS")

    test_temporary_physical_basis()
    print("Temporary physical basis: PASS")

    test_f_preserves_norm_and_total_charge()
    print("F norm and total charge: PASS")

    test_nontrivial_f_mixing_occurs()
    print("Nontrivial F mixing: PASS")

    test_f_sequence_and_inverse_restore_system()
    print("F inverse restoration: PASS")

    test_invalid_f_move_rolls_back()
    print("Invalid F rollback: PASS")

    test_f_input_validation()
    print("F input validation: PASS")

    print("All section 12 quantum F-move tests passed.")


if __name__ == "__main__":
    main()
