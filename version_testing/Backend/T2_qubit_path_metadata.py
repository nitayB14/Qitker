"""Section 2: logical-qubit path metadata tests."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from qitker.anyons.FusionSystem import FusionSystem


def ids_in_subtree(tree, path):
    """Return the ordered anyon IDs contained below a tree path."""
    node = tree.get_node_at_path(path)
    return [anyon.get_id() for anyon in tree.flatten(node)]


def test_qubit_paths(qubits_num):
    """Check root and pair paths for every logical qubit in a system."""
    fusion_system = FusionSystem(qubits_num)
    for qubit in fusion_system.qubits:
        # Each stored path must lead to the expected physical anyon group.
        paths = fusion_system.basis.qubit_paths[qubit.qubit_id]
        assert set(paths) == {"root", "left_pair", "right_pair"}
        assert ids_in_subtree(fusion_system.tree, paths["root"]) == qubit.get_id_list()
        assert ids_in_subtree(fusion_system.tree, paths["left_pair"]) == [
            anyon.get_id() for anyon in qubit.get_left_pair()
        ]
        assert ids_in_subtree(fusion_system.tree, paths["right_pair"]) == [
            anyon.get_id() for anyon in qubit.get_right_pair()
        ]


def main():
    """Run path-metadata checks for systems of one through four qubits."""
    for qubits_num in range(1, 5):
        test_qubit_paths(qubits_num)
        print(f"{qubits_num} qubit path metadata: PASS")
    print("Section 2 qubit-path metadata tests passed.")


if __name__ == "__main__":
    main()
