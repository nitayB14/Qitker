"""Section 17: dynamic recoupling of adjacent anyons with F-moves."""

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


def capture_system_state(fusion_system):
    """Capture all state that a failed recoupling must preserve."""
    return {
        "tree": fusion_system.tree.to_ids(),
        "order": fusion_system.get_current_anyon_order(),
        "basis": fusion_system.basis,
        "hilbert_basis": fusion_system.hilbertSpace.basis,
        "state_vector": fusion_system.hilbertSpace.state_vector.copy(),
        "dimension": fusion_system.hilbertSpace.dimension,
        "history": list(fusion_system.operation_history),
        "local_braids": [
            operator.copy()
            for operator in (
                fusion_system.hilbertSpace.local_braid_operators
            )
        ],
    }


def assert_system_state_unchanged(fusion_system, snapshot):
    """Check exact restoration after rejection or rollback."""
    assert fusion_system.tree.to_ids() == snapshot["tree"]
    assert fusion_system.get_current_anyon_order() == snapshot["order"]
    assert fusion_system.basis is snapshot["basis"]
    assert fusion_system.hilbertSpace.basis is snapshot["hilbert_basis"]
    assert fusion_system.hilbertSpace.dimension == snapshot["dimension"]
    assert np.array_equal(
        fusion_system.hilbertSpace.state_vector,
        snapshot["state_vector"],
    )
    assert fusion_system.operation_history == snapshot["history"]

    for actual, expected in zip(
        fusion_system.hilbertSpace.local_braid_operators,
        snapshot["local_braids"],
    ):
        assert np.array_equal(actual, expected)

    fusion_system._validate_system_coherence()


def assert_system_state_equivalent(fusion_system, snapshot):
    """Check physical restoration when a fresh equivalent basis is valid."""
    assert fusion_system.tree.to_ids() == snapshot["tree"]
    assert fusion_system.get_current_anyon_order() == snapshot["order"]
    assert fusion_system.basis.tree_signature == snapshot["tree"]
    assert fusion_system.hilbertSpace.basis is fusion_system.basis
    assert fusion_system.hilbertSpace.dimension == snapshot["dimension"]
    assert np.allclose(
        fusion_system.hilbertSpace.state_vector,
        snapshot["state_vector"],
    )
    assert fusion_system.operation_history == snapshot["history"]

    for actual, expected in zip(
        fusion_system.hilbertSpace.local_braid_operators,
        snapshot["local_braids"],
    ):
        assert np.array_equal(actual, expected)

    fusion_system._validate_system_coherence()


def boundary_ids(fusion_system, position):
    """Return identities at adjacent one-based physical positions."""
    first_id = (
        fusion_system
        .get_anyon_at_position(position)
        .get_id()
    )
    second_id = (
        fusion_system
        .get_anyon_at_position(position + 1)
        .get_id()
    )
    return first_id, second_id


def test_adjacent_anyon_validation():
    """Accept only distinct adjacent identities in left-to-right order."""
    fusion_system = FusionSystem(2)

    fusion_system._validate_adjacent_anyons(4, 5)

    for first_id, second_id in (
        (4, 4),
        (3, 5),
        (5, 4),
        (1, 8),
    ):
        snapshot = capture_system_state(fusion_system)
        assert_raises(
            ValueError,
            lambda first=first_id, second=second_id: (
                fusion_system._validate_adjacent_anyons(
                    first,
                    second,
                )
            ),
        )
        assert_system_state_unchanged(fusion_system, snapshot)

    for first_id, second_id in (
        (True, 2),
        (1, False),
        (1.0, 2),
        (1, "2"),
    ):
        snapshot = capture_system_state(fusion_system)
        assert_raises(
            TypeError,
            lambda first=first_id, second=second_id: (
                fusion_system._validate_adjacent_anyons(
                    first,
                    second,
                )
            ),
        )
        assert_system_state_unchanged(fusion_system, snapshot)

    for first_id, second_id in ((0, 1), (8, 9)):
        snapshot = capture_system_state(fusion_system)
        assert_raises(
            ValueError,
            lambda first=first_id, second=second_id: (
                fusion_system._validate_adjacent_anyons(
                    first,
                    second,
                )
            ),
        )
        assert_system_state_unchanged(fusion_system, snapshot)


