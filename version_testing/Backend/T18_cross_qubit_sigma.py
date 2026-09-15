"""Section 18: physical cross-qubit sigma operations in fusion space."""

import sys
from pathlib import Path

import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent)
)

from qitker.anyons.Anyon import Charge
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
    """Capture all state restored by a failed global sigma transaction."""
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


def assert_exactly_restored(fusion_system, snapshot):
    """Check exact rollback, including basis object identity."""
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


def expected_swapped_order(order, global_index):
    """Return an order with exactly positions i and i+1 exchanged."""
    expected = list(order)
    left = global_index - 1
    right = global_index
    expected[left], expected[right] = expected[right], expected[left]
    return tuple(expected)


def effective_operator(word):
    """Build a 13x13 operator from physical evolution for testing only."""
    dimension = len(FusionSystem(2).basis.states)
    columns = []
    final_tree = None
    final_order = None

    for input_index in range(dimension):
        fusion_system = FusionSystem(2)
        fusion_system.hilbertSpace.state_vector[:] = 0
        fusion_system.hilbertSpace.state_vector[input_index] = 1

        for index in word:
            fusion_system.sigma_global(index)

        fusion_system._validate_system_coherence()
        assert fusion_system.basis.classify_logical is True
        assert np.isclose(
            np.linalg.norm(fusion_system.hilbertSpace.state_vector),
            1.0,
        )

        if final_tree is None:
            final_tree = fusion_system.tree.to_ids()
            final_order = fusion_system.get_current_anyon_order()
        else:
            assert fusion_system.tree.to_ids() == final_tree
            assert fusion_system.get_current_anyon_order() == final_order

        columns.append(
            fusion_system.hilbertSpace.state_vector.copy()
        )

    return np.column_stack(columns), final_tree, final_order


def test_sigma_four_basic_physical_action():
    """Apply sigma4 to the initial two-qubit physical state."""
    fusion_system = FusionSystem(2)
    tree_before = fusion_system.tree.to_ids()
    order_before = fusion_system.get_current_anyon_order()
    norm_before = np.linalg.norm(
        fusion_system.hilbertSpace.state_vector
    )

    fusion_system.sigma_global(4)

    assert fusion_system.hilbertSpace.dimension == 13
    assert fusion_system.hilbertSpace.state_vector.shape == (13,)
    assert fusion_system.get_current_anyon_order() == expected_swapped_order(
        order_before,
        4,
    )
    assert fusion_system.tree.to_ids() != tree_before
    assert fusion_system.basis.classify_logical is True
    assert fusion_system.basis._total_charge is Charge.VACUUM
    assert all(
        state["total"] is Charge.VACUUM
        for state in fusion_system.basis.states
    )
    assert np.isclose(
        np.linalg.norm(fusion_system.hilbertSpace.state_vector),
        norm_before,
    )
    fusion_system._validate_system_coherence()


def test_sigma_four_is_unitary_on_full_physical_space():
    """Check sigma4 and its inverse as complete 13D operators."""
    sigma_four, _, _ = effective_operator([4])
    sigma_four_inverse, _, _ = effective_operator([-4])
    identity = np.eye(13, dtype=complex)

    assert np.allclose(
        sigma_four.conj().T @ sigma_four,
        identity,
    )
    assert np.allclose(
        sigma_four @ sigma_four.conj().T,
        identity,
    )
    assert np.allclose(
        sigma_four_inverse,
        sigma_four.conj().T,
    )


def test_sigma_four_inverse_restores_every_basis_state():
    """Check both inverse orders on all computational and leakage states."""
    identity = np.eye(13, dtype=complex)

    positive_then_inverse, tree_a, order_a = effective_operator([4, -4])
    inverse_then_positive, tree_b, order_b = effective_operator([-4, 4])
    initial = FusionSystem(2)

    assert np.allclose(positive_then_inverse, identity)
    assert np.allclose(inverse_then_positive, identity)
    assert tree_a == initial.tree.to_ids()
    assert tree_b == initial.tree.to_ids()
    assert order_a == initial.get_current_anyon_order()
    assert order_b == initial.get_current_anyon_order()


def test_sigma_four_inverse_restores_complex_superposition():
    """Restore a normalized nontrivial 13D state and tree."""
    fusion_system = FusionSystem(2)
    random_generator = np.random.default_rng(1804)
    initial_state = (
        random_generator.normal(size=13)
        + 1j * random_generator.normal(size=13)
    )
    initial_state /= np.linalg.norm(initial_state)
    fusion_system.hilbertSpace.state_vector = initial_state.copy()
    tree_before = fusion_system.tree.to_ids()
    order_before = fusion_system.get_current_anyon_order()

    fusion_system.sigma_global(4)
    fusion_system.sigma_global(-4)

    assert np.allclose(
        fusion_system.hilbertSpace.state_vector,
        initial_state,
    )
    assert fusion_system.tree.to_ids() == tree_before
    assert fusion_system.get_current_anyon_order() == order_before
    assert len(fusion_system.operation_history) == 2
    fusion_system._validate_system_coherence()


