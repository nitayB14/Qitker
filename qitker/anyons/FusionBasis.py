from qitker.anyons.Anyon import Anyon, Charge, fusion_outcomes
from qitker.anyons.FusionTree import FusionTree
from qitker.anyons.AnyonicQubit import AnyonicQubit


class FusionBasis:
    """
    Describes a fusion basis for one FusionTree topology.

    The basis stores metadata and index mappings only. Quantum amplitudes
    belong to HilbertSpace and are not stored here.

    Attributes:
        qubits_num:
            Number of logical four-anyon qubits represented by the basis.
        tree_signature:
            Snapshot of the anyon-ID tree topology used to build the basis.
        qubit_paths:
            Paths to each qubit root and its left and right fusion pairs.
        states:
            Valid fusion-charge labelings with the requested total charge.
        state_to_index:
            Reverse mapping from an immutable state key to its basis index.
        computational_indices:
            Indices whose logical-qubit block totals are all vacuum.
        leakage_indices:
            Valid physical indices outside the computational subspace.
        logical_to_physical:
            Maps a logical bitstring to its physical fusion-basis index.
        physical_to_logical:
            Maps a computational physical index back to its bitstring.
    """

    def __init__(self, tree: FusionTree, qubits: list[AnyonicQubit], total_charge: Charge = Charge.VACUUM,):
        """Initialize the containers for a basis tied to 'tree' ."""
        self._validate_inputs(tree, qubits, total_charge)

        # Objects that define which physical fusion space this basis describes.
        self._tree = tree
        self._qubits = qubits
        self.qubits_num = len(self._qubits)
        self._total_charge = total_charge

        # Snapshot and path metadata for the current tree topology.
        self.tree_signature = tree.to_ids()
        self.qubit_paths = {}

        # Ordered physical basis and its reverse index lookup.
        self.states = []
        self.state_to_index = {}

        # Partition of the physical basis into logical and leakage subspaces.
        self.computational_indices = []
        self.leakage_indices = []

        # Translation between logical bitstrings and physical basis indices.
        self.logical_to_physical = {}
        self.physical_to_logical = {}

        self._build_qubit_paths()

        all_states = self._enumerate_subtree(
            self._tree.structure
        )

        self.states = [state for state in all_states if state["total"] is self._total_charge]

        self.state_to_index = {
            self._state_key(state["labels"]): index
            for index, state in enumerate(self.states)
        }

        if len(self.state_to_index) != len(self.states):
            raise ValueError(
                "Fusion basis contains duplicate states."
            )

        self._classify_states()



    @staticmethod
    def _validate_inputs(
        tree: FusionTree,
        qubits: list[AnyonicQubit],
        total_charge: Charge,
    ) -> None:
        """Validate that the tree, qubits, and charge describe one system."""
        if not isinstance(tree, FusionTree):
            raise TypeError("tree must be a FusionTree object.")

        if not isinstance(qubits, list):
            raise TypeError("qubits must be a list.")

        if not qubits:
            raise ValueError("qubits must contain at least one logical qubit.")

        if not all(isinstance(qubit, AnyonicQubit) for qubit in qubits):
            raise TypeError(
                "Every element in qubits must be an AnyonicQubit object."
            )

        if not isinstance(total_charge, Charge):
            raise TypeError("total_charge must be a Charge value.")

        if (
            tree.total_charge is not None
            and tree.total_charge is not total_charge
        ):
            raise ValueError(
                "total_charge must match the FusionTree total charge."
            )

        qubit_ids = [qubit.qubit_id for qubit in qubits]

        if len(qubit_ids) != len(set(qubit_ids)):
            raise ValueError("Logical qubit IDs must be unique.")

        if qubit_ids != list(range(len(qubits))):
            raise ValueError(
                "Logical qubits must be ordered with IDs from 0 to n-1."
            )

        qubit_anyons = [
            anyon
            for qubit in qubits
            for anyon in qubit.anyons
        ]
        qubit_anyon_ids = [anyon.get_id() for anyon in qubit_anyons]

        if len(qubit_anyon_ids) != len(set(qubit_anyon_ids)):
            raise ValueError("An anyon cannot belong to multiple qubits.")

        if not all(anyon.get_charge() is Charge.TAU for anyon in qubit_anyons):
            raise ValueError(
                "Every physical anyon in the four-anyon encoding must be TAU."
            )

        tree_anyons = tree.flatten()

        if not all(isinstance(anyon, Anyon) for anyon in tree_anyons):
            raise TypeError("Every FusionTree leaf must be an Anyon object.")

        tree_anyon_ids = [anyon.get_id() for anyon in tree_anyons]

        if len(tree_anyon_ids) != len(set(tree_anyon_ids)):
            raise ValueError("FusionTree anyon IDs must be unique.")

        if set(tree_anyon_ids) != set(qubit_anyon_ids):
            raise ValueError(
                "FusionTree leaves must match the anyons owned by qubits."
            )


    @staticmethod
    def _common_path(paths: list[tuple]) -> tuple:
        """Return the longest common prefix shared by all paths."""

        if not paths:
            raise ValueError(
                "paths must contain at least one path."
            )

        common = []

        for directions in zip(*paths):
            if len(set(directions)) != 1:
                break

            common.append(directions[0])

        return tuple(common)


    def _build_qubit_paths(self) -> None:
        """Build logical-qubit paths from current leaf positions."""

        current_anyons = self._tree.flatten()
        qubit_paths = {}

        for qubit_id in range(self.qubits_num):
            start = 4 * qubit_id
            end = start + 4
            block_anyons = current_anyons[start:end]

            if len(block_anyons) != 4:
                raise ValueError(
                    f"Qubit block {qubit_id} does not contain "
                    "exactly four anyons."
                )

            leaf_paths = [
                self._tree.find_path(anyon.get_id())
                for anyon in block_anyons
            ]

            if any(path is None for path in leaf_paths):
                raise ValueError(
                    f"Qubit block {qubit_id} was not found "
                    "completely in the fusion tree."
                )

            qubit_paths[qubit_id] = {
                "root": self._common_path(leaf_paths),
                "left_pair": self._common_path(leaf_paths[:2]),
                "right_pair": self._common_path(leaf_paths[2:]),
            }

        self.qubit_paths = qubit_paths

    def _enumerate_subtree(
        self,
        node,
        path: tuple = (),
    ) -> list[dict]:
        """Enumerate all valid fusion labelings of a subtree."""

        if not isinstance(node, tuple):
            return [
                {
                    "total": node.get_charge(),
                    "labels": {},
                }
            ]

        left_states = self._enumerate_subtree(
            node[0],
            path + (0,),
        )

        right_states = self._enumerate_subtree(
            node[1],
            path + (1,),
        )

        states = []

        for left_state in left_states:
            for right_state in right_states:
                outcomes = fusion_outcomes(
                    left_state["total"],
                    right_state["total"],
                )

                for total_charge in outcomes:
                    states.append({
                        "total": total_charge,
                        "labels": {
                            **left_state["labels"],
                            **right_state["labels"],
                            path: total_charge,
                        },
                    })

        return states

    def get_reindex_map(self, new_basis: "FusionBasis",) -> tuple[int, ...]:
        """
        Map every index in this basis to its matching index
        in another basis with the same fusion-label space.
        """

        if not isinstance(new_basis, FusionBasis):
            raise TypeError(
                "new_basis must be a FusionBasis object."
            )

        if len(self.states) != len(new_basis.states):
            raise ValueError(
                "Fusion bases have different dimensions."
            )

        reindex_map = []

        for state in self.states:
            try:
                new_index = new_basis.get_index(state)
            except ValueError as error:
                raise ValueError(
                    "Fusion bases do not contain the same "
                    "fusion-label states."
                ) from error

            reindex_map.append(new_index)

        if len(set(reindex_map)) != len(reindex_map):
            raise ValueError(
                "Fusion-basis mapping is not one-to-one."
            )

        return tuple(reindex_map)


    @staticmethod
    def _state_key(labels: dict) -> tuple:
        """Return an immutable, consistently ordered state-label key."""

        if not isinstance(labels, dict):
            raise TypeError(
                "labels must be a dictionary."
            )

        return tuple(
            sorted(
                labels.items(),
                key=lambda item: item[0],
            )
        )


    def get_state(self, index: int) -> dict:
        """Return the basis state stored at a physical index."""

        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(
                "index must be an integer."
            )

        if index < 0 or index >= len(self.states):
            raise IndexError(
                "basis state index is out of range."
            )

        return self.states[index]


    def get_index(self, state: dict) -> int:
        """Return the physical index of a state in this fusion basis."""

        if not isinstance(state, dict):
            raise TypeError(
                "state must be a dictionary."
            )

        if "labels" not in state:
            raise ValueError(
                "state must contain labels."
            )

        key = self._state_key(state["labels"])

        if key not in self.state_to_index:
            raise ValueError(
                "state does not belong to this fusion basis."
            )

        return self.state_to_index[key]


    def _is_computational(self, state: dict) -> bool:
        """Return whether a physical state encodes valid logical qubits."""

        return all(
            state["labels"][paths["root"]]
            is Charge.VACUUM
            for paths in self.qubit_paths.values()
        )


    def _get_logical_label(self, state: dict) -> str:
        """Decode the logical bitstring of a computational state."""

        if not self._is_computational(state):
            raise ValueError(
                "Cannot decode a leakage state."
            )

        bits = []

        for paths in self.qubit_paths.values():
            left_pair_charge = state["labels"][
                paths["left_pair"]
            ]

            bit = (
                "0"
                if left_pair_charge is Charge.VACUUM
                else "1"
            )

            bits.append(bit)

        return "".join(bits)


    def _classify_states(self) -> None:
        """Classify states and build logical-to-physical mappings."""

        for index, state in enumerate(self.states):
            if not self._is_computational(state):
                self.leakage_indices.append(index)
                continue

            logical_label = self._get_logical_label(state)

            if logical_label in self.logical_to_physical:
                raise ValueError(
                    f"Duplicate logical state: {logical_label}."
                )

            self.computational_indices.append(index)
            self.logical_to_physical[logical_label] = index
            self.physical_to_logical[index] = logical_label