def test_lca_paths_for_different_tree_shapes():
    """Find boundary LCAs dynamically in two-, three-, and four-qubit trees."""
    two_qubits = FusionSystem(2)
    assert two_qubits._find_lca_path(4, 5) == ()
    assert two_qubits._find_lca_path(3, 4) == (0, 1)
    assert two_qubits._find_lca_path(5, 6) == (1, 0)

    three_qubits = FusionSystem(3)
    assert three_qubits._find_lca_path(4, 5) == (0,)
    assert three_qubits._find_lca_path(8, 9) == ()

    four_qubits = FusionSystem(4)
    assert four_qubits._find_lca_path(4, 5) == (0,)
    assert four_qubits._find_lca_path(8, 9) == ()
    assert four_qubits._find_lca_path(12, 13) == (1,)


def test_sigma_four_recoupling_sequence():
    """Check the known initial path while keeping the algorithm dynamic."""
    fusion_system = FusionSystem(2)
    history_before = list(fusion_system.operation_history)

    steps = fusion_system._recouple_adjacent_anyons(4, 5)

    assert steps == (
        ((), "right"),
        ((1,), "right"),
        ((1, 1), "left"),
        ((1, 1, 0), "left"),
    )
    assert fusion_system.tree.is_siblings(4, 5)
    assert fusion_system.get_current_anyon_order() == (
        1, 2, 3, 4, 5, 6, 7, 8,
    )
    assert fusion_system.basis.classify_logical is False
    assert fusion_system.operation_history == history_before
    assert fusion_system.hilbertSpace.dimension == 13
    assert np.isclose(
        np.linalg.norm(fusion_system.hilbertSpace.state_vector),
        1.0,
    )
    fusion_system._validate_system_coherence()


def test_recouple_and_undo_on_every_13d_basis_state():
    """Verify F recoupling inversion on the complete two-qubit space."""
    dimension = len(FusionSystem(2).basis.states)

    for input_index in range(dimension):
        fusion_system = FusionSystem(2)
        fusion_system.hilbertSpace.state_vector[:] = 0
        fusion_system.hilbertSpace.state_vector[input_index] = 1
        snapshot = capture_system_state(fusion_system)

        steps = fusion_system._recouple_adjacent_anyons(4, 5)
        assert fusion_system.tree.is_siblings(4, 5)
        assert np.isclose(
            np.linalg.norm(fusion_system.hilbertSpace.state_vector),
            1.0,
        )

        fusion_system._undo_recoupling(steps)
        assert_system_state_equivalent(fusion_system, snapshot)
        assert fusion_system.basis.classify_logical is True


def test_recouple_and_undo_random_superposition():
    """Check coherent inversion for a nontrivial complex statevector."""
    fusion_system = FusionSystem(2)
    random_generator = np.random.default_rng(1704)
    state = (
        random_generator.normal(size=13)
        + 1j * random_generator.normal(size=13)
    )
    state /= np.linalg.norm(state)
    fusion_system.hilbertSpace.state_vector = state
    snapshot = capture_system_state(fusion_system)

    steps = fusion_system._recouple_adjacent_anyons(4, 5)
    fusion_system._undo_recoupling(steps)

    assert np.allclose(
        fusion_system.hilbertSpace.state_vector,
        snapshot["state_vector"],
    )
    assert fusion_system.tree.to_ids() == snapshot["tree"]
    assert fusion_system.get_current_anyon_order() == snapshot["order"]
    assert fusion_system.operation_history == snapshot["history"]
    fusion_system._validate_system_coherence()


def test_future_boundary_recoupling():
    """Use the same recoupling engine for sigma4, sigma8, and sigma12 boundaries."""
    cases = (
        (2, 4),
        (3, 4),
        (3, 8),
        (4, 4),
        (4, 8),
        (4, 12),
    )

    for qubits_num, position in cases:
        fusion_system = FusionSystem(qubits_num)
        first_id, second_id = boundary_ids(
            fusion_system,
            position,
        )
        snapshot = capture_system_state(fusion_system)

        steps = fusion_system._recouple_adjacent_anyons(
            first_id,
            second_id,
        )

        assert steps
        assert fusion_system.tree.is_siblings(
            first_id,
            second_id,
        )
        assert fusion_system.basis.classify_logical is False
        assert np.isclose(
            np.linalg.norm(fusion_system.hilbertSpace.state_vector),
            1.0,
        )
        fusion_system._validate_system_coherence()

        fusion_system._undo_recoupling(steps)
        assert_system_state_equivalent(fusion_system, snapshot)


