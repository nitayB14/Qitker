
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from itertools import product

from qitker.anyons.Anyon import Charge
from qitker.anyons.FusionBasis import FusionBasis
from qitker.anyons.FusionSystem import FusionSystem




def test_fusion_system_owns_basis():
    fusion_system = FusionSystem(3)

    basis = fusion_system.basis

    # FusionSystem created a real FusionBasis.
    assert isinstance(basis, FusionBasis)

    # The basis belongs to this exact tree and qubit list.
    assert basis._tree is fusion_system.tree
    assert basis._qubits is fusion_system.qubits

    # The global physical charge is vacuum.
    assert basis._total_charge is Charge.VACUUM

    # The basis was built from the current tree topology.
    assert (
        basis.tree_signature
        == fusion_system.tree.to_ids()
    )

    # Three qubits have an 89-dimensional physical space.
    assert len(basis.states) == 89
    assert len(basis.computational_indices) == 8
    assert len(basis.leakage_indices) == 81

    # All physical states belong to exactly one subspace.
    assert (
        len(basis.computational_indices)
        + len(basis.leakage_indices)
        == len(basis.states)
    )

    # Logical/physical mappings contain all 3-qubit states.
    assert set(basis.logical_to_physical) == {
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    }

    # Section 7 must not change HilbertSpace yet.
    assert fusion_system.hilbertSpace.qubits_num == 3
    assert fusion_system.hilbertSpace.dimension == 8
    assert fusion_system.hilbertSpace.state_vector.shape == (8,)

    print("FusionSystem owns FusionBasis: PASS")
    print(f"  physical states:      {len(basis.states)}")
    print(
        "  computational states: "
        f"{len(basis.computational_indices)}"
    )
    print(
        f"  leakage states:       "
        f"{len(basis.leakage_indices)}"
    )
    print(
        f"  old Hilbert dimension: "
        f"{fusion_system.hilbertSpace.dimension}"
    )


def main():
    test_fusion_system_owns_basis()
    print("All FusionSystem section 7 tests passed.")


if __name__ == "__main__":
    main()