def test_sigma_four_creates_leakage_from_logical_states():
    """Measure computational/leakage mixing for all logical inputs."""
    leakage_probabilities = []

    for logical_label in ("00", "01", "10", "11"):
        fusion_system = FusionSystem(2)
        physical_index = fusion_system.basis.logical_to_physical[
            logical_label
        ]
        fusion_system.hilbertSpace.state_vector[:] = 0
        fusion_system.hilbertSpace.state_vector[physical_index] = 1

        fusion_system.sigma_global(4)

        computational_probability = (
            fusion_system.hilbertSpace.computational_probability()
        )
        leakage_probability = (
            fusion_system.hilbertSpace.leakage_probability()
        )
        leakage_probabilities.append(leakage_probability)

        assert 0.0 <= computational_probability <= 1.0
        assert 0.0 <= leakage_probability <= 1.0
        assert np.isclose(
            computational_probability + leakage_probability,
            1.0,
        )

    assert any(
        probability > 1e-12
        for probability in leakage_probabilities
    )


def test_cross_qubit_history_is_one_global_operation():
    """Hide internal F/R steps and record identities at current positions."""
    fusion_system = FusionSystem(2)
    local_braids_before = [
        operator.copy()
        for operator in fusion_system.hilbertSpace.local_braid_operators
    ]

    fusion_system.sigma_global(4)

    assert len(fusion_system.operation_history) == 1
    first_operation = fusion_system.operation_history[0]
    assert first_operation.operation_type == "SIGMA_GLOBAL"
    assert first_operation.inverse is False
    assert first_operation.parameters["global_index"] == 4
    assert first_operation.parameters["first_id"] == 4
    assert first_operation.parameters["second_id"] == 5
    assert first_operation.parameters["recoupling_steps"]
    assert "Global Sigma: σ4" in fusion_system.get_operation_history()

    for actual, expected in zip(
        fusion_system.hilbertSpace.local_braid_operators,
        local_braids_before,
    ):
        assert np.array_equal(actual, expected)

    fusion_system.sigma_global(-4)

    assert len(fusion_system.operation_history) == 2
    second_operation = fusion_system.operation_history[1]
    assert second_operation.operation_type == "SIGMA_GLOBAL"
    assert second_operation.inverse is True
    assert second_operation.parameters["global_index"] == 4
    assert second_operation.parameters["first_id"] == 5
    assert second_operation.parameters["second_id"] == 4
    assert "Global Sigma: σ4⁻¹" in fusion_system.get_operation_history()


def test_cross_qubit_sigma_rollback_after_r_failure():
    """Roll back the complete operation if R fails after recoupling."""
    fusion_system = FusionSystem(2)
    snapshot = capture_system_state(fusion_system)

    def fail_r_move(*args, **kwargs):
        raise RuntimeError("Forced cross-qubit R failure.")

    fusion_system._apply_r_move = fail_r_move

    assert_raises(
        RuntimeError,
        lambda: fusion_system.sigma_global(4),
    )
    assert_exactly_restored(fusion_system, snapshot)


def test_cross_qubit_sigma_rollback_after_undo_failure():
    """Roll back recoupling and R if the inverse F sequence fails."""
    fusion_system = FusionSystem(2)
    snapshot = capture_system_state(fusion_system)

    def fail_undo(*args, **kwargs):
        raise RuntimeError("Forced cross-qubit undo failure.")

    fusion_system._undo_recoupling = fail_undo

    assert_raises(
        RuntimeError,
        lambda: fusion_system.sigma_global(4),
    )
    assert_exactly_restored(fusion_system, snapshot)


def test_cross_qubit_sigma_rollback_after_history_failure():
    """Roll back physical evolution if recording the operation fails."""
    fusion_system = FusionSystem(2)
    snapshot = capture_system_state(fusion_system)

    def fail_record(*args, **kwargs):
        raise RuntimeError("Forced history failure.")

    fusion_system.record_operation = fail_record

    assert_raises(
        RuntimeError,
        lambda: fusion_system.sigma_global(4),
    )
    assert_exactly_restored(fusion_system, snapshot)


def assert_global_words_equal(left_word, right_word):
    """Compare two braid words on the complete 13D physical basis."""
    left_operator, left_tree, left_order = effective_operator(left_word)
    right_operator, right_tree, right_order = effective_operator(right_word)

    assert np.allclose(left_operator, right_operator)
    assert left_tree == right_tree
    assert left_order == right_order


