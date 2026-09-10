"""Section 7: FusionBasis ownership and FusionSystem integration tests."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qitker.anyons.Anyon import Charge
from qitker.anyons.FusionBasis import FusionBasis
from qitker.anyons.FusionSystem import FusionSystem


def test_fusion_system_owns_basis():
    """Check that FusionSystem creates and owns the expected FusionBasis."""
    fusion_system = FusionSystem(3)
    basis = fusion_system.basis

    assert isinstance(basis, FusionBasis)
    assert basis._tree is fusion_system.tree
    assert basis._qubits is fusion_system.qubits
    assert basis._total_charge is Charge.VACUUM
    assert basis.tree_signature == fusion_system.tree.to_ids()
    assert len(basis.states) == 89
    assert len(basis.computational_indices) == 8
    assert len(basis.leakage_indices) == 81
    assert set(basis.logical_to_physical) == {
        "000", "001", "010", "011", "100", "101", "110", "111"
    }


def test_hilbert_space_uses_owned_basis():
    """Check that HilbertSpace uses the same physical basis instance."""
    fusion_system = FusionSystem(3)
    assert fusion_system.hilbertSpace.basis is fusion_system.basis
    assert fusion_system.hilbertSpace.dimension == len(fusion_system.basis.states)
    assert fusion_system.hilbertSpace.dimension == 89
    assert fusion_system.hilbertSpace.state_vector.shape == (89,)


def main():
    """Run the section 7 FusionBasis integration checks."""
    test_fusion_system_owns_basis()
    test_hilbert_space_uses_owned_basis()
    print("Section 7 FusionBasis integration tests passed.")


if __name__ == "__main__":
    main()
