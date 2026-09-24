"""Section 3: recursive fusion-state enumeration tests."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qitker.anyons.Anyon import Charge
from qitker.anyons.FusionSystem import FusionSystem


EXPECTED_SECTORS = {1: (2, 3, 5), 2: (13, 21, 34), 3: (89, 144, 233)}


def test_enumeration(qubits_num, expected):
    """Check recursive enumeration counts and the shape of every state."""
    fusion_system = FusionSystem(qubits_num)
    states = fusion_system.basis._enumerate_subtree(fusion_system.tree.structure)
    vacuum_expected, tau_expected, total_expected = expected
    assert len(states) == total_expected
    assert sum(s["total"] is Charge.VACUUM for s in states) == vacuum_expected
    assert sum(s["total"] is Charge.TAU for s in states) == tau_expected
    internal_nodes = 4 * qubits_num - 1
    # A full binary tree with 4n leaves has 4n - 1 internal labels.
    for state in states:
        assert set(state) == {"total", "labels"}
        assert len(state["labels"]) == internal_nodes
        assert state["labels"][()] is state["total"]
        assert all(isinstance(path, tuple) for path in state["labels"])
        assert all(isinstance(charge, Charge) for charge in state["labels"].values())


def main():
    """Run enumeration checks for four, eight, and twelve anyons."""
    for qubits_num, expected in EXPECTED_SECTORS.items():
        test_enumeration(qubits_num, expected)
        print(f"{4 * qubits_num} anyon enumeration: PASS")
    print("Section 3 fusion-state enumeration tests passed.")


if __name__ == "__main__":
    main()
