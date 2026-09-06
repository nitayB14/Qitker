
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from itertools import product

from qitker.anyons.Anyon import Charge, fusion_outcomes
from qitker.anyons.FusionBasis import FusionBasis
from qitker.anyons.FusionSystem import FusionSystem


EXPECTED_DIMENSIONS = {
    1: {
        "vacuum": 2,
        "tau": 3,
        "all": 5,
        "computational": 2,
        "leakage": 0,
    },
    2: {
        "vacuum": 13,
        "tau": 21,
        "all": 34,
        "computational": 4,
        "leakage": 9,
    },
    3: {
        "vacuum": 89,
        "tau": 144,
        "all": 233,
        "computational": 8,
        "leakage": 81,
    },
    4: {
        "vacuum": 610,
        "tau": 987,
        "all": 1597,
        "computational": 16,
        "leakage": 594,
    },
    5: {
        "vacuum": 4181,
        "tau": 6765,
        "all": 10946,
        "computational": 32,
        "leakage": 4149,
    },
    6: {
        "vacuum": 28657,
        "tau": 46368,
        "all": 75025,
        "computational": 64,
        "leakage": 28593,
    },
}


def assert_raises(expected_exception, function):
    try:
        function()
    except expected_exception:
        return

    raise AssertionError(
        f"Expected {expected_exception.__name__} "
        "to be raised."
    )


def build_basis(qubits_num):
    fusion_system = FusionSystem(qubits_num)

    basis = FusionBasis(
        tree=fusion_system.tree,
        qubits=fusion_system.qubits,
        total_charge=Charge.VACUUM,
    )

    return fusion_system, basis


def test_fusion_rules():
    assert fusion_outcomes(
        Charge.VACUUM,
        Charge.VACUUM,
    ) == (Charge.VACUUM,)

    assert fusion_outcomes(
        Charge.VACUUM,
        Charge.TAU,
    ) == (Charge.TAU,)

    assert fusion_outcomes(
        Charge.TAU,
        Charge.VACUUM,
    ) == (Charge.TAU,)

    assert fusion_outcomes(
        Charge.TAU,
        Charge.TAU,
    ) == (
        Charge.VACUUM,
        Charge.TAU,
    )

    assert_raises(
        TypeError,
        lambda: fusion_outcomes(
            "tau",
            Charge.TAU,
        ),
    )

    assert_raises(
        TypeError,
        lambda: fusion_outcomes(
            Charge.TAU,
            "tau",
        ),
    )

    print("Fusion rules: PASS")


def test_qubit_paths(fusion_system, basis):
    for qubit in fusion_system.qubits:
        paths = basis.qubit_paths[qubit.qubit_id]

        root_node = fusion_system.tree.get_node_at_path(
            paths["root"]
        )
        left_pair_node = (
            fusion_system.tree.get_node_at_path(
                paths["left_pair"]
            )
        )
        right_pair_node = (
            fusion_system.tree.get_node_at_path(
                paths["right_pair"]
            )
        )

        root_ids = [
            anyon.get_id()
            for anyon in fusion_system.tree.flatten(
                root_node
            )
        ]

        left_pair_ids = [
            anyon.get_id()
            for anyon in fusion_system.tree.flatten(
                left_pair_node
            )
        ]

        right_pair_ids = [
            anyon.get_id()
            for anyon in fusion_system.tree.flatten(
                right_pair_node
            )
        ]

        expected_root_ids = qubit.get_id_list()

        expected_left_ids = [
            anyon.get_id()
            for anyon in qubit.get_left_pair()
        ]

        expected_right_ids = [
            anyon.get_id()
            for anyon in qubit.get_right_pair()
        ]

        assert root_ids == expected_root_ids
        assert left_pair_ids == expected_left_ids
        assert right_pair_ids == expected_right_ids


def test_enumeration(fusion_system, basis, expected):
    all_states = basis._enumerate_subtree(
        fusion_system.tree.structure
    )

    vacuum_states = [
        state
        for state in all_states
        if state["total"] is Charge.VACUUM
    ]

    tau_states = [
        state
        for state in all_states
        if state["total"] is Charge.TAU
    ]

    assert len(all_states) == expected["all"]
    assert len(vacuum_states) == expected["vacuum"]
    assert len(tau_states) == expected["tau"]

    assert (
        len(vacuum_states) + len(tau_states)
        == len(all_states)
    )

    expected_internal_nodes = (
        4 * fusion_system.qubits_num - 1
    )

    for state in all_states:
        assert "total" in state
        assert "labels" in state

        assert isinstance(state["labels"], dict)

        assert len(state["labels"]) == (
            expected_internal_nodes
        )

        assert state["labels"][()] is state["total"]

        assert all(
            isinstance(path, tuple)
            for path in state["labels"]
        )

        assert all(
            isinstance(charge, Charge)
            for charge in state["labels"].values()
        )


def test_filtered_states(basis, expected):
    assert len(basis.states) == expected["vacuum"]

    assert all(
        state["total"] is Charge.VACUUM
        for state in basis.states
    )

    assert all(
        state["labels"][()] is Charge.VACUUM
        for state in basis.states
    )


