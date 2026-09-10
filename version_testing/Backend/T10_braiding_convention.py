"""Section 10: moving-anyon identity convention and basis reindexing."""

import sys
from pathlib import Path
import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent)
)

from qitker.anyons.FusionSystem import FusionSystem
from qitker.anyons.Anyon import Charge
from qitker.anyons.FusionBasis import FusionBasis


def assert_raises(expected_exception, function):
    """Verify that calling function raises the expected exception."""
    try:
        function()
    except expected_exception:
        return

    raise AssertionError(
        f"Expected {expected_exception.__name__} to be raised."
    )


def block_ids(fusion_system, qubit_id):
    """Return IDs currently occupying a positional four-anyon block."""
    return tuple(
        anyon.get_id()
        for anyon in fusion_system.get_current_qubit_block(
            qubit_id
        )
    )


def test_initial_position_metadata():
    """Check the initial identity order and qubit-block positions."""
    fusion_system = FusionSystem(2)

    assert (
        fusion_system.BRAID_CONVENTION
        == "MOVING_ANYON_IDENTITIES"
    )

    assert fusion_system.get_current_anyon_order() == (
        1, 2, 3, 4, 5, 6, 7, 8,
    )

    assert (
        fusion_system.get_anyon_at_position(4).get_id()
        == 4
    )

    assert block_ids(fusion_system, 0) == (1, 2, 3, 4)
    assert block_ids(fusion_system, 1) == (5, 6, 7, 8)


def test_position_validation():
    """Check validation of one-based anyon-position access."""
    fusion_system = FusionSystem(2)

    assert_raises(
        TypeError,
        lambda: fusion_system.get_anyon_at_position(True),
    )
    assert_raises(
        TypeError,
        lambda: fusion_system.get_anyon_at_position(1.0),
    )
    assert_raises(
        ValueError,
        lambda: fusion_system.get_anyon_at_position(0),
    )
    assert_raises(
        ValueError,
        lambda: fusion_system.get_anyon_at_position(9),
    )

    assert_raises(
        TypeError,
        lambda: fusion_system.get_current_qubit_block(True),
    )
    assert_raises(
        TypeError,
        lambda: fusion_system.get_current_qubit_block("0"),
    )
    assert_raises(
        ValueError,
        lambda: fusion_system.get_current_qubit_block(-1),
    )
    assert_raises(
        ValueError,
        lambda: fusion_system.get_current_qubit_block(2),
    )


def test_identity_moves_between_positions():
    """Check that R moves identities while preserving permanent IDs."""
    fusion_system = FusionSystem(2)

    anyon_3 = fusion_system.get_anyon(3)
    anyon_4 = fusion_system.get_anyon(4)

    fusion_system.tree._swap_siblings(3, 4)

    assert fusion_system.get_current_anyon_order() == (
        1, 2, 4, 3, 5, 6, 7, 8,
    )

    assert fusion_system.get_anyon_at_position(3) is anyon_4
    assert fusion_system.get_anyon_at_position(4) is anyon_3

    # Lookup by ID still returns the same permanent identity.
    assert fusion_system.get_anyon(3) is anyon_3
    assert fusion_system.get_anyon(4) is anyon_4

    # Position-based qubit blocks follow the current leaf order.
    assert block_ids(fusion_system, 0) == (1, 2, 4, 3)
    assert block_ids(fusion_system, 1) == (5, 6, 7, 8)

    # The original AnyonicQubit ownership is not rewritten in 10.1.
    assert tuple(
        anyon.get_id()
        for anyon in fusion_system.get_qubit(0).anyons
    ) == (1, 2, 3, 4)


def test_inverse_restores_positions():
    """Check that the inverse position swap restores the initial order."""
    fusion_system = FusionSystem(2)
    initial_order = fusion_system.get_current_anyon_order()

    fusion_system.tree._swap_siblings(3, 4)
    fusion_system.tree._swap_siblings(3, 4)

    assert fusion_system.get_current_anyon_order() == initial_order
    assert block_ids(fusion_system, 0) == (1, 2, 3, 4)
    assert block_ids(fusion_system, 1) == (5, 6, 7, 8)


def test_basis_uses_current_qubit_blocks():
    """Check that basis metadata follows current positional qubit blocks."""
    fusion_system = FusionSystem(2)

    fusion_system.tree._swap_siblings(3, 4)

    moved_basis = FusionBasis(
        tree=fusion_system.tree,
        qubits=fusion_system.qubits,
        total_charge=Charge.VACUUM,
    )

    assert moved_basis.tree_signature == (
        ((1, 2), (4, 3)),
        ((5, 6), (7, 8)),
    )

    assert len(moved_basis.states) == 13
    assert len(moved_basis.computational_indices) == 4
    assert len(moved_basis.leakage_indices) == 9

    assert set(moved_basis.logical_to_physical) == {
        "00",
        "01",
        "10",
        "11",
    }

    q0_root = moved_basis.qubit_paths[0]["root"]
    q1_root = moved_basis.qubit_paths[1]["root"]

    q0_subtree = fusion_system.tree.get_node_at_path(
        q0_root
    )
    q1_subtree = fusion_system.tree.get_node_at_path(
        q1_root
    )

    q0_ids = tuple(
        anyon.get_id()
        for anyon in fusion_system.tree.flatten(q0_subtree)
    )
    q1_ids = tuple(
        anyon.get_id()
        for anyon in fusion_system.tree.flatten(q1_subtree)
    )

    assert q0_ids == (1, 2, 4, 3)
    assert q1_ids == (5, 6, 7, 8)

