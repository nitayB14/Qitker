import sys
from pathlib import Path

import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent)
)

from qitker.QuantumMath.constant import math_constant
from qitker.anyons.Anyon import Charge
from qitker.anyons.FusionSystem import FusionSystem


def assert_raises(expected_exception, function):
    try:
        function()
    except expected_exception:
        return

    raise AssertionError(
        f"Expected {expected_exception.__name__} to be raised."
    )


def basis_index_for_parent_charge(
    fusion_system,
    parent_path,
    charge,
):
    return next(
        index
        for index, state in enumerate(
            fusion_system.basis.states
        )
        if state["labels"][parent_path] is charge
    )


def test_r_symbol_constants():
    assert np.isclose(
        math_constant.R_VACUUM,
        np.exp(-4j * np.pi / 5),
    )
    assert np.isclose(
        math_constant.R_TAU,
        np.exp(3j * np.pi / 5),
    )
    assert np.allclose(
        math_constant.R,
        np.diag([
            math_constant.R_VACUUM,
            math_constant.R_TAU,
        ]),
    )


def test_r_phase_for_channel(charge, expected_phase):
    fusion_system = FusionSystem(1)
    parent_path = fusion_system.basis.qubit_paths[0][
        "left_pair"
    ]
    old_index = basis_index_for_parent_charge(
        fusion_system,
        parent_path,
        charge,
    )
    old_state = fusion_system.basis.get_state(old_index)

    fusion_system.hilbertSpace.state_vector[:] = 0
    fusion_system.hilbertSpace.state_vector[old_index] = 1

    step = fusion_system._apply_r_move(1, 2)

    new_index = fusion_system.basis.get_index(old_state)
    expected_state = np.zeros(2, dtype=complex)
    expected_state[new_index] = expected_phase

    assert np.allclose(
        fusion_system.hilbertSpace.state_vector,
        expected_state,
    )
    assert fusion_system.get_current_anyon_order() == (
        2, 1, 3, 4,
    )
    assert step["type"] == "R"
    assert step["inverse"] is False
    assert step["parent_path"] == parent_path
    assert step["tree_before"] != step["tree_after"]
    assert fusion_system.operation_history == []


def test_inverse_r_phase_for_channel(
    charge,
    expected_phase,
):
    fusion_system = FusionSystem(1)
    parent_path = fusion_system.basis.qubit_paths[0][
        "left_pair"
    ]
    old_index = basis_index_for_parent_charge(
        fusion_system,
        parent_path,
        charge,
    )
    old_state = fusion_system.basis.get_state(old_index)

    fusion_system.hilbertSpace.state_vector[:] = 0
    fusion_system.hilbertSpace.state_vector[old_index] = 1

    step = fusion_system._apply_r_move(
        1,
        2,
        inverse=True,
    )

    new_index = fusion_system.basis.get_index(old_state)
    expected_state = np.zeros(2, dtype=complex)
    expected_state[new_index] = np.conjugate(
        expected_phase
    )

    assert np.allclose(
        fusion_system.hilbertSpace.state_vector,
        expected_state,
    )
    assert step["inverse"] is True


def test_r_preserves_norm_in_physical_space():
    fusion_system = FusionSystem(2)
    dimension = len(fusion_system.basis.states)

    state = np.arange(
        1,
        dimension + 1,
        dtype=complex,
    )
    state += 1j * np.arange(
        dimension,
        dtype=complex,
    )
    state /= np.linalg.norm(state)

    fusion_system.hilbertSpace.state_vector = state.copy()
    fusion_system._apply_r_move(3, 4)

    assert fusion_system.hilbertSpace.state_vector.shape == (
        13,
    )
    assert np.isclose(
        np.linalg.norm(
            fusion_system.hilbertSpace.state_vector
        ),
        1.0,
    )
    assert fusion_system.basis.tree_signature == (
        fusion_system.tree.to_ids()
    )
    assert (
        fusion_system.hilbertSpace.basis
        is fusion_system.basis
    )


def test_r_then_inverse_restores_system():
    fusion_system = FusionSystem(2)
    dimension = len(fusion_system.basis.states)

    state = np.arange(
        1,
        dimension + 1,
        dtype=complex,
    )
    state += 1j * np.arange(
        dimension - 1,
        -1,
        -1,
        dtype=complex,
    )
    state /= np.linalg.norm(state)

    fusion_system.hilbertSpace.state_vector = state.copy()
    initial_tree = fusion_system.tree.to_ids()

    fusion_system._apply_r_move(3, 4)
    fusion_system._apply_r_move(
        3,
        4,
        inverse=True,
    )

    assert fusion_system.tree.to_ids() == initial_tree
    assert fusion_system.basis.tree_signature == initial_tree
    assert np.allclose(
        fusion_system.hilbertSpace.state_vector,
        state,
    )
    assert fusion_system.operation_history == []


def test_invalid_r_move_rolls_back():
    fusion_system = FusionSystem(2)
    tree_before = fusion_system.tree.to_ids()
    basis_before = fusion_system.basis
    state_before = (
        fusion_system.hilbertSpace.state_vector.copy()
    )

    assert_raises(
        ValueError,
        lambda: fusion_system._apply_r_move(4, 5),
    )

    assert fusion_system.tree.to_ids() == tree_before
    assert fusion_system.basis is basis_before
    assert fusion_system.hilbertSpace.basis is basis_before
    assert np.array_equal(
        fusion_system.hilbertSpace.state_vector,
        state_before,
    )
    assert fusion_system.operation_history == []


def test_r_input_validation():
    fusion_system = FusionSystem(1)
    parent_path = fusion_system.basis.qubit_paths[0][
        "left_pair"
    ]

    assert_raises(
        TypeError,
        lambda: fusion_system._apply_r_move(
            1,
            2,
            inverse=1,
        ),
    )
    assert_raises(
        TypeError,
        lambda: fusion_system.hilbertSpace.state_vector_after_r(
            list(parent_path)
        ),
    )
    assert_raises(
        TypeError,
        lambda: fusion_system.hilbertSpace.state_vector_after_r(
            parent_path,
            inverse=1,
        ),
    )
    assert_raises(
        ValueError,
        lambda: fusion_system.hilbertSpace.state_vector_after_r(
            (9, 9),
        ),
    )


def main():
    test_r_symbol_constants()
    print("R-symbol constants: PASS")

    test_r_phase_for_channel(
        Charge.VACUUM,
        math_constant.R_VACUUM,
    )
    print("R VACUUM channel: PASS")

    test_r_phase_for_channel(
        Charge.TAU,
        math_constant.R_TAU,
    )
    print("R TAU channel: PASS")

    test_inverse_r_phase_for_channel(
        Charge.VACUUM,
        math_constant.R_VACUUM,
    )
    test_inverse_r_phase_for_channel(
        Charge.TAU,
        math_constant.R_TAU,
    )
    print("Inverse R channels: PASS")

    test_r_preserves_norm_in_physical_space()
    print("Physical-space norm: PASS")

    test_r_then_inverse_restores_system()
    print("R inverse restoration: PASS")

    test_invalid_r_move_rolls_back()
    print("Invalid R rollback: PASS")

    test_r_input_validation()
    print("R input validation: PASS")

    print("All section 11 quantum R-move tests passed.")


if __name__ == "__main__":
    main()
