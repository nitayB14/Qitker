"""Section 15: verify the braid-group relations of the physical sigma engine."""

import sys
from pathlib import Path

import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent)
)

from qitker.anyons.FusionSystem import FusionSystem


def assert_coherent(fusion_system):
    """Check tree, basis, and HilbertSpace agreement after a braid word."""
    fusion_system._validate_system_coherence()
    assert fusion_system.basis.classify_logical is True
    assert fusion_system.basis.tree_signature == fusion_system.tree.to_ids()
    assert fusion_system.hilbertSpace.basis is fusion_system.basis
    assert np.isclose(
        np.linalg.norm(fusion_system.hilbertSpace.state_vector),
        1.0,
    )


def run_local_word(qubits_num, qubit_id, word, input_index):
    """Apply one local braid word to a selected physical basis vector."""
    fusion_system = FusionSystem(qubits_num)
    fusion_system.hilbertSpace.state_vector[:] = 0
    fusion_system.hilbertSpace.state_vector[input_index] = 1

    for sigma_index in word:
        fusion_system.sigma(qubit_id, sigma_index)

    assert len(fusion_system.operation_history) == len(word)
    assert_coherent(fusion_system)
    return fusion_system


def assert_local_words_equal(qubits_num, qubit_id, left_word, right_word):
    """Compare two braid words on every state of the physical fusion basis."""
    dimension = len(FusionSystem(qubits_num).basis.states)

    # Testing every basis vector compares the complete physical operators,
    # including their action on leakage states in the 13-dimensional case.
    for input_index in range(dimension):
        left = run_local_word(
            qubits_num,
            qubit_id,
            left_word,
            input_index,
        )
        right = run_local_word(
            qubits_num,
            qubit_id,
            right_word,
            input_index,
        )

        assert left.tree.to_ids() == right.tree.to_ids()
        assert (
            left.get_current_anyon_order()
            == right.get_current_anyon_order()
        )
        assert np.allclose(
            left.hilbertSpace.state_vector,
            right.hilbertSpace.state_vector,
        )


def run_disjoint_word(word, input_index):
    """Apply a word whose entries identify both qubit and local sigma."""
    fusion_system = FusionSystem(2)
    fusion_system.hilbertSpace.state_vector[:] = 0
    fusion_system.hilbertSpace.state_vector[input_index] = 1

    for qubit_id, sigma_index in word:
        fusion_system.sigma(qubit_id, sigma_index)

    assert_coherent(fusion_system)
    return fusion_system


def test_yang_baxter_sigma_1_sigma_2():
    """Check sigma1 sigma2 sigma1 = sigma2 sigma1 sigma2."""
    assert_local_words_equal(
        1,
        0,
        [1, 2, 1],
        [2, 1, 2],
    )


def test_yang_baxter_sigma_2_sigma_3():
    """Check sigma2 sigma3 sigma2 = sigma3 sigma2 sigma3."""
    assert_local_words_equal(
        1,
        0,
        [2, 3, 2],
        [3, 2, 3],
    )


def test_distant_generators_commute():
    """Check that sigma1 and sigma3 commute inside one qubit."""
    assert_local_words_equal(
        1,
        0,
        [1, 3],
        [3, 1],
    )


def test_generators_and_inverses():
    """Check both inverse orders for all three local generators."""
    for sigma_index in (1, 2, 3):
        assert_local_words_equal(
            1,
            0,
            [sigma_index, -sigma_index],
            [],
        )
        assert_local_words_equal(
            1,
            0,
            [-sigma_index, sigma_index],
            [],
        )


def test_relations_in_full_13d_space():
    """Check local braid relations on computational and leakage states."""
    for qubit_id in (0, 1):
        assert_local_words_equal(
            2,
            qubit_id,
            [1, 2, 1],
            [2, 1, 2],
        )
        assert_local_words_equal(
            2,
            qubit_id,
            [2, 3, 2],
            [3, 2, 3],
        )
        assert_local_words_equal(
            2,
            qubit_id,
            [1, 3],
            [3, 1],
        )


def test_different_qubits_commute():
    """Check that braid operations on separate qubit blocks commute."""
    dimension = len(FusionSystem(2).basis.states)
    left_word = [(0, 2), (1, -3)]
    right_word = [(1, -3), (0, 2)]

    for input_index in range(dimension):
        left = run_disjoint_word(left_word, input_index)
        right = run_disjoint_word(right_word, input_index)

        assert left.tree.to_ids() == right.tree.to_ids()
        assert (
            left.get_current_anyon_order()
            == right.get_current_anyon_order()
        )
        assert np.allclose(
            left.hilbertSpace.state_vector,
            right.hilbertSpace.state_vector,
        )


def main():
    """Run all section 15 braid-relation checks."""
    test_yang_baxter_sigma_1_sigma_2()
    print("Yang-Baxter sigma1/sigma2: PASS")

    test_yang_baxter_sigma_2_sigma_3()
    print("Yang-Baxter sigma2/sigma3: PASS")

    test_distant_generators_commute()
    print("Distant local generators: PASS")

    test_generators_and_inverses()
    print("Generator inverses: PASS")

    test_relations_in_full_13d_space()
    print("Full 13D physical relations: PASS")

    test_different_qubits_commute()
    print("Different-qubit commutation: PASS")

    print("All section 15 braid-relation tests passed.")


if __name__ == "__main__":
    main()
