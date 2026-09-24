"""Section 16: global sigma indexing and local-sigma routing tests."""

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
    """Capture the observable state needed for no-mutation checks."""
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
    """Check that a rejected global sigma did not mutate the system."""
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


def test_global_index_validation():
    """Accept exactly the nonzero global generators ±1..±(4n-1)."""
    fusion_system = FusionSystem(2)

    for index in range(1, 8):
        fusion_system._validate_global_sigma_input(index)
        fusion_system._validate_global_sigma_input(-index)

    for invalid_index in (True, False, 1.0, "1", None):
        assert_raises(
            TypeError,
            lambda value=invalid_index: (
                fusion_system._validate_global_sigma_input(value)
            ),
        )

    for invalid_index in (0, 8, -8, 100, -100):
        assert_raises(
            ValueError,
            lambda value=invalid_index: (
                fusion_system._validate_global_sigma_input(value)
            ),
        )


def test_global_to_local_mapping():
    """Map every non-boundary global generator to its local qubit pair."""
    fusion_system = FusionSystem(4)

    expected_mappings = {
        1: (0, 1),
        2: (0, 2),
        3: (0, 3),
        5: (1, 1),
        6: (1, 2),
        7: (1, 3),
        9: (2, 1),
        10: (2, 2),
        11: (2, 3),
        13: (3, 1),
        14: (3, 2),
        15: (3, 3),
    }

    for global_index, expected in expected_mappings.items():
        assert (
            fusion_system._global_to_local_sigma(global_index)
            == expected
        )

        expected_qubit, expected_local = expected
        assert (
            fusion_system._global_to_local_sigma(-global_index)
            == (expected_qubit, -expected_local)
        )


def test_cross_qubit_indices_cannot_be_mapped_locally():
    """Recognize every four-anyon boundary as a cross-qubit braid."""
    fusion_system = FusionSystem(4)

    for index in (4, -4, 8, -8, 12, -12):
        assert_raises(
            ValueError,
            lambda value=index: (
                fusion_system._global_to_local_sigma(value)
            ),
        )


def run_sigma_on_basis_state(use_global, index, input_index):
    """Apply a global or equivalent local sigma to one 13D basis state."""
    fusion_system = FusionSystem(2)
    fusion_system.hilbertSpace.state_vector[:] = 0
    fusion_system.hilbertSpace.state_vector[input_index] = 1

    if use_global:
        fusion_system.sigma_global(index)
    else:
        absolute_index = abs(index)
        qubit_id = (absolute_index - 1) // 4
        local_index = ((absolute_index - 1) % 4) + 1

        if index < 0:
            local_index = -local_index

        fusion_system.sigma(qubit_id, local_index)

    fusion_system._validate_system_coherence()
    return fusion_system


def test_global_sigma_matches_local_sigma_in_full_13d_space():
    """Compare global routing with local sigma on every physical state."""
    dimension = len(FusionSystem(2).basis.states)

    for global_index in (
        1, -1, 2, -2, 3, -3,
        5, -5, 6, -6, 7, -7,
    ):
        for input_index in range(dimension):
            global_system = run_sigma_on_basis_state(
                True,
                global_index,
                input_index,
            )
            local_system = run_sigma_on_basis_state(
                False,
                global_index,
                input_index,
            )

            assert (
                global_system.tree.to_ids()
                == local_system.tree.to_ids()
            )
            assert (
                global_system.get_current_anyon_order()
                == local_system.get_current_anyon_order()
            )
            assert np.allclose(
                global_system.hilbertSpace.state_vector,
                local_system.hilbertSpace.state_vector,
            )
            assert (
                global_system.hilbertSpace.local_braid_operators[0]
                == local_system.hilbertSpace.local_braid_operators[0]
            ).all()
            assert (
                global_system.hilbertSpace.local_braid_operators[1]
                == local_system.hilbertSpace.local_braid_operators[1]
            ).all()


def test_global_sigma_five_routes_to_second_qubit_sigma_one():
    """Document the intended sigma5 -> q[1] local sigma1 conversion."""
    fusion_system = FusionSystem(2)
    fusion_system.sigma_global(5)

    assert len(fusion_system.operation_history) == 1

    operation = fusion_system.operation_history[0]
    assert operation.operation_type == "SIGMA"
    assert operation.parameters["qubit_id"] == 1
    assert operation.parameters["sigma_index"] == 1
    assert operation.parameters["first_id"] == 5
    assert operation.parameters["second_id"] == 6


def test_cross_qubit_sigma_four_is_supported():
    """Check that the global API executes sigma4 coherently."""
    fusion_system = FusionSystem(2)
    order_before = fusion_system.get_current_anyon_order()
    norm_before = np.linalg.norm(
        fusion_system.hilbertSpace.state_vector
    )

    fusion_system.sigma_global(4)

    expected_order = list(order_before)
    expected_order[3], expected_order[4] = (
        expected_order[4],
        expected_order[3],
    )

    assert fusion_system.get_current_anyon_order() == tuple(expected_order)
    assert fusion_system.basis.classify_logical is True
    assert fusion_system.hilbertSpace.dimension == 13
    assert np.isclose(
        np.linalg.norm(fusion_system.hilbertSpace.state_vector),
        norm_before,
    )
    fusion_system._validate_system_coherence()


def test_future_cross_qubit_boundaries_use_global_engine():
    """Check sigma8 and sigma12 through the same global API path."""
    for qubits_num, index in ((3, 8), (4, 12)):
        fusion_system = FusionSystem(qubits_num)
        order_before = fusion_system.get_current_anyon_order()
        norm_before = np.linalg.norm(
            fusion_system.hilbertSpace.state_vector
        )

        fusion_system.sigma_global(index)

        expected_order = list(order_before)
        expected_order[index - 1], expected_order[index] = (
            expected_order[index],
            expected_order[index - 1],
        )

        assert fusion_system.get_current_anyon_order() == tuple(expected_order)
        assert fusion_system.basis.classify_logical is True
        assert np.isclose(
            np.linalg.norm(fusion_system.hilbertSpace.state_vector),
            norm_before,
        )
        fusion_system._validate_system_coherence()


def test_global_sigma_rejects_temporary_logical_topology():
    """Reject global braiding while logical block metadata is unavailable."""
    fusion_system = FusionSystem(2)
    fusion_system.apply_f_move((), "right")

    assert fusion_system.basis.classify_logical is False
    snapshot = capture_system_state(fusion_system)

    assert_raises(
        RuntimeError,
        lambda: fusion_system.sigma_global(1),
    )

    assert_system_state_unchanged(
        fusion_system,
        snapshot,
    )


def main():
    """Run all section 16 global-sigma API checks."""
    test_global_index_validation()
    print("Global sigma validation: PASS")

    test_global_to_local_mapping()
    print("Global-to-local mapping: PASS")

    test_cross_qubit_indices_cannot_be_mapped_locally()
    print("Cross-qubit boundary recognition: PASS")

    test_global_sigma_matches_local_sigma_in_full_13d_space()
    print("Global/local full 13D equivalence: PASS")

    test_global_sigma_five_routes_to_second_qubit_sigma_one()
    print("Sigma5 routing: PASS")

    test_cross_qubit_sigma_four_is_supported()
    print("Sigma4 global execution: PASS")

    test_future_cross_qubit_boundaries_use_global_engine()
    print("Future boundary execution: PASS")

    test_global_sigma_rejects_temporary_logical_topology()
    print("Temporary-topology rejection: PASS")

    print("All section 16 global-sigma API tests passed.")


if __name__ == "__main__":
    main()
