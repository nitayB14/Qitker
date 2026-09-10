"""Section 8: physical Hilbert-space initialization and dimension tests."""

import sys
from pathlib import Path

import numpy as np

sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent)
)

from qitker.anyons.FusionSystem import FusionSystem


EXPECTED_DIMENSIONS = {
    1: 2,
    2: 13,
    3: 89,
}


def test_physical_hilbert_space():
    """Check physical dimensions, initial logical state, and unit norm."""
    for qubits_num, expected_dimension in (
        EXPECTED_DIMENSIONS.items()
    ):
        # Each system starts in the physical basis state encoding |00...0>.
        fusion_system = FusionSystem(qubits_num)

        basis = fusion_system.basis
        hilbert_space = fusion_system.hilbertSpace

        initial_label = "0" * qubits_num
        initial_index = (
            basis.logical_to_physical[
                initial_label
            ]
        )

        # HilbertSpace owns the same basis.
        assert hilbert_space.basis is basis

        # Physical dimension.
        assert hilbert_space.qubits_num == qubits_num
        assert (
            hilbert_space.dimension
            == expected_dimension
        )
        assert hilbert_space.state_vector.shape == (
            expected_dimension,
        )

        # Correct initial physical basis state.
        assert (
            hilbert_space.state_vector[
                initial_index
            ]
            == 1
        )

        assert np.count_nonzero(
            hilbert_space.state_vector
        ) == 1

        # The initial state is computational |00...0>.
        assert (
            initial_index
            in basis.computational_indices
        )

        assert (
            basis.physical_to_logical[
                initial_index
            ]
            == initial_label
        )

        # No initial amplitude appears in leakage states.
        assert np.allclose(
            hilbert_space.state_vector[
                basis.leakage_indices
            ],
            0,
        )

        # Statevector is normalized.
        assert np.isclose(
            np.linalg.norm(
                hilbert_space.state_vector
            ),
            1.0,
        )

        print(f"{qubits_num} qubits:")
        print(
            f"  physical dimension: "
            f"{hilbert_space.dimension}"
        )
        print(
            f"  initial label:       "
            f"{initial_label}"
        )
        print(
            f"  initial index:       "
            f"{initial_index}"
        )
        print("  norm:                1")
        print("  result:              PASS")
        print()


def main():
    """Run all section 8 physical Hilbert-space checks."""
    test_physical_hilbert_space()
    print(
        "All physical HilbertSpace tests passed."
    )


if __name__ == "__main__":
    main()
