"""Section 4: global-total-charge filtering tests."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qitker.anyons.Anyon import Charge
from qitker.anyons.FusionSystem import FusionSystem


EXPECTED_VACUUM_DIMENSIONS = {1: 2, 2: 13, 3: 89, 4: 610, 5: 4181, 6: 28657}


def test_total_charge_filter(qubits_num, expected_dimension):
    """Check that only the requested global vacuum sector is retained."""
    basis = FusionSystem(qubits_num).basis
    assert basis._total_charge is Charge.VACUUM
    assert len(basis.states) == expected_dimension
    assert all(state["total"] is Charge.VACUUM for state in basis.states)
    assert all(state["labels"][()] is Charge.VACUUM for state in basis.states)


def main():
    """Verify the physical vacuum-sector dimensions through six qubits."""
    for qubits_num, expected in EXPECTED_VACUUM_DIMENSIONS.items():
        test_total_charge_filter(qubits_num, expected)
        print(f"{qubits_num} qubit vacuum sector ({expected} states): PASS")
    print("Section 4 total-charge filtering tests passed.")


if __name__ == "__main__":
    main()
