import sys
from pathlib import Path

import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent)
)

from qitker.anyons.FusionSystem import FusionSystem


def test_initial_state_probabilities():
    fusion_system = FusionSystem(2)
    space = fusion_system.hilbertSpace

    assert np.isclose(
        space.computational_probability(),
        1.0,
    )

    assert np.isclose(
        space.leakage_probability(),
        0.0,
    )

    assert np.isclose(
        space.computational_probability()
        + space.leakage_probability(),
        1.0,
    )

    print("Initial probabilities: PASS")


def test_full_leakage_state():
    fusion_system = FusionSystem(2)
    space = fusion_system.hilbertSpace

    leakage_index = (
        space.basis.leakage_indices[0]
    )

    space.state_vector[:] = 0
    space.state_vector[leakage_index] = 1

    assert np.isclose(
        space.computational_probability(),
        0.0,
    )

    assert np.isclose(
        space.leakage_probability(),
        1.0,
    )

    assert (
        space._decode_measurement(
            leakage_index
        )
        == "LEAKAGE"
    )

    # A deterministic leakage state must always
    # produce a LEAKAGE measurement.
    assert space.run_measurements(100) == {
        "LEAKAGE": 100
    }

    print("Full leakage state: PASS")


def test_mixed_computational_and_leakage_state():
    fusion_system = FusionSystem(2)
    space = fusion_system.hilbertSpace

    computational_index = (
        space.basis.logical_to_physical["00"]
    )

    leakage_index = (
        space.basis.leakage_indices[0]
    )

    space.state_vector[:] = 0

    space.state_vector[
        computational_index
    ] = np.sqrt(0.8)

    space.state_vector[
        leakage_index
    ] = np.sqrt(0.2)

    computational_probability = (
        space.computational_probability()
    )

    leakage_probability = (
        space.leakage_probability()
    )

    assert np.isclose(
        computational_probability,
        0.8,
    )

    assert np.isclose(
        leakage_probability,
        0.2,
    )

    assert np.isclose(
        computational_probability
        + leakage_probability,
        1.0,
    )

    assert np.isclose(
        np.linalg.norm(space.state_vector),
        1.0,
    )

    print("Mixed state probabilities: PASS")


def test_computational_measurement_decoding():
    fusion_system = FusionSystem(2)
    space = fusion_system.hilbertSpace
    basis = fusion_system.basis

    for logical_label, physical_index in (
        basis.logical_to_physical.items()
    ):
        decoded_result = (
            space._decode_measurement(
                physical_index
            )
        )

        assert decoded_result == logical_label

    print("Computational decoding: PASS")


def test_deterministic_logical_measurement():
    fusion_system = FusionSystem(2)
    space = fusion_system.hilbertSpace

    target_label = "11"

    target_index = (
        space.basis.logical_to_physical[
            target_label
        ]
    )

    space.state_vector[:] = 0
    space.state_vector[target_index] = 1

    assert space.run_measurements(100) == {
        target_label: 100
    }

    assert np.isclose(
        space.computational_probability(),
        1.0,
    )

    assert np.isclose(
        space.leakage_probability(),
        0.0,
    )

    print("Logical measurement: PASS")


def main():
    test_initial_state_probabilities()
    test_full_leakage_state()
    test_mixed_computational_and_leakage_state()
    test_computational_measurement_decoding()
    test_deterministic_logical_measurement()

    print()
    print(
        "All leakage probability and "
        "measurement tests passed."
    )


if __name__ == "__main__":
    main()