def test_cross_qubit_yang_baxter_relations():
    """Check braid relations on both sides of the qubit boundary."""
    assert_global_words_equal(
        [3, 4, 3],
        [4, 3, 4],
    )
    assert_global_words_equal(
        [4, 5, 4],
        [5, 4, 5],
    )


def test_future_cross_qubit_generators():
    """Smoke-test sigma8 and sigma12 with the general recoupling engine."""
    for qubits_num, global_index in ((3, 8), (4, 12)):
        fusion_system = FusionSystem(qubits_num)
        order_before = fusion_system.get_current_anyon_order()
        norm_before = np.linalg.norm(
            fusion_system.hilbertSpace.state_vector
        )

        fusion_system.sigma_global(global_index)

        assert fusion_system.get_current_anyon_order() == (
            expected_swapped_order(order_before, global_index)
        )
        assert fusion_system.basis.classify_logical is True
        assert np.isclose(
            np.linalg.norm(fusion_system.hilbertSpace.state_vector),
            norm_before,
        )
        assert len(fusion_system.operation_history) == 1
        fusion_system._validate_system_coherence()

        fusion_system.sigma_global(-global_index)

        assert fusion_system.get_current_anyon_order() == order_before
        assert np.isclose(
            np.linalg.norm(fusion_system.hilbertSpace.state_vector),
            norm_before,
        )
        assert fusion_system.basis.classify_logical is True
        fusion_system._validate_system_coherence()


def test_sigma_four_runtime_report():
    """Print the logical blocks, leakage, and operation data after sigma4."""
    fusion_system = FusionSystem(2)
    initial_label = "00"

    fusion_system.sigma_global(4)

    qubit_blocks = []

    for qubit_id in range(fusion_system.qubits_num):
        block_ids = tuple(
            anyon.get_id()
            for anyon in fusion_system.get_current_qubit_block(
                qubit_id
            )
        )
        qubit_blocks.append(block_ids)

    computational_probability = (
        fusion_system.hilbertSpace.computational_probability()
    )
    leakage_probability = (
        fusion_system.hilbertSpace.leakage_probability()
    )
    operation = fusion_system.operation_history[-1]
    recoupling_steps = operation.parameters["recoupling_steps"]

    assert qubit_blocks == [
        (1, 2, 3, 5),
        (4, 6, 7, 8),
    ]
    assert np.isclose(
        computational_probability + leakage_probability,
        1.0,
    )
    assert operation.operation_type == "SIGMA_GLOBAL"
    assert operation.parameters["global_index"] == 4

    print()
    print("Sigma4 runtime report")
    print(f"  initial logical state:    |{initial_label}>")
    print(f"  current anyon order:      {fusion_system.get_current_anyon_order()}")
    print(f"  logical block q[0]:       {qubit_blocks[0]}")
    print(f"  logical block q[1]:       {qubit_blocks[1]}")
    print(
        "  computational probability: "
        f"{computational_probability:.12f}"
    )
    print(
        "  leakage probability:       "
        f"{leakage_probability:.12f}"
    )
    print(f"  recoupling F-moves:       {recoupling_steps}")
    print("  operation history:")

    for line in fusion_system.get_operation_history().splitlines():
        print(f"    {line}")


def main():
    """Run all section 18 cross-qubit sigma checks."""
    test_sigma_four_basic_physical_action()
    print("Sigma4 physical action: PASS")

    test_sigma_four_is_unitary_on_full_physical_space()
    print("Sigma4 full 13D unitarity: PASS")

    test_sigma_four_inverse_restores_every_basis_state()
    print("Sigma4 basis-state inverses: PASS")

    test_sigma_four_inverse_restores_complex_superposition()
    print("Sigma4 superposition inverse: PASS")

    test_sigma_four_creates_leakage_from_logical_states()
    print("Sigma4 computational/leakage mixing: PASS")

    test_cross_qubit_history_is_one_global_operation()
    print("Cross-qubit operation history: PASS")

    test_cross_qubit_sigma_rollback_after_r_failure()
    print("Cross-qubit R rollback: PASS")

    test_cross_qubit_sigma_rollback_after_undo_failure()
    print("Cross-qubit undo rollback: PASS")

    test_cross_qubit_sigma_rollback_after_history_failure()
    print("Cross-qubit history rollback: PASS")

    test_cross_qubit_yang_baxter_relations()
    print("Cross-qubit Yang-Baxter relations: PASS")

    test_future_cross_qubit_generators()
    print("Future sigma8/sigma12 generators: PASS")

    test_sigma_four_runtime_report()
    print("Sigma4 runtime report: PASS")

    print("All section 18 cross-qubit sigma tests passed.")


if __name__ == "__main__":
    main()