def test_state_keys(basis):
    assert len(basis.state_to_index) == len(
        basis.states
    )

    generated_keys = [
        basis._state_key(state["labels"])
        for state in basis.states
    ]

    assert len(generated_keys) == len(
        set(generated_keys)
    )

    for key in generated_keys:
        assert isinstance(key, tuple)

        assert all(
            isinstance(item, tuple)
            and len(item) == 2
            for item in key
        )

    first_labels = basis.states[0]["labels"]

    reversed_labels = dict(
        reversed(
            list(first_labels.items())
        )
    )

    assert basis._state_key(first_labels) == (
        basis._state_key(reversed_labels)
    )


def test_state_index_round_trip(basis):
    for expected_index, expected_state in enumerate(
        basis.states
    ):
        actual_state = basis.get_state(
            expected_index
        )

        actual_index = basis.get_index(
            expected_state
        )

        assert actual_state == expected_state
        assert actual_index == expected_index

        copied_state = {
            "total": expected_state["total"],
            "labels": dict(
                expected_state["labels"]
            ),
        }

        assert basis.get_index(
            copied_state
        ) == expected_index

    assert_raises(
        TypeError,
        lambda: basis.get_state(True),
    )

    assert_raises(
        TypeError,
        lambda: basis.get_state(1.5),
    )

    assert_raises(
        IndexError,
        lambda: basis.get_state(-1),
    )

    assert_raises(
        IndexError,
        lambda: basis.get_state(
            len(basis.states)
        ),
    )

    assert_raises(
        TypeError,
        lambda: basis.get_index("state"),
    )

    assert_raises(
        ValueError,
        lambda: basis.get_index({}),
    )

    unknown_labels = dict(
        basis.states[0]["labels"]
    )

    unknown_labels[(999,)] = Charge.TAU

    unknown_state = {
        "total": Charge.VACUUM,
        "labels": unknown_labels,
    }

    assert_raises(
        ValueError,
        lambda: basis.get_index(
            unknown_state
        ),
    )


def test_classification(
    fusion_system,
    basis,
    expected,
):
    computational = set(
        basis.computational_indices
    )

    leakage = set(
        basis.leakage_indices
    )

    all_indices = set(
        range(len(basis.states))
    )

    assert len(computational) == (
        expected["computational"]
    )

    assert len(leakage) == expected["leakage"]

    assert computational.isdisjoint(leakage)

    assert computational | leakage == all_indices

    assert all(
        basis._is_computational(
            basis.get_state(index)
        )
        for index in computational
    )

    assert all(
        not basis._is_computational(
            basis.get_state(index)
        )
        for index in leakage
    )

    expected_logical_labels = {
        "".join(bits)
        for bits in product(
            "01",
            repeat=fusion_system.qubits_num,
        )
    }

    assert set(
        basis.logical_to_physical
    ) == expected_logical_labels

    assert set(
        basis.physical_to_logical.values()
    ) == expected_logical_labels

    assert len(
        basis.logical_to_physical
    ) == expected["computational"]

    assert len(
        basis.physical_to_logical
    ) == expected["computational"]

    for logical_label, physical_index in (
        basis.logical_to_physical.items()
    ):
        assert physical_index in computational

        assert (
            basis.physical_to_logical[
                physical_index
            ]
            == logical_label
        )

        state = basis.get_state(
            physical_index
        )

        assert basis._get_logical_label(
            state
        ) == logical_label

        for qubit_id, bit in enumerate(
            logical_label
        ):
            paths = basis.qubit_paths[
                qubit_id
            ]

            left_charge = state["labels"][
                paths["left_pair"]
            ]

            right_charge = state["labels"][
                paths["right_pair"]
            ]

            expected_charge = (
                Charge.VACUUM
                if bit == "0"
                else Charge.TAU
            )

            assert left_charge is expected_charge

            # In a computational four-anyon
            # encoding, both pair channels match.
            assert right_charge is expected_charge

    if leakage:
        leakage_index = next(iter(leakage))
        leakage_state = basis.get_state(
            leakage_index
        )

        assert_raises(
            ValueError,
            lambda: basis._get_logical_label(
                leakage_state
            ),
        )


def test_one_basis(qubits_num):
    expected = EXPECTED_DIMENSIONS[
        qubits_num
    ]

    fusion_system, basis = build_basis(
        qubits_num
    )

    test_qubit_paths(
        fusion_system,
        basis,
    )

    test_enumeration(
        fusion_system,
        basis,
        expected,
    )

    test_filtered_states(
        basis,
        expected,
    )

    test_state_keys(basis)

    test_state_index_round_trip(basis)

    test_classification(
        fusion_system,
        basis,
        expected,
    )

    print(f"{qubits_num} qubits:")
    print(
        f"  all fusion states: {expected['all']}"
    )
    print(
        f"  total VACUUM:      "
        f"{len(basis.states)}"
    )
    print(
        f"  total TAU:         {expected['tau']}"
    )
    print(
        f"  computational:     "
        f"{len(basis.computational_indices)}"
    )
    print(
        f"  leakage:           "
        f"{len(basis.leakage_indices)}"
    )
    print(
        f"  unique keys:       "
        f"{len(basis.state_to_index)}"
    )
    print(
        f"  round trips:       "
        f"{len(basis.states)}/"
        f"{len(basis.states)}"
    )
    print("  result:            PASS")
    print()


def main():
    test_fusion_rules()

    for qubits_num in range(1, 7):
        test_one_basis(qubits_num)

    print("All FusionBasis tests passed.")


if __name__ == "__main__":
    main()