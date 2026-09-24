"""Section 6: computational/leakage classification tests."""

import sys
from itertools import product
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qitker.anyons.Anyon import Charge
from qitker.anyons.FusionSystem import FusionSystem


EXPECTED_COUNTS = {
    1: (2, 0),
    2: (4, 9),
    3: (8, 81),
}


def assert_raises(expected_exception, function):
    """Verify that calling function raises the expected exception."""
    try:
        function()
    except expected_exception:
        return
    raise AssertionError(f"Expected {expected_exception.__name__} to be raised.")


def test_classification(qubits_num, expected_counts):
    """Check the complete split between computational and leakage states."""
    basis = FusionSystem(qubits_num).basis
    computational_expected, leakage_expected = expected_counts
    computational = set(basis.computational_indices)
    leakage = set(basis.leakage_indices)
    all_indices = set(range(len(basis.states)))

    assert len(computational) == computational_expected
    assert len(leakage) == leakage_expected
    assert computational.isdisjoint(leakage)
    assert computational | leakage == all_indices

    expected_labels = {
        # Every n-bit logical label must map to one physical basis state.
        "".join(bits) for bits in product("01", repeat=qubits_num)
    }
    assert set(basis.logical_to_physical) == expected_labels
    assert set(basis.physical_to_logical.values()) == expected_labels

    for logical_label, physical_index in basis.logical_to_physical.items():
        # Confirm both map directions and the pair-charge encoding of each bit.
        state = basis.get_state(physical_index)
        assert physical_index in computational
        assert basis.physical_to_logical[physical_index] == logical_label
        assert basis._get_logical_label(state) == logical_label

        for qubit_id, bit in enumerate(logical_label):
            paths = basis.qubit_paths[qubit_id]
            expected_charge = Charge.VACUUM if bit == "0" else Charge.TAU
            assert state["labels"][paths["left_pair"]] is expected_charge
            assert state["labels"][paths["right_pair"]] is expected_charge

    for physical_index in leakage:
        assert not basis._is_computational(basis.get_state(physical_index))

    if leakage:
        leakage_state = basis.get_state(next(iter(leakage)))
        assert_raises(ValueError, lambda: basis._get_logical_label(leakage_state))


def main():
    """Run classification checks for one, two, and three qubits."""
    for qubits_num, expected in EXPECTED_COUNTS.items():
        test_classification(qubits_num, expected)
        print(f"{qubits_num} qubit computational/leakage classification: PASS")
    print("Section 6 classification tests passed.")


if __name__ == "__main__":
    main()