def test_recoupling_uses_current_identities_after_braids():
    """Select boundary identities from positions after earlier local braids."""
    fusion_system = FusionSystem(3)
    fusion_system.sigma(0, 3)
    fusion_system.sigma(1, 1)

    first_id, second_id = boundary_ids(fusion_system, 4)
    assert (first_id, second_id) == (3, 6)
    snapshot = capture_system_state(fusion_system)

    steps = fusion_system._recouple_adjacent_anyons(
        first_id,
        second_id,
    )

    assert fusion_system.tree.is_siblings(
        first_id,
        second_id,
    )
    assert fusion_system.get_current_anyon_order() == snapshot["order"]

    fusion_system._undo_recoupling(steps)
    assert_system_state_equivalent(fusion_system, snapshot)


def test_already_sibling_pair_requires_no_f_moves():
    """Return an empty reversible plan when adjacent anyons are siblings."""
    fusion_system = FusionSystem(2)
    snapshot = capture_system_state(fusion_system)

    steps = fusion_system._recouple_adjacent_anyons(1, 2)

    assert steps == ()
    assert fusion_system.tree.is_siblings(1, 2)
    assert_system_state_unchanged(fusion_system, snapshot)

    fusion_system._undo_recoupling(steps)
    assert_system_state_unchanged(fusion_system, snapshot)


def test_recoupling_failure_rolls_back_full_sequence():
    """Undo earlier successful F-moves when a later F-move fails."""
    fusion_system = FusionSystem(2)
    snapshot = capture_system_state(fusion_system)
    real_apply_f_move = fusion_system._apply_f_move
    calls = 0

    def fail_on_second_f_move(*args, **kwargs):
        nonlocal calls
        calls += 1

        if calls == 2:
            raise RuntimeError("Forced recoupling failure.")

        return real_apply_f_move(*args, **kwargs)

    fusion_system._apply_f_move = fail_on_second_f_move

    assert_raises(
        RuntimeError,
        lambda: fusion_system._recouple_adjacent_anyons(4, 5),
    )

    assert calls == 2
    assert_system_state_unchanged(fusion_system, snapshot)


def test_undo_validation_and_rollback():
    """Reject malformed undo plans without leaving partial changes."""
    malformed_plans = (
        [((), "right")],
        (((),),),
        (("not-a-path", "right"),),
        (((), "clockwise"),),
    )

    for plan in malformed_plans:
        fusion_system = FusionSystem(2)
        snapshot = capture_system_state(fusion_system)
        expected_exception = TypeError if isinstance(plan, list) else ValueError

        if plan == (("not-a-path", "right"),):
            expected_exception = TypeError

        assert_raises(
            expected_exception,
            lambda value=plan: fusion_system._undo_recoupling(value),
        )
        assert_system_state_unchanged(fusion_system, snapshot)

    fusion_system = FusionSystem(2)
    steps = fusion_system._recouple_adjacent_anyons(4, 5)
    recoupled_snapshot = capture_system_state(fusion_system)
    real_apply_f_move = fusion_system._apply_f_move
    calls = 0

    def fail_on_second_undo_move(*args, **kwargs):
        nonlocal calls
        calls += 1

        if calls == 2:
            raise RuntimeError("Forced undo failure.")

        return real_apply_f_move(*args, **kwargs)

    fusion_system._apply_f_move = fail_on_second_undo_move

    assert_raises(
        RuntimeError,
        lambda: fusion_system._undo_recoupling(steps),
    )

    assert calls == 2
    assert_system_state_unchanged(
        fusion_system,
        recoupled_snapshot,
    )


def main():
    """Run all section 17 adjacent-anyon recoupling checks."""
    test_adjacent_anyon_validation()
    print("Adjacent-anyon validation: PASS")

    test_lca_paths_for_different_tree_shapes()
    print("Dynamic LCA paths: PASS")

    test_sigma_four_recoupling_sequence()
    print("Sigma4 recoupling sequence: PASS")

    test_recouple_and_undo_on_every_13d_basis_state()
    print("Full 13D recoupling inversion: PASS")

    test_recouple_and_undo_random_superposition()
    print("Complex superposition inversion: PASS")

    test_future_boundary_recoupling()
    print("Future sigma4/sigma8/sigma12 boundaries: PASS")

    test_recoupling_uses_current_identities_after_braids()
    print("Current-identity recoupling: PASS")

    test_already_sibling_pair_requires_no_f_moves()
    print("Already-sibling no-op: PASS")

    test_recoupling_failure_rolls_back_full_sequence()
    print("Recoupling rollback: PASS")

    test_undo_validation_and_rollback()
    print("Undo validation and rollback: PASS")

    print("All section 17 adjacent-anyon recoupling tests passed.")


if __name__ == "__main__":
    main()
