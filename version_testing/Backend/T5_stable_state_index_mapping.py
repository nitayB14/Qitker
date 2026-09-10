"""Section 5: stable fusion-state index mapping tests."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qitker.anyons.Anyon import Charge
from qitker.anyons.FusionSystem import FusionSystem


def assert_raises(expected_exception, function):
    """Verify that calling function raises the expected exception."""
    try:
        function()
    except expected_exception:
        return
    raise AssertionError(f"Expected {expected_exception.__name__} to be raised.")


def test_stable_keys_and_round_trips(qubits_num):
    """Check unique stable keys and state/index round trips."""
    basis = FusionSystem(qubits_num).basis
    assert len(basis.state_to_index) == len(basis.states)

    keys = [basis._state_key(state["labels"]) for state in basis.states]
    assert len(keys) == len(set(keys))

    for expected_index, expected_state in enumerate(basis.states):
        assert basis.get_state(expected_index) == expected_state
        assert basis.get_index(expected_state) == expected_index
        copied_state = {
            "total": expected_state["total"],
            "labels": dict(expected_state["labels"]),
        }
        assert basis.get_index(copied_state) == expected_index

    labels = basis.states[0]["labels"]
    # Dictionary insertion order must not affect the immutable state key.
    reversed_labels = dict(reversed(list(labels.items())))
    assert basis._state_key(labels) == basis._state_key(reversed_labels)


def test_mapping_validation():
    """Check validation for invalid physical indices and unknown states."""
    basis = FusionSystem(1).basis
    assert_raises(TypeError, lambda: basis.get_state(True))
    assert_raises(IndexError, lambda: basis.get_state(-1))
    assert_raises(IndexError, lambda: basis.get_state(len(basis.states)))
    assert_raises(TypeError, lambda: basis.get_index("state"))
    assert_raises(ValueError, lambda: basis.get_index({}))

    unknown_labels = dict(basis.states[0]["labels"])
    unknown_labels[(999,)] = Charge.TAU
    assert_raises(
        ValueError,
        lambda: basis.get_index({"total": Charge.VACUUM, "labels": unknown_labels}),
    )


def main():
    """Run stable-index tests for systems of one through four qubits."""
    for qubits_num in range(1, 5):
        test_stable_keys_and_round_trips(qubits_num)
        print(f"{qubits_num} qubit stable index mapping: PASS")
    test_mapping_validation()
    print("Section 5 stable state-index mapping tests passed.")


if __name__ == "__main__":
    main()