def test_basis_reindexing_after_position_swap():
    """Check state reindexing between bases with swapped sibling leaves."""
    fusion_system = FusionSystem(2)

    old_basis = fusion_system.basis
    old_state_vector = np.arange(
        len(old_basis.states),
        dtype=complex,
    )

    fusion_system.hilbertSpace.state_vector = (
        old_state_vector.copy()
    )

    fusion_system.tree._swap_siblings(3, 4)

    new_basis = FusionBasis(
        tree=fusion_system.tree,
        qubits=fusion_system.qubits,
        total_charge=Charge.VACUUM,
    )

    reindex_map = old_basis.get_reindex_map(
        new_basis
    )

    new_state_vector = (
        fusion_system.hilbertSpace.state_vector_in_basis(
            new_basis
        )
    )

    assert len(reindex_map) == 13
    assert set(reindex_map) == set(range(13))

    for old_index, new_index in enumerate(reindex_map):
        assert (
            new_state_vector[new_index]
            == old_state_vector[old_index]
        )

    # Computing the mapped vector must not commit any changes.
    assert fusion_system.basis is old_basis
    assert fusion_system.hilbertSpace.basis is old_basis
    assert np.array_equal(
        fusion_system.hilbertSpace.state_vector,
        old_state_vector,
    )


def test_basis_reindexing_preserves_norm():
    """Check that pure reindexing leaves the statevector norm unchanged."""
    fusion_system = FusionSystem(2)

    normalized_state = np.arange(
        1,
        len(fusion_system.basis.states) + 1,
        dtype=complex,
    )
    normalized_state /= np.linalg.norm(normalized_state)

    fusion_system.hilbertSpace.state_vector = (
        normalized_state.copy()
    )

    fusion_system.tree._swap_siblings(3, 4)

    new_basis = FusionBasis(
        tree=fusion_system.tree,
        qubits=fusion_system.qubits,
        total_charge=Charge.VACUUM,
    )

    mapped_state = (
        fusion_system.hilbertSpace.state_vector_in_basis(
            new_basis
        )
    )

    assert np.isclose(
        np.linalg.norm(mapped_state),
        1.0,
    )

    assert np.array_equal(
        fusion_system.hilbertSpace.state_vector,
        normalized_state,
    )


def test_basis_reindexing_validation():
    """Check rejection of incompatible basis reindexing requests."""
    fusion_system = FusionSystem(2)
    one_qubit_system = FusionSystem(1)

    assert_raises(
        TypeError,
        lambda: fusion_system.basis.get_reindex_map(None),
    )

    assert_raises(
        ValueError,
        lambda: fusion_system.basis.get_reindex_map(
            one_qubit_system.basis
        ),
    )


def test_commit_validation_and_copy():
    """Check commit input validation and defensive statevector copying."""
    fusion_system = FusionSystem(1)

    assert_raises(
        TypeError,
        lambda: fusion_system._commit_basis_state(
            None,
            fusion_system.hilbertSpace.state_vector,
        ),
    )
    assert_raises(
        TypeError,
        lambda: fusion_system._commit_basis_state(
            fusion_system.basis,
            [1, 0],
        ),
    )
    assert_raises(
        ValueError,
        lambda: fusion_system._commit_basis_state(
            fusion_system.basis,
            np.zeros(3, dtype=complex),
        ),
    )

    source_vector = np.array(
        [0.25 + 0.5j, 0.75 - 0.5j],
        dtype=complex,
    )
    expected_vector = source_vector.copy()

    fusion_system._commit_basis_state(
        fusion_system.basis,
        source_vector,
    )

    source_vector[:] = 0

    assert np.array_equal(
        fusion_system.hilbertSpace.state_vector,
        expected_vector,
    )


def main():
    """Run all section 10 braiding-convention checks."""
    test_initial_position_metadata()
    print("Initial position metadata: PASS")

    test_position_validation()
    print("Position validation: PASS")

    test_identity_moves_between_positions()
    print("Moving anyon identities: PASS")

    test_inverse_restores_positions()
    print("Inverse position restoration: PASS")

    test_basis_uses_current_qubit_blocks()
    print("Position-based FusionBasis paths: PASS")

    test_basis_reindexing_after_position_swap()
    print("FusionBasis reindexing: PASS")

    test_basis_reindexing_preserves_norm()
    print("Reindexing norm preservation: PASS")

    test_basis_reindexing_validation()
    print("Reindexing validation: PASS")

    test_commit_validation_and_copy()
    print("Commit validation and copy: PASS")

    print("All section 10 braiding-convention tests passed.")


if __name__ == "__main__":
    main